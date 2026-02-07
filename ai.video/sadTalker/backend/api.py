"""
SadTalker API Server
基于 FastAPI 的后端服务，用于调用 SadTalker 生成说话视频
"""

# numpy 兼容性补丁 (新版本移除了 np.float 等别名)
import numpy as np
np.float = np.float64
np.int = np.int_
np.object = object
np.bool = bool

# torchvision 兼容性补丁 (新版本移除了 functional_tensor)
import torchvision.transforms.functional as _F
import torchvision.transforms as _transforms
_transforms.functional_tensor = _F

import os
import sys
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加 SadTalker 路径
SADTALKER_PATH = Path(__file__).parent.parent / "SadTalker"
sys.path.insert(0, str(SADTALKER_PATH))

app = FastAPI(
    title="SadTalker API",
    description="使用 SadTalker 生成说话视频的 API 服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 文件存储路径
UPLOAD_DIR = Path(__file__).parent / "uploads"
RESULTS_DIR = Path(__file__).parent / "results"
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# SadTalker 实例（延迟加载）
sad_talker = None


def get_sadtalker():
    """获取 SadTalker 实例（懒加载）"""
    global sad_talker
    if sad_talker is None:
        from src.gradio_demo import SadTalker
        checkpoint_path = str(SADTALKER_PATH / "checkpoints")
        config_path = str(SADTALKER_PATH / "src" / "config")
        sad_talker = SadTalker(checkpoint_path, config_path, lazy_load=True)
    return sad_talker


# 任务状态存储
tasks = {}


@app.get("/")
async def root():
    """API 根路径"""
    return {"message": "SadTalker API Server", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/generate")
async def generate_video(
    background_tasks: BackgroundTasks,
    source_image: UploadFile = File(..., description="源图片文件"),
    driven_audio: UploadFile = File(..., description="驱动音频文件"),
    preprocess: str = Form("crop", description="预处理方式: crop, resize, full, extcrop, extfull"),
    still_mode: bool = Form(False, description="静止模式，减少头部运动"),
    use_enhancer: bool = Form(False, description="使用 GFPGAN 增强"),
    batch_size: int = Form(2, description="批处理大小"),
    size: int = Form(256, description="图像尺寸: 256 或 512"),
    pose_style: int = Form(0, description="姿态风格: 0-45"),
    expression_scale: float = Form(1.0, description="表情缩放"),
):
    """
    生成说话视频

    - source_image: 包含人脸的源图片
    - driven_audio: 驱动面部动画的音频文件
    """
    task_id = str(uuid.uuid4())

    # 创建任务目录
    task_dir = UPLOAD_DIR / task_id
    task_dir.mkdir(exist_ok=True)

    try:
        # 保存上传的文件
        image_path = task_dir / source_image.filename
        audio_path = task_dir / driven_audio.filename

        with open(image_path, "wb") as f:
            content = await source_image.read()
            f.write(content)

        with open(audio_path, "wb") as f:
            content = await driven_audio.read()
            f.write(content)

        # 初始化任务状态
        tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "message": "开始处理...",
            "result": None,
            "error": None
        }

        # 在后台执行生成任务
        background_tasks.add_task(
            process_video_generation,
            task_id,
            str(image_path),
            str(audio_path),
            preprocess,
            still_mode,
            use_enhancer,
            batch_size,
            size,
            pose_style,
            expression_scale
        )

        return {"task_id": task_id, "status": "processing", "message": "任务已提交"}

    except Exception as e:
        # 清理任务目录
        if task_dir.exists():
            shutil.rmtree(task_dir)
        raise HTTPException(status_code=500, detail=str(e))


def process_video_generation(
    task_id: str,
    image_path: str,
    audio_path: str,
    preprocess: str,
    still_mode: bool,
    use_enhancer: bool,
    batch_size: int,
    size: int,
    pose_style: int,
    expression_scale: float
):
    """后台处理视频生成"""
    try:
        tasks[task_id]["message"] = "正在加载模型..."
        tasks[task_id]["progress"] = 10

        talker = get_sadtalker()

        tasks[task_id]["message"] = "正在生成视频..."
        tasks[task_id]["progress"] = 30

        # 设置结果目录
        result_dir = str(RESULTS_DIR / task_id)
        os.makedirs(result_dir, exist_ok=True)

        # 调用 SadTalker 生成视频
        result_path = talker.test(
            source_image=image_path,
            driven_audio=audio_path,
            preprocess=preprocess,
            still_mode=still_mode,
            use_enhancer=use_enhancer,
            batch_size=batch_size,
            size=size,
            pose_style=pose_style,
            exp_scale=expression_scale,
            result_dir=result_dir
        )

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "视频生成完成"
        tasks[task_id]["result"] = result_path

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["message"] = f"生成失败: {str(e)}"


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    return tasks[task_id]


@app.get("/api/download/{task_id}")
async def download_video(task_id: str):
    """下载生成的视频"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="视频尚未生成完成")

    result_path = task["result"]
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="视频文件不存在")

    return FileResponse(
        result_path,
        media_type="video/mp4",
        filename=f"sadtalker_{task_id}.mp4"
    )


@app.delete("/api/task/{task_id}")
async def delete_task(task_id: str):
    """删除任务及其文件"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 清理上传目录
    task_upload_dir = UPLOAD_DIR / task_id
    if task_upload_dir.exists():
        shutil.rmtree(task_upload_dir)

    # 清理结果目录
    task_result_dir = RESULTS_DIR / task_id
    if task_result_dir.exists():
        shutil.rmtree(task_result_dir)

    # 删除任务记录
    del tasks[task_id]

    return {"message": "任务已删除"}


@app.get("/api/tasks")
async def list_tasks():
    """列出所有任务"""
    return {"tasks": tasks}


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8802,
        reload=True
    )
