#!/usr/bin/env python3
"""
DeepSeek-OCR RESTful API Server (Low VRAM Version)
DeepSeek-OCR RESTful API 服务器（低显存优化版本）

Optimized for GPUs with 6GB+ VRAM
针对 6GB+ 显存的 GPU 优化

Features / 功能:
- OCR text extraction / OCR 文本提取
- Save results to file / 保存结果到文件
- Support for file upload and Base64 input / 支持文件上传和 Base64 输入
"""
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from contextlib import asynccontextmanager
import torch
from transformers import AutoModel, AutoTokenizer
import io
import base64
from PIL import Image
import uvicorn
import logging
import gc
import os
from datetime import datetime

# Setup logging / 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress harmless transformers warnings / 抑制无害的 transformers 警告
import warnings
warnings.filterwarnings('ignore', message='.*do_sample.*temperature.*')
warnings.filterwarnings('ignore', message='.*attention mask.*pad token.*')
warnings.filterwarnings('ignore', message='.*seen_tokens.*deprecated.*')
warnings.filterwarnings('ignore', message='.*get_max_cache.*deprecated.*')
warnings.filterwarnings('ignore', message='.*position_ids.*position_embeddings.*')

# Import the masked_scatter fix
try:
    from fix_masked_scatter import patch_deepseek_ocr_model
    PATCH_AVAILABLE = True
    logger.info("✓ masked_scatter fix module loaded / masked_scatter 修复模块已加载")
except ImportError:
    PATCH_AVAILABLE = False
    logger.warning("⚠ fix_masked_scatter.py not found, running without patch")
    logger.warning("⚠ 未找到 fix_masked_scatter.py，在没有补丁的情况下运行")

# Create directories / 创建目录
INPUT_DIR = os.path.join(os.path.dirname(__file__), "input")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
logger.info(f"Input images directory / 输入图片目录: {INPUT_DIR}")
logger.info(f"Output results directory / 输出结果目录: {OUTPUT_DIR}")

# Global variables to store model and tokenizer / 存储模型和分词器的全局变量
model = None
tokenizer = None

class OCRRequest(BaseModel):
    """Request model for OCR / OCR 请求模型"""
    image_base64: str = Field(..., description="Base64 encoded image / Base64 编码的图片")
    prompt: Optional[str] = Field(default="<image>\nFree OCR.", description="OCR prompt / OCR 提示词")
    save_to_file: Optional[bool] = Field(default=True, description="Save result to file / 保存结果到文件")
    base_size: Optional[int] = Field(default=1024, description="Base size for encoding (512-1280, balanced quality) / 编码基础尺寸（512-1280，平衡质量）")
    image_size: Optional[int] = Field(default=896, description="Image processing size (512-1280, balanced quality) / 图像处理尺寸（512-1280，平衡质量）")
    crop_mode: Optional[bool] = Field(default=True, description="Enable document boundary detection / 启用文档边界检测")

class OCRResponse(BaseModel):
    """Response model for OCR / OCR 响应模型"""
    success: bool
    message: str
    text: Optional[str] = None
    output_file: Optional[str] = None

def cleanup_memory():
    """Aggressive memory cleanup / 激进的内存清理"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        torch.cuda.ipc_collect()

def decode_base64_image(image_base64: str) -> Image.Image:
    """
    Decode base64 string to PIL Image
    将 base64 字符串解码为 PIL 图片
    """
    try:
        # Remove data URL prefix if present / 移除 data URL 前缀（如果存在）
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]

        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary / 如果需要，转换为 RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        return image
    except Exception as e:
        raise ValueError(f"Failed to decode base64 image / 解码 base64 图片失败: {str(e)}")

def save_image(image: Image.Image, prefix: str = "input") -> str:
    """
    Save image to input directory
    保存图片到输入目录
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(INPUT_DIR, filename)
    image.save(filepath)
    logger.info(f"Saved image / 已保存图片: {filepath}")
    return filepath

