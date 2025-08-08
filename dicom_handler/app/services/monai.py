import numpy as np
import torch
from monai.networks.nets import DenseNet121
from monai.transforms import Compose, ScaleIntensity, EnsureChannelFirst, Resize, ToTensor
from monai.networks.nets import UNet

def run_monai_test():
    dummy_image = np.random.rand(96, 96).astype(np.float32)
    dummy_image = np.expand_dims(dummy_image, axis=0)  # Add channel dim

    transforms = Compose([
        EnsureChannelFirst(),  # instead of AddChannel()
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

def preprocess_volume(volume: np.ndarray, target_size=(64, 128, 128)) -> torch.Tensor:
    transforms = Compose([
        ScaleIntensity(),
        AddChannel(),          # add channel dim
        Resize(target_size),   # resample to model input size
        ToTensor(),
    ])
    tensor = transforms(volume)
    tensor = tensor.unsqueeze(0)  # batch dimension
    return tensor

def load_model(model_path="path_to_your_model.pth") -> torch.nn.Module:
    model = UNet(
        spatial_dims=3,
        in_channels=1,
        out_channels=2,  # number of classes for segmentation
        channels=(16, 32, 64, 128, 256),
        strides=(2, 2, 2, 2),
        num_res_units=2,
    )
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    return model

def run_inference(volume_tensor: torch.Tensor, model: torch.nn.Module) -> np.ndarray:
    with torch.no_grad():
        output = model(volume_tensor)
        segmentation = torch.argmax(output, dim=1)
    return segmentation.squeeze(0).cpu().numpy()
