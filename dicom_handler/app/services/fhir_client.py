import httpx

FHIR_BASE_URL = "http://fhir:8080"  # container network URL

async def search_patient(patient_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FHIR_BASE_URL}/Patient?identifier={patient_id}")
        response.raise_for_status()
        return response.json()
