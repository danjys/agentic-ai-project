import numpy as np
import logging
from app.services import orthanc

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Dummy MONAI model
class DummyModel:
    def __call__(self, volume_tensor):
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
    Run auto-contouring pipeline for a single instance or full study.
    """
    ds = orthanc.download_dicom_instance(instance_id) if is_instance else None
    study_id = ds.StudyInstanceUID if is_instance else instance_id

    volume, slices = orthanc.load_volume_from_study_or_instance(study_id, is_instance=False)
    tensor = preprocess_volume(volume)
    model = load_model()
    segmentation = run_inference(tensor, model)

    logger.info(f"Auto-contour completed for study {study_id}")
    return {"message": "Auto-contouring done", "study_id": study_id, "seg_shape": segmentation.shape}
