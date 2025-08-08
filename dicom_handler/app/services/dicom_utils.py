import pydicom

def parse_dicom_metadata(file_path):
    dcm = pydicom.dcmread(file_path, force=True)
    return {
        "PatientID": dcm.get("PatientID", "Unknown"),
        "StudyDate": dcm.get("StudyDate", "Unknown"),
        "Modality": dcm.get("Modality", "Unknown"),
        "StudyDescription": dcm.get("StudyDescription", "Unknown"),
    }
