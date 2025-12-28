# TTS（语音合成）选择指南

## 概述

AI Generator 支持多种TTS（文本转语音）提供商，每种都有其优缺点和适用场景。

## 可用的TTS选项

### 1. Windows PowerShell TTS ⭐️ 推荐（免费）

**优点：**
- ✅ 完全免费
- ✅ 无需网络连接
- ✅ 无需API密钥
- ✅ 自动检测和安装
- ✅ 快速生成

**缺点：**
- ⚠️ 中文支持有限（取决于系统语音包）
- ⚠️ 音质一般
- ⚠️ 长文本批量处理可能不稳定
- ⚠️ 语音较少

**适用场景：**
- 快速测试和原型开发
- 英文文本（支持良好）
- 无网络环境
- 对音质要求不高

**配置：**
```python
# 无需配置，自动检测
provider = "windows"  # 或 "auto"
```

**中文语音包：**
如果需要更好的中文支持，请在Windows设置中安装中文语音包：
1. 设置 → 时间和语言 → 语言
2. 添加中文（简体）
3. 选项 → 下载语音包

---

### 2. Azure TTS ⭐️⭐️⭐️ 推荐（中文）

**优点：**
- ✅ 优秀的中文支持
- ✅ 多种自然语音（Neural语音）
- ✅ 高质量音质
- ✅ 情感表达丰富
- ✅ 稳定可靠
- ✅ 支持SSML（语音合成标记语言）

**缺点：**
- ⚠️ 需要API密钥
- ⚠️ 免费额度有限
- ⚠️ 需要网络连接
- ⚠️ 付费使用

**适用场景：**
- 中文内容生产（强烈推荐）
- 商业应用
- 对音质要求高
- 需要多种语音选择

**配置：**
```env
# .env文件
AZURE_TTS_KEY=your_azure_key_here
AZURE_TTS_REGION=eastasia
AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural
```

**免费试用：**
1. 访问：https://azure.microsoft.com/zh-cn/services/cognitive-services/text-to-speech/
2. 创建免费Azure账户
3. 创建"语音服务"资源
4. 选择"免费(F0)"定价层
5. 获取密钥和区域

**免费额度：**
- 每月：5百万字符
- 足够生成约5000分钟的语音

**推荐中文语音：**
- `zh-CN-XiaoxiaoNeural` - 晓晓（女声，自然亲切）
- `zh-CN-YunxiNeural` - 云希（男声，沉稳专业）
- `zh-CN-XiaoyiNeural` - 晓伊（女声，年轻活泼）
- `zh-CN-YunjianNeural` - 云健（男声，成熟稳重）

---

### 3. ElevenLabs ⭐️⭐️⭐️ 推荐（最高质量）

**优点：**
- ✅ 业界最佳音质
- ✅ 高度自然的语音
- ✅ 丰富的情感表达
- ✅ 多语言支持
- ✅ 语音克隆功能

**缺点：**
- ⚠️ 付费服务
- ⚠️ 需要API密钥
- ⚠️ 需要网络连接
- ⚠️ 成本较高

**适用场景：**
- 专业内容制作
- 商业项目
- 对音质要求极高
- 需要语音克隆

**配置：**
```env
# .env文件
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

**获取密钥：**
1. 访问：https://elevenlabs.io/
2. 注册账户
3. 获取API密钥
4. 选择适合的定价计划

**定价：**
- 免费计划：10,000字符/月
- Starter计划：$5/月（30,000字符）
- Creator计划：$22/月（100,000字符）

---

### 4. ChatTTS ⭐️ 本地AI模型

**优点：**
- ✅ 本地运行
- ✅ 无需API密钥
- ✅ 中文支持较好
- ✅ 可离线使用
- ✅ 开源免费

**缺点：**
- ⚠️ 需要安装大量依赖
- ⚠️ 需要下载大模型（几GB）
- ⚠️ 需要GPU才能获得良好性能
- ⚠️ 安装配置复杂
- ⚠️ 生成速度较慢（CPU）

**适用场景：**
- 有强大GPU的本地环境
- 对隐私要求高
- 需要离线使用
- 愿意花时间配置

**安装步骤：**
```bash
# 1. 安装依赖
pip install torch torchaudio numba pybase16384 transformers vocos
pip install vector_quantize_pytorch gradio pydub av

