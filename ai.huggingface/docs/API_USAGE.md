# DeepSeek-OCR API Usage Guide / API 使用指南

Complete API reference for DeepSeek-OCR RESTful API

DeepSeek-OCR RESTful API 完整参考

---

## Table of Contents / 目录

- [Getting Started / 快速开始](#getting-started--快速开始)
- [Base URL / 基础 URL](#base-url--基础-url)
- [Endpoints / 端点](#endpoints--端点)
  - [GET / - API Information / API 信息](#get----api-information--api-信息)
  - [GET /health - Health Check / 健康检查](#get-health---health-check--健康检查)
  - [POST /ocr - OCR from File / 文件 OCR](#post-ocr---ocr-from-file--文件-ocr)
  - [POST /ocr-base64 - OCR from Base64 / Base64 OCR](#post-ocr-base64---ocr-from-base64--base64-ocr)
  - [GET /results/{filename} - Download Result / 下载结果](#get-resultsfilename---download-result--下载结果)
  - [POST /cleanup - Cleanup Memory / 清理内存](#post-cleanup---cleanup-memory--清理内存)
- [Error Handling / 错误处理](#error-handling--错误处理)
- [Examples / 示例](#examples--示例)

---

## Getting Started / 快速开始

Before using the API, make sure the server is running:

使用 API 前，确保服务器正在运行：

```bash
cd ai.huggingface
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

python deepseek_ocr/deepseek_ocr_api_low_vram.py
```

The server will start on `http://localhost:8031`

服务器将在 `http://localhost:8031` 启动

---

## Base URL / 基础 URL

```
http://localhost:8031
```

For remote access, replace `localhost` with your server's IP address.

远程访问时，将 `localhost` 替换为服务器的 IP 地址。

---

## Endpoints / 端点

### GET `/` - API Information / API 信息

Get basic information about the API.

获取 API 的基本信息。

**Response / 响应:**

```json
{
  "name": "DeepSeek-OCR API (Low VRAM Mode)",
  "name_zh": "DeepSeek-OCR API（低显存模式）",
  "status": "running",
  "model": "deepseek-ai/DeepSeek-OCR",
  "mode": "Low VRAM Optimized",
  "endpoints": { ... }
}
```

**Example / 示例:**

```bash
# curl
curl http://localhost:8031/

# Python
import requests
response = requests.get("http://localhost:8031/")
print(response.json())
```

---

### GET `/health` - Health Check / 健康检查

Check if the API is healthy and get GPU memory statistics.

检查 API 是否健康并获取 GPU 内存统计。

**Response / 响应:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "tokenizer_loaded": true,
  "device": "cuda",
  "mode": "Low VRAM (torch.bfloat16)",
  "gpu_name": "NVIDIA GeForce RTX 3060",
  "gpu_memory_total": "12.00 GB",
  "gpu_memory_allocated": "3.45 GB",
  "gpu_memory_reserved": "4.12 GB",
  "gpu_memory_free": "7.88 GB"
}
```

**Example / 示例:**

```bash
# curl
curl http://localhost:8031/health

# Python
import requests
response = requests.get("http://localhost:8031/health")
print(response.json())
```

---

### POST `/ocr` - OCR from File / 文件 OCR

Extract text from an uploaded image file.

从上传的图片文件中提取文本。

**Request Parameters / 请求参数:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | File | Yes | - | Image file (PNG, JPG, etc.) / 图片文件 (PNG, JPG 等) |
| `prompt` | String | No | `"<image>\nFree OCR."` | OCR prompt / OCR 提示词 |
| `save_to_file` | Boolean | No | `true` | Save result to file / 保存结果到文件 |

**Response / 响应:**

```json
{
  "success": true,
  "message": "OCR completed successfully / OCR 成功完成",
  "text": "Extracted text content here...",
  "output_file": "ocr_result_20250127_143022.txt"
}
```

**Example / 示例:**

```bash
# curl
curl -X POST http://localhost:8031/ocr \
  -F "image=@/path/to/image.png" \
  -F "prompt=<image>\nFree OCR." \
  -F "save_to_file=true"

# Python
import requests

# Upload image file
with open("image.png", "rb") as f:
    files = {"image": f}
    data = {
        "prompt": "<image>\nFree OCR.",
        "save_to_file": True
    }
    response = requests.post(
        "http://localhost:8031/ocr",
        files=files,
        data=data
    )
    result = response.json()
    print(result["text"])
```

**Python Complete Example / Python 完整示例:**

```python
import requests

def ocr_from_file(image_path, prompt="<image>\nFree OCR.", save_to_file=True):
    """
    Perform OCR on an image file
    对图片文件执行 OCR
    """
    url = "http://localhost:8031/ocr"

    with open(image_path, "rb") as f:
        files = {"image": ("image.png", f, "image/png")}
        data = {
            "prompt": prompt,
            "save_to_file": save_to_file
        }

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            print("✓ OCR Success!")
            print(f"Text: {result['text']}")
            if result.get("output_file"):
                print(f"Saved to: {result['output_file']}")
            return result
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.json())
            return None

# Usage
result = ocr_from_file("document.png")
```

---

### POST `/ocr-base64` - OCR from Base64 / Base64 OCR

Extract text from a base64 encoded image.

从 base64 编码的图片中提取文本。

**Request Body / 请求体:**

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "prompt": "<image>\nFree OCR.",
  "save_to_file": true
}
```

**Response / 响应:**

```json
{
  "success": true,
  "message": "OCR completed successfully / OCR 成功完成",
  "text": "Extracted text content here...",
  "output_file": "ocr_result_20250127_143022.txt"
}
```

**Example / 示例:**

```bash
# curl
curl -X POST http://localhost:8031/ocr-base64 \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/png;base64,iVBORw0KGgo...",
    "prompt": "<image>\nFree OCR.",
    "save_to_file": true
  }'
```

**Python Example / Python 示例:**

```python
import requests
import base64

def ocr_from_base64(image_path, prompt="<image>\nFree OCR.", save_to_file=True):
    """
    Perform OCR on an image using base64 encoding
    使用 base64 编码对图片执行 OCR
    """
    url = "http://localhost:8031/ocr-base64"

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Add data URL prefix (optional)
    image_base64 = f"data:image/png;base64,{image_base64}"

    # Prepare request
    payload = {
        "image_base64": image_base64,
        "prompt": prompt,
        "save_to_file": save_to_file
    }

    # Send request
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        print("✓ OCR Success!")
        print(f"Text: {result['text']}")
        if result.get("output_file"):
            print(f"Saved to: {result['output_file']}")
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.json())
        return None

# Usage
result = ocr_from_base64("document.png")
```

---

### GET `/results/{filename}` - Download Result / 下载结果

Download a saved OCR result file.

下载保存的 OCR 结果文件。

**Example / 示例:**

```bash
# curl
curl http://localhost:8031/results/ocr_result_20250127_143022.txt \
  -o result.txt

# Python
import requests

filename = "ocr_result_20250127_143022.txt"
url = f"http://localhost:8031/results/{filename}"

response = requests.get(url)
if response.status_code == 200:
    with open("downloaded_result.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("✓ File downloaded successfully!")
else:
    print(f"✗ Error: {response.status_code}")
```

---

### POST `/cleanup` - Cleanup Memory / 清理内存

Force GPU memory cleanup. Useful when experiencing memory issues.

强制 GPU 内存清理。在遇到内存问题时很有用。

**Response / 响应:**

```json
{
  "message": "Memory cleanup completed / 内存清理完成",
  "gpu_memory_allocated": "1.23 GB",
  "gpu_memory_reserved": "2.45 GB"
}
```

**Example / 示例:**

```bash
# curl
curl -X POST http://localhost:8031/cleanup

# Python
import requests
response = requests.post("http://localhost:8031/cleanup")
print(response.json())
```

---

## Error Handling / 错误处理

The API uses standard HTTP status codes:

API 使用标准的 HTTP 状态码：

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful / 请求成功 |
| 400 | Bad Request | Invalid input / 输入无效 |
| 404 | Not Found | Resource not found / 资源未找到 |
| 500 | Internal Server Error | Server error / 服务器错误 |
| 503 | Service Unavailable | Model not loaded / 模型未加载 |
| 507 | Insufficient Storage | Out of memory / 内存不足 |

**Error Response Example / 错误响应示例:**

```json
{
  "detail": {
    "error": "GPU out of memory / GPU 内存不足",
    "message": "The OCR process exceeded available GPU memory",
    "suggestions": [
      "Reduce image size / 减小图片尺寸",
      "Close all other GPU applications / 关闭其他 GPU 应用程序",
      "Restart the API server / 重启 API 服务器"
    ]
  }
}
```

---

## Examples / 示例

### Complete Python Script / 完整 Python 脚本

```python
#!/usr/bin/env python3
"""
DeepSeek-OCR API Client Example
DeepSeek-OCR API 客户端示例
"""
import requests
import base64
import sys

API_BASE_URL = "http://localhost:8031"

def check_health():
    """Check API health / 检查 API 健康状态"""
    response = requests.get(f"{API_BASE_URL}/health")
    return response.json()

def ocr_file(image_path, prompt="<image>\nFree OCR.", save_to_file=True):
    """
    OCR from file upload
    从文件上传进行 OCR
    """
    url = f"{API_BASE_URL}/ocr"

    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"prompt": prompt, "save_to_file": save_to_file}
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"OCR failed: {response.json()}")

def ocr_base64(image_path, prompt="<image>\nFree OCR.", save_to_file=True):
    """
    OCR from base64 encoding
    从 base64 编码进行 OCR
    """
    url = f"{API_BASE_URL}/ocr-base64"

    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "image_base64": f"data:image/png;base64,{image_base64}",
        "prompt": prompt,
        "save_to_file": save_to_file
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"OCR failed: {response.json()}")

def download_result(filename, output_path):
    """
    Download OCR result file
    下载 OCR 结果文件
    """
    url = f"{API_BASE_URL}/results/{filename}"
    response = requests.get(url)

    if response.status_code == 200:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        return True
    else:
        raise Exception(f"Download failed: {response.status_code}")

def main():
    """Main function / 主函数"""
    # Check health / 检查健康状态
    print("Checking API health... / 检查 API 健康状态...")
    health = check_health()
    print(f"Status: {health['status']}")
    print(f"Device: {health['device']}")
    print()

    # Perform OCR / 执行 OCR
    if len(sys.argv) < 2:
        print("Usage: python api_client.py <image_path>")
        print("用法: python api_client.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]
    print(f"Processing image: {image_path}")
    print(f"处理图片: {image_path}")
    print()

    # Method 1: File upload / 方法 1: 文件上传
    print("Method 1: File upload / 方法 1: 文件上传")
    result = ocr_file(image_path)
    print(f"✓ Success! / 成功！")
    print(f"Text length: {len(result['text'])} characters")
    print(f"文本长度: {len(result['text'])} 字符")
    print(f"Output file: {result.get('output_file', 'N/A')}")
    print(f"输出文件: {result.get('output_file', '无')}")
    print()

    # Display extracted text / 显示提取的文本
    print("Extracted text / 提取的文本:")
    print("-" * 60)
    print(result['text'])
    print("-" * 60)

if __name__ == "__main__":
    main()
```

**Save this as `api_client.py` and run:**

**保存为 `api_client.py` 并运行:**

```bash
python api_client.py document.png
```

---

### JavaScript/Node.js Example / JavaScript/Node.js 示例

```javascript
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const API_BASE_URL = 'http://localhost:8031';

async function ocrFile(imagePath) {
    const form = new FormData();
    form.append('image', fs.createReadStream(imagePath));
    form.append('prompt', '<image>\nFree OCR.');
    form.append('save_to_file', 'true');

    try {
        const response = await axios.post(
            `${API_BASE_URL}/ocr`,
            form,
            { headers: form.getHeaders() }
        );

        console.log('✓ OCR Success!');
        console.log('Text:', response.data.text);
        console.log('Output file:', response.data.output_file);
        return response.data;
    } catch (error) {
        console.error('✗ OCR failed:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
ocrFile('document.png')
    .then(result => console.log('Done!'))
    .catch(err => console.error('Error:', err));
```

---

### cURL Examples / cURL 示例

```bash
# Health check / 健康检查
curl http://localhost:8031/health

# OCR from file / 文件 OCR
curl -X POST http://localhost:8031/ocr \
  -F "image=@document.png" \
  -F "prompt=<image>\nFree OCR." \
  -F "save_to_file=true"

# Download result / 下载结果
curl http://localhost:8031/results/ocr_result_20250127_143022.txt \
  -o result.txt

# Cleanup memory / 清理内存
curl -X POST http://localhost:8031/cleanup
```

---

## Tips / 提示

1. **Image Format / 图片格式**: Supports PNG, JPG, JPEG, etc. / 支持 PNG、JPG、JPEG 等格式
2. **Image Size / 图片尺寸**: Smaller images process faster / 较小的图片处理更快
3. **Memory / 内存**: If you get OOM errors, try reducing image size / 如果出现 OOM 错误，尝试减小图片尺寸
4. **Prompts / 提示词**: Use `"<image>\nFree OCR."` for general OCR / 一般 OCR 使用 `"<image>\nFree OCR."`
5. **Markdown Conversion / Markdown 转换**: Use `"<image>\nConvert document to markdown"` for structured output / 使用 `"<image>\nConvert document to markdown"` 获取结构化输出

---

## Interactive API Documentation / 交互式 API 文档

FastAPI provides automatic interactive documentation:

FastAPI 提供自动交互式文档：

- **Swagger UI**: http://localhost:8031/docs
- **ReDoc**: http://localhost:8031/redoc

You can test all endpoints directly in your browser!

你可以直接在浏览器中测试所有端点！

---

For more information, see:

更多信息，请参阅：

- [Quick Start Guide / 快速开始指南](QUICK_START.md)
- [Low VRAM Guide / 低显存指南](LOW_VRAM_GUIDE.md)
- [Project README / 项目说明](../README.md)
