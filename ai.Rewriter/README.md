# AI 文本改写器 (AI Rewriter)

一个基于 FastAPI 和 React 的智能文本改写 Web 应用，支持云端和本地两种 AI 模式。

## 功能特点

- **双模式支持**：云端 Qwen 模型和本地 Mistral 7B Instruct 模型
- **分段改写**：支持长文本分段处理，保持上下文连贯性
- **智能拼接**：自动将分段改写结果拼接成完整文本
- **现代化界面**：基于 Ant Design 的响应式用户界面
- **实时反馈**：提供处理进度和结果展示

## 技术栈

### 后端
- **FastAPI**：现代化的 Python Web 框架
- **Qwen API**：阿里云通义千问大语言模型
- **Ollama**：本地 Mistral 7B 模型服务
- **Pydantic**：数据验证和序列化

### 前端
- **React 18**：现代化前端框架
- **TypeScript**：类型安全的 JavaScript
- **Ant Design**：企业级 UI 组件库
- **Axios**：HTTP 客户端

## 项目结构

```
ai.Rewriter/
├── backend/                 # 后端代码
│   ├── main.py             # FastAPI 主应用
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── App.tsx        # 主应用组件
│   │   ├── services/
│   │   │   └── api.ts     # API 服务
│   │   └── App.css        # 样式文件
│   └── package.json       # 前端依赖
└── README.md              # 项目说明
```

## 快速开始

### 方法一：一键启动（推荐）

选择以下任一方式启动应用：

#### Windows 用户：

**选项1：快速启动**
```cmd
start.bat
```
常规启动，适合日常使用。

**选项2：清理启动（推荐用于首次运行或遇到问题时）**
```cmd
start_clean.bat
```
完全清理启动，包括：
- 停止所有现有服务
- 验证环境配置
- 重新安装依赖（如需要）
- 详细启动日志
- 适合用于故障排除

**选项3：使用Python脚本（跨平台）**
```bash
python start.py
```
支持 Windows/macOS/Linux，包含服务监控功能。

#### 跨平台：
```bash
python start.py
```

这些脚本会：
- 自动停止占用端口8000和3000的进程
- 创建虚拟环境并安装依赖
- 启动后端和前端服务
- 提供启动状态信息和故障排除提示

### 方法二：手动启动

#### 1. 环境准备

**Python 环境** (后端):
```bash
# Python 3.8+
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**Node.js 环境** (前端):
```bash
# Node.js 16+
cd frontend
npm install
```

### 2. 配置环境变量

复制后端环境变量示例文件：
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：
```env
# Qwen API Configuration
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Local Model Configuration (如果使用本地模式)
LOCAL_MODEL_HOST=localhost
LOCAL_MODEL_PORT=11434
LOCAL_MODEL_NAME=mistral:7b-instruct

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 3. 启动服务

**启动后端服务**:
```bash
cd backend
python main.py
```
后端服务将在 `http://localhost:8000` 启动

**启动前端服务**:
```bash
cd frontend
npm start
```
前端应用将在 `http://localhost:3000` 启动

### 4. 使用本地模型 (可选)

如果要使用本地 Mistral 模型，需要先安装和启动 Ollama：

1. **安装 Ollama**:
```bash
# macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - 下载安装包
# https://ollama.ai/download
```

2. **下载 Mistral 模型**:
```bash
ollama pull mistral:7b-instruct
```

3. **启动 Ollama 服务**:
```bash
ollama serve
```

## API 文档

启动后端服务后，可以通过以下地址访问 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要 API 端点

- `POST /rewrite` - 文本改写
- `GET /health` - 健康检查

## 使用方法

1. 在浏览器中打开 `http://localhost:3000`
2. 在左侧输入框中填入要改写的原始文本
3. 输入改写要求（例如：使文本更简洁、改变语气等）
4. 选择改写模式：
   - **云端模式**：使用 Qwen API，需要配置 API Key
   - **本地模式**：使用本地 Mistral 模型，需要启动 Ollama 服务
