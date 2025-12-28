# AI Generator 使用指南

## 项目概述

AI Generator 是一个完整的AI视频生成系统，可以从文本脚本自动生成包含配音的视频内容。

## 功能特性

✅ **脚本处理**
- 自动分段和关键词提取
- 时长估算
- 支持中文

✅ **视频生成**
- FFmpeg驱动的视频合成
- 支持多种分辨率（1920x1080等）
- 自动文本渲染
- 梯度背景
- 关键词高亮
- 视频段落合并

✅ **音频生成**
- 支持多种TTS提供商
- 批量处理
- 格式转换

## 系统架构

```
ai.generator/
├── script_processor/    # 脚本处理模块
├── audio_generator/     # 音频生成模块
├── video_generator/     # 视频生成模块
├── shared/            # 共享组件
│   ├── config/        # 配置管理
│   └── storage/       # JSON文件存储
├── input/            # 输入文件目录
│   └── scripts.txt    # 脚本文本
├── output/           # 输出文件目录
│   └── YYYYMMDD_HHMMSS/
│       ├── audio/     # 音频文件
│       ├── video/     # 视频段落
│       └── final/     # 合并后的最终视频
└── data/            # 项目数据
    └── projects/     # 项目JSON文件
```

## 快速开始

### 1. 安装依赖

```bash
cd ai.generator
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件：

```env
# Azure TTS（推荐，中文支持好）
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=eastasia
AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural

# ElevenLabs（高质量，需要付费）
ELEVENLABS_API_KEY=your_elevenlabs_key

# Windows本地TTS（免费，但中文支持有限）
# 无需配置，自动检测
```

### 3. 准备输入文件

将您的文本脚本放入 `input/scripts.txt`。

示例：
```
今天我们要讲一个重要的话题...
（您的文本内容）
```

### 4. 运行测试

```bash
python test_generation.py
```

## TTS提供商选择

### Windows PowerShell TTS（本地免费）

**优点：**
- ✅ 完全免费
- ✅ 无需网络
- ✅ 自动检测

**缺点：**
- ⚠️ 中文支持有限
- ⚠️ 音质一般
- ⚠️ 可能出现编码问题

**状态：** 系统默认尝试使用，但不保证中文生成质量

### Azure TTS（推荐）

**优点：**
- ✅ 优秀的中文支持
- ✅ 多种语音选择
- ✅ 高质量音质
- ✅ Neural语音自然

**配置：**
```env
AZURE_TTS_KEY=your_key_here
AZURE_TTS_REGION=eastasia
AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural
```

**获取API密钥：**
1. 访问 https://azure.microsoft.com/zh-cn/services/cognitive-services/text-to-speech/
2. 创建免费账户
3. 创建语音服务资源
4. 获取密钥和区域

### ElevenLabs（最高质量）

**优点：**
- ✅ 业界最佳音质
- ✅ 高度自然的语音
- ✅ 情感表达丰富

**配置：**
```env
ELEVENLABS_API_KEY=your_key_here
```

**获取API密钥：**
1. 访问 https://elevenlabs.io/
2. 注册账户
3. 获取API密钥
4. 选择语音ID

## 使用示例

### Python API

```python
import asyncio
from audio_generator import AudioGenerator, AudioGenerationRequest
from script_processor import ScriptProcessor, ScriptProcessRequest
from video_generator import VideoGenerator, VideoGenerationRequest

async def generate_video():
    # 1. 处理脚本
    processor = ScriptProcessor()
    with open('input/scripts.txt', 'r', encoding='utf-8') as f:
        script_text = f.read()
    
    script_result = await processor.process_script(
        ScriptProcessRequest(
            project_id="my_project",
            script_text=script_text,
            language="zh"
        )
    )
    
    # 2. 生成音频
    audio_gen = AudioGenerator()
    audio_result = await audio_gen.generate_audio(
        AudioGenerationRequest(
            project_id="my_project",
            segments=[seg.model_dump() for seg in script_result.segments],
            provider="auto",  # 或 "azure", "elevenlabs", "windows"
            language="zh",
            output_format="wav"
        )
    )
    
    # 3. 生成视频
    video_gen = VideoGenerator()
    video_result = await video_gen.generate_video(
        VideoGenerationRequest(
            project_id="my_project",
            segments=[seg.model_dump() for seg in script_result.segments],
            audio_files=[seg.file_path for seg in audio_result.segments],
            duration=5.0,
            resolution="1920x1080",
            fps=30,
            merge_segments=True
        )
    )

asyncio.run(generate_video())
```

## 输出结果

生成完成后，文件将保存在 `output/` 目录下：

```
output/20251228_122841/
├── audio/
│   ├── xxx_audio_0001.wav
│   ├── xxx_audio_0002.wav
│   └── ...
├── video/
│   ├── xxx_video_0001.mp4
│   ├── xxx_video_0002.mp4
│   └── ...
└── final/
    └── xxx_final.mp4  # 最终合并视频
```

## 常见问题

### Q1: 生成的音频没有声音

**A:** Windows PowerShell TTS对中文支持有限。解决方案：
1. 配置Azure TTS（推荐）
2. 配置ElevenLabs
3. 使用英文文本测试

### Q2: 视频生成成功但没有音轨

**A:** 检查音频文件是否有效生成：
```bash
# 检查音频文件大小
ls -lh output/YYYYMMDD_HHMMSS/audio/
```

如果音频文件很小（< 1KB），说明TTS失败，请配置Azure或ElevenLabs。

### Q3: 如何提高视频质量？

**A:** 调整VideoGenerationRequest参数：
```python
request = VideoGenerationRequest(
    # ...
    resolution="3840x2160",  # 4K
    fps=60,                   # 更高帧率
    font_size=64,             # 更大字体
    font_family="Microsoft YaHei"  # 更好的中文字体
)
```

### Q4: 支持哪些语言？

**A:** 
- **Azure TTS:** 支持多种语言，包括中文、英文、日文等
- **ElevenLabs:** 支持多种语言的多语言语音
- **Windows TTS:** 取决于系统安装的语音包

## 项目数据管理

项目数据以JSON格式保存在 `data/projects/` 目录：

```json
{
  "id": "project_id",
  "name": "项目名称",
  "status": "completed",
  "created_at": "2025-12-28T12:00:00",
  "scripts": [...],
  "audio_segments": [...],
  "video_segments": [...]
}
```

## 技术栈

- **Python 3.10+**
- **FFmpeg:** 视频生成和合并
- **pydub:** 音频处理
- **Azure Cognitive Services:** 云端TTS（可选）
- **ElevenLabs API:** 云端TTS（可选）
- **System.Speech:** Windows本地TTS

## 下一步

### 功能增强建议

1. **字幕生成**
   - 集成语音识别API
   - 自动生成字幕文件（SRT/VTT）
   - 嵌入视频字幕

2. **更多视频样式**
   - 图片背景
   - 动画效果
   - 多种布局选项

3. **Web界面**
   - Flask/FastAPI后端
   - React/Vue前端
   - 实时进度显示

4. **批量处理**
   - 支持多个脚本
   - 队列管理
   - 并行处理

## 支持

如有问题，请检查：
1. 依赖是否正确安装
2. FFmpeg是否在PATH中
3. API密钥配置是否正确
4. 输入文件编码是否为UTF-8

## 许可证

本项目仅供学习和研究使用。
