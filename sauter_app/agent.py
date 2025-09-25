from google.adk.agents import Agent, LlmAgent
from google.adk.tools import google_search, FunctionTool, agent_tool
from google.cloud import bigquery
import datetime

GEMINI_MODEL = "gemini-2.5-flash"

def consulta_reservatorio(nome_reservatorio: str, data_inicio: str, data_fim: str) -> dict:
    """
    Consulta o BigQuery para calcular o volume médio de um reservatório em um período específico.
    """
    try:
        if data_fim.lower() in ["hoje", "atual", "recente"]:
            data_fim = datetime.date.today().strftime('%Y-%m-%d')

        client = bigquery.Client()
        query = """
            SELECT AVG(ear_reservatorio_percentual) as volume_medio_percentual
            FROM `sauter-project.ons_trusted.ear_diario_por_reservatorio`
            WHERE lower(nom_reservatorio) LIKE lower(@nome_reservatorio_param)
              AND ear_data BETWEEN @data_inicio_param AND @data_fim_param
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("nome_reservatorio_param", "STRING", f"%{nome_reservatorio}%"),
                bigquery.ScalarQueryParameter("data_inicio_param", "DATE", data_inicio),
                bigquery.ScalarQueryParameter("data_fim_param", "DATE", data_fim),
            ]
        )
        results = client.query(query, job_config=job_config).to_dataframe()

        if results.empty or results.iloc[0]["volume_medio_percentual"] is None:
            return {"status": "not_found", "message": f"Nenhum dado encontrado para '{nome_reservatorio}'."}

        return {
            "status": "success",
            "reservatorio": nome_reservatorio,
            "periodo": f"{data_inicio} a {data_fim}",
            "volume_medio_percentual": round(results.iloc[0]["volume_medio_percentual"], 2)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

bigquery_function_tool = FunctionTool(func=consulta_reservatorio)

sauter_agent = Agent(
    name="sauter_info_agent",
    model=GEMINI_MODEL,
    description="Agente para responder perguntas sobre a empresa Sauter Digital.",
    tools=[google_search],
    instruction="""
    Você responde perguntas sobre a empresa Sauter Digital.
    Sempre use a ferramenta google_search com o filtro 'site:sauter.digital' 
    para garantir que as informações sejam obtidas exclusivamente desse domínio.
    """
)

ons_agent = Agent(
    name="ons_data_agent",
    model=GEMINI_MODEL,
    description="Agente para responder dúvidas sobre volumes de reservatórios usando BigQuery.",
    tools=[bigquery_function_tool],
    instruction="""
    Você é um especialista em dados da ONS.
    Sua tarefa é:
    1. Extrair da pergunta o nome do reservatório, a data de início e a data de fim.
    2. Se a data final for "hoje", use a data atual do sistema.
    3. Sempre chame a ferramenta `consulta_reservatorio` com esses parâmetros.
    4. Retorne o relatório claro e objetivo com o valor médio encontrado.
    """
)

root_agent = LlmAgent(
    name="HelpDeskCoordinator",
    model=GEMINI_MODEL,
    description="Orquestrador principal que direciona perguntas para os agentes corretos.",
    instruction="""
    Você é o agente orquestrador principal do Help Desk.
    Encaminhe a pergunta para:
    - 'sauter_info_agent' se for sobre a empresa Sauter Digital ou informações do site sauter.digital.
    - 'ons_data_agent' se for sobre reservatórios, volumes de água ou dados históricos da ONS.
    Se não tiver certeza, peça esclarecimentos ao usuário.
    """,
    tools=[
        agent_tool.AgentTool(agent=sauter_agent),
        agent_tool.AgentTool(agent=ons_agent)
    ],
)
