import requests
from bs4 import BeautifulSoup
import os

URLS = [
    "https://sauter.digital/",
    "https://sauter.digital/quem-somos/",
]
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'sauter_knowledge.txt')

def scrape_and_save():
    print("Iniciando a coleta de informações do site da Sauter...")
    full_text = ""
    for url in URLS:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            full_text += f"\n\n--- Conteúdo da página: {url} ---\n\n{text}"
            print(f"Sucesso ao extrair dados de: {url}")
        except requests.RequestException as e:
            print(f"Erro ao acessar a URL {url}: {e}")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\nConhecimento salvo com sucesso em: {OUTPUT_FILE}")
    except IOError as e:
        print(f"Erro ao salvar o arquivo: {e}")

if __name__ == "__main__":
    scrape_and_save()