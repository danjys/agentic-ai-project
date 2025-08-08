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
     -F "file=@/Users/danjys/Projects/data/xor_test/001848_003.dcm"

RETRIEVE
curl -o retrieved.dcm http://localhost:8002/retrieve_dicom/1f96f67d8-14909f81-3b9b4dcf-114d15f0-ad81e62a

SEARCH STUDY AND PATIENT ID
curl "http://localhost:8002/search_studies?patient_id=XDbxJIVWlkn"

docker-compose build dicom
docker-compose up -d dicom
docker-compose logs -f dicom 
