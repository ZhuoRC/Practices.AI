# DeepSeek-OCR Quick Start Guide

# DeepSeek-OCR 快速开始指南

Get started with DeepSeek-OCR in 3 simple steps!

三步快速开始使用 DeepSeek-OCR！

---

## Prerequisites / 前置要求

- **Python**: 3.12.9+ / Python 3.12.9+
- **GPU**: NVIDIA GPU with 6GB+ VRAM / NVIDIA GPU，6GB+ 显存
- **CUDA**: 11.8 or 12.1 / CUDA 11.8 或 12.1
- **OS**: Windows, Linux, or macOS / Windows、Linux 或 macOS

---

## Step 1: Environment Setup / 步骤 1: 环境设置

### Create Virtual Environment / 创建虚拟环境

```bash
# Navigate to project directory / 进入项目目录
cd ai.huggingface

# Create virtual environment / 创建虚拟环境
python -m venv .venv

# Activate virtual environment / 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Upgrade pip / 升级 pip
python -m pip install --upgrade pip
```

### Install PyTorch with CUDA / 安装支持 CUDA 的 PyTorch

First, check your CUDA version:

首先，检查你的 CUDA 版本：

```bash
nvidia-smi
```

Then install PyTorch based on your CUDA version:

然后根据 CUDA 版本安装 PyTorch：

```bash
# For CUDA 12.1 / 适用于 CUDA 12.1
pip install torch==2.5.1+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8 / 适用于 CUDA 11.8
pip install torch==2.5.1+cu118 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Install Flash Attention / 安装 Flash Attention

**IMPORTANT**: This is **required** for DeepSeek-OCR to work!

**重要**: 这是 DeepSeek-OCR 运行的**必需**组件！

```bash
pip install flash-attn==2.7.3 --no-build-isolation
```

**Note**: This may take 5-10 minutes to compile.

**注意**: 编译可能需要 5-10 分钟。

### Install Other Dependencies / 安装其他依赖

```bash
pip install -r requirements.txt
```

---

## Step 2: Verify Installation / 步骤 2: 验证安装

Run the GPU check script to verify everything is installed correctly:

运行 GPU 检查脚本以验证所有组件是否正确安装：

```bash
python check_gpu.py
```

**Expected output / 预期输出:**

```
======================================================================
    GPU Detection and Diagnostic Tool for DeepSeek-OCR
    GPU 检测和诊断工具 - DeepSeek-OCR
======================================================================

[INFO] System information / 系统信息:
[INFO] Operating system / 操作系统: Windows 11
[INFO] Python version / Python 版本: 3.12.9

[OK] NVIDIA driver is installed / NVIDIA 驱动已安装
[OK] PyTorch version / PyTorch 版本: 2.5.1+cu121
[OK] CUDA available / CUDA 可用: True
[OK] Flash Attention version / Flash Attention 版本: 2.7.3
[OK] transformers version / transformers 版本: 4.46.3

======================================================================
[RESULT] Diagnostic results / 诊断结果:
======================================================================
[OK] GPU environment is properly configured! / GPU 环境配置正确！
[OK] You can use GPU acceleration / 可以使用 GPU 加速
[OK] DeepSeek-OCR is ready to run / DeepSeek-OCR 已准备就绪
```

If you see any errors, follow the suggestions provided by the script.

如果看到任何错误，请按照脚本提供的建议操作。

---

## Step 3: Start the API Server / 步骤 3: 启动 API 服务器

```bash
python deepseek_ocr/deepseek_ocr_api_low_vram.py
```

**You should see / 你应该看到:**

```
======================================================================
Starting DeepSeek-OCR API Server (LOW VRAM MODE)
启动 DeepSeek-OCR API 服务器（低显存模式）
======================================================================

======================================================================
Loading DeepSeek-OCR model (LOW VRAM MODE)
加载 DeepSeek-OCR 模型（低显存模式）
======================================================================
GPU: NVIDIA GeForce RTX 3060
Total GPU Memory / 总显存: 12.0 GB
Using torch.bfloat16 for memory efficiency
使用 torch.bfloat16 节省内存

Loading tokenizer... / 加载分词器...
✓ Tokenizer loaded successfully / 分词器加载成功

Loading model... / 加载模型...
(This may take several minutes on first run)
（首次运行可能需要几分钟）

======================================================================
Applying memory optimizations:
应用内存优化:
======================================================================
✓ Model moved to GPU / 模型已移至 GPU
✓ Initial memory cleanup completed / 初始内存清理完成

======================================================================
Model loaded successfully! / 模型加载成功！
======================================================================

GPU memory allocated / GPU 已分配内存: 3.45 GB
GPU memory reserved / GPU 已保留内存: 4.12 GB

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8031
```

**The API is now running on / API 现在运行在:** `http://localhost:8031`

---

## Quick Test / 快速测试

### Method 1: Using Web Browser / 方法 1: 使用浏览器

Open your browser and navigate to:

打开浏览器并访问：

```
http://localhost:8031/docs
```

You'll see the **interactive API documentation** (Swagger UI) where you can test all endpoints!

你将看到**交互式 API 文档** (Swagger UI)，可以在此测试所有端点！

### Method 2: Using cURL / 方法 2: 使用 cURL

