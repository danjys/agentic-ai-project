from fastapi import APIRouter, File, UploadFile, HTTPException, Response
from tempfile import NamedTemporaryFile
import os
from app.services import orthanc, monai, dicom_utils

router = APIRouter()

@router.get("/process/health")
async def health_check():
    return {"status": "ok"}

@router.post("/process/health")
async def health_check_post():
    return {"status": "ok"}

@router.get("/process/monai_test")
async def monai_test():
    try:
        predicted_class = monai.run_monai_test()
        return {"predicted_class": predicted_class}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MONAI test failed: {str(e)}")

@router.post("/upload_dicom")
async def upload_dicom(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".dcm"):
        raise HTTPException(status_code=400, detail="Only .dcm (DICOM) files are supported.")

    tmp_path = None
    try:
        contents = await file.read()

        orthanc_response = await orthanc.upload_dicom_to_orthanc(contents)

        with NamedTemporaryFile(delete=False, suffix=".dcm") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        metadata = dicom_utils.parse_dicom_metadata(tmp_path)

        return {
            "message": "DICOM file uploaded successfully and sent to Orthanc.",
            "orthanc_id": orthanc_response.get("ID", "Unknown"),
            **metadata
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process DICOM file: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.get("/retrieve_dicom/{orthanc_id}")
def retrieve_dicom(orthanc_id: str):
    try:
        content = orthanc.retrieve_dicom_from_orthanc(orthanc_id)
        return Response(content=content, media_type="application/dicom")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orthanc retrieval failed: {e}")

@router.get("/search_studies")
def search_studies(patient_id: str = None, study_date: str = None):
    try:
        results = orthanc.search_studies(patient_id, study_date)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")
