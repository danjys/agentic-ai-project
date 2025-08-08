import httpx
import requests
from io import BytesIO
import pydicom
import numpy as np
import logging
from app.config import ORTHANC_URL, ORTHANC_USERNAME, ORTHANC_PASSWORD

# Setup logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust as needed (DEBUG/INFO/WARNING/ERROR)

# Console handler for logging
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(ch)


async def upload_dicom_to_orthanc(dicom_bytes: bytes):
    logger.info("Starting upload to Orthanc")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                ORTHANC_URL,
                content=dicom_bytes,
                auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD),
                headers={"Content-Type": "application/dicom"}
            )
            response.raise_for_status()
            logger.info(f"Upload successful, Orthanc response: {response.json()}")
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Upload failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            raise


def retrieve_dicom_from_orthanc(orthanc_id: str):
    logger.info(f"Retrieving DICOM instance {orthanc_id} from Orthanc")
    try:
        r = requests.get(
            f"{ORTHANC_URL}/instances/{orthanc_id}/file",
            auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD)
        )
        r.raise_for_status()
        logger.info(f"Successfully retrieved DICOM instance {orthanc_id}")
        return r.content
    except requests.HTTPError as e:
        logger.error(f"Failed to retrieve DICOM instance {orthanc_id}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving DICOM instance {orthanc_id}: {str(e)}")
        raise


def search_studies(patient_id=None, study_date=None):
    base_url = ORTHANC_URL.rsplit('/', 1)[0]  # strip '/instances' from config URL
    query = {"Level": "Study", "Query": {}}
    if patient_id:
        query["Query"]["PatientID"] = patient_id
    if study_date:
        query["Query"]["StudyDate"] = study_date

    logger.info(f"Searching studies with query: {query}")
    try:
        r = requests.post(f"{base_url}/tools/find", json=query, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
        r.raise_for_status()
        logger.info("Search successful")
        return r.json()
    except requests.HTTPError as e:
        logger.error(f"Search failed with status {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}")
        raise


def get_series_ids(study_id: str):
    url = f"{ORTHANC_URL}/studies/{study_id}/series"
    logger.info(f"Getting series IDs for study {study_id}")
    try:
        r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
        r.raise_for_status()
        logger.info(f"Retrieved series IDs: {r.json()}")
        return r.json()
    except requests.HTTPError as e:
        logger.error(f"Failed to get series IDs for study {study_id}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting series IDs: {str(e)}")
        raise


def get_instance_ids(series_id: str):
    url = f"{ORTHANC_URL}/series/{series_id}/instances"
    logger.info(f"Getting instance IDs for series {series_id}")
    try:
        r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
        r.raise_for_status()
        logger.info(f"Retrieved instance IDs: {r.json()}")
        return r.json()
    except requests.HTTPError as e:
        logger.error(f"Failed to get instance IDs for series {series_id}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting instance IDs: {str(e)}")
        raise


def download_dicom_instance(instance_id: str) -> pydicom.Dataset:
    url = f"{ORTHANC_URL}/instances/{instance_id}/file"
    logger.info(f"Downloading DICOM instance {instance_id}")
    try:
        r = requests.get(url, auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
        r.raise_for_status()
        ds = pydicom.dcmread(BytesIO(r.content))
        logger.info(f"Downloaded and read DICOM instance {instance_id}")
        return ds
    except requests.HTTPError as e:
        logger.error(f"Failed to download DICOM instance {instance_id}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error downloading DICOM instance {instance_id}: {str(e)}")
        raise


def load_volume_from_study(study_id: str) -> (np.ndarray, list):
    logger.info(f"Loading volume from study {study_id}")
    series_ids = get_series_ids(study_id)
    if not series_ids:
        err = f"No series found for study {study_id}"
        logger.error(err)
        raise Exception(err)
    series_id = series_ids[0]
    instance_ids = get_instance_ids(series_id)
    if not instance_ids:
        err = f"No instances found in series {series_id}"
        logger.error(err)
        raise Exception(err)
    slices = []
    for inst_id in instance_ids:
        ds = download_dicom_instance(inst_id)
        slices.append(ds)
    # Sort slices by SliceLocation or InstanceNumber
    try:
        slices.sort(key=lambda s: float(getattr(s, "SliceLocation", getattr(s, "InstanceNumber", 0))))
    except Exception as e:
        logger.warning(f"Could not sort slices by SliceLocation or InstanceNumber: {str(e)}")
    volume = np.stack([s.pixel_array for s in slices], axis=0)
    logger.info(f"Loaded volume shape: {volume.shape}")
    return volume, slices
