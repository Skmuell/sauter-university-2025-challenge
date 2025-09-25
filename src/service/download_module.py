import requests
import logging
import os
import pandas as pd  # type: ignore
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import shutil
from handler.gcs_handler import upload_folder_to_gcs 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("download_ear.log"), logging.StreamHandler()]
)

DOWNLOAD_DIR = "src/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def filter_by_year(
    data: List[Dict],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Filters a list of dictionaries keeping only items whose year,
    extracted from the resource name, is within the range of start_date and end_date.
    
    If start_date or end_date are not provided, uses yesterday and today as the interval.
    """
    if not start_date or not end_date:
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        start_year = yesterday.year
        end_year = today.year
    else:
        start_year = datetime.strptime(start_date, "%d-%m-%Y").year
        end_year = datetime.strptime(end_date, "%d-%m-%Y").year

    return [
        item for item in data
        if start_year <= int(item["name"].split("-")[-1]) <= end_year
    ]


def download_resources(json_data: Dict):
    """
    Downloads each resource from the JSON, forces column types to string,
    saves them locally as Parquet in DOWNLOAD_DIR, overwriting originals.
    """
    for item in json_data.get("data", []):
        resource_id = item.get("id")
        resource_name = item.get("name", resource_id)

        if not resource_id:
            continue

        # Resource URL
        url = f"https://dados.ons.org.br/api/3/action/resource_show?id={resource_id}"
        res = requests.get(url).json()
        resource_url = res.get("result", {}).get("url")
        if not resource_url:
            logging.warning(f"URL not found for {resource_id}")
            continue

        # Local path
        filepath = os.path.join(DOWNLOAD_DIR, f"{resource_name}.parquet")

        # Download file
        file_res = requests.get(resource_url)
        with open(filepath, "wb") as f:
            f.write(file_res.content)

        # Read Parquet and force types
        df = pd.read_parquet(filepath)
        df = df.astype(str)
        df.to_parquet(filepath, index=False)

        logging.info(f"✅ Download and type conversion completed: {filepath}")
