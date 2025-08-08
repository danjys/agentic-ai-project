from fastapi import FastAPI
import uvicorn
from monai.transforms import Compose, EnsureChannelFirst, ScaleIntensity, ToTensor
from monai.networks.nets import DenseNet121
import torch
import numpy as np

app = FastAPI()

@app.get("/process/monai_test")
async def monai_test():
    dummy_image = np.random.rand(96, 96).astype(np.float32)

    transforms = Compose([
        EnsureChannelFirst(channel_dim="no_channel"),  # explicitly state there's no channel dim
        ScaleIntensity(),
        ToTensor()
    ])

    input_tensor = transforms(dummy_image).unsqueeze(0)  # Add batch dimension [B, C, H, W]

    model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=2)
    model.eval()

    with torch.no_grad():
        output = model(input_tensor)
        predicted_class = output.argmax(dim=1).item()

    return {"predicted_class": predicted_class}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
