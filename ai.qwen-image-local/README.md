# Qwen Image Studio

基于 Qwen-VL 和 Z-Image 模型的本地图像处理工具，提供直观的 Web 界面进行图像编辑和文生图。

## 功能特性

### 图像编辑 (Image Editing)
- ✨ **图像上传** - 支持拖拽或点击上传图片
- 🎨 **智能编辑** - 通过自然语言描述编辑图像
- ⚙️ **高级参数** - 支持推理步数、引导系数等参数调整
- 🎯 **实时预览** - 原图和编辑结果对比显示
- 💾 **一键下载** - 方便保存编辑后的图片

### 文生图 (Text to Image)
- 🖼️ **文本生成图像** - 输入描述即可生成高质量图像
- 🎨 **负面提示词** - 排除不想要的元素
- 📐 **自定义尺寸** - 支持多种输出尺寸（256-2048px）
- 🎲 **随机种子** - 固定种子可重现相同结果
- ✨ **提示词增强** - 自动优化提示词以获得更好效果

### 通用特性
- 📱 **响应式设计** - 支持桌面和移动设备
- 🚀 **高性能** - GPU 加速推理
- 🔧 **灵活配置** - 丰富的参数调整选项

## 系统要求

- Python 3.8+
- Node.js 16+
- GPU（推荐，用于加速推理）

## 项目结构

```
ai.qwen-image-local/
├── frontend/                    # React 前端
│   ├── public/                  # 静态资源
│   ├── src/                     # 源代码
│   │   ├── components/          # React 组件
│   │   │   ├── ImageUpload.tsx  # 图片上传组件
│   │   │   ├── ImageEditor.tsx  # 图像编辑组件
│   │   │   ├── ImageDisplay.tsx # 结果展示组件
│   │   │   └── ImageGenerator.tsx # 文生图组件
│   │   ├── services/            # API 服务
│   │   │   ├── imageEditApi.ts  # 图像编辑API
│   │   │   └── imageGenApi.ts   # 文生图API
│   │   ├── types/               # TypeScript 类型
│   │   ├── App.tsx              # 主应用
│   │   └── index.tsx            # 入口文件
│   ├── package.json             # 前端依赖
│   └── start.bat                # 前端启动脚本
├── qwen_image_edit/             # 图像编辑后端
│   └── qwen_image_edit_api.py   # FastAPI 服务（端口 8500）
├── qwen_image/                  # 文生图后端
│   └── qwen_image_api.py        # FastAPI 服务（端口 8501）
├── requirements.txt             # Python 依赖
├── start.bat                    # 完整启动脚本 (CMD)
├── start.ps1                    # 完整启动脚本 (PowerShell)
└── install-deps.bat             # 依赖安装脚本
```

## 快速开始

### 1. 安装后端依赖

**重要：** 
- 必须从 GitHub 安装 diffusers，因为 PyPI 版本不包含 QwenImageEditPipeline
- 安装会在虚拟环境 (.venv) 中进行，避免污染系统 Python 环境

**方式一：使用安装脚本（推荐）**
```bash
cd ai.qwen-image-local
install-deps.bat
```

此脚本会：
1. 创建并激活虚拟环境 (.venv)
2. 安装 PyTorch with CUDA support
3. 从 GitHub 安装 diffusers
4. 安装其他依赖

**方式二：手动安装**
```bash
cd ai.qwen-image-local

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate.bat

# 安装依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install git+https://github.com/huggingface/diffusers
pip install -r requirements.txt
```

> **注意**：如果没有 NVIDIA GPU，安装会使用 CPU 版本（速度较慢）

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 启动服务

#### 方式一：启动文生图服务（推荐用于只使用文生图功能）

在 `ai.qwen-image-local` 目录下运行：

```bash
start-gen.bat
```

这将自动启动：
- 文生图 API（端口 8501）
- 前端界面（端口 3500）

**访问应用后，切换到 "Text to Image" 标签即可使用文生图功能。**

#### 方式二：启动所有服务（图像编辑 + 文生图）

**Windows 命令提示符 (CMD)：**
在 `ai.qwen-image-local` 目录下运行：

```bash
start.bat
```

**Windows PowerShell：**
在 `ai.qwen-image-local` 目录下运行：

```powershell
.\start.ps1
```

这将自动启动：
- 图像编辑 API（端口 8500）
- 文生图 API（端口 8501）
- 前端界面（端口 3500）

#### 方式二：分别启动

**启动图像编辑 API（端口 8500）：**
```bash
python qwen_image_edit/qwen_image_edit_api.py
```

**启动文生图 API（端口 8501）：**
```bash
python qwen_image/qwen_image_api.py
```

**启动前端界面（端口 3500）：**
```bash
cd frontend
npm start
```

### 4. 访问应用

打开浏览器访问：http://localhost:3500

## 使用说明

### 图像编辑 (Image Editing)

1. **切换到 Image Editing 标签**
2. **上传图片** - 点击上传区域或拖拽图片到上传框
3. **输入提示词** - 在编辑提示词框中描述您想要的编辑效果
   - 示例："添加一个红色的帽子"
   - 示例："将背景改为蓝天白云"
4. **调整参数（可选）** - 点击"高级参数"展开更多选项
5. **开始编辑** - 点击"开始编辑"按钮
6. **下载结果** - 编辑完成后，点击"下载图片"保存结果

#### 高级参数说明

