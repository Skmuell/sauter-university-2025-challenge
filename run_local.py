from src.agents import OrchestratorAgent

def main():
    print("Iniciando sistema de agentes. Digite 'sair' para terminar.")
    print("-" * 30)
    
    orchestrator = OrchestratorAgent()

    while True:
        try:
            question = input("\nSua pergunta: ")
            if question.lower() == 'sair':
                break
            if not question:
                continue

            response = orchestrator.handle_question(question)
            print("\n>> Resposta do Agente:", response)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nOcorreu um erro: {e}")
    
    print("\nEncerrando o sistema. Até logo!")

if __name__ == "__main__":
    main()