5. 选择分段大小（用于长文本处理）
6. 点击"开始改写"按钮
7. 在右侧查看改写结果，可以复制到剪贴板

## 配置说明

### 云端模式配置

1. 获取阿里云通义千问 API Key：
   - 访问 [阿里云灵积平台](https://dashscope.console.aliyun.com/)
   - 注册并开通服务
   - 获取 API Key

2. 在 `.env` 文件中配置：
```env
QWEN_API_KEY=your_actual_api_key
```

### 本地模式配置

1. 确保已安装 Ollama 和 Mistral 模型
2. 启动 Ollama 服务（默认端口 11434）
3. 确保模型名称正确（默认：mistral:7b-instruct）

## 分段改写说明

对于长文本，系统会自动进行分段处理：

- 按照句子边界智能分段，保持语义完整性
- 前一段的改写结果会作为后一段的上下文信息
- 最终将所有段落拼接成完整的改写文本

## 故障排除

### 常见问题

1. **后端启动失败**：
   - 检查 Python 版本是否为 3.8+
   - 确保所有依赖已正确安装
   - 检查端口 8000 是否被占用
   - 尝试使用 `start_clean.bat` 清理重启

2. **前端无法连接后端**：
   - 确保后端服务正在运行
   - 检查防火墙设置
   - 确认 API 地址配置正确

3. **云端模式失败**：
   - 检查 API Key 是否正确
   - 确认网络连接正常
   - 检查 API 配额和余额

4. **本地模式失败**：
   - 确保 Ollama 服务正在运行
   - 检查模型是否已下载
   - 确认模型名称正确

5. **请求发送后没有响应**：
   - 检查后端日志 (`backend/app.log`) 查看详细错误信息
   - 确认 `.env` 文件配置正确，特别是 `QWEN_BASE_URL` 和 `QWEN_API_KEY`
   - 对于 Qwen API：
     - 如使用兼容模式：`QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`
     - 如使用原生 API：`QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1`
   - 检查网络连接和防火墙设置
   - 尝试重启后端服务

6. **请求超时或挂起**：
   - 后端已优化中间件，确保使用最新代码
   - 检查文本长度，考虑增大分段大小
   - 查看 `backend/app.log` 确认请求是否到达端点
   - 如果请求到达中间件但未到达处理函数，说明可能是代码版本问题，请更新代码

## 开发说明

### 添加新的 AI 模型

1. 在 `backend/main.py` 中添加新的 API 调用方法
2. 更新 `rewrite_text` 函数以支持新模式
3. 在前端添加相应的选项

### 自定义分段逻辑

修改 `AIReWriter.split_text_into_segments` 方法来自定义分段策略。

## 更新日志

### v1.0.1 (2025-11-03)
**Bug 修复**
- 🐛 修复了 middleware 中请求体消耗导致请求挂起的关键问题
  - 问题：middleware 读取请求体后未缓存，导致 FastAPI 端点无法解析请求
  - 解决：实现请求体缓存机制，允许 middleware 记录日志的同时保持请求体可读
  - 影响：修复前所有 `/rewrite` 请求都会挂起无响应

**改进**
- ✨ 新增 `start_clean.bat` 清理启动脚本
- 📝 更新 README 故障排除部分，添加详细的调试指南
- 📝 完善启动文档，提供多种启动选项说明

### v1.0.0 (2025-11-02)
- 🎉 初始版本发布
- ✅ 支持云端 Qwen 和本地 Mistral 双模式
- ✅ 实现智能分段改写功能
- ✅ 现代化 React + Ant Design UI

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 技术支持

遇到问题？
1. 首先查看[故障排除](#故障排除)部分
2. 检查 `backend/app.log` 日志文件
3. 使用 `start_clean.bat` 尝试清理启动
4. 在 GitHub Issues 中提问