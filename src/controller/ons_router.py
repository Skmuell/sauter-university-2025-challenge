import os
import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Request, Query, HTTPException, status
from pydantic import BaseModel
from google.cloud import bigquery
from src.utils.colored_log import create_logger
from src.service.ons_api import get_resource_ids
from src.service.download_module import filter_by_year, download_resources
from src.service.pagination import fetch_records_from_bq, paginate_records
from src.handler.gcs_handler import upload_folder_to_gcs
from src.handler.bq_handler import check_has_updated, trigger_procedure

logger = create_logger("logger")
router = APIRouter()

# Carrega variáveis de ambiente
load_dotenv()

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Variável de ambiente obrigatória '{name}' não está definida.")
    return value

project_id: str = get_env_var("PROJECT_ID")
dataset_id: str = get_env_var("BQ_DATASET")
table_id: str = get_env_var("BQ_TABLE")
dataset_trusted: str = get_env_var("DATASET_TRUSTED")
dataset_raw: str = get_env_var("DATASET_RAW")


@router.post("/download_upload", status_code=status.HTTP_200_OK)
async def request_ons(request: Request):
    try:
        body = await request.json()
        first = body[0]

        package_name = first.get("package_name")
        package_id = first.get("package_id")
        start_date = first.get("start_date")
        end_date = first.get("end_date")

        if not package_name or not package_id:
            raise HTTPException(status_code=400, detail="package_name ou package_id ausente")

        if check_has_updated(
            project_id=project_id,
            dataset_id=dataset_raw,
            table_id=package_name,
            start_date=start_date,
            end_date=end_date
        ):
            return {"message": "The data is already updated"}


        result = get_resource_ids(package_id)
        result_filtered = filter_by_year(result, start_date, end_date)
        download_resources({"data": result_filtered})
        upload_folder_to_gcs("sauter-project-raw", "src/downloads", package_name)
        trigger_procedure(project_id, dataset_trusted, "storage_procedure_atualizacao")

        return {
            "message": "Success!",
            "data": result_filtered,
            "start_date": start_date,
            "end_date": end_date
        }

    except Exception as e:
        return {"message": "Error", "detail": str(e)}


@router.get("/records")
async def get_records(
    page_size: int = Query(100, gt=0, le=100),
    cursor: Optional[str] = None  # YYYY-MM-DD
):
    table_full_id = f"{project_id}.{dataset_trusted}.{table_id}"
    results, pages_remaining = fetch_records_from_bq(table_full_id, page_size, cursor)
    response = paginate_records(results, pages_remaining)
    return response
