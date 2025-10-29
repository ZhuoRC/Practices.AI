# DeepSeek-OCR Local Deployment

# DeepSeek-OCR 本地部署

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/deepseek-ai/DeepSeek-OCR/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/pytorch-2.5.1-orange.svg)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/cuda-11.8%2B-green.svg)](https://developer.nvidia.com/cuda-downloads)

Local deployment of DeepSeek-OCR with RESTful API, optimized for low VRAM GPUs (6GB+).

本地部署 DeepSeek-OCR 并提供 RESTful API，针对低显存 GPU（6GB+）优化。

---

## ✨ Features / 功能特性

- 🚀 **RESTful API**: Easy-to-use HTTP API / 易用的 HTTP API
- 💾 **Low VRAM Optimized**: Runs on GPUs with 6GB+ VRAM / 在 6GB+ 显存的 GPU 上运行
- 📁 **File Upload Support**: Upload images directly / 直接上传图片
- 🔤 **Base64 Support**: Process base64 encoded images / 处理 base64 编码的图片
- 💿 **Auto-save Results**: Automatically save OCR results to files / 自动保存 OCR 结果到文件
- 🌐 **Interactive Docs**: Built-in Swagger UI / 内置 Swagger UI
- 🔧 **GPU Diagnostics**: Built-in GPU checking tool / 内置 GPU 检测工具
- 📖 **Bilingual Docs**: Complete Chinese & English documentation / 完整的中英文文档

---

## 📋 Table of Contents / 目录

- [Quick Start / 快速开始](#-quick-start--快速开始)
- [Requirements / 系统要求](#-requirements--系统要求)
- [Installation / 安装](#-installation--安装)
- [Usage / 使用方法](#-usage--使用方法)
- [API Endpoints / API 端点](#-api-endpoints--api-端点)
- [Examples / 示例](#-examples--示例)
- [Documentation / 文档](#-documentation--文档)
- [Troubleshooting / 故障排除](#-troubleshooting--故障排除)
- [Project Structure / 项目结构](#-project-structure--项目结构)
- [License / 许可证](#-license--许可证)

---

## 🚀 Quick Start / 快速开始

Get started in 3 simple steps! / 三步快速开始！

### 1. Install Dependencies / 安装依赖

```bash
# Create virtual environment / 创建虚拟环境
python -m venv .venv

# Activate / 激活
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install PyTorch with CUDA / 安装支持 CUDA 的 PyTorch
pip install torch==2.5.1+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Flash Attention / 安装 Flash Attention
pip install flash-attn==2.7.3 --no-build-isolation

# Install other dependencies / 安装其他依赖
pip install -r requirements.txt
```

### 2. Verify Installation / 验证安装

```bash
python check_gpu.py
```

### 3. Start API Server / 启动 API 服务器

```bash
python deepseek_ocr/deepseek_ocr_api_low_vram.py
```

**🎉 Done! API is running on / 完成！API 运行在:** `http://localhost:8031`

**📚 Interactive Docs / 交互式文档:** `http://localhost:8031/docs`

---

## 💻 Requirements / 系统要求

### Hardware / 硬件

- **GPU**: NVIDIA GPU with 6GB+ VRAM / NVIDIA GPU，6GB+ 显存
  - Recommended / 推荐: GTX 1660 Ti, RTX 3060, RTX 4060 or better / 或更好
  - Minimum / 最低: GTX 1060 6GB (with optimizations) / 搭配优化
- **RAM**: 16GB+ system memory / 16GB+ 系统内存
- **Disk**: 20GB+ free space / 20GB+ 可用空间

### Software / 软件

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS
- **Python**: 3.12.9+ (3.12 recommended / 推荐 3.12)
- **CUDA**: 11.8 or 12.1
- **NVIDIA Driver**: Latest / 最新版本

---

## 📦 Installation / 安装

### Step 1: Clone or Download / 克隆或下载

This project is part of the `Practices.AI` monorepo:

本项目是 `Practices.AI` 单体仓库的一部分：

```bash
# Navigate to the project / 进入项目目录
cd ai.huggingface
```

### Step 2: Create Virtual Environment / 创建虚拟环境

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Step 3: Install PyTorch with CUDA / 安装支持 CUDA 的 PyTorch

**Check your CUDA version first / 首先检查 CUDA 版本:**

```bash
nvidia-smi
```

**Install PyTorch / 安装 PyTorch:**

```bash
# For CUDA 12.1 / 适用于 CUDA 12.1
pip install torch==2.5.1+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8 / 适用于 CUDA 11.8
pip install torch==2.5.1+cu118 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 4: Install Flash Attention / 安装 Flash Attention

**⚠️ IMPORTANT / 重要**: This is **required** for DeepSeek-OCR!

这是 DeepSeek-OCR 的**必需**组件！

```bash
pip install flash-attn==2.7.3 --no-build-isolation
```

**Note / 注意**: This may take 5-10 minutes to compile.

编译可能需要 5-10 分钟。

### Step 5: Install Other Dependencies / 安装其他依赖

```bash
pip install -r requirements.txt
```

### Step 6: Verify Installation / 验证安装

```bash
python check_gpu.py
```

**Expected output / 期望输出:**

```
[OK] GPU environment is properly configured!
[OK] DeepSeek-OCR is ready to run
```

---

## 🎯 Usage / 使用方法

### Start the API Server / 启动 API 服务器

```bash
python deepseek_ocr/deepseek_ocr_api_low_vram.py
```

The server will start on `http://localhost:8031`

服务器将在 `http://localhost:8031` 启动

### Using the API / 使用 API

#### Method 1: Web Browser (Interactive Docs) / 方法 1: 浏览器（交互式文档）

Navigate to `http://localhost:8031/docs` for interactive API documentation.

访问 `http://localhost:8031/docs` 查看交互式 API 文档。

#### Method 2: cURL

```bash
# Health check / 健康检查
curl http://localhost:8031/health

# OCR from file / 文件 OCR
curl -X POST http://localhost:8031/ocr \
  -F "image=@document.png" \
  -F "save_to_file=true"
```

#### Method 3: Python

```python
import requests

# Perform OCR / 执行 OCR
with open("document.png", "rb") as f:
    files = {"image": f}
    response = requests.post("http://localhost:8031/ocr", files=files)
    result = response.json()
    print(result["text"])
```

See [API Usage Guide](docs/API_USAGE.md) for complete examples.

完整示例见 [API 使用指南](docs/API_USAGE.md)。

---

## 🔌 API Endpoints / API 端点

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information / API 信息 |
| `/health` | GET | Health check with GPU stats / 健康检查和 GPU 统计 |
| `/ocr` | POST | OCR from uploaded file / 上传文件进行 OCR |
| `/ocr-base64` | POST | OCR from base64 image / Base64 图片 OCR |
| `/results/{filename}` | GET | Download saved result / 下载保存的结果 |
| `/cleanup` | POST | Force GPU memory cleanup / 强制清理 GPU 内存 |
| `/docs` | GET | Interactive API docs (Swagger) / 交互式 API 文档 |

---

## 📝 Examples / 示例

### Python Example / Python 示例

```python
import requests

def ocr_image(image_path):
    """
    Perform OCR on an image
    对图片执行 OCR
    """
    url = "http://localhost:8031/ocr"

    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {
            "prompt": "<image>\nFree OCR.",
            "save_to_file": True
        }

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            print("✓ OCR Success!")
            print(f"Text: {result['text']}")
            print(f"Saved to: {result['output_file']}")
            return result
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.json())
            return None

# Usage / 使用
result = ocr_image("document.png")
```

### JavaScript Example / JavaScript 示例

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function ocrImage(imagePath) {
    const form = new FormData();
    form.append('image', fs.createReadStream(imagePath));
    form.append('save_to_file', 'true');

    const response = await axios.post(
        'http://localhost:8031/ocr',
        form,
        { headers: form.getHeaders() }
    );

    console.log('Text:', response.data.text);
    return response.data;
}

ocrImage('document.png');
```

### cURL Example / cURL 示例

```bash
# Basic OCR / 基础 OCR
curl -X POST http://localhost:8031/ocr \
  -F "image=@document.png"

# With custom prompt / 使用自定义提示词
curl -X POST http://localhost:8031/ocr \
  -F "image=@document.png" \
  -F "prompt=<image>\nConvert document to markdown"

# Download result / 下载结果
curl http://localhost:8031/results/ocr_result_20250127_143022.txt -o result.txt
```

---

## 📚 Documentation / 文档

Complete documentation is available in the `docs/` directory:

完整文档位于 `docs/` 目录：

- **[Quick Start Guide / 快速开始指南](docs/QUICK_START.md)**: Get started in 3 steps / 三步快速开始
- **[API Usage Guide / API 使用指南](docs/API_USAGE.md)**: Complete API reference with examples / 完整的 API 参考和示例
- **[Low VRAM Guide / 低显存指南](docs/LOW_VRAM_GUIDE.md)**: Optimization tips for 6GB GPUs / 6GB GPU 优化技巧

---

## 🔧 Troubleshooting / 故障排除

### Common Issues / 常见问题

#### Issue 1: CUDA Out of Memory / 问题 1: CUDA 内存不足

**Error / 错误:**
```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Solution / 解决方案:**
1. Close other GPU applications / 关闭其他 GPU 应用程序
2. Reduce image size / 减小图片尺寸
3. Use the cleanup endpoint: `curl -X POST http://localhost:8031/cleanup`
4. See [Low VRAM Guide](docs/LOW_VRAM_GUIDE.md) / 查看[低显存指南](docs/LOW_VRAM_GUIDE.md)

#### Issue 2: Flash Attention Not Found / 问题 2: Flash Attention 未找到

**Error / 错误:**
```
ModuleNotFoundError: No module named 'flash_attn'
```

**Solution / 解决方案:**
```bash
pip install flash-attn==2.7.3 --no-build-isolation
```

#### Issue 3: Model Not Loading / 问题 3: 模型未加载

**Error / 错误:**
```
503 Service Unavailable: Model not loaded
```

**Solution / 解决方案:**
1. Check server logs for errors / 检查服务器日志中的错误
2. Run `python check_gpu.py` / 运行 `python check_gpu.py`
3. Verify all dependencies are installed / 验证所有依赖已安装
4. Restart the server / 重启服务器

### Getting Help / 获取帮助

1. **Check the logs / 检查日志**: The server prints detailed logs
2. **Run diagnostics / 运行诊断**: `python check_gpu.py`
3. **Check GPU status / 检查 GPU 状态**: `nvidia-smi`
4. **Read the guides / 阅读指南**: See [Documentation](#-documentation--文档)

---

## 📁 Project Structure / 项目结构

```
ai.huggingface/
├── .venv/                          # Virtual environment / 虚拟环境
├── check_gpu.py                    # GPU diagnostics tool / GPU 诊断工具
├── requirements.txt                # Python dependencies / Python 依赖
├── README.md                       # This file / 本文件
├── docs/                           # Documentation / 文档
│   ├── API_USAGE.md               # API usage guide / API 使用指南
│   ├── QUICK_START.md             # Quick start guide / 快速开始指南
│   └── LOW_VRAM_GUIDE.md          # Low VRAM optimization / 低显存优化
└── deepseek_ocr/                  # OCR module / OCR 模块
    ├── input/                     # Input images / 输入图片
    ├── output/                    # OCR results / OCR 结果
    └── deepseek_ocr_api_low_vram.py  # API server (Low VRAM) / API 服务器（低显存）
```

---

## 🎨 Features in Detail / 功能详解

### Memory Optimizations / 内存优化

The API includes several built-in optimizations:

API 包含多项内置优化：

- ✅ **torch.bfloat16**: 50% memory reduction / 减少 50% 内存
- ✅ **Flash Attention 2**: 30% memory reduction / 减少 30% 内存
- ✅ **Inference mode**: No gradient computation / 无梯度计算
- ✅ **Automatic cleanup**: Clears CUDA cache after each request / 每次请求后清理 CUDA 缓存

### Input Formats / 输入格式

Supports multiple input methods:

支持多种输入方式：

- 📤 **File upload**: Upload images directly via multipart/form-data / 通过 multipart/form-data 直接上传图片
- 📋 **Base64**: Send base64 encoded images / 发送 base64 编码的图片
- 🖼️ **Image formats**: PNG, JPG, JPEG, etc. / PNG、JPG、JPEG 等

### Output Options / 输出选项

Flexible output handling:

灵活的输出处理：

- 📄 **JSON response**: Get text in API response / 在 API 响应中获取文本
- 💾 **Auto-save**: Automatically save results to files / 自动保存结果到文件
- 📥 **File download**: Download saved results via API / 通过 API 下载保存的结果

---

## 🌟 Model Information / 模型信息

- **Model / 模型**: [deepseek-ai/DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- **Parameters / 参数**: 3B (3 billion / 30 亿)
- **License / 许可证**: MIT
- **Task / 任务**: Optical Character Recognition (OCR) / 光学字符识别
- **Features / 特性**:
  - Text extraction / 文本提取
  - Markdown conversion / Markdown 转换
  - Multi-language support / 多语言支持

---

## 🤝 Contributing / 贡献

Contributions are welcome! / 欢迎贡献！

1. Fork the repository / Fork 仓库
2. Create your feature branch / 创建功能分支
3. Commit your changes / 提交更改
4. Push to the branch / 推送到分支
5. Open a Pull Request / 打开 Pull Request

---

## 📄 License / 许可证

This project is licensed under the MIT License.

本项目采用 MIT 许可证。

The DeepSeek-OCR model is licensed under the MIT License by DeepSeek AI.

DeepSeek-OCR 模型由 DeepSeek AI 采用 MIT 许可证授权。

---

## 🙏 Acknowledgments / 致谢

- [DeepSeek AI](https://www.deepseek.com/) for the DeepSeek-OCR model / 提供 DeepSeek-OCR 模型
- [Hugging Face](https://huggingface.co/) for model hosting / 提供模型托管
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework / 提供 Web 框架
- [PyTorch](https://pytorch.org/) for the deep learning framework / 提供深度学习框架

---

## 📞 Support / 支持

- **Documentation / 文档**: See [docs/](docs/) directory / 查看 [docs/](docs/) 目录
- **Issues / 问题**: Check [Troubleshooting](#-troubleshooting--故障排除) section / 查看[故障排除](#-troubleshooting--故障排除)部分
- **Model Info / 模型信息**: [HuggingFace Model Page](https://huggingface.co/deepseek-ai/DeepSeek-OCR)

---

**Made with ❤️ for the AI community**

**为 AI 社区用心制作**

---

**Quick Links / 快速链接:**

- 📖 [Quick Start / 快速开始](docs/QUICK_START.md)
- 📚 [API Documentation / API 文档](docs/API_USAGE.md)
- 🔧 [Low VRAM Guide / 低显存指南](docs/LOW_VRAM_GUIDE.md)
- 🌐 [Interactive API Docs / 交互式 API 文档](http://localhost:8031/docs) (when server is running / 服务器运行时)
