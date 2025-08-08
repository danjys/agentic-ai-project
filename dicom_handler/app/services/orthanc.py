import httpx
import requests
from io import BytesIO
import pydicom
import numpy as np
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
    base_url = ORTHANC_URL.rsplit('/', 1)[0]  # strip '/instances' from config URL
    query = {"Level": "Study", "Query": {}}
    if patient_id:
        query["Query"]["PatientID"] = patient_id
    if study_date:
        query["Query"]["StudyDate"] = study_date

    r = requests.post(f"{base_url}/tools/find", json=query, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    r.raise_for_status()
    return r.json()

def get_series_ids(study_id: str):
    url = f"{ORTHANC_URL}/studies/{study_id}/series"
    r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    r.raise_for_status()
    return r.json()

def get_instance_ids(series_id: str):
    url = f"{ORTHANC_URL}/series/{series_id}/instances"
    r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    r.raise_for_status()
    return r.json()

def download_dicom_instance(instance_id: str) -> pydicom.Dataset:
    url = f"{ORTHANC_URL}/instances/{instance_id}/file"
    r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    r.raise_for_status()
    return pydicom.dcmread(BytesIO(r.content))

def load_volume_from_study(study_id: str) -> (np.ndarray, list):
    series_ids = get_series_ids(study_id)
    if not series_ids:
        raise Exception(f"No series found for study {study_id}")
    # For now, take the first series
    series_id = series_ids[0]
    instance_ids = get_instance_ids(series_id)
    if not instance_ids:
        raise Exception(f"No instances found in series {series_id}")
    slices = []
    for inst_id in instance_ids:
        ds = download_dicom_instance(inst_id)
        slices.append(ds)
    # Sort slices by SliceLocation or InstanceNumber
    slices.sort(key=lambda s: float(getattr(s, "SliceLocation", getattr(s, "InstanceNumber", 0))))
    volume = np.stack([s.pixel_array for s in slices], axis=0)
    return volume, slices