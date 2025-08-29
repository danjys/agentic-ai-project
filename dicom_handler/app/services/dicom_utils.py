import pydicom
import numpy as np

def parse_dicom_metadata(file_path):
    dcm = pydicom.dcmread(file_path, force=True)
    return {
        "PatientID": dcm.get("PatientID", "Unknown"),
        "StudyDate": dcm.get("StudyDate", "Unknown"),
        "Modality": dcm.get("Modality", "Unknown"),
        "StudyDescription": dcm.get("StudyDescription", "Unknown"),
    }

def create_rtstruct_from_mask(mask: np.ndarray, original_ds: pydicom.Dataset) -> bytes:
    """
    Placeholder: returns dummy bytes. Implement RTSTRUCT creation here.
    """
    return b"DUMMY_RTSTRUCT_CONTENT"
