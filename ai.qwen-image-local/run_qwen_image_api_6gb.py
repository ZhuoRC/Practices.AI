from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import DiffusionPipeline
import torch
import warnings
import uvicorn
import os

# Suppress all warnings from diffusers and transformers
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

app = FastAPI(title="Qwen Image Generation API", description="Generate images using Qwen model")

@app.get("/")
async def root():
    return {
        "message": "Qwen Image Generation API is running!",
        "docs": "/docs",
        "generate_endpoint": "/generate"
    }

print("⏳ 加载轻量模型 Qwen/Qwen-Image 中...")

# ✅ 显存友好设置
# 检测是否有足够的 GPU 显存，如果不足则使用 CPU
use_gpu = torch.cuda.is_available()

if use_gpu:
    try:
        print("🔍 尝试使用 GPU 加载模型...")
        pipe = DiffusionPipeline.from_pretrained(
            "Qwen/Qwen-Image",
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        pipe = pipe.to("cuda")

        # 启用内存优化
        if hasattr(pipe, "enable_model_cpu_offload"):
            pipe.enable_model_cpu_offload()
        if hasattr(pipe, "enable_attention_slicing"):
            pipe.enable_attention_slicing(1)
        if hasattr(pipe, "enable_vae_slicing"):
            pipe.enable_vae_slicing()

        print("✅ 模型已加载（GPU 模式）！")
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        print(f"⚠️ GPU 加载失败: {str(e)}")
        print("⚠️ 切换到 CPU 模式...")
        use_gpu = False

if not use_gpu:
    print("🔍 使用 CPU 加载模型...")
    pipe = DiffusionPipeline.from_pretrained(
        "Qwen/Qwen-Image",
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    pipe = pipe.to("cpu")
    print("✅ 模型已加载（CPU 模式）！")

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(req: Prompt):
    print(f"🎨 生成中: {req.prompt}")
    try:
        with torch.inference_mode():
            result = pipe(
                prompt=req.prompt,
                num_inference_steps=20,  # 减少步骤省显存
                guidance_scale=1.0,
                height=512, width=512     # 降低分辨率省显存
            )
        image = result.images[0]
        image.save("output.png")
        print("✅ 图片已保存：output.png")
        return {"message": "ok", "file": "output.png", "prompt": req.prompt}
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        return {"message": "error", "error": str(e)}

if __name__ == "__main__":
    print("🚀 启动 Qwen Image API 服务...")
    print("📍 API 地址: http://localhost:8000")
    print("📖 文档地址: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
