
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from google.cloud import bigquery
import math


def fetch_records_from_bq(table_id: str, page_size: int, cursor: Optional[str] = None):
    client = bigquery.Client(project="sauter-project")
    
    if cursor:
        query = f"""
            SELECT *
            FROM `{table_id}`
            WHERE DATE(ear_data) > DATE('{cursor}')
            ORDER BY DATE(ear_data) ASC
            LIMIT {page_size}
        """
    else:
        query = f"""
            SELECT *
            FROM `{table_id}`
            ORDER BY DATE(ear_data) ASC
            LIMIT {page_size}
        """
    
    try:
        query_job = client.query(query)
        records = list(query_job.result())
        
        # Contar registros restantes
        if records:
            last_ear_data = records[-1]["ear_data"]
            count_query = f"""
                SELECT COUNT(*) as remaining
                FROM `{table_id}`
                WHERE DATE(ear_data) > DATE('{last_ear_data}')
            """
            count_job = client.query(count_query)
            remaining_count = list(count_job.result())[0].remaining
        else:
            remaining_count = 0

        pages_remaining = math.ceil(remaining_count / page_size)
        return records, pages_remaining

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

def paginate_records(results, pages_remaining):
    records = [dict(row) for row in results]
    next_cursor = records[-1]["ear_data"] if records else None
    return {
        "data": records,
        "next_cursor": next_cursor,
        "pages_remaining": pages_remaining
    }