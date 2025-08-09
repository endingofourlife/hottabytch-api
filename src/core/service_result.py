from fastapi import HTTPException
from src.services import ServiceResult

def handle_service_result(result: ServiceResult):
    if result.is_success:
        return result.data
    raise HTTPException(status_code=result.status_code if result.status_code else 500, detail=result.error)