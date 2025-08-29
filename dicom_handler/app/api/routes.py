from fastapi import APIRouter, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
import os
import logging
import asyncio

from app.services import orthanc, auto_contour_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/process/health")
async def health():
    return {"status": "ok"}

@router.post("/upload_dicom_series")
async def upload_dicom_series(files: list[UploadFile] = File(...)):
    """
    Upload a full CT series (multiple DICOM files) to Orthanc and trigger auto-contouring
    once all slices are uploaded.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    instance_ids = []
    tmp_paths = []

    try:
        for file in files:
            if not file.filename.lower().endswith(".dcm"):
                raise HTTPException(status_code=400, detail=f"Only .dcm files supported: {file.filename}")

            contents = await file.read()
            response = await orthanc.upload_dicom_to_orthanc(contents)
            instance_id = response["ID"]
            instance_ids.append(instance_id)

            with NamedTemporaryFile(delete=False, suffix=".dcm") as tmp:
                tmp.write(contents)
                tmp_paths.append(tmp.name)

        # Trigger auto-contour pipeline asynchronously
        # Pass the first instance ID to fetch the whole study
        asyncio.create_task(auto_contour_service.run_auto_contour_pipeline(instance_ids[0], is_instance=True))

        return {"message": "DICOM series uploaded and auto-contour triggered", "instance_ids": instance_ids}

    finally:
        for tmp_path in tmp_paths:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
