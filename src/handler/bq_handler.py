from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from datetime import date
from typing import cast

def check_has_updated(project_id: str, dataset_id: str, table_id: str, start_date: str, end_date: str) -> bool:
    """
        Checks if the table contains records for today's date (column dt).
        
        Args:
            project_id (str): GCP project ID.
            dataset_id (str): BigQuery dataset ID.
            table_id (str): Table name.
        
        Returns:
            bool: True if records exist for today, False otherwise.
    """
    client = bigquery.Client(project=project_id)
    today = date.today().strftime("%Y-%m-%d")

    query = f"""
        SELECT COUNT(1) AS total
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE dt = '{today}'
    """

    try:
        result = client.query(query).result()
        for row in result:
            return cast(bool, row.total > 0)
    except NotFound:
        return False
    except Exception as e:

        print(f"An unexpected error occurred during BigQuery query: {e}")
        return False

    return False

def trigger_procedure(project_id: str, dataset_id: str, procedure_name: str) -> None:
    """
    Triggers a stored procedure in BigQuery with error handling.
    
    Args:
        project_id (str): GCP project ID.
        dataset_id (str): BigQuery dataset ID.
        procedure_name (str): The procedure name to call.
    """
    client = bigquery.Client(project=project_id)

    query = f"""
        CALL `{project_id}.{dataset_id}.{procedure_name}`();
    """

    try:
        query_job = client.query(query)
        query_job.result()  # Wait for completion
        print(f"Procedure {procedure_name} executed successfully.")
    except Exception as e:
        print(f"Failed to execute procedure {procedure_name}. Error: {e}")