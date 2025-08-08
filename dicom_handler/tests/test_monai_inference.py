from app.services.orthanc import load_volume_from_study
from app.services.monai import preprocess_volume, load_model, run_inference

if __name__ == "__main__":
    study_id = "your_study_id_here"
    volume, _ = load_volume_from_study(study_id)

    volume_tensor = preprocess_volume(volume)

    model = load_model("models/your_model.pth")

    segmentation = run_inference(volume_tensor, model)

    print(f"Segmentation shape: {segmentation.shape}")
