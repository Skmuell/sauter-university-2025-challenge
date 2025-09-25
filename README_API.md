# Projeto: Download e Upload de Recursos ONS

# Autor da api: João Samuel Leal de Oliveira

## 1. Resumo Executivo

Este projeto fornece uma **API em FastAPI** que automatiza o download de arquivos Parquet da base de dados do ONS, filtra por período, converte colunas para string e faz o upload para o **Google Cloud Storage (GCS)**.

O sistema garante:

* Automação do download de recursos de pacotes ONS
* Filtragem de recursos por intervalo de datas
* Conversão segura de tipos de dados
* Upload organizado para GCS com data no caminho (`dt=YYYY-MM-DD`)
* Limpeza local após upload
* Observabilidade por logs e tratamento de erros

---

## 2. Casos de Uso

1. **Download de recursos Parquet de pacotes ONS**: o usuário fornece `package_id` e intervalo de datas.
2. **Upload para GCS**: arquivos baixados são enviados para o bucket configurado.
3. **API para solicitação de dados**: endpoint `/get_data` retorna lista de recursos baixados.

---

## 3. Fluxo de Dados

### Sequência de Chamadas

1. `POST /get_data` → `request_ons()`
2. `get_resource_ids(package_id)` → obtém lista de recursos Parquet
3. `filter_by_year()` → filtra recursos por datas
4. `download_resources()` → baixa e converte arquivos
5. `upload_folder_to_gcs()` → envia arquivos para GCS
6. Retorna JSON final ao usuário

---

## 4. Guia de Implementação

### Pré-requisitos

* Python >= 3.11
* Pacotes do `requirements.txt`
* Conta e bucket no **Google Cloud Storage**
* Configuração de autenticação GCP (`gcloud auth application-default login`)

### Setup Local

```bash
git clone <[repo_url](https://github.com/Skmuell/sauter-university-2025-challenge.git)>
cd <repo_folder>
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
mkdir -p src/downloads
```

### Rodar a API

```bash
uvicorn api:app --reload
```

API disponível em `http://127.0.0.1:8000`.

### Testar Download e Upload

Fazer `POST` no endpoint `/get_data` com JSON:

```json
[
  {
 
  "package_name": "ear_diario_por_reservatorio",
  "package_id": "61e92787-9847-4731-8b73-e878eb5bc158",
  "start_date": "",
  "end_date": ""

  }
]  
```

* Ver logs no console ou em `download_ear.log`
* Verificar upload no GCS:

```
gs://<bucket>/ons/ear_diario_por_reservatorio/dt=<YYYY-MM-DD>/
```

### Reversão

Para reverter upload: deletar arquivos do GCS ou restaurar backup local.

---

## 5. Testes e Validação

* **Entrada:** pacote ONS válido com recursos Parquet
* **Saída:** arquivos baixados, convertidos, enviados para GCS, JSON de sucesso
* **Logs:** `download_ear.log`

---

## 6. Observabilidade e Runbook

* Logs locais: `download_ear.log`
* Upload GCS: mensagens no console
* Dashboard sugerido: Cloud Logging / Monitoring

**Passos para incidentes comuns**:

1. Download falhou → verificar URL/pacote ONS
2. Upload falhou → verificar autenticação GCP/permissões
3. Erros JSON → validar input do POST

---

## 7. Segurança

* Nunca commitar secrets (`.env` ou `.env.example`)
* Bucket GCS com permissões mínimas: `Storage Object Admin`
* Validar que dados sensíveis não aparecem nos logs

---

## 8. Decisões Arquiteturais

* Parquet como padrão → fácil leitura e compatibilidade com Pandas
* Upload diário com dt=YYYY-MM-DD → organiza dados por dia
* FastAPI → leve, assíncrona e fácil integração
* Pasta local limpa após upload → evita acúmulo de dados

---

## 9. Changelog

| Data       | Alterações                                             |
| ---------- | ------------------------------------------------------ |
| 2025-09-20 | Estrutura inicial da API, download de recursos Parquet |
| 2025-09-21 | Upload para GCS, limpeza de pastas locais              |
| 2025-09-22 | Logging, filtragem por ano, tratamento de erros        |

---

## 10. Requirements.txt

```
fastapi
uvicorn
pydantic
requests
pandas
pyarrow
google-cloud-storage
bigquery
```


