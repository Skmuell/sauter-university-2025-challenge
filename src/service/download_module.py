import requests
import logging
from datetime import datetime
from typing import List, Dict
from datetime import timedelta
from typing import Optional



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("download_ear.log"), logging.StreamHandler()]
)


def download_excel_file(url: str, output_excel: str) -> str:
    """
    Downloads an Excel file from a URL and saves it locally.
    
    :param url: URL of the Excel file
    :param output_excel: Path where the Excel file will be saved
    :return: Path to the saved Excel file
    """
    try:
        print(f"Downloading file: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_excel, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"File downloaded and saved as: {output_excel}")
        return output_excel
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        raise


def filter_by_year(
    data: List[Dict],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Filters a list of dicts to keep only items where the year
    extracted from item["name"] is within the range of start_date and end_date.
    
    If start_date or end_date are empty, uses yesterday and today as the interval.
    """
    if not start_date or not end_date:
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        start_year = yesterday.year
        end_year = today.year
    else:
        start_year = datetime.strptime(start_date, "%d-%m-%Y").year
        end_year   = datetime.strptime(end_date, "%d-%m-%Y").year

    return [
        item for item in data
        if start_year <= int(item["name"].split("-")[-1]) <= end_year
    ]


def download_resources(json_data: Dict):
    """
    Receives a JSON with 'data' containing resource IDs, downloads each CSV, 
    and saves it locally with the resource name.
    """
    for item in json_data.get("data", []):
        resource_id = item.get("id")
        resource_name = item.get("name", resource_id)

        if not resource_id:
            continue  

        url = f"https://dados.ons.org.br/api/3/action/resource_show?id={resource_id}"
        res = requests.get(url).json()

        resource_url = res.get("result", {}).get("url")
        if not resource_url:
            print(f"URL não encontrada para {resource_id}")
            continue

        file_res = requests.get(resource_url)
        filename = f"{resource_name}.parquet"

        with open(filename, "wb") as f:
            f.write(file_res.content)

        print(f"Download concluído: {filename}")