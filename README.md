| Layer         | Tools                      |
| ------------- | -------------------------- |
| Language      | Python                     |
| Container     | Docker, Docker Compose     |
| AI Models     | PyTorch, MONAI, U-Net      |
| HL7 FHIR      | `fhir.resources`, REST API |
| DICOM         | `pydicom`, `pynetdicom`    |
| API Server    | `FastAPI`                  |
| Orchestration | LangChain, CrewAI, FSM     |


Project: Agentic AI for DICOM-FHIR Workflows
💡 Goal

Build a containerized AI system that:

    Connects to a FHIR server and PACS/DICOM node

    Submits DICOM images for auto-contouring or analysis

    Uses agents to orchestrate tasks (e.g., fetch → analyze → store)

    Outputs results as DICOM-RTSTRUCT and updates patient data in FHIR

🧱 Project Components (Microservice Style)
1. agent_controller (Central AI Agent)

    Coordinates the steps needed for each goal

    Talks to other modules via APIs

    Implements LangChain, CrewAI, or Autogen (or your own finite-state machine)

Python Packages: langchain, pydantic, fastapi
2. dicom_handler (DICOM I/O Agent)

    Receives DICOM from PACS

    Converts to numpy/image for processing

    Stores back to DICOM or sends to next service

Python Packages: pydicom, pynetdicom, SimpleITK, dicomweb-client
3. fhir_handler (FHIR Agent)

    Communicates with the hospital FHIR server (e.g., HAPI FHIR, Google Cloud)

    Searches/Updates ImagingStudy, Patient, ServiceRequest

Python Packages: fhir.resources, requests, fhirclient
4. ml_processor (Autocontouring / Analysis Engine)

    Receives image data

    Runs a segmentation model (U-Net or plug in MONAI or other models)

    Outputs DICOM RTSTRUCT or annotated results

Python Packages: torch, monai, numpy, pydicom
5. storage_service (Optional)

    Stores results to local disk or object storage (e.g., MinIO, AWS S3)

    Keeps track of input-output mapping for auditing

🔁 Agentic Workflow Example

Goal: "Analyze all pending CT scans for lung segmentation and store RTSTRUCT in PACS."

    agent_controller receives the goal

    Fetches ImagingStudies with status “registered” from fhir_handler

    For each ImagingStudy:

        Uses dicom_handler to download DICOM from PACS

        Sends to ml_processor for lung segmentation

        Creates RTSTRUCT via dicom_handler

        Stores back to PACS

        Updates ImagingStudy.status = available via fhir_handler




Stretch Goals

    🧠 Trainable model with fine-tuning using MONAI and DICOM masks

    📊 Dashboard for job tracking

    🔒 Authentication for FHIR and PACS

    🔁 Retry/fallback agent behaviors

    🧠 Tool-using agents that write their own DICOM pipelines

🧰 Learning Resources

    MONAI Tutorials

    FHIR Spec

    PACS DICOM setup

    LangChain Agent Docs

✅ Summary

This project gives you:

    A modular AI-driven architecture

    Real-world medical imaging + EHR integration

    Strong understanding of agentic workflows

    Dockerized, testable environment


Build all services and containers
docker-compose build

Start all services in detached mode
docker-compose up -d

Check running containers
docker-compose ps

See logs for your agent container to check status and errors
docker-compose logs -f agent

To stop all running containers
docker-compose down


DEBUG
Check all Docker containers
docker ps -a

Find any container, stop and remove it
docker stop <container_id_or_name>
docker rm <container_id_or_name>

You can also prune unused containers and networks to clean up
docker system prune


If only one container changes then
docker-compose up -d --build agent
docker-compose logs -f agent



docker-compose build
docker-compose up -d
docker-compose ps
docker-compose logs -f


docker-compose down -v  # stops and removes volumes/networks/containers
docker-compose up -d --build



Need to swithc to Poetry for dependency manager from requirements.txt


HEALTH (GET)
curl http://localhost:8002/process/health

HEALTH (POST)
curl -X POST http://localhost:8002/process/health

MONAI
curl http://localhost:8002/process/monai_test


UPLOAD
curl -X POST http://localhost:8002/upload_dicom \
     -F "file=@/Users/danjys/Projects/data/xor_test/001848_005.dcm"

RETRIEVE
curl -o retrieved.dcm http://localhost:8002/retrieve_dicom/1f96f67d8-14909f81-3b9b4dcf-114d15f0-ad81e62a

SEARCH STUDY AND PATIENT ID
curl "http://localhost:8002/search_studies?patient_id=XDbxJIVWlkn"

docker-compose build dicom
docker-compose up -d dicom
docker-compose logs -f dicom 


1. Set up the Auto-Contouring Pipeline
Extract DICOM series/volume:
From Orthanc, fetch the full CT volume (all instances in the Study/Series) needed for contouring.

Preprocess volume for MONAI model:

Convert DICOM images to a 3D numpy array or tensor as MONAI expects.

Apply intensity normalization and any spatial resampling.

Handle cropping/padding to model input size.

Run the segmentation model:

Use a MONAI-trained model (e.g., U-Net) to infer auto-contours on the CT volume.

Postprocess results:

Threshold probability maps to get segmentation masks.

Convert masks back to DICOM RTSTRUCT or Segmentation format.

2. Store and Communicate Results
Push generated contour DICOM objects back to Orthanc
This keeps all study data together and accessible.

Update FHIR resources

Create/update FHIR ImagingStudy or ImagingManifest to reference new segmentations/contours.

Optionally notify clinical systems or trigger workflows via FHIR messaging.

3. Agentic Orchestration
Implement an agent-like workflow to orchestrate these steps:

Triggering:

Either on-demand API call or listening for new uploads in Orthanc or FHIR.

Task orchestration:

Fetch data → preprocess → model inference → postprocess → store results → notify.

Error handling & retry.

Logging and audit trail.

4. Build API endpoints for full workflow
E.g., POST /auto_contour?study_id=xyz

E.g., GET /contour_result/{study_id}

5. UI / Visualization
Build a simple web UI or integration to view original CT and overlay auto-contours.

6. Testing and validation
Validate contour accuracy on sample data, adjust models or postprocessing.


Oneliner to RESET everrything
docker-compose down --volumes --remove-orphans && docker-compose up -d



ORTHANC DEBUGGING
docker exec -it orthanc cat /etc/orthanc/orthanc.json
docker logs orthanc | grep -i error
docker logs orthanc
docker inspect orthanc

docker exec -it orthanc ls /usr/share/orthanc/plugins
docker exec -it orthanc ls /usr/local/share/orthanc/plugins
