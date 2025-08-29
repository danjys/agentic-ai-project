import logging
import numpy as np
from app.services import orthanc

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Dummy MONAI model ---
class DummyModel:
    def __call__(self, volume_tensor):
        # Return zeros same shape as input
        return np.zeros_like(volume_tensor)

def preprocess_volume(volume: np.ndarray):
    return volume.astype(np.float32)

def load_model(path: str = None):
    logger.info("Loading dummy model for auto-contour")
    return DummyModel()

def run_inference(volume_tensor, model):
    return model(volume_tensor)

async def run_auto_contour_pipeline(instance_id: str, is_instance=True):
    """
    Run the auto-contouring pipeline for a full CT study.
    - instance_id: ID of one DICOM instance in the series
    - is_instance: True if passing a single instance
    """
    try:
        # Download instance to get StudyInstanceUID
        ds = orthanc.download_dicom_instance(instance_id) if is_instance else None
        study_id = ds.StudyInstanceUID if is_instance else instance_id

        # Load full volume
        volume, slices = orthanc.load_volume_from_study_or_instance(study_id, is_instance=False)
        logger.info(f"Volume loaded with shape: {volume.shape}")

        # Preprocess
        tensor = preprocess_volume(volume)
        logger.info("Volume preprocessing done")

        # Load model
        model = load_model()
        logger.info("Model loaded")

        # Run inference
        segmentation = run_inference(tensor, model)
        logger.info("Auto-contouring done")

        return {"message": "Auto-contouring completed", "study_id": study_id, "volume_shape": volume.shape, "seg_shape": segmentation.shape}

    except Exception as e:
        logger.error(f"Auto-contour pipeline failed: {e}", exc_info=True)
        raise
