import requests
import time

FHIR_BASE_URL = "http://fhir:8080/fhir"
DICOM_URL = "http://dicom:8002/process/"

def wait_for_service(url, service_name, timeout=60, interval=5, method='GET'):
    print(f"Waiting for {service_name} service to be ready at {url} ...")
    start_time = time.time()
    while True:
        try:
            if method == 'GET':
                r = requests.get(url)
            elif method == 'POST':
                r = requests.post(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            if r.status_code == 200:
                print(f"{service_name} is ready!")
                return
        except requests.RequestException:
            pass

        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout waiting for {service_name} at {url}")

        print(f"{service_name} not ready yet, retrying in {interval}s...")
        time.sleep(interval)


def main_loop():
    print("Agent Controller Starting...")

    wait_for_service(f"{FHIR_BASE_URL}/ImagingStudy?_count=1", "FHIR")
    wait_for_service(f"{DICOM_URL}health", "DICOM", method='POST')

    while True:
        try:
            print("Fetching imaging studies...")
            response = requests.get(f"{FHIR_BASE_URL}/ImagingStudy")
            response.raise_for_status()

            bundle = response.json()
            studies = []

            if bundle.get("resourceType") == "Bundle":
                entries = bundle.get("entry", [])
                for entry in entries:
                    resource = entry.get("resource", {})
                    if resource.get("resourceType") == "ImagingStudy":
                        studies.append(resource)

            print(f"Found {len(studies)} imaging studies")

            for study in studies:
                study_id = study.get("id")
                print(f"Processing study: {study_id}")
                r = requests.post(f"{DICOM_URL}{study_id}")
                print(f"Response: {r.json()}")

        except Exception as e:
            print(f"[ERROR] {e}")
            print("Retrying in 10s...")

        time.sleep(30)

if __name__ == "__main__":
    main_loop()
