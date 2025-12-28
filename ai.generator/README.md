# AI Generator - AI视频生成系统

## 项目概述

AI Generator是一个完整的AI视频生成系统，能够将文本内容转换为专业级视频。系统支持多种TTS提供商、智能文本处理、动态视频效果和自动化音视频合并。所有数据使用JSON文件存储，无需数据库。

## 核心功能

### 1. 脚本处理系统 (script_processor)
- **AI文本改写**：支持OpenAI和Anthropic API进行智能文本改写
- **智能分段**：基于句子边界和长度的智能分段算法
- **关键词提取**：使用jieba进行中文关键词提取
- **情感检测**：基于关键词的简单情感分析
- **时长估算**：根据语言和字符数估算语音时长

### 2. 音频生成系统 (audio_generator)
- **多TTS支持**：
  - Azure TTS（微软认知服务）
  - ElevenLabs（高质量语音合成）
- **音频格式转换**：支持WAV、MP3等格式
- **批量处理**：支持并发批量生成音频
- **质量控制**：音频时长估算和质量评分

### 3. 视频生成系统 (video_generator)
- **动态背景**：
  - 渐变背景
  - 纯色背景
  - 粒子背景
- **文字动画**：
  - 淡入效果
  - 打字机效果
  - 滑入效果
- **关键词高亮**：自动高亮文本中的关键词
- **自定义样式**：支持自定义字体、颜色、大小

### 4. 数据存储系统 (shared/storage)
- **JSON文件存储**：所有项目数据以JSON格式存储
- **项目管理**：创建、读取、更新、删除项目
- **版本控制**：支持项目导出和导入
- **数据备份**：简单的JSON文件备份

## 项目结构

```
ai.generator/
├── shared/                      # 共享模块
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── storage/                 # JSON文件存储
│   │   ├── __init__.py
│   │   └── json_storage.py
│   └── utils/                   # 工具函数
│
├── script_processor/            # 脚本处理模块
│   ├── __init__.py
│   ├── models.py
│   └── processor.py
│
├── audio_generator/             # 音频生成模块
│   ├── __init__.py
│   ├── models.py
│   └── generator.py
│
├── video_generator/             # 视频生成模块
│   ├── __init__.py
│   ├── models.py
│   └── generator.py
│
├── aggregator/                 # 合并模块（待实现）
│
├── web_interface/              # Web界面（待实现）
│
├── input/                     # 输入文件
│   └── scripts.txt
│
├── output/                    # 输出文件
│   ├── audio/
│   ├── video/
│   └── final/
│
├── data/                      # 数据存储目录
│   ├── projects/              # 项目JSON文件
│   └── segments/              # 段落数据
│
├── temp/                      # 临时文件
├── logs/                      # 日志文件
├── ffmpeg/                    # FFmpeg二进制文件
├── requirements.txt            # Python依赖
├── .env.example              # 环境变量模板
└── README.md                 # 项目说明
```

## 快速开始

### 1. 环境准备

#### Python环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑`.env`文件，配置以下变量：

```env
# 基础配置
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# OpenAI配置（用于文本改写）
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic配置（备用）
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-opus-20240229

# Azure TTS配置
AZURE_TTS_KEY=your-azure-tts-key
AZURE_TTS_REGION=your-azure-region
AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural

# ElevenLabs配置
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_VOICE=21m00Tcm4TlvDq8ikWAM

# 视频生成配置
VIDEO_RESOLUTION=1920x1080
VIDEO_FPS=30
VIDEO_CODEC=libx264
VIDEO_QUALITY=23

# FFmpeg配置
FFMPEG_PATH=/path/to/ffmpeg
```

### 3. 使用示例

#### 通过Python代码使用

