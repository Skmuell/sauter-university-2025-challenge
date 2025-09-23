from src.utils.colored_log import create_logger
from fastapi import status,APIRouter
from src.service.ons_api import get_resource_ids
from pydantic import BaseModel
from fastapi import Request
from src.service.download_module import filter_by_year
from src.service.download_module import download_resources


logger = create_logger("logger")
router = APIRouter()

class DataRequest(BaseModel):
    package_id: str
    start_date: str
    end_date: str


@router.post("/get_data", status_code=status.HTTP_200_OK)
async def request_ons(request: Request):
    try:
        body = await request.json()  
        print(body)

        first = body[0]
        package_name = first.get("package_name")
        package_id = first.get("package_id")
        start_date = first.get("start_date")
        end_date = first.get("end_date")

        result = get_resource_ids(package_id) 
        result_filtered = filter_by_year(result, start_date, end_date)

        download_resources({"data": result_filtered})
        
        return {
            "message": "Success!",
            "data": result_filtered,
            "start_date": start_date,
            "end_date": end_date
        }

    except Exception as e:
        return {
            "message": "Error",
            "detail": str(e)
        }
        

        

