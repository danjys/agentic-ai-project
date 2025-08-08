from app.services.orthanc import load_volume_from_study

if __name__ == "__main__":
    study_id = "your_study_id_here"  # replace with real ID
    volume, slices = load_volume_from_study(study_id)
    print(f"Loaded volume shape: {volume.shape}")
