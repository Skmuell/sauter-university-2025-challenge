from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.cloud import bigquery
from google.genai.types import Tool, GenerateContentConfig
#from google.adk.tools import url_context
import datetime

GEMINI_MODEL = "gemini-2.5-pro" 

def ativar_url_context_sauter(pergunta: str) -> dict:
    """
    Ativa o url_context para acessar o site da Sauter baseado no tipo de pergunta
    """
    pergunta_lower = pergunta.lower()
    
    if any(p in pergunta_lower for p in ['endereço', 'localização', 'contato', 'telefone', 'email']):
        urls = ["https://sauter.digital/contato/", "https://sauter.digital/"]
    elif any(p in pergunta_lower for p in ['serviços', 'serviço', 'o que faz', 'soluções']):
        urls = ["https://sauter.digital/servicos/", "https://sauter.digital/"]
    elif any(p in pergunta_lower for p in ['sobre', 'quem somos', 'história', 'empresa']):
        urls = ["https://sauter.digital/quem-somos/", "https://sauter.digital/"]
    elif any(p in pergunta_lower for p in ['parceiros', 'parcerias', 'clientes', 'cases']):
        urls = ["https://sauter.digital/parceiros/", "https://sauter.digital/cases/"]
    else:
        urls = ["https://sauter.digital/", "https://sauter.digital/quem-somos/", "https://sauter.digital/servicos/", "https://sauter.digital/sauterimpact/"]
    
    return {
        "acao": "usar_url_context",
        "urls": urls,
        "instrucao": f"Acesse {', '.join(urls)} via url_context para responder: {pergunta}"
    }

url_context_tool = FunctionTool(func=ativar_url_context_sauter)

def consulta_reservatorio(nome_reservatorio: str, data_inicio: str, data_fim: str) -> dict:
    """
    Consulta o BigQuery para calcular o volume médio de um reservatório em um período específico.
    """
    try:
        # MUDANÇA 1: Deixando a ferramenta mais inteligente para entender "hoje"
        if data_fim.lower() in ["hoje", "recente", "mais recente", "atual"]:
            data_fim = datetime.date.today().strftime('%Y-%m-%d')

        client = bigquery.Client()
        table_path = "`sauter-project.ons_trusted.ear_diario_por_reservatorio`"
        coluna_volume = "ear_reservatorio_percentual"
        coluna_nome_reservatorio = "nom_reservatorio"
        coluna_data = "ear_data"

        query = f"""
            SELECT AVG({coluna_volume}) as volume_medio_percentual
            FROM {table_path}
            WHERE lower({coluna_nome_reservatorio}) LIKE lower(@nome_reservatorio_param)
            AND {coluna_data} BETWEEN @data_inicio_param AND @data_fim_param
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("nome_reservatorio_param", "STRING", f"%{nome_reservatorio}%"),
                bigquery.ScalarQueryParameter("data_inicio_param", "DATE", data_inicio),
                bigquery.ScalarQueryParameter("data_fim_param", "DATE", data_fim),
            ]
        )
        query_job = client.query(query, job_config=job_config)
        results = query_job.to_dataframe()
        
        if results.empty or results.iloc[0]['volume_medio_percentual'] is None:
            report = f"Não foram encontrados dados para o reservatório '{nome_reservatorio}' no período de {data_inicio} a {data_fim}."
        else:
            volume_medio = results.iloc[0]['volume_medio_percentual']
            report = f"O volume médio do reservatório '{nome_reservatorio}' entre {data_inicio} e {data_fim} foi de {volume_medio:.2f}%."

        return {"status": "success", "report": report}
    except Exception as e:
        print(f"ERRO no BigQuery: {e}")
        return {"status": "error", "error_message": str(e)}

bigquery_function_tool = FunctionTool(func=consulta_reservatorio)

sauter_agent = Agent(
    name="sauter_expert",
    model=GEMINI_MODEL,
    description="Especialista que usa url_context para acessar o site da Sauter em tempo real.",
    
    tools=[url_context_tool],
    
    instruction="""
    VOCÊ É UM ESPECIALISTA NA EMPRESA SAUTER.

    ⚠️ **REGRA ABSOLUTA:** USE URL_CONTEXT PARA TODAS AS PERGUNTAS SOBRE A SAUTER.

    **PROCEDIMENTO OBRIGATÓRIO:**
    1. Use a ferramenta 'ativar_url_context_sauter' para definir as URLs a serem acessadas
    2. A ferramenta retornará as URLs específicas do site da Sauter
    3. Use a funcionalidade nativa url_context do Gemini para acessar essas URLs
    4. Baseie sua resposta 100% no conteúdo extraído

    **COMO USAR URL_CONTEXT (conforme documentação oficial):**
    - O Gemini 2.0+ tem suporte nativo a url_context
    - Basta configurar a tool com {"url_context": {}}
    - O modelo automaticamente acessará as URLs mencionadas

    **EXEMPLO DE FLUXO CORRETO:**
    Usuário: "Quais serviços a Sauter oferece?"
    → ativar_url_context_sauter: "Acesse https://sauter.digital/servicos/ via url_context"
    → url_context: Extrai conteúdo da página de serviços
    → Você: Responde com base no conteúdo extraído

    **URLs PRINCIPAIS:**
    - https://sauter.digital/ (Página principal)
    - https://sauter.digital/servicos/ (Serviços)
    - https://sauter.digital/quem-somos/ (Sobre)
    - https://sauter.digital/contato/ (Contato)
    - https://sauter.digital/parceiros/ (Parceiros)
    - https://sauter.digital/cases/ (Cases)

    **NUNCA use conhecimento prévio!** Sempre acesse via url_context.
    """
)

ena_agent = Agent(
    name="data_expert",
    model=GEMINI_MODEL,
    description="Analista de dados que responde dúvidas sobre o volume de uma bacia hidrográfica em um determinado período.",
    tools=[bigquery_function_tool],
    instruction="""
    Você é um analista de dados especialista em dados históricos da ONS. Sua única tarefa é responder perguntas sobre volumes de reservatórios em períodos específicos.

    **PROCEDIMENTO OBRIGATÓRIO:**
    1.  Analise a pergunta do usuário para extrair as três informações essenciais: o `nome_reservatorio`, a `data_inicio` e a `data_fim`.
    2.  As datas devem estar no formato 'AAAA-MM-DD'. Se o usuário disser "em janeiro de 2024", use `data_inicio='2024-01-01'` e `data_fim='2024-01-31'`.
    3.  **MUDANÇA 2: Ensinando o Agente a usar "hoje"**
        Se o usuário falar "até hoje", "data mais recente" ou "atual", passe a string "hoje" para o parâmetro `data_fim`.
    4.  Chame a ferramenta `consulta_reservatorio` passando os três parâmetros que você extraiu.
    5.  A ferramenta já retornará um relatório completo. Sua única tarefa é entregar este relatório ao usuário de forma clara.
    """
)

root_agent = Agent(
    name="orchestrator",
    model=GEMINI_MODEL,
    sub_agents=[sauter_agent, ena_agent],
    instruction="""
    Delegue para 'sauter_expert' se a pergunta mencionar Sauter ou temas corporativos.
    Delegue para 'data_expert' se for sobre dados, reservatórios, ONS.
    """
)