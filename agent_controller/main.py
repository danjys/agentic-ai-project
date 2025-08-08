import requests
import time

FHIR_URL = "http://fhir:8001/studies"
DICOM_URL = "http://dicom:8002/process/"

def main_loop():
    print("Agent Controller Starting...")
    while True:
        try:
            print("Fetching imaging studies...")
            response = requests.get(FHIR_URL)
            response.raise_for_status()
            studies = response.json().get("studies", [])

            for study in studies:
                study_id = study["id"]
                print(f"Processing study: {study_id}")
                r = requests.post(f"{DICOM_URL}{study_id}")
                print(f"Response: {r.json()}")

        except Exception as e:
            print(f"[ERROR] {e}")
            print("Retrying in 10s...")

        time.sleep(30)

if __name__ == "__main__":
    main_loop()
