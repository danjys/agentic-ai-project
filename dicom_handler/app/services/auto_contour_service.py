import tempfile
import pydicom
import numpy as np
from app.services import orthanc, monai, dicom_utils

async def run_auto_contour_pipeline(instance_id: str):
    # Step 1: Retrieve DICOM bytes from Orthanc
    dicom_bytes = orthanc.retrieve_dicom_from_orthanc(instance_id)
    if not dicom_bytes:
        raise ValueError("DICOM instance not found in Orthanc")

    # Step 2: Save to temporary file for pydicom
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dcm") as tmp:
        tmp.write(dicom_bytes)
        tmp_path = tmp.name

    try:
        # Step 3: Load DICOM dataset and extract image
        ds = pydicom.dcmread(tmp_path)
        image = ds.pixel_array.astype(np.float32)

        # Step 4: Run MONAI auto-contour model (implement this in monai.py)
        contour_mask = monai.run_auto_contour_model(image)

        # Step 5: Create RT Structure Set DICOM bytes from mask and original ds
        contour_dicom_bytes = dicom_utils.create_rtstruct_from_mask(contour_mask, ds)

        # Step 6: Upload contour DICOM to Orthanc
        upload_response = await orthanc.upload_dicom_to_orthanc(contour_dicom_bytes)

        return {
            "message": "Auto-contour completed and uploaded",
            "contour_orthanc_id": upload_response.get("ID"),
        }
    finally:
        import os
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