```python
from shared.storage import storage
from script_processor import ScriptProcessor
from audio_generator import AudioGenerator
from video_generator import VideoGenerator
import asyncio

async def main():
    # 创建项目
    project = storage.create_project(
        name="示例项目",
        description="这是一个测试项目"
    )
    project_id = project["id"]
    print(f"项目已创建: {project_id}")
    
    # 读取脚本
    with open("input/scripts.txt", "r", encoding="utf-8") as f:
        script_text = f.read()
    
    # 处理脚本
    processor = ScriptProcessor()
    request = ScriptProcessingRequest(
        project_id=project_id,
        script_text=script_text,
        language="zh",
        enable_rewrite=False,
        enable_segmentation=True
    )
    result = await processor.process_script(request)
    print(f"脚本处理完成: {len(result.segments)} 个段落")
    
    # 保存脚本数据
    storage.save_script(project_id, [seg.dict() for seg in result.segments])
    
    # 生成音频
    audio_gen = AudioGenerator()
    audio_request = AudioGenerationRequest(
        project_id=project_id,
        segments=[seg.dict() for seg in result.segments],
        provider="azure",
        language="zh"
    )
    audio_result = await audio_gen.generate_audio(audio_request)
    print(f"音频生成完成: {audio_result.total_duration} 秒")
    
    # 生成视频
    video_gen = VideoGenerator()
    video_request = VideoGenerationRequest(
        project_id=project_id,
        segments=[seg.dict() for seg in result.segments],
        duration=5.0,  # 每个段落5秒
        resolution="1920x1080",
        fps=30,
        background_style="gradient",
        text_animation="fade_in"
    )
    video_result = await video_gen.generate_video(video_request)
    print(f"视频生成完成: {len(video_result.segments)} 个段落")
    
    # 保存数据
    storage.save_audio_segments(
        project_id,
        [seg.dict() for seg in audio_result.segments]
    )
    storage.save_video_segments(
        project_id,
        [seg.dict() for seg in video_result.segments]
    )

# 运行主函数
asyncio.run(main())
```

## 数据存储

### 项目数据结构

项目数据以JSON格式存储在`data/projects/`目录下：

```json
{
  "id": "project-uuid",
  "name": "项目名称",
  "description": "项目描述",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00",
  "status": "completed",
  "metadata": {},
  "scripts": [],
  "audio_segments": [],
  "video_segments": [],
  "final_video": null
}
```

### 数据管理API

```python
from shared.storage import storage

# 创建项目
project = storage.create_project("项目名称", "项目描述")

# 获取项目
project = storage.get_project(project_id)

# 更新项目
storage.update_project(project_id, status="completed")

# 列出项目
projects = storage.list_projects(status="completed")

# 删除项目
storage.delete_project(project_id)

# 导出项目
storage.export_project(project_id, "export.json")

# 导入项目
new_id = storage.import_project("export.json")

# 清理旧项目
count = storage.cleanup_old_projects(days=30)
```

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 技术栈

### 后端
- **框架**: FastAPI
- **数据存储**: JSON文件
- **AI服务**: OpenAI, Anthropic
- **TTS服务**: Azure TTS, ElevenLabs
- **视频处理**: MoviePy, FFmpeg
- **音频处理**: pydub
- **中文处理**: jieba

## 开发指南

### 添加新的TTS提供商

1. 在`audio_generator/generator.py`中添加新的生成方法
2. 在`_get_default_voice`中添加语音映射
3. 在`get_available_voices`中添加语音列表

### 添加新的视频效果

1. 在`video_generator/generator.py`的`_create_background`中添加新的背景样式
2. 在`_create_text_clip`中添加新的动画效果
3. 在`get_available_effects`中添加效果描述

### 扩展数据存储

在`shared/storage/json_storage.py`中添加新的存储方法：

```python
def save_custom_data(self, project_id: str, data: Dict) -> bool:
    """保存自定义数据"""
    project = self.get_project(project_id)
    if not project:
        return False
    
    project["custom_data"] = data
    return self.update_project(project_id, custom_data=data)
```

## 性能优化建议

1. **并发处理**：使用asyncio进行并发任务处理
2. **文件缓存**：对频繁访问的数据进行缓存
3. **批量操作**：批量处理音频和视频生成
4. **资源清理**：定期清理临时文件和旧项目

## 故障排查

### 常见问题

1. **FFmpeg未找到**
   - 确保FFmpeg已安装并配置正确
   - 检查`.env`文件中的`FFMPEG_PATH`
   - 或将FFmpeg放在项目`ffmpeg/`目录下

2. **TTS API调用失败**
   - 检查API密钥是否正确配置
   - 确认网络连接正常
   - 查看API配额是否用完

3. **视频生成失败**
   - 检查字体文件是否存在
   - 确保临时目录有写权限
   - 查看内存是否足够

4. **数据存储错误**
   - 确保`data/`目录有写权限
   - 检查JSON文件格式是否正确
   - 查看磁盘空间是否充足

## 数据备份

### 手动备份

```bash
# 备份所有项目数据
cp -r data/ backup/data_$(date +%Y%m%d)

# 备份单个项目
python -c "from shared.storage import storage; storage.export_project('project-id', 'backup.json')"
```

### 自动备份

可以设置定时任务定期备份数据：

```bash
# 每天备份数据
0 2 * * * cp -r /path/to/ai.generator/data /path/to/backup/data_$(date +\%Y\%m\%d)
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue或联系项目维护者。