# 2. 启用ChatTTS
# .env文件
CHATTTS_ENABLED=True
CHATTTS_USE_GPU=True  # 如果有GPU
```

**系统要求：**
- Python 3.8+
- CUDA支持的NVIDIA GPU（推荐）
- 8GB+ RAM
- 10GB+ 磁盘空间

---

## 推荐方案

### 方案1：快速测试（推荐）
```python
provider = "windows"  # 或 "auto"
```
使用Windows PowerShell TTS，快速开始。

### 方案2：中文内容（强烈推荐）
```env
AZURE TTS（免费额度5M字符/月）
AZURE_TTS_KEY=your_key
AZURE_TTS_REGION=eastasia
AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural
```
使用Azure TTS，获得最好的中文效果。

### 方案3：专业制作（预算充足）
```env
ELEVENLABS_API_KEY=your_key
```
使用ElevenLabs，获得业界最佳音质。

### 方案4：本地离线（技术能力强）
```env
CHATTTS_ENABLED=True
CHATTTS_USE_GPU=True
```
使用ChatTTS，完全本地运行。

---

## 优先级设置

系统按照以下优先级自动选择TTS提供商（当provider="auto"时）：

1. **ChatTTS** - 如果可用且已启用
2. **Windows PowerShell TTS** - 如果检测到
3. **Azure TTS** - 如果配置了密钥
4. **ElevenLabs** - 如果配置了密钥

---

## 性能对比

| TTS提供商 | 音质 | 中文支持 | 速度 | 成本 | 难度 |
|---------|------|---------|------|------|------|
| Windows TTS | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 | 简单 |
| Azure TTS | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 付费 | 简单 |
| ElevenLabs | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 付费 | 简单 |
| ChatTTS | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 免费 | 困难 |

---

## 使用示例

### Python API
```python
from audio_generator import AudioGenerator, AudioGenerationRequest

# 创建生成器
generator = AudioGenerator()

# 使用Windows TTS
request = AudioGenerationRequest(
    project_id="test_project",
    segments=[{"text": "你好，世界", "index": 1}],
    provider="windows",  # 或 "auto", "azure", "elevenlabs", "chattts"
    language="zh",
    output_format="wav"
)

# 生成音频
result = await generator.generate_audio(request)
print(f"生成状态: {result.status}")
```

### 命令行测试
```bash
# 测试Windows TTS
python test_audio_fix.py

# 测试完整流程
python test_generation.py
```

---

## 故障排除

### Q1: Windows TTS中文发音不自然
**A:** 安装中文语音包：
1. Windows设置 → 时间和语言 → 语言
2. 中文（简体）→ 选项 → 下载语音包

### Q2: Azure TTS密钥无效
**A:** 检查：
1. 密钥和区域是否正确
2. 资源是否创建成功
3. 是否在免费额度内

### Q3: ChatTTS加载失败
**A:** 确保：
1. 所有依赖已安装
2. 有足够的磁盘空间
3. CUDA驱动正确安装（如果使用GPU）

### Q4: 音频文件没有声音
**A:** 检查：
1. 音频文件大小（<1KB说明生成失败）
2. 查看错误日志
3. 尝试使用不同的TTS提供商

---

## 下一步

根据你的需求选择合适的TTS方案：

1. **快速测试** → 使用Windows TTS（已配置）
2. **中文内容** → 配置Azure TTS（推荐）
3. **专业制作** → 使用ElevenLabs
4. **本地离线** → 安装ChatTTS

如有问题，请参考各个TTS提供商的官方文档。
