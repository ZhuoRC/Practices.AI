import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import uuid
import threading
import time
from datetime import datetime
from contextlib import asynccontextmanager

# 全局变量存储任务状态
tasks: Dict[str, Dict[str, Any]] = {}
lock = threading.Lock()

# 上传文件存储目录 - 使用绝对路径
UPLOAD_DIR = Path(__file__).parent / "uploads"
OUTPUT_DIR = Path(__file__).parent / "outputs"

# 确保目录存在
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时不再清理文件，保留已上传的视频
    yield
    # 关闭时的清理工作（如果需要）

app = FastAPI(
    title="Video Subtitle Remover API", 
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加静态文件服务 - 使用绝对路径修复404错误
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

from pydantic import ConfigDict

class FileInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    name: str
    url: str
    size: int
    created_at: str

class ProcessRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    filePath: str
    algorithm: str = "sttn"
    detectionMode: str = "auto"
    subtitleArea: Optional[Dict[str, int]] = None  # 修复：坐标应该是整数
    sttnParams: Optional[Dict[str, Any]] = None
    propainterParams: Optional[Dict[str, Any]] = None
    lamaParams: Optional[Dict[str, Any]] = None
    commonParams: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: Optional[str] = None
    result_url: Optional[str] = None
    error: Optional[str] = None

@app.get("/files", response_model=List[FileInfo])
async def list_uploaded_files():
    """获取uploads目录中的文件列表"""
    try:
        files = []
        
        # 遍历uploads目录中的所有文件
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.avi', '.flv', '.wmv', '.mov', '.mkv']:
                # 获取文件信息
                stat = file_path.stat()
                
                # 使用文件名作为ID（去除扩展名）
                file_id = file_path.stem
                file_name = file_path.name
                
                # 构建访问URL
                file_url = f"/uploads/{file_name}"
                
                files.append(FileInfo(
                    id=file_id,
                    name=file_name,
                    url=file_url,
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime).isoformat()
                ))
        
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@app.get("/outputs", response_model=List[FileInfo])
async def list_output_files():
    """获取outputs目录中的文件列表"""
    try:
        files = []
        
        # 遍历outputs目录中的所有文件
        for file_path in OUTPUT_DIR.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.avi', '.flv', '.wmv', '.mov', '.mkv']:
                # 获取文件信息
                stat = file_path.stat()
                
                # 使用文件名作为ID（去除扩展名）
                file_id = file_path.stem
                file_name = file_path.name
                
                # 构建访问URL
                file_url = f"/outputs/{file_name}"
                
                files.append(FileInfo(
                    id=file_id,
                    name=file_name,
                    url=file_url,
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime).isoformat()
                ))
        
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取输出文件列表失败: {str(e)}")

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """删除上传的文件"""
    try:
        # 查找文件 - 支持多种格式
        file_path = None
        
        # 首先尝试直接匹配完整文件名（包含扩展名）
        direct_path = UPLOAD_DIR / file_id
        if direct_path.exists() and direct_path.is_file():
            file_path = direct_path
        else:
            # 尝试匹配文件stem（去除扩展名）+ 常见视频扩展名
            for ext in ['.mp4', '.avi', '.flv', '.wmv', '.mov', '.mkv']:
                test_path = UPLOAD_DIR / f"{file_id}{ext}"
                if test_path.exists() and test_path.is_file():
                    file_path = test_path
                    break
            
            # 如果还没找到，尝试查找包含file_id的文件（UUID前缀匹配）
            if not file_path:
                for path in UPLOAD_DIR.glob("*"):
                    if path.is_file() and (path.stem == file_id or path.name.startswith(file_id)):
                        file_path = path
                        break
        
        if not file_path:
            print(f"File not found for deletion: {file_id}")
            print(f"Available files: {[f.name for f in UPLOAD_DIR.glob('*') if f.is_file()]}")
            raise HTTPException(status_code=404, detail="文件不存在")
        
        print(f"Deleting file: {file_path}")
        
        # 尝试删除文件，如果被占用则等待重试
        max_retries = 3
        for attempt in range(max_retries):
            try:
                file_path.unlink()
                print(f"File deleted successfully: {file_path}")
                break
            except PermissionError as e:
                if "being used by another process" in str(e).lower():
                    if attempt < max_retries - 1:
                        print(f"File is in use, retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(2)
                    else:
                        raise HTTPException(
                            status_code=409,  # Conflict
                            detail=f"文件正在被其他程序使用，请稍后再试。可能的原因：\n"
                                   f"1. 视频正在播放中\n"
                                   f"2. 文件正在被其他程序打开\n"
                                   f"3. 浏览器正在预览该文件\n"
                                   f"建议：关闭所有可能使用该文件的程序后重试"
                        )
                else:
                    raise
        
        return {"message": "文件已删除"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传视频文件"""
    if not file.filename.lower().endswith(('.mp4', '.avi', '.flv', '.wmv', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    safe_filename = f"{file_id}{file_extension}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "size": file_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.post("/debug-process")
async def debug_process(request: Request):
    """调试处理请求"""
    try:
        # 获取原始请求数据
        body = await request.json()
        print(f"Received request body: {json.dumps(body, indent=2)}")
        
        # 尝试验证
        process_request = ProcessRequest(**body)
        print(f"Validated request: {process_request}")
        
        return {"status": "valid", "data": process_request.model_dump()}  # 修复：使用model_dump替代dict
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.post("/process", response_model=TaskResponse)
async def start_processing(request: ProcessRequest, background_tasks: BackgroundTasks):
    """开始处理视频"""
    task_id = str(uuid.uuid4())
    
    # 检查文件是否存在
    if not os.path.exists(request.filePath):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 创建任务记录
    with lock:
        tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "任务已创建",
            "result_url": None,
            "error": None,
            "created_at": datetime.now(),
            "file_path": request.filePath,
            "config": request.model_dump()  # 修复：使用model_dump替代dict
        }
    
    # 在后台启动处理任务
    background_tasks.add_task(
        process_video_task,
        task_id,
        request.filePath,
        request.model_dump()  # 修复：使用model_dump替代dict
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        progress=0,
        message="处理任务已开始"
    )

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    with lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = tasks[task_id]
        
        return TaskResponse(
            task_id=task_id,
            status=task["status"],
            progress=task["progress"],
            message=task.get("message"),
            result_url=task.get("result_url"),
            error=task.get("error")
        )

@app.get("/tasks")
async def list_tasks():
    """获取所有任务列表"""
    with lock:
        return {
            "tasks": [
                {
                    "task_id": task_id,
                    "status": task["status"],
                    "progress": task["progress"],
                    "created_at": task["created_at"].isoformat()
                }
                for task_id, task in tasks.items()
            ]
        }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    with lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 清理相关文件
        task = tasks[task_id]
        if task.get("result_url"):
            try:
                result_path = Path(task["result_url"])
                if result_path.exists():
                    result_path.unlink()
            except:
                pass
        
        del tasks[task_id]
        
        return {"message": "任务已删除"}

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """下载处理结果"""
    with lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = tasks[task_id]
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="任务未完成")
        
        if not task.get("result_url"):
            raise HTTPException(status_code=404, detail="结果文件不存在")
        
        result_path = Path(task["result_url"])
        if not result_path.exists():
            raise HTTPException(status_code=404, detail="结果文件已被删除")
        
        return FileResponse(
            path=result_path,
            filename=result_path.name,
            media_type='application/octet-stream'
        )

def process_video_task(task_id: str, file_path: str, config: Dict[str, Any]):
    """后台处理视频任务"""
    try:
        # 延迟导入main模块以避免启动时的torch权限问题
        import main as subtitle_remover
        
        # 更新任务状态为处理中
        with lock:
            tasks[task_id]["status"] = "processing"
            tasks[task_id]["message"] = "开始处理视频"
        
        # 构建字幕区域参数 - 修复数据格式匹配问题
        subtitle_area = None
        if config.get("detectionMode") == "manual" and config.get("subtitleArea"):
            area = config["subtitleArea"]
            # 转换为后端期望的格式 (ymin, ymax, xmin, xmax)
            # 坐标已经是整数类型，无需转换
            subtitle_area = (
                int(area["y"]),  # ymin
                int(area["y"] + area["height"]),  # ymax
                int(area["x"]),  # xmin  
                int(area["x"] + area["width"])   # xmax
            )
        
        # 创建字幕去除器实例
        remover = subtitle_remover.SubtitleRemover(
            vd_path=file_path,
            sub_area=subtitle_area,
            gui_mode=False
        )
        
        # 开始处理
        with lock:
            tasks[task_id]["message"] = "正在处理视频..."
        
        # 运行字幕去除
        remover.run()
        
        # 获取输出文件路径
        output_path = remover.video_out_name
        
        # 复制输出文件到outputs目录
        output_file = Path(output_path)
        safe_output_name = f"{task_id}_{output_file.name}"
        final_output_path = OUTPUT_DIR / safe_output_name
        
        shutil.copy2(output_path, final_output_path)
        
        # 更新任务状态为完成
        with lock:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["progress"] = 100
            tasks[task_id]["message"] = "处理完成"
            tasks[task_id]["result_url"] = str(final_output_path)
        
    except Exception as e:
        # 处理失败
        error_message = str(e)
        print(f"Task {task_id} failed: {error_message}")
        
        with lock:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = error_message
            tasks[task_id]["message"] = f"处理失败: {error_message}"

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "Video Subtitle Remover API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "/upload - 上传视频文件",
            "process": "/process - 开始处理",
            "debug_process": "/debug-process - 调试处理请求",
            "task_status": "/tasks/{task_id} - 获取任务状态",
            "list_tasks": "/tasks - 获取任务列表",
            "files": "/files - 获取uploads目录中的文件列表",
            "outputs": "/outputs - 获取outputs目录中的文件列表",
            "delete_file": "/files/{file_id} - 删除上传文件",
            "download": "/download/{task_id} - 下载结果",
            "delete_task": "/tasks/{task_id} - 删除任务",
            "static_uploads": "/uploads/ - 静态文件服务（上传文件）",
            "static_outputs": "/outputs/ - 静态文件服务（输出文件）"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