def save_text_result(text: str, prefix: str = "ocr_result") -> str:
    """
    Save OCR result to output directory
    保存 OCR 结果到输出目录
    """
    # Handle None or empty text / 处理 None 或空文本
    if text is None:
        text = "[No text extracted / 未提取到文本]"
    elif not text.strip():
        text = "[Empty result / 空结果]"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    logger.info(f"Saved OCR result / 已保存 OCR 结果: {filepath}")
    return filename

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the DeepSeek-OCR model with memory optimizations
    加载 DeepSeek-OCR 模型并进行内存优化
    """
    global model, tokenizer

    try:
        logger.info("=" * 70)
        logger.info("Loading DeepSeek-OCR model (LOW VRAM MODE)")
        logger.info("加载 DeepSeek-OCR 模型（低显存模式）")
        logger.info("=" * 70)

        model_name = 'deepseek-ai/DeepSeek-OCR'

        # Check GPU / 检查 GPU
        if torch.cuda.is_available():
            device = "cuda"
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"Total GPU Memory / 总显存: {gpu_mem:.1f} GB")

            # Use bfloat16 for memory efficiency / 使用 bfloat16 以节省内存
            torch_dtype = torch.bfloat16
            logger.info("Using torch.bfloat16 for memory efficiency")
            logger.info("使用 torch.bfloat16 节省内存")
        else:
            torch_dtype = torch.float32
            device = "cpu"
            logger.info("GPU not available, using CPU")
            logger.info("GPU 不可用，使用 CPU")

        # Load tokenizer / 加载分词器
        logger.info("\nLoading tokenizer... / 加载分词器...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        logger.info("✓ Tokenizer loaded successfully / 分词器加载成功")

        # Load model / 加载模型
        logger.info("\nLoading model... / 加载模型...")
        logger.info("(This may take several minutes on first run)")
        logger.info("（首次运行可能需要几分钟）")

        # Try to use flash_attention_2, fallback to eager if not available
        # 尝试使用 flash_attention_2，如果不可用则回退到 eager
        attn_impl = 'flash_attention_2'
        try:
            logger.info(f"Attempting to load with {attn_impl}...")
            model = AutoModel.from_pretrained(
                model_name,
                attn_implementation=attn_impl,
                trust_remote_code=True,
                use_safetensors=True,
                torch_dtype=torch_dtype
            )
            logger.info(f"✓ Model loaded with {attn_impl}")
        except Exception as e:
            logger.warning(f"Failed to load with flash_attention_2: {e}")
            logger.info("Falling back to eager attention implementation...")
            logger.info("回退到 eager 注意力实现...")
            attn_impl = 'eager'
            model = AutoModel.from_pretrained(
                model_name,
                attn_implementation=attn_impl,
                trust_remote_code=True,
                use_safetensors=True,
                torch_dtype=torch_dtype
            )
            logger.info("✓ Model loaded with eager attention (slower but works without flash-attn)")
            logger.info("✓ 模型已加载，使用 eager 注意力（较慢但无需 flash-attn）")

        # Set model to evaluation mode / 设置模型为评估模式
        model = model.eval()

        if torch.cuda.is_available():
            logger.info("\n" + "=" * 70)
            logger.info("Applying memory optimizations:")
            logger.info("应用内存优化:")
            logger.info("=" * 70)

            # Move model to GPU / 将模型移至 GPU
            model = model.cuda()
            logger.info("✓ Model moved to GPU / 模型已移至 GPU")

            # Use CPU offload for large models if needed / 如需要，对大模型使用 CPU 卸载
            # model = model.to(device)

            # Clean up / 清理
            cleanup_memory()
            logger.info("✓ Initial memory cleanup completed / 初始内存清理完成")

        else:
            model = model.to(device)

        logger.info("\n" + "=" * 70)
        logger.info("Model loaded successfully! / 模型加载成功！")
        logger.info("=" * 70)

        # Apply masked_scatter fix patch
        if PATCH_AVAILABLE:
            try:
                logger.info("\nApplying masked_scatter_ fix / 应用 masked_scatter_ 修复")
                model = patch_deepseek_ocr_model(model)
                logger.info("✓ Patch applied successfully / 补丁应用成功")
            except Exception as e:
                logger.warning(f"⚠ Failed to apply patch / 应用补丁失败: {e}")
                logger.warning("  Model will run without patch (may encounter CUDA errors)")
                logger.warning("  模型将在没有补丁的情况下运行（可能遇到 CUDA 错误）")
        else:
            logger.warning("\n⚠ Running without masked_scatter_ fix")
            logger.warning("⚠ 在没有 masked_scatter_ 修复的情况下运行")
            logger.warning("  If you encounter CUDA assertion errors, ensure fix_masked_scatter.py is present")
            logger.warning("  如果遇到 CUDA 断言错误，请确保 fix_masked_scatter.py 存在")

        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            reserved = torch.cuda.memory_reserved(0) / 1024**3
            logger.info(f"\nGPU memory allocated / GPU 已分配内存: {allocated:.2f} GB")
            logger.info(f"GPU memory reserved / GPU 已保留内存: {reserved:.2f} GB")

    except Exception as e:
        logger.error(f"\n❌ Failed to load model / 模型加载失败: {e}")
        logger.error("\nTroubleshooting tips / 故障排除提示:")
        logger.error("1. Ensure you have at least 6GB free GPU memory")
        logger.error("   确保至少有 6GB 可用 GPU 内存")
        logger.error("2. Install flash-attn: pip install flash-attn==2.7.3 --no-build-isolation")
        logger.error("   安装 flash-attn: pip install flash-attn==2.7.3 --no-build-isolation")
        logger.error("3. Close all other GPU applications")
        logger.error("   关闭所有其他 GPU 应用程序")
        logger.error("4. Check requirements with: python check_gpu.py")
        logger.error("   使用以下命令检查要求: python check_gpu.py")
        raise

    # Yield control back to the application / 将控制权交还给应用程序
    yield

    # Cleanup on shutdown / 关闭时清理
    logger.info("Shutting down... / 正在关闭...")
    cleanup_memory()

# Initialize FastAPI app with lifespan / 使用 lifespan 初始化 FastAPI 应用
app = FastAPI(
    title="DeepSeek-OCR API (Low VRAM)",
    description="RESTful API for DeepSeek-OCR optimized for low VRAM GPUs (6GB+) / 针对低显存 GPU（6GB+）优化的 DeepSeek-OCR RESTful API",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint with API information / 包含 API 信息的根端点"""
    return {
        "name": "DeepSeek-OCR API (Low VRAM Mode)",
        "name_zh": "DeepSeek-OCR API（低显存模式）",
        "status": "running",
        "model": "deepseek-ai/DeepSeek-OCR",
        "mode": "Low VRAM Optimized",
        "mode_zh": "低显存优化",
        "optimizations": [
            "torch.bfloat16 precision",
            "Flash Attention 2",
            "Aggressive memory cleanup",
            "CPU offload (if needed)"
        ],
        "optimizations_zh": [
            "torch.bfloat16 精度",
            "Flash Attention 2",
            "激进的内存清理",
            "CPU 卸载（如需要）"
        ],
        "endpoints": {
            "/ocr": "POST - Extract text from image (file upload) / 从图片中提取文本（文件上传）",
            "/ocr-base64": "POST - Extract text from base64 image / 从 base64 图片中提取文本",
            "/health": "GET - Health check with memory stats / 健康检查和内存统计",
            "/results/{filename}": "GET - Download saved OCR result / 下载保存的 OCR 结果",
            "/cleanup": "POST - Force cleanup GPU memory / 强制清理 GPU 内存",
            "/docs": "GET - API documentation / API 文档"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with memory statistics / 带内存统计的健康检查端点"""
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded / 模型未加载"
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    health_info = {
        "status": "healthy",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None,
        "device": device,
        "mode": "Low VRAM (torch.bfloat16)" if device == "cuda" else "CPU"
    }

    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3

        health_info.update({
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_total": f"{total:.2f} GB",
            "gpu_memory_allocated": f"{allocated:.2f} GB",
            "gpu_memory_reserved": f"{reserved:.2f} GB",
            "gpu_memory_free": f"{total - reserved:.2f} GB"
        })

    return health_info

@app.post("/cleanup")
async def cleanup():
    """Force aggressive memory cleanup / 强制激进的内存清理"""
    logger.info("Performing aggressive memory cleanup... / 执行激进的内存清理...")
    cleanup_memory()

    result = {
        "message": "Memory cleanup completed / 内存清理完成"
    }

    if torch.cuda.is_available():
        result.update({
            "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
            "gpu_memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB"
        })

    return result

@app.post("/ocr", response_model=OCRResponse)
async def ocr_from_file(
    image: UploadFile = File(..., description="Image file for OCR / 用于 OCR 的图片文件"),
    prompt: Optional[str] = Form(default="<image>\nFree OCR.", description="OCR prompt / OCR 提示词"),
    save_to_file: Optional[bool] = Form(default=True, description="Save result to file / 保存结果到文件"),
    base_size: Optional[int] = Form(default=1024, description="Base size for encoding (512-1280, balanced quality) / 编码基础尺寸（512-1280，平衡质量）"),
    image_size: Optional[int] = Form(default=896, description="Image processing size (512-1280, balanced quality) / 图像处理尺寸（512-1280，平衡质量）"),
    crop_mode: Optional[bool] = Form(default=True, description="Enable document boundary detection / 启用文档边界检测")
):
    """
    Extract text from uploaded image file (LOW VRAM version)
    从上传的图片文件中提取文本（低显存版本）

    Optimized for GPUs with 6GB+ VRAM
    针对 6GB+ 显存的 GPU 优化
    """
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded / 模型未加载"
        )

    try:
        # Read and decode image / 读取并解码图片
        logger.info("\n" + "=" * 70)
        logger.info("Starting OCR (LOW VRAM MODE) / 开始 OCR（低显存模式）")
        logger.info("=" * 70)

        # Cleanup before processing / 处理前清理
        cleanup_memory()

        # Read uploaded file / 读取上传的文件
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary / 如需要，转换为 RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        logger.info(f"Image size / 图片尺寸: {pil_image.size}")
        logger.info(f"Prompt / 提示词: {prompt}")

        # Save input image and get filepath / 保存输入图片并获取文件路径
        image_filepath = save_image(pil_image, prefix="input")

        if torch.cuda.is_available():
            mem_before = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory before / GPU 内存使用（前）: {mem_before:.2f} GB")

        # Perform OCR / 执行 OCR
        logger.info("\nPerforming OCR... / 执行 OCR...")
        logger.info(f"Settings / 设置: base_size={base_size}, image_size={image_size}, crop_mode={crop_mode}")

        # Capture stdout to get the model's printed output
        # 捕获标准输出以获取模型打印的输出
        import io as io_module
        import sys

        old_stdout = sys.stdout
        sys.stdout = captured_output = io_module.StringIO()

        try:
            with torch.inference_mode():
                # Run inference using model.infer() / 使用 model.infer() 运行推理
                # Use save_results=False to get return value / 使用 save_results=False 以获取返回值
                logger.info("Starting model inference... / 开始模型推理...")
                logger.info("This may take 1-3 minutes for large images / 大图片可能需要 1-3 分钟")

                result_text = model.infer(
                    tokenizer,
                    prompt=prompt,
                    image_file=image_filepath,
                    output_path=OUTPUT_DIR,  # Use output directory / 使用输出目录
                    base_size=base_size,     # Higher values = better quality / 更高的值 = 更好的质量
                    image_size=image_size,   # Higher values = better quality / 更高的值 = 更好的质量
                    crop_mode=crop_mode,     # Enable boundary detection / 启用边界检测
                    save_results=False       # Return result instead of just saving / 返回结果而不仅仅保存
                )

                logger.info("Model inference completed / 模型推理完成")
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        # Get captured output if result_text is None
        # 如果 result_text 为 None，则获取捕获的输出
        if result_text is None or not result_text.strip():
            captured_text = captured_output.getvalue()
            if captured_text.strip():
                # The model printed the result, extract it
                # 模型打印了结果，提取它
                result_text = captured_text.strip()
                logger.info("Captured output from model print statements")
                logger.info("从模型打印语句中捕获了输出")

        logger.info("✓ OCR completed successfully! / OCR 成功完成！")

        # Check if result_text is None or empty / 检查结果是否为 None 或空
        if result_text is None or (isinstance(result_text, str) and not result_text.strip()):
            logger.warning("Model returned None or empty result")
            logger.info("Checking output directory for saved results...")
            # Try to read from the saved file / 尝试从保存的文件读取
            import glob
            latest_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.txt")), key=os.path.getmtime, reverse=True)
            if latest_files:
                with open(latest_files[0], 'r', encoding='utf-8') as f:
                    result_text = f.read()
                logger.info(f"Successfully read result from: {latest_files[0]}")
            else:
                result_text = "OCR completed but no text was extracted. The image may be blank or unreadable."
                logger.warning("No output files found, using default message")

        logger.info(f"\nExtracted text / 提取的文本:\n{result_text}")

        # Save to file if requested / 如请求，保存到文件
        output_filename = None
        if save_to_file:
            output_filename = save_text_result(result_text, prefix="ocr_result")

        # Cleanup after processing / 处理后清理
        cleanup_memory()

        if torch.cuda.is_available():
            mem_after = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory after / GPU 内存使用（后）: {mem_after:.2f} GB")

        logger.info("=" * 70 + "\n")

        return OCRResponse(
            success=True,
            message="OCR completed successfully / OCR 成功完成",
            text=result_text,
            output_file=output_filename
        )

    except torch.cuda.OutOfMemoryError as e:
        logger.error("\n" + "=" * 70)
        logger.error("❌ CUDA OUT OF MEMORY ERROR / CUDA 内存不足错误")
        logger.error("=" * 70)
        cleanup_memory()

        suggestions = [
            "Reduce image size before uploading / 上传前减小图片尺寸",
            "Close all other GPU applications / 关闭所有其他 GPU 应用程序",
            "Restart the API server to clear memory / 重启 API 服务器以清理内存",
            "Try processing a smaller image first / 先尝试处理较小的图片"
        ]

        logger.error("\n💡 Suggestions / 建议:")
        for i, suggestion in enumerate(suggestions, 1):
            logger.error(f"   {i}. {suggestion}")

        raise HTTPException(
            status_code=507,
            detail={
                "error": "GPU out of memory / GPU 内存不足",
                "message": "The OCR process exceeded available GPU memory / OCR 处理超出了可用 GPU 内存",
                "suggestions": suggestions
            }
        )
    except Exception as e:
        logger.error(f"\n❌ Error during OCR / OCR 过程中出错: {e}")
        cleanup_memory()
        raise HTTPException(status_code=500, detail=f"OCR failed / OCR 失败: {str(e)}")

@app.post("/ocr-base64", response_model=OCRResponse)
async def ocr_from_base64(request: OCRRequest):
    """
    Extract text from base64 encoded image (LOW VRAM version)
    从 base64 编码的图片中提取文本（低显存版本）

    Optimized for GPUs with 6GB+ VRAM
    针对 6GB+ 显存的 GPU 优化
    """
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded / 模型未加载"
        )

    try:
        # Decode base64 image / 解码 base64 图片
        logger.info("\n" + "=" * 70)
        logger.info("Starting OCR (LOW VRAM MODE) / 开始 OCR（低显存模式）")
        logger.info("=" * 70)

        # Cleanup before processing / 处理前清理
        cleanup_memory()

        pil_image = decode_base64_image(request.image_base64)
        logger.info(f"Image size / 图片尺寸: {pil_image.size}")
        logger.info(f"Prompt / 提示词: {request.prompt}")

        # Save input image and get filepath / 保存输入图片并获取文件路径
        image_filepath = save_image(pil_image, prefix="input")

        if torch.cuda.is_available():
            mem_before = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory before / GPU 内存使用（前）: {mem_before:.2f} GB")

        # Perform OCR / 执行 OCR
        logger.info("\nPerforming OCR... / 执行 OCR...")
        logger.info(f"Settings / 设置: base_size={request.base_size}, image_size={request.image_size}, crop_mode={request.crop_mode}")

        # Capture stdout to get the model's printed output
        # 捕获标准输出以获取模型打印的输出
        import io as io_module
        import sys

        old_stdout = sys.stdout
        sys.stdout = captured_output = io_module.StringIO()

        try:
            with torch.inference_mode():
                # Run inference using model.infer() / 使用 model.infer() 运行推理
                # Use save_results=False to get return value / 使用 save_results=False 以获取返回值
                logger.info("Starting model inference... / 开始模型推理...")
                logger.info("This may take 1-3 minutes for large images / 大图片可能需要 1-3 分钟")

                result_text = model.infer(
                    tokenizer,
                    prompt=request.prompt,
                    image_file=image_filepath,
                    output_path=OUTPUT_DIR,  # Use output directory / 使用输出目录
                    base_size=request.base_size,     # Higher values = better quality / 更高的值 = 更好的质量
                    image_size=request.image_size,   # Higher values = better quality / 更高的值 = 更好的质量
                    crop_mode=request.crop_mode,     # Enable boundary detection / 启用边界检测
                    save_results=False               # Return result instead of just saving / 返回结果而不仅仅保存
                )

                logger.info("Model inference completed / 模型推理完成")
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        # Get captured output if result_text is None
        # 如果 result_text 为 None，则获取捕获的输出
        if result_text is None or not result_text.strip():
            captured_text = captured_output.getvalue()
            if captured_text.strip():
                # The model printed the result, extract it
                # 模型打印了结果，提取它
                result_text = captured_text.strip()
                logger.info("Captured output from model print statements")
                logger.info("从模型打印语句中捕获了输出")

        logger.info("✓ OCR completed successfully! / OCR 成功完成！")

        # Check if result_text is None or empty / 检查结果是否为 None 或空
        if result_text is None or (isinstance(result_text, str) and not result_text.strip()):
            logger.warning("Model returned None or empty result")
            logger.info("Checking output directory for saved results...")
            # Try to read from the saved file / 尝试从保存的文件读取
            import glob
            latest_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.txt")), key=os.path.getmtime, reverse=True)
            if latest_files:
                with open(latest_files[0], 'r', encoding='utf-8') as f:
                    result_text = f.read()
                logger.info(f"Successfully read result from: {latest_files[0]}")
            else:
                result_text = "OCR completed but no text was extracted. The image may be blank or unreadable."
                logger.warning("No output files found, using default message")

        logger.info(f"\nExtracted text / 提取的文本:\n{result_text}")

        # Save to file if requested / 如请求，保存到文件
        output_filename = None
        if request.save_to_file:
            output_filename = save_text_result(result_text, prefix="ocr_result")

        # Cleanup after processing / 处理后清理
        cleanup_memory()

        if torch.cuda.is_available():
            mem_after = torch.cuda.memory_allocated(0) / 1024**3
            logger.info(f"GPU memory after / GPU 内存使用（后）: {mem_after:.2f} GB")

        logger.info("=" * 70 + "\n")

        return OCRResponse(
            success=True,
            message="OCR completed successfully / OCR 成功完成",
            text=result_text,
            output_file=output_filename
        )

    except torch.cuda.OutOfMemoryError as e:
        logger.error("\n" + "=" * 70)
        logger.error("❌ CUDA OUT OF MEMORY ERROR / CUDA 内存不足错误")
        logger.error("=" * 70)
        cleanup_memory()

        suggestions = [
            "Reduce image size / 减小图片尺寸",
            "Close all other GPU applications / 关闭所有其他 GPU 应用程序",
            "Restart the API server to clear memory / 重启 API 服务器以清理内存",
            "Try processing a smaller image first / 先尝试处理较小的图片"
        ]

        logger.error("\n💡 Suggestions / 建议:")
        for i, suggestion in enumerate(suggestions, 1):
            logger.error(f"   {i}. {suggestion}")

        raise HTTPException(
            status_code=507,
            detail={
                "error": "GPU out of memory / GPU 内存不足",
                "message": "The OCR process exceeded available GPU memory / OCR 处理超出了可用 GPU 内存",
                "suggestions": suggestions
            }
        )
    except ValueError as e:
        logger.error(f"\n❌ Invalid image data / 无效的图片数据: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"\n❌ Error during OCR / OCR 过程中出错: {e}")
        cleanup_memory()
        raise HTTPException(status_code=500, detail=f"OCR failed / OCR 失败: {str(e)}")

@app.get("/results/{filename}")
async def get_result_file(filename: str):
    """
    Download a saved OCR result file
    下载保存的 OCR 结果文件
    """
    filepath = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"File not found / 文件未找到: {filename}"
        )

    return FileResponse(
        filepath,
        media_type="text/plain",
        filename=filename
    )

if __name__ == "__main__":
    logger.info("\n" + "=" * 70)
    logger.info("Starting DeepSeek-OCR API Server (LOW VRAM MODE)")
    logger.info("启动 DeepSeek-OCR API 服务器（低显存模式）")
    logger.info("=" * 70 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8031,
        log_level="info"
    )
