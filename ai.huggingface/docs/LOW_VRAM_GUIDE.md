# DeepSeek-OCR Low VRAM Optimization Guide

# DeepSeek-OCR 低显存优化指南

Complete guide for running DeepSeek-OCR on GPUs with limited VRAM (6GB or less)

在显存有限的 GPU（6GB 或更少）上运行 DeepSeek-OCR 的完整指南

---

## Table of Contents / 目录

- [Understanding VRAM Requirements / 理解显存需求](#understanding-vram-requirements--理解显存需求)
- [Built-in Optimizations / 内置优化](#built-in-optimizations--内置优化)
- [Additional Optimization Strategies / 额外优化策略](#additional-optimization-strategies--额外优化策略)
- [Troubleshooting OOM Errors / 解决内存不足错误](#troubleshooting-oom-errors--解决内存不足错误)
- [Performance vs Memory Trade-offs / 性能与内存权衡](#performance-vs-memory-trade-offs--性能与内存权衡)
- [Monitoring GPU Memory / 监控 GPU 内存](#monitoring-gpu-memory--监控-gpu-内存)

---

## Understanding VRAM Requirements / 理解显存需求

### Model Size / 模型大小

DeepSeek-OCR is a 3B (3 billion parameters) model, which requires:

DeepSeek-OCR 是一个 3B（30 亿参数）的模型，需要：

- **Minimum / 最低**: ~6GB VRAM (with optimizations) / 约 6GB 显存（带优化）
- **Recommended / 推荐**: 8-12GB VRAM / 8-12GB 显存
- **Comfortable / 舒适**: 12GB+ VRAM / 12GB+ 显存

### Memory Breakdown / 内存分解

| Component | Memory Usage | Description |
|-----------|--------------|-------------|
| Model Weights / 模型权重 | ~3GB (bfloat16) | Model parameters / 模型参数 |
| Activation Memory / 激活内存 | ~1-2GB | Temporary computation / 临时计算 |
| Image Processing / 图像处理 | ~0.5-1GB | Input image tensors / 输入图像张量 |
| PyTorch Overhead / PyTorch 开销 | ~0.5GB | CUDA context / CUDA 上下文 |
| **Total / 总计** | **~5-6.5GB** | **Minimum required / 最低需求** |

---

## Built-in Optimizations / 内置优化

The API already includes several optimizations:

API 已包含多项优化：

### 1. Mixed Precision (bfloat16) / 混合精度 (bfloat16)

**What it does / 作用:**
- Reduces memory by 50% (vs float32) / 相比 float32 减少 50% 内存
- Maintains numerical stability / 保持数值稳定性

**Automatically enabled / 自动启用:**
```python
torch_dtype = torch.bfloat16  # Built into the API / 内置于 API
```

### 2. Flash Attention 2

**What it does / 作用:**
- Memory-efficient attention mechanism / 内存高效的注意力机制
- Reduces memory usage by ~30% / 减少约 30% 内存使用
- Faster inference / 更快的推理

**Required dependency / 必需依赖:**
```bash
pip install flash-attn==2.7.3 --no-build-isolation
```

### 3. Inference Mode / 推理模式

**What it does / 作用:**
- Disables gradient computation / 禁用梯度计算
- Reduces memory overhead / 减少内存开销

**Automatically enabled / 自动启用:**
```python
with torch.inference_mode():  # Built into the API / 内置于 API
    result = model.chat(...)
```

### 4. Aggressive Memory Cleanup / 激进的内存清理

**What it does / 作用:**
- Clears CUDA cache after each request / 每次请求后清理 CUDA 缓存
- Forces garbage collection / 强制垃圾回收

**Automatically enabled / 自动启用:**
```python
gc.collect()
torch.cuda.empty_cache()
torch.cuda.synchronize()
```

---

## Additional Optimization Strategies / 额外优化策略

If you're still experiencing OOM (Out of Memory) errors, try these strategies:

如果仍然遇到 OOM（内存不足）错误，请尝试以下策略：

### Strategy 1: Reduce Image Size / 策略 1: 减小图片尺寸

**Problem / 问题:**

Large images consume more VRAM during processing.

大图片在处理时消耗更多显存。

**Solution / 解决方案:**

Resize images before sending to the API:

发送到 API 前调整图片大小：

```python
from PIL import Image

def resize_image(image_path, max_size=2048):
    """
    Resize image while maintaining aspect ratio
    在保持宽高比的同时调整图片大小
    """
    img = Image.open(image_path)

    # Get current size / 获取当前尺寸
    width, height = img.size

    # Calculate new size / 计算新尺寸
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))

        img = img.resize((new_width, new_height), Image.LANCZOS)
        print(f"Resized from {width}x{height} to {new_width}x{new_height}")

    return img

# Usage / 使用
resized_img = resize_image("large_document.png", max_size=2048)
resized_img.save("resized_document.png")

# Now send the resized image to API / 现在将调整大小后的图片发送到 API
```

**Recommended sizes / 推荐尺寸:**

| VRAM | Max Image Size | Description |
|------|----------------|-------------|
| 6GB | 1536x1536 | Safe for most cases / 大多数情况下安全 |
| 8GB | 2048x2048 | Comfortable / 舒适 |
| 12GB+ | 4096x4096 | No restrictions / 无限制 |

### Strategy 2: Process Images in Batches / 策略 2: 分批处理图片

**Problem / 问题:**

Processing multiple images consecutively can accumulate memory.

连续处理多个图片会累积内存。

**Solution / 解决方案:**

Add cleanup between requests:

在请求之间添加清理：

```python
import requests
import time

def process_images_safely(image_paths):
    """
    Process multiple images with memory cleanup
    处理多个图片并清理内存
    """
    results = []

    for i, image_path in enumerate(image_paths):
        print(f"Processing image {i+1}/{len(image_paths)}: {image_path}")

        # Send OCR request / 发送 OCR 请求
        with open(image_path, "rb") as f:
            files = {"image": f}
            response = requests.post(
                "http://localhost:8031/ocr",
                files=files
            )

        results.append(response.json())

        # Force cleanup between images / 在图片之间强制清理
        if i < len(image_paths) - 1:
            requests.post("http://localhost:8031/cleanup")
            time.sleep(1)  # Give GPU time to clean up / 给 GPU 时间清理

    return results

# Usage / 使用
images = ["doc1.png", "doc2.png", "doc3.png"]
results = process_images_safely(images)
```

### Strategy 3: Close Other GPU Applications / 策略 3: 关闭其他 GPU 应用程序

**Problem / 问题:**

Other applications using the GPU reduce available VRAM.

其他使用 GPU 的应用程序会减少可用显存。

**Solution / 解决方案:**

1. Close web browsers with hardware acceleration / 关闭启用硬件加速的浏览器
2. Close gaming applications / 关闭游戏应用程序
3. Close other ML/AI applications / 关闭其他 ML/AI 应用程序
4. Close video editing software / 关闭视频编辑软件

**Check what's using your GPU / 检查什么在使用你的 GPU:**

```bash
# Windows
nvidia-smi

# Look for processes under "Processes" / 查看"进程"下的进程
```

### Strategy 4: Restart the API Server / 策略 4: 重启 API 服务器

**Problem / 问题:**

Memory fragmentation over time can reduce available VRAM.

内存碎片化会随时间减少可用显存。

**Solution / 解决方案:**

Restart the server periodically:

定期重启服务器：

```bash
# Stop the server (Ctrl+C) / 停止服务器 (Ctrl+C)
# Then restart / 然后重启
python deepseek_ocr/deepseek_ocr_api_low_vram.py
```

**Automated restart script / 自动重启脚本:**

```python
#!/usr/bin/env python3
"""
Auto-restart API server after N requests
处理 N 个请求后自动重启 API 服务器
"""
import requests
import subprocess
import time
import sys

MAX_REQUESTS = 50  # Restart after 50 requests / 处理 50 个请求后重启

def start_server():
    """Start the API server / 启动 API 服务器"""
    return subprocess.Popen(
        ["python", "deepseek_ocr/deepseek_ocr_api_low_vram.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():
    request_count = 0
    server_process = start_server()

    print("API server started with auto-restart enabled")
    print(f"Will restart after {MAX_REQUESTS} requests")

    try:
        while True:
            time.sleep(10)  # Check every 10 seconds / 每 10 秒检查一次

            # In production, track requests via a counter file
            # 在生产环境中，通过计数文件跟踪请求
            # For now, just demonstrate the concept
            # 现在只是演示概念

            if request_count >= MAX_REQUESTS:
                print(f"Reached {MAX_REQUESTS} requests, restarting...")
                server_process.terminate()
                server_process.wait()
                time.sleep(5)
                server_process = start_server()
                request_count = 0
                print("API server restarted successfully")

    except KeyboardInterrupt:
        print("\nShutting down...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
```

### Strategy 5: Use CPU Offload (Advanced) / 策略 5: 使用 CPU 卸载（高级）

**Problem / 问题:**

6GB VRAM is still not enough.

6GB 显存仍然不够。

**Solution / 解决方案:**

Modify the API to use CPU offload for some components:

修改 API 以对某些组件使用 CPU 卸载：

```python
# In deepseek_ocr_api_low_vram.py
# Find the model loading section and add:

# Load model with device_map for automatic offloading
# 使用 device_map 加载模型以自动卸载
model = AutoModel.from_pretrained(
    model_name,
    attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch_dtype,
    device_map="auto",  # Add this line / 添加这一行
    max_memory={0: "5GB", "cpu": "16GB"}  # Limit GPU usage / 限制 GPU 使用
)
```

**Warning / 警告:** This will make inference slower but uses less VRAM.

这会使推理变慢但使用更少的显存。

---

## Troubleshooting OOM Errors / 解决内存不足错误

### Error: CUDA Out of Memory / 错误: CUDA 内存不足

```
torch.cuda.OutOfMemoryError: CUDA out of memory.
Tried to allocate 512.00 MiB (GPU 0; 6.00 GiB total capacity)
```

**Step-by-Step Solution / 逐步解决方案:**

1. **Check available memory / 检查可用内存:**
   ```bash
   nvidia-smi
   ```
   Look at "Memory-Usage" column / 查看"内存使用"列

2. **Close other GPU applications / 关闭其他 GPU 应用程序**
   - Browsers, games, other ML apps / 浏览器、游戏、其他 ML 应用

3. **Reduce image size / 减小图片尺寸**
   - Resize to 1536x1536 or smaller / 调整到 1536x1536 或更小

4. **Force cleanup / 强制清理**
   ```bash
   curl -X POST http://localhost:8031/cleanup
   ```

5. **Restart the API server / 重启 API 服务器**
   - Stop (Ctrl+C) and restart / 停止 (Ctrl+C) 并重启

6. **If still failing, use CPU offload / 如果仍然失败，使用 CPU 卸载**
   - See Strategy 5 above / 见上面的策略 5

---

## Performance vs Memory Trade-offs / 性能与内存权衡

| Optimization | Memory Saved | Speed Impact | Recommended |
|--------------|--------------|--------------|-------------|
| bfloat16 | 50% | Minimal / 最小 | ✅ Yes / 是 |
| Flash Attention | 30% | Faster / 更快 | ✅ Yes / 是 |
| Image Resize (2048→1536) | 20% | None / 无 | ✅ Yes (if needed) / 是（如需要） |
| CPU Offload | 40% | **Much slower / 慢很多** | ⚠️ Only if necessary / 仅在必要时 |
| Attention Slicing | 15% | Slower / 较慢 | ⚠️ Only if necessary / 仅在必要时 |

**Recommendation / 建议:**

1. Start with the default settings (bfloat16 + Flash Attention)
   从默认设置开始（bfloat16 + Flash Attention）

2. If OOM, resize images to 1536x1536
   如果 OOM，将图片调整到 1536x1536

3. If still OOM, close other GPU applications
   如果仍然 OOM，关闭其他 GPU 应用程序

4. As a last resort, use CPU offload
   作为最后手段，使用 CPU 卸载

---

## Monitoring GPU Memory / 监控 GPU 内存

### Real-time Monitoring / 实时监控

**Terminal / 终端:**
```bash
# Update every 1 second / 每 1 秒更新
watch -n 1 nvidia-smi
```

**Python Script / Python 脚本:**
```python
import requests
import time

def monitor_memory():
    """
    Monitor API memory usage
    监控 API 内存使用
    """
    while True:
        try:
            response = requests.get("http://localhost:8031/health")
            data = response.json()

            if "gpu_memory_allocated" in data:
                print(f"Allocated: {data['gpu_memory_allocated']}")
                print(f"Reserved:  {data['gpu_memory_reserved']}")
                print(f"Free:      {data['gpu_memory_free']}")
                print("-" * 40)

            time.sleep(2)

        except KeyboardInterrupt:
            print("\nStopped monitoring")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_memory()
```

### Memory Usage Log / 内存使用日志

The API automatically logs memory usage:

API 自动记录内存使用：

```
GPU memory before / GPU 内存使用（前）: 3.45 GB
GPU memory after / GPU 内存使用（后）: 3.52 GB
```

---

## Summary / 总结

### For 6GB VRAM GPUs / 对于 6GB 显存的 GPU:

✅ **Do / 做:**
- Use the low VRAM version (already provided) / 使用低显存版本（已提供）
- Resize large images to 1536x1536 / 将大图片调整到 1536x1536
- Close other GPU applications / 关闭其他 GPU 应用程序
- Use cleanup endpoint between batches / 在批次之间使用清理端点

❌ **Don't / 不要:**
- Process very large images (4K+) / 处理非常大的图片（4K+）
- Run multiple GPU applications simultaneously / 同时运行多个 GPU 应用程序
- Ignore OOM warnings / 忽略 OOM 警告

### For 8GB+ VRAM GPUs / 对于 8GB+ 显存的 GPU:

You should have no issues with most images! / 大多数图片应该没有问题！

✅ Can process images up to 2048x2048 comfortably
✅ Can run other lightweight GPU applications
✅ No special optimizations needed

---

## Getting Help / 获取帮助

If you're still experiencing issues after following this guide:

如果按照本指南操作后仍然遇到问题：

1. Check the API logs for specific error messages
   检查 API 日志中的具体错误信息

2. Run `python check_gpu.py` to verify your environment
   运行 `python check_gpu.py` 验证环境

3. Check GPU usage with `nvidia-smi`
   使用 `nvidia-smi` 检查 GPU 使用情况

4. Review the [API Usage Guide](API_USAGE.md) for correct usage
   查看 [API 使用指南](API_USAGE.md) 了解正确用法

5. Review the [Quick Start Guide](QUICK_START.md) for setup issues
   查看[快速开始指南](QUICK_START.md) 了解设置问题

---

**Remember / 记住:** The low VRAM version is already optimized for 6GB GPUs. Most users won't need additional optimizations!

低显存版本已针对 6GB GPU 进行优化。大多数用户不需要额外的优化！
