import requests
from io import BytesIO
import pydicom
import numpy as np
import logging
from app.config import ORTHANC_URL, ORTHANC_USERNAME, ORTHANC_PASSWORD

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def upload_dicom_to_orthanc(dicom_bytes: bytes):
    logger.info("Uploading DICOM to Orthanc")
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ORTHANC_URL}/instances",
            content=dicom_bytes,
            auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD),
            headers={"Content-Type": "application/dicom"}
        )
        response.raise_for_status()
        return response.json()

def download_dicom_instance(instance_id: str) -> pydicom.Dataset:
    url = f"{ORTHANC_URL}/instances/{instance_id}/file"
    r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    r.raise_for_status()
    return pydicom.dcmread(BytesIO(r.content))

def load_volume_from_study_or_instance(id: str, is_instance=False):
    """
    Load full CT volume from StudyInstanceUID or single instance ID
    """
    if is_instance:
        ds = download_dicom_instance(id)
        study_id = ds.StudyInstanceUID
    else:
        study_id = id

    series_ids = get_series_ids(study_id)
    if not series_ids:
        raise Exception(f"No series found for study {study_id}")

    instance_ids = []
    for series_id in series_ids:
        instance_ids.extend(get_instance_ids(series_id))
    if not instance_ids:
        raise Exception(f"No instances found for study {study_id}")

    slices = [download_dicom_instance(inst_id) for inst_id in instance_ids]
    slices.sort(key=lambda s: float(getattr(s, "SliceLocation", getattr(s, "InstanceNumber", 0))))
    volume = np.stack([s.pixel_array for s in slices], axis=0)
    return volume, slices

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
