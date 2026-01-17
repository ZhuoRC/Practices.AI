# AI Video Splitter - 智能视频分割系统

基于 AI 的智能视频分割应用,使用 Whisper 提取字幕,LLM 进行语义分析,自动将长视频分割成约 10 分钟的章节。

## 功能特性

- **视频上传**: 支持常见视频格式 (MP4, AVI, MOV, MKV)
- **字幕提取**: 使用 OpenAI Whisper 自动提取带时间戳的字幕
- **智能分割**: 使用 Qwen3-VL-32B-Instruct 进行语义分析,智能分割章节
- **视频处理**: 使用 ffmpeg 自动分割视频为独立章节
- **树形展示**: 父子关系树形展示原视频和章节视频
- **预览功能**: 支持视频和字幕的在线预览

## 系统要求

### 必需软件

1. **Python 3.8+**
   - 下载: https://www.python.org/downloads/

2. **Node.js 16+**
   - 下载: https://nodejs.org/

3. **ffmpeg**
   - 下载: https://ffmpeg.org/download.html
   - 安装后需添加到系统 PATH

### API 密钥

- **Qwen API Key**: 用于 LLM 章节分割
  - 获取: https://dashscope.aliyuncs.com/

## 快速开始

### 1. 配置环境

复制环境配置文件并填写 API 密钥:

```bash
cd backend
copy .env.example .env
```

编辑 `backend/.env` 文件,填写必要配置:

```env
# LLM Provider: qwen 或 ollama
LLM_PROVIDER=qwen

# 必填: Qwen API Key (如果使用 qwen)
QWEN_API_KEY=your_api_key_here

# 可选: Whisper 模型大小 (tiny, base, small, medium, large)
WHISPER_MODEL=base

# 可选: 目标章节时长 (秒)
TARGET_CHAPTER_DURATION=600
```

### 2. 启动应用

双击运行 `start.bat`:

```bash
start.bat
```

脚本会自动:
- 创建 Python 虚拟环境
- 安装所有依赖
- 启动后端服务 (http://localhost:8003)
- 启动前端服务 (http://localhost:5173)

### 3. 使用应用

1. 打开浏览器访问 http://localhost:5173
2. 上传视频文件
3. 等待处理完成 (可实时查看进度)
4. 查看视频树形结构
5. 点击节点预览视频和字幕

## 技术架构

### 后端 (FastAPI)

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   └── video.py      # 视频处理接口
│   ├── services/         # 业务逻辑
│   │   ├── whisper_service.py    # Whisper 字幕提取
│   │   ├── llm_service.py        # LLM 章节分割
│   │   ├── video_service.py      # 视频处理
│   │   └── task_manager.py       # 任务管理
│   ├── config.py         # 配置管理
│   ├── models.py         # 数据模型
│   └── main.py           # FastAPI 应用
├── requirements.txt      # Python 依赖
└── run.py               # 启动脚本
```

### 前端 (React + Ant Design)

```
frontend/
├── src/
│   ├── components/       # React 组件
│   │   ├── VideoUpload.tsx       # 视频上传
│   │   ├── ProcessingProgress.tsx # 进度显示
│   │   ├── VideoTree.tsx         # 树形展示
│   │   └── VideoPreview.tsx      # 视频预览
│   ├── services/         # API 服务
│   │   └── api.ts        # API 客户端
│   ├── types/            # TypeScript 类型
│   │   └── index.ts
│   ├── App.tsx           # 主应用
│   └── main.tsx          # 入口文件
├── package.json          # Node 依赖
└── vite.config.ts        # Vite 配置
```

## 处理流程

1. **上传视频** → 保存到 `backend/data/uploads/`
2. **提取字幕** → Whisper 生成带时间戳的字幕
3. **分析内容** → LLM 分析字幕,确定章节分割点
4. **分割视频** → ffmpeg 根据时间戳分割视频
5. **生成结果** → 保存到 `backend/data/processed/`

## 配置说明

### Whisper 模型选择

| 模型 | 大小 | 内存需求 | 速度 | 准确度 |
|------|------|----------|------|--------|
| tiny | ~1GB | ~1GB | 最快 | 较低 |
| base | ~1GB | ~1GB | 快 | 中等 |
| small | ~2GB | ~2GB | 中等 | 较高 |
| medium | ~5GB | ~5GB | 慢 | 高 |
| large | ~10GB | ~10GB | 最慢 | 最高 |

**推荐**: `base` 或 `small` - 速度和准确度的良好平衡

### 章节时长配置

```env
TARGET_CHAPTER_DURATION=600  # 目标时长: 10 分钟
MIN_CHAPTER_DURATION=300     # 最小时长: 5 分钟
MAX_CHAPTER_DURATION=900     # 最大时长: 15 分钟
```

## API 文档

启动后端后访问: http://localhost:8003/docs

主要接口:
- `POST /api/video/upload` - 上传视频
- `GET /api/video/status/{task_id}` - 查询处理状态
- `GET /api/video/tree/{video_id}` - 获取视频树
- `GET /api/video/preview/{video_id}` - 预览视频
- `GET /api/video/subtitle/{video_id}` - 获取字幕

## 常见问题

### 1. 首次运行很慢?

首次运行会下载 Whisper 模型 (~1-10GB),请耐心等待。

### 2. ffmpeg 错误?

确保 ffmpeg 已安装并添加到系统 PATH:
```bash
ffmpeg -version
```

### 3. API Key 错误?

检查 `backend/.env` 文件中的 `ZHIPU_API_KEY` 是否正确。

### 4. 内存不足?

尝试使用更小的 Whisper 模型 (如 `tiny` 或 `base`)。

## 开发说明

### 手动启动

**后端**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**前端**:
```bash
cd frontend
npm install
npm run dev
```

### 构建生产版本

```bash
cd frontend
npm run build
```

## 许可证

MIT License

## 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 字幕提取
- [Qwen](https://dashscope.aliyuncs.com/) - LLM 服务
- [FFmpeg](https://ffmpeg.org/) - 视频处理
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [React](https://react.dev/) - 前端框架
- [Ant Design](https://ant.design/) - UI 组件库
