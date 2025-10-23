from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from PIL import Image
import io, torch
from diffusers import QwenImageEditPlusPipeline

app = FastAPI()

print("⏳ 正在加载模型 Qwen-Image-Edit-2509，请稍等...")
pipe = QwenImageEditPlusPipeline.from_pretrained(
    "Qwen/Qwen-Image-Edit-2509",
    dtype=torch.bfloat16
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
print("✅ 模型加载完成！")

class PromptReq(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(req: PromptReq, file: UploadFile = File(None)):
    inputs = {"prompt": req.prompt, "num_inference_steps": 40, "guidance_scale": 1.0}
    if file:
        image = Image.open(io.BytesIO(await file.read()))
        inputs["image"] = [image]
    with torch.inference_mode():
        out = pipe(**inputs)
    img = out.images[0]
    img.save("output.png")
    return {"message": "ok", "file": "output.png"}
