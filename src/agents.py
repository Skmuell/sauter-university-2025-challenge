import os
import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# --- CONFIGURAÇÃO INICIAL ---
PROJECT_ID = "seu-projeto-gcp"  # <<<--- ATENÇÃO: MUDE AQUI
LOCATION = "us-central1"

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(model_name="gemini-1.5-flash-001")
except Exception as e:
    print(f"Erro ao inicializar Vertex AI: {e}")
    model = None

KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'sauter_knowledge.txt')
MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_ons_data.csv')

class SauterInfoAgent:
    def __init__(self):
        try:
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                self.knowledge = f.read()
        except FileNotFoundError:
            self.knowledge = ""
    
    def answer(self, question: str) -> str:
        if not self.knowledge or not model: return "Agente da Sauter indisponível."
        prompt = f"""Você é um assistente especialista sobre a empresa Sauter. Responda à pergunta do usuário usando APENAS a informação do contexto abaixo. Se a resposta não estiver no contexto, diga 'Não encontrei essa informação na minha base de dados sobre a Sauter.'
        --- CONTEXTO ---
        {self.knowledge}
        --- FIM DO CONTEXTO ---
        Pergunta do Usuário: "{question}"
        Resposta:"""
        response = model.generate_content(prompt)
        return response.text

class EnaDataAgent:
    def __init__(self):
        try:
            self.dataframe = pd.read_csv(MOCK_DATA_FILE)
        except FileNotFoundError:
            self.dataframe = None

    def answer(self, question: str) -> str:
        if self.dataframe is None or not model: return "Agente de dados indisponível."
        bacia_encontrada = next((bacia for bacia in self.dataframe['bacia'].unique() if bacia.lower() in question.lower()), None)
        if not bacia_encontrada: return "Não identifiquei uma bacia hidrográfica na sua pergunta."
        
        filtered_data = self.dataframe[self.dataframe['bacia'] == bacia_encontrada]
        prompt = f"""Você é um analista de dados especialista em Energia Natural Afluente (ENA). Responda à pergunta do usuário usando APENAS os dados da tabela abaixo.
        --- DADOS ---
        {filtered_data.to_string()}
        --- FIM DOS DADOS ---
        Pergunta do Usuário: "{question}"
        Resposta Concisa:"""
        response = model.generate_content(prompt)
        return response.text

class OrchestratorAgent:
    def __init__(self):
        self.sauter_agent = SauterInfoAgent()
        self.ena_agent = EnaDataAgent()
    
    def handle_question(self, question: str) -> str:
        if not model: return "Serviço de IA indisponível."
        
        routing_prompt = Part.from_text(f"""
        Classifique a pergunta do usuário para o especialista correto. Responda APENAS com 'sauter_agent' ou 'data_agent'.
        - 'sauter_agent': perguntas sobre a empresa Sauter.
        - 'data_agent': perguntas sobre dados, volumes de água, bacias, reservatórios ou ENA.
        Pergunta: "{question}"
        Especialista:""")
        
        response = model.generate_content(routing_prompt, generation_config={"candidate_count": 1, "temperature": 0})
        chosen_agent = response.text.strip()
        
        print(f"DEBUG: Roteado para -> {chosen_agent}")

        if "sauter_agent" in chosen_agent:
            return self.sauter_agent.answer(question)
        elif "data_agent" in chosen_agent:
            return self.ena_agent.answer(question)
        else:
            return "Não consegui determinar o especialista para sua pergunta."