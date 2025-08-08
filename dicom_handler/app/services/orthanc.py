import httpx
from app.config import ORTHANC_URL, ORTHANC_USERNAME, ORTHANC_PASSWORD

async def upload_dicom_to_orthanc(dicom_bytes: bytes):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ORTHANC_URL,
            content=dicom_bytes,
            auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD),
            headers={"Content-Type": "application/dicom"}
        )
        response.raise_for_status()
        return response.json()

def retrieve_dicom_from_orthanc(orthanc_id: str):
    # synchronous version for now; can async if needed
    import requests
    r = requests.get(
        f"{ORTHANC_URL}/instances/{orthanc_id}/file",
        auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD)
    )
    r.raise_for_status()
    return r.content

def search_studies(patient_id=None, study_date=None):
    import requests
    query = {"Level": "Study", "Query": {}}
    if patient_id:
        query["Query"]["PatientID"] = patient_id
    if study_date:
        query["Query"]["StudyDate"] = study_date
    r = requests.post(f"{ORTHANC_URL}/tools/find", json=query, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    r.raise_for_status()
    return r.json()