```bash
# Check health / 检查健康状态
curl http://localhost:8031/health

# Perform OCR / 执行 OCR
curl -X POST http://localhost:8031/ocr \
  -F "image=@document.png" \
  -F "prompt=<image>\nFree OCR." \
  -F "save_to_file=true"
```

### Method 3: Using Python / 方法 3: 使用 Python

Create a file `test_ocr.py`:

创建文件 `test_ocr.py`:

```python
import requests

# Check API health / 检查 API 健康状态
response = requests.get("http://localhost:8031/health")
print("Health:", response.json())

# Perform OCR / 执行 OCR
with open("document.png", "rb") as f:
    files = {"image": f}
    data = {"prompt": "<image>\nFree OCR.", "save_to_file": True}
    response = requests.post(
        "http://localhost:8031/ocr",
        files=files,
        data=data
    )

result = response.json()
print("Success:", result["success"])
print("Text:", result["text"])
print("Output file:", result.get("output_file"))
```

Run it:

运行：

```bash
python test_ocr.py
```

---

## Common Issues / 常见问题

### Issue 1: CUDA Out of Memory / 问题 1: CUDA 内存不足

**Symptom / 症状:**
```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Solution / 解决方案:**

1. Close all other GPU applications / 关闭所有其他 GPU 应用程序
2. Reduce image size before uploading / 上传前减小图片尺寸
3. Restart the API server / 重启 API 服务器
4. See [Low VRAM Guide](LOW_VRAM_GUIDE.md) for more tips / 更多提示见[低显存指南](LOW_VRAM_GUIDE.md)

### Issue 2: Flash Attention Not Found / 问题 2: Flash Attention 未找到

**Symptom / 症状:**
```
ModuleNotFoundError: No module named 'flash_attn'
```

**Solution / 解决方案:**

```bash
pip install flash-attn==2.7.3 --no-build-isolation
```

If this fails, make sure you have:

如果失败，请确保：

1. CUDA 11.8+ installed / 已安装 CUDA 11.8+
2. Latest NVIDIA driver / 最新的 NVIDIA 驱动
3. Sufficient disk space for compilation / 足够的磁盘空间用于编译

### Issue 3: Model Not Loading / 问题 3: 模型未加载

**Symptom / 症状:**
```
503 Service Unavailable: Model not loaded
```

**Solution / 解决方案:**

1. Check the server logs for error messages / 检查服务器日志中的错误信息
2. Run `python check_gpu.py` to verify environment / 运行 `python check_gpu.py` 验证环境
3. Ensure all dependencies are installed / 确保所有依赖已安装
4. Try restarting the server / 尝试重启服务器

### Issue 4: Slow First Request / 问题 4: 首次请求慢

**Symptom / 症状:**

The first OCR request takes a very long time.

首次 OCR 请求耗时很长。

**Explanation / 解释:**

This is normal! The model needs to download (on first run) and load into memory.

这是正常的！模型需要下载（首次运行时）并加载到内存中。

**Solution / 解决方案:**

Just wait for the first request to complete. Subsequent requests will be much faster.

只需等待第一个请求完成。后续请求会快得多。

---

## Next Steps / 下一步

1. **Read the API Usage Guide / 阅读 API 使用指南**: [API_USAGE.md](API_USAGE.md)
   - Learn about all available endpoints / 了解所有可用端点
   - See complete examples in Python, JavaScript, cURL / 查看 Python、JavaScript、cURL 的完整示例

2. **Optimize for Your GPU / 为你的 GPU 优化**: [LOW_VRAM_GUIDE.md](LOW_VRAM_GUIDE.md)
   - Tips for low VRAM GPUs (6GB or less) / 低显存 GPU（6GB 或更少）的技巧
   - Memory optimization strategies / 内存优化策略

3. **Integrate into Your Project / 集成到你的项目**
   - Use the API in your applications / 在应用程序中使用 API
   - Build OCR workflows / 构建 OCR 工作流

---

## Troubleshooting / 故障排除

If you encounter any issues:

如果遇到任何问题：

1. **Check the logs / 检查日志**: The server prints detailed logs, including error messages
   服务器打印详细日志，包括错误信息

2. **Run diagnostics / 运行诊断**: `python check_gpu.py`

3. **Check GPU memory / 检查 GPU 内存**: `nvidia-smi`

4. **Read the guides / 阅读指南**:
   - [API Usage Guide / API 使用指南](API_USAGE.md)
   - [Low VRAM Guide / 低显存指南](LOW_VRAM_GUIDE.md)

5. **Check the requirements / 检查要求**: Ensure all dependencies are installed correctly
   确保所有依赖正确安装

---

## Summary / 总结

**You've successfully set up DeepSeek-OCR! / 你已成功设置 DeepSeek-OCR！**

✓ Environment configured / 环境已配置
✓ Dependencies installed / 依赖已安装
✓ GPU verified / GPU 已验证
✓ API server running / API 服务器运行中
✓ Ready to perform OCR / 准备执行 OCR

**API Endpoint / API 端点:** `http://localhost:8031`
**Interactive Docs / 交互式文档:** `http://localhost:8031/docs`

Happy OCR-ing! / OCR 愉快！
