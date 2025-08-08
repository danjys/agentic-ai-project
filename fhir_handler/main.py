from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/studies")
def get_imaging_studies():
    # Simulated FHIR ImagingStudy list
    return {"studies": [{"id": "study1"}, {"id": "study2"}]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
