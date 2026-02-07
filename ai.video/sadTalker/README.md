# SadTalker Video Generator

基于 [SadTalker](https://github.com/OpenTalker/SadTalker) 的说话视频生成工具，提供 Web 界面和 API 接口。

## 功能特点

- Vite + React 前端界面（端口 3802）
- FastAPI 后端 API（端口 8802）
- 支持多种预处理模式（crop/resize/full）
- 可选 GFPGAN 面部增强
- 任务进度实时显示

## 项目结构

```
sadTalker/
├── SadTalker/              # SadTalker 核心代码
├── backend/
│   └── api.py              # FastAPI 后端服务 (端口 8802)
├── web/                    # Vite + React 前端 (端口 3802)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt        # Python 依赖
├── setup.bat / setup.sh    # 环境安装脚本
├── start.bat / start.sh    # 统一启动脚本
├── start-backend.bat       # 单独启动后端
└── start-frontend.bat      # 单独启动前端
```

## 安装步骤

### 1. 环境要求

- Python 3.8+
- Node.js 18+
- CUDA 11.8+（推荐，用于 GPU 加速）
- FFmpeg

### 2. 安装后端依赖

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3. 安装前端依赖

```bash
cd web
npm install
```

### 4. 下载模型权重

按照 [SadTalker 官方指南](https://github.com/OpenTalker/SadTalker#2-download-models) 下载模型文件：

1. 下载 checkpoints 并放置到 `SadTalker/checkpoints/` 目录
2. 下载 gfpgan weights 放置到对应目录

或者使用脚本自动下载：
```bash
cd SadTalker
bash scripts/download_models.sh
```

## 启动服务

### 方式一：统一启动（推荐）

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### 方式二：分别启动

**启动后端（终端1）：**
```bash
start-backend.bat    # Windows
./start-backend.sh   # Linux/Mac
```

**启动前端（终端2）：**
```bash
start-frontend.bat   # Windows
./start-frontend.sh  # Linux/Mac
```

### 服务地址

- **前端界面**: http://localhost:3802
- **后端 API**: http://localhost:8802
- **API 文档**: http://localhost:8802/docs

## API 接口

### 生成视频

```
POST /api/generate
```

**参数（multipart/form-data）:**
| 参数 | 类型 | 说明 |
|------|------|------|
| source_image | File | 源图片文件 |
| driven_audio | File | 驱动音频文件 |
| preprocess | string | 预处理方式 (crop/resize/full/extcrop/extfull) |
| still_mode | bool | 静止模式 |
| use_enhancer | bool | 使用面部增强 |
| batch_size | int | 批处理大小 |
| size | int | 图像尺寸 (256/512) |
| pose_style | int | 姿态风格 (0-45) |
| expression_scale | float | 表情强度 |

**响应:**
```json
{
    "task_id": "xxx",
    "status": "processing",
    "message": "任务已提交"
}
```

### 查询任务状态

```
GET /api/task/{task_id}
```

### 下载视频

```
GET /api/download/{task_id}
```

## 使用说明

1. 打开 http://localhost:3802
2. 上传包含人脸的图片
3. 上传驱动音频（WAV/MP3）
4. 调整生成参数
5. 点击"生成视频"
6. 等待处理完成后下载视频

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| preprocess | crop=裁剪人脸, full=全身 | crop |
| still_mode | 减少头部运动 | false |
| use_enhancer | GFPGAN 面部增强 | false |
| size | 输出分辨率 | 256 |
| pose_style | 姿态风格 0-45 | 0 |
| expression_scale | 表情强度 | 1.0 |

## 常见问题

**Q: CUDA out of memory**
A: 降低 batch_size 或使用 256 分辨率

**Q: 生成速度慢**
A: 确保使用 GPU 加速，检查 CUDA 是否正确安装

**Q: 无法检测人脸**
A: 确保图片中人脸清晰可见，正面照片效果最佳

## License

本项目基于 SadTalker，遵循其开源协议。
