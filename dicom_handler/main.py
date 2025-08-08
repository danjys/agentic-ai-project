from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/process/{study_id}")
def process_study(study_id: str):
    # Simulate DICOM processing
    return {"status": "processed", "study_id": study_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