- **负面提示词** - 描述不希望出现在结果中的内容
- **推理步数** (10-100) - 步数越多质量越好，但速度越慢。推荐：50
- **引导系数** (1.0-20.0) - 控制模型对提示词的遵循程度。推荐：7.5
- **随机种子** - 固定种子可以重现相同的结果
- **输出尺寸** - 自定义输出图片的宽度和高度

### 文生图 (Text to Image)

1. **切换到 Text to Image 标签**
2. **输入提示词** - 描述您想要生成的图像
   - 示例："一只可爱的橘猫在花园里玩耍，阳光明媚，背景有花朵"
   - 示例："未来的城市天际线，高楼大厦，飞行汽车，科幻风格"
3. **调整参数（可选）** - 点击"Advanced Parameters"展开更多选项
4. **开始生成** - 点击"Generate Image"按钮
5. **下载结果** - 生成完成后，点击"Download"保存图像

#### 高级参数说明

- **Negative Prompt** - 排除不想要的元素（如：模糊，低质量，扭曲）
- **Width / Height** - 自定义输出尺寸（256-2048px，推荐 1024x1024）
- **Inference Steps** - 推理步数（10-100，推荐 50）
- **Guidance Scale** - 引导系数（1.0-20.0，推荐 4.0）
- **Seed** - 随机种子，固定种子可重现结果
- **Enhance Prompt** - 自动优化提示词以获得更好效果

## API 端点

### 图像编辑 API (端口 8500)

#### POST /api/edit

编辑图像

**请求参数：**
- `image` (file) - 要编辑的图片文件
- `prompt` (string, 必需) - 编辑提示词
- `negative_prompt` (string, 可选) - 负面提示词
- `width` (number, 可选) - 输出宽度
- `height` (number, 可选) - 输出高度
- `num_inference_steps` (number, 可选) - 推理步数，默认 50
- `guidance_scale` (number, 可选) - 引导系数，默认 7.5
- `seed` (number, 可选) - 随机种子
- `return_base64` (boolean, 可选) - 是否返回 base64 格式，默认 false

**响应：**
- 成功：返回图片文件 (Content-Type: image/png)
- 失败：返回 JSON 错误信息

#### GET /api/health

健康检查

**响应：**
```json
{
  "status": "ok",
  "model": "Qwen-VL-Chat"
}
```

### 文生图 API (端口 8501)

#### POST /generate

生成图像

**请求参数：**
- `prompt` (string, 必需) - 生成图像的提示词
- `negative_prompt` (string, 可选) - 负面提示词，默认 " "
- `width` (number, 可选) - 输出宽度，默认 1024
- `height` (number, 可选) - 输出高度，默认 1024
- `num_inference_steps` (number, 可选) - 推理步数，默认 50
- `true_cfg_scale` (number, 可选) - 引导系数，默认 4.0
- `seed` (number, 可选) - 随机种子
- `enhance_prompt` (boolean, 可选) - 是否增强提示词，默认 true
- `return_base64` (boolean, 可选) - 是否返回 base64 格式，默认 false

**响应：**
- 成功：返回图片文件 (Content-Type: image/png) 或 base64 字符串
- 失败：返回 JSON 错误信息

#### GET /health

健康检查

**响应：**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

## 技术栈

### 前端
- React 18
- TypeScript
- Ant Design 5
- Axios

### 后端
- FastAPI
- Qwen-VL 模型（图像编辑）
- Z-Image 模型（文生图）- 更轻量、更快速
- Diffusers
- PyTorch

## 常见问题

### 1. 端口被占用

如果端口 8500、8501 或 3500 被占用，可以修改对应的端口配置：

- 图像编辑后端：修改 `qwen_image_edit/qwen_image_edit_api.py` 中的 `port` 参数
- 文生图后端：修改 `qwen_image/qwen_image_api.py` 中的 `port` 参数
- 前端：修改 `frontend/.env` 中的 `PORT` 变量

### 2. 依赖安装失败

**后端依赖：**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**前端依赖：**
```bash
cd frontend
npm install --legacy-peer-deps
```

### 3. GPU 内存不足

如果遇到 CUDA OOM 错误，可以：
- 减小推理步数
- 减小输出图片尺寸
- 使用 CPU 推理（速度较慢）

### 4. 编辑/生成结果不理想

**图像编辑：**
- 尝试更详细的提示词描述
- 调整引导系数（提高会更严格遵循提示词）
- 使用负面提示词排除不想要的内容

**文生图：**
- 使用更具体、详细的提示词
- 启用提示词增强功能
- 调整引导系数和推理步数
- 使用负面提示词排除不想要的元素

### 5. 服务启动失败

- 确保已运行 `install-deps.bat` 安装依赖
- 检查虚拟环境是否正确创建（`.venv` 文件夹）
- 查看单独窗口中的错误信息
- 确保端口未被其他程序占用

## 开发说明

### 添加新功能

1. 前端组件：在 `frontend/src/components/` 下创建新组件
2. API 接口：在 `frontend/src/services/` 中添加新的 API 服务文件
3. 后端接口：在对应的 `qwen_image_edit/` 或 `qwen_image/` 目录中添加新的路由
4. 更新导航：在 `frontend/src/App.tsx` 中添加新的 Tab

### 构建生产版本

```bash
cd frontend
npm run build
```

构建后的文件在 `frontend/build/` 目录。

## 许可证

MIT License

## 致谢

- [Qwen-VL](https://github.com/QwenLM/Qwen-VL) - 阿里开源的多模态大模型
- [Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) - 阿里开源的文生图模型
- [Diffusers](https://github.com/huggingface/diffusers) - Hugging Face 的扩散模型库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言和 React 组件库