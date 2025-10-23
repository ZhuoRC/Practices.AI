# Qwen Image API 本地服务

基于 Qwen Image 模型的本地图片生成 API 服务。

## 🚀 快速启动

### 方法 1: 简单启动
双击 `start.bat` 文件或在命令行运行：
```cmd
start.bat
```

### 方法 2: 高级启动
```cmd
# 基础启动
python start_advanced.py

# 指定端口和地址
python start_advanced.py --host 0.0.0.0 --port 8080

# 多进程启动
python start_advanced.py --workers 2

# 跳过环境检查（快速启动）
python start_advanced.py --skip-checks
```

### 方法 3: 手动启动
```cmd
# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动服务
python run_qwen_image_api_6gb.py
```

## 📖 API 使用

服务启动后，访问 http://localhost:8000/docs 查看交互式 API 文档。

### 生成图片
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "一只可爱的猫咪在花园里玩耍"}'
```

### Python 客户端示例
```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={"prompt": "一只可爱的猫咪在花园里玩耍"}
)
print(response.json())
```

## ⚙️ 配置说明

- **默认分辨率**: 512x512 (可节省显存)
- **推理步数**: 15 (平衡速度和质量)
- **引导系数**: 0.8 (创意度)
- **自动设备选择**: GPU可用时使用GPU，否则使用CPU

## 🔧 环境要求

- Python 3.8+
- CUDA (可选，用于GPU加速)
- 至少 6GB 显存 (推荐使用 GPU)

## 📁 文件说明

- `run_qwen_image_api_6gb.py` - 主服务程序
- `start.bat` - Windows 批处理启动脚本
- `start_advanced.py` - 高级 Python 启动脚本
- `requirements.txt` - 依赖包列表
- `output.png` - 生成的图片文件

## 🛠️ 故障排除

1. **显存不足**: 程序已优化为 6GB 显存友好模式
2. **模型加载慢**: 首次运行需要下载模型，请耐心等待
3. **依赖安装失败**: 确保网络连接正常，或使用国内镜像源

## 📝 日志

程序运行时会显示详细的加载和生成日志，便于调试和监控。