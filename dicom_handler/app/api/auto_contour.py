from fastapi import APIRouter, HTTPException
from app.services import auto_contour_service

router = APIRouter()

@router.post("/process/auto_contour/{instance_id}")
async def auto_contour(instance_id: str):
    try:
        result = await auto_contour_service.run_auto_contour_pipeline(instance_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
