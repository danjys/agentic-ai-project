from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import os
import pydicom
from tempfile import NamedTemporaryFile
import numpy as np
import torch
from monai.transforms import Compose, EnsureChannelFirst, ScaleIntensity, ToTensor
from monai.networks.nets import DenseNet121

app = FastAPI()


@app.get("/process/health")
async def health_check():
    return {"status": "ok"}


@app.post("/process/health")
async def health_check_post():
    return {"status": "ok"}


@app.get("/process/monai_test")
async def monai_test():
    try:
        # Step 1: Create dummy image as (1, 96, 96)
        dummy_image = np.random.rand(96, 96).astype(np.float32)
        dummy_image = np.expand_dims(dummy_image, axis=0)  # (1, 96, 96)

        # Step 2: Apply MONAI transforms (no need for EnsureChannelFirst anymore)
        transforms = Compose([
            ScaleIntensity(),
            ToTensor()
        ])

        input_tensor = transforms(dummy_image)  # (1, 96, 96)
        input_tensor = input_tensor.unsqueeze(0)  # Add batch dim -> (1, 1, 96, 96)

        # Step 3: Load MONAI model
        model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=2)
        model.eval()

        with torch.no_grad():
            output = model(input_tensor)
            predicted_class = output.argmax(dim=1).item()

        return {"predicted_class": predicted_class}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MONAI test failed: {str(e)}")


@app.post("/upload_dicom")
async def upload_dicom(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".dcm"):
        raise HTTPException(status_code=400, detail="Only .dcm (DICOM) files are supported.")

    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=".dcm") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        dcm = pydicom.dcmread(tmp_path, force=True)

        patient_id = dcm.get("PatientID", "Unknown")
        study_date = dcm.get("StudyDate", "Unknown")
        modality = dcm.get("Modality", "Unknown")
        study_desc = dcm.get("StudyDescription", "Unknown")

        return {
            "message": "DICOM file uploaded successfully.",
            "PatientID": patient_id,
            "StudyDate": study_date,
            "Modality": modality,
            "StudyDescription": study_desc,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process DICOM file: {str(e)}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
