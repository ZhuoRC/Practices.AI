# AI Summarizer

智能文档摘要系统，使用 Map-Reduce 架构和 LLM 技术提供高质量的文档摘要服务。

## 功能特性

- 📄 **多格式支持**: PDF、DOCX、TXT、Markdown 文件
- 🌐 **网页摘要**: 直接从 URL 提取和摘要网页内容
- 🔄 **Map-Reduce 架构**:
  - Map 阶段：独立摘要每个文本块
  - Reduce 阶段：合并生成最终摘要
- 🤖 **双模式 LLM**: 支持云端 API (Qwen) 和本地 Ollama
- 🎯 **智能分块**: 尊重句子边界的智能文本切分
- 🎨 **现代化界面**: React + Ant Design 响应式 UI

## 技术栈

### 后端
- FastAPI (Python Web 框架)
- OpenAI SDK (LLM 接口)
- PyPDF2, python-docx (文档处理)
- BeautifulSoup4 (网页解析)

### 前端
- React 18
- TypeScript
- Vite (构建工具)
- Ant Design (UI 组件库)
- Axios (HTTP 客户端)

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- (可选) Ollama (本地运行)

### 配置

1. **配置后端环境变量**

   ```bash
   cd backend
   cp .env.example .env
   ```

2. **编辑 `backend/.env` 文件**

   **使用云端 API (推荐用于生产环境):**
   ```env
   LLM_PROVIDER=cloud
   QWEN_API_KEY=your_actual_api_key_here  # 从阿里云 DashScope 获取
   ```

   **或使用本地 Ollama:**
   ```env
   LLM_PROVIDER=local
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:7b-instruct
   ```

### 一键启动

#### Windows
双击运行或在命令行执行:
```cmd
start.bat
```

#### Linux/Mac
```bash
./start.sh
```

启动脚本会自动：
1. ✅ 检查并创建 Python 虚拟环境
2. ✅ 安装/更新 Python 依赖
3. ✅ 安装/更新 Node.js 依赖
4. ✅ 启动后端服务 (http://localhost:8002)
5. ✅ 启动前端服务 (http://localhost:5173)

### 手动启动

如果需要分别启动服务：

**后端:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
python -m app.main
```

**前端:**
```bash
cd frontend
npm install
npm run dev
```

## 使用方法

1. 访问 http://localhost:5173 打开前端界面
2. 选择上传文档或输入网页 URL
3. 点击"生成摘要"
4. 等待 Map-Reduce 处理完成
5. 查看生成的摘要结果

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

### 主要接口

- `POST /api/summarize/document` - 上传文档生成摘要
- `POST /api/summarize/webpage` - 从 URL 生成摘要
- `GET /api/summarize/health` - 健康检查

## 项目结构

```
ai.Summarizer/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── services/      # 业务逻辑
│   │   ├── prompts/       # LLM 提示词
│   │   ├── config.py      # 配置管理
│   │   └── main.py        # 应用入口
│   ├── data/              # 文档存储
│   ├── .env.example       # 环境变量模板
│   └── requirements.txt   # Python 依赖
├── frontend/              # React 前端
│   ├── src/
│   │   ├── components/    # React 组件
│   │   └── services/      # API 服务
│   ├── package.json       # Node.js 依赖
│   └── vite.config.ts     # Vite 配置
├── start.bat              # Windows 启动脚本
├── start.sh               # Linux/Mac 启动脚本
└── README.md              # 项目文档
```

## 配置选项

### 分块配置 (backend/.env)

**默认配置（优化性能）：**
```env
MIN_CHUNK_SIZE=2000     # 最小块大小
MAX_CHUNK_SIZE=3000     # 最大块大小
CHUNK_OVERLAP=200       # 块重叠大小
```

**性能 vs 质量权衡：**

| 配置场景 | MIN_SIZE | MAX_SIZE | OVERLAP | 优点 | 缺点 |
|---------|----------|----------|---------|------|------|
| **快速模式** | 2000 | 3000 | 200 | 处理速度快，API调用少 | 可能丢失部分细节 |
| **平衡模式** | 1200 | 2000 | 150 | 速度和质量平衡 | - |
| **精细模式** | 800 | 1200 | 100 | 摘要更详细准确 | 处理时间长，成本高 |

**性能提示：**
- Chunk 数量 = 文档长度 / 平均块大小
- 处理时间 ≈ Chunk 数量 × 2-3 秒
- Token 消耗 = Chunk 数量 × (平均块大小 + 摘要长度)

**示例：** 一个 100,000 字的文档
- 快速模式：~40 chunks，~2-3 分钟
- 平衡模式：~65 chunks，~3-5 分钟
- 精细模式：~100 chunks，~5-8 分钟

### 服务配置
```env
HOST=0.0.0.0           # 服务器地址
PORT=8002              # 后端端口
```

## 开发

### 后端开发
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8002
```

### 前端开发
```bash
cd frontend
npm run dev
```

### 代码检查
```bash
cd frontend
npm run lint
```

### 构建
```bash
cd frontend
npm run build
```

## 故障排除

### 后端无法启动
- 检查 `.env` 文件是否正确配置
- 如使用云端 API，确认 API Key 有效
- 如使用本地 Ollama，确认 Ollama 服务已启动

### 前端无法连接后端
- 确认后端在 http://localhost:8002 运行
- 检查 CORS 配置
- 查看浏览器控制台错误信息

### 依赖安装失败
- 确认 Python 和 Node.js 版本符合要求
- 尝试清理缓存：`pip cache purge` 或 `npm cache clean --force`
- 检查网络连接

## 获取 Qwen API Key

1. 访问 [阿里云 DashScope](https://dashscope.aliyuncs.com)
2. 注册/登录账号
3. 在控制台创建 API Key
4. 将 API Key 填入 `backend/.env` 的 `QWEN_API_KEY`

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
