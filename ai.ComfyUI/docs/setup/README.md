# 环境准备与安装

## 前置准备
- **硬件**：建议 8GB 以上显存 (如 RTX 3060)，也可用 CPU/低显存但生成时间会更长
- **软件**：Windows 10/11、Python 3.10/3.11、Git；可选安装 7-Zip 便于解压模型
- **模型资源**：基础 SD1.5 或 SDXL checkpoint、VAE、LoRA、ControlNet 权重等，可放入 `ComfyUI/models/` 下对应子目录

## 安装与启动
1. 克隆官方仓库
   ```powershell
   git clone https://github.com/comfyanonymous/ComfyUI.git
   cd ComfyUI
   ```
2. (可选) 创建虚拟环境
   ```powershell
   python -m venv .venv
   .\\.venv\\Scripts\\activate
   ```
3. 安装依赖
   ```powershell
   pip install -r requirements.txt
   ```
4. 启动 ComfyUI
   ```powershell
   python main.py --windows-standalone-build
   ```
   首次运行会在 `ComfyUI/custom_nodes`、`ComfyUI/web/extensions` 等目录生成必要文件，浏览器访问 `http://127.0.0.1:8188/` 即可。
