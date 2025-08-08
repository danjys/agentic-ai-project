import numpy as np
import torch
from monai.transforms import Compose, ScaleIntensity, ToTensor
from monai.networks.nets import DenseNet121

def run_monai_test():
    dummy_image = np.random.rand(96, 96).astype(np.float32)
    dummy_image = np.expand_dims(dummy_image, axis=0)

    transforms = Compose([
        ScaleIntensity(),
        ToTensor()
    ])
    input_tensor = transforms(dummy_image).unsqueeze(0)

    model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=2)
    model.eval()

    with torch.no_grad():
        output = model(input_tensor)
        predicted_class = output.argmax(dim=1).item()

    return predicted_class
