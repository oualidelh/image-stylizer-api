from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline
import tempfile

app = FastAPI()

# Load model
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)
pipe.to("cuda" if torch.cuda.is_available() else "cpu")

@app.post("/stylize")
async def stylize_image(style: str = Form(...), image: UploadFile = File(...)):
    # Save uploaded image to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name

    # Open image
    input_img = Image.open(tmp_path).convert("RGB")

    # Build prompt
    prompt = f"A {style} style painting of the image"

    # Generate image
    output = pipe(prompt=prompt, image=input_img).images[0]

    # Save output
    output_path = tmp_path.replace(".png", "_stylized.png")
    output.save(output_path)

    return FileResponse(output_path, media_type="image/png")
