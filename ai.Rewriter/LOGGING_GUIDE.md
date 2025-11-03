# 后端日志系统详细指南

## 📋 日志功能概述

我们已经为AI文本改写器后端添加了全面的日志记录系统，包括：

### 🔧 日志配置
- **文件日志**: `backend/app.log` (UTF-8编码)
- **控制台日志**: 实时显示在终端
- **日志级别**: INFO级别，包含详细操作信息
- **格式**: 时间戳 - 模块名 - 级别 - 消息

### 📊 日志记录内容

#### 1. 请求日志 (HTTP中间件)
```
2025-11-02 19:33:18,289 - __main__ - INFO - Incoming Request: POST http://localhost:8001/rewrite
2025-11-02 19:33:18,289 - __main__ - INFO - Client IP: 127.0.0.1
2025-11-02 19:33:18,289 - __main__ - INFO - Headers: {'host': 'localhost:8001', ...}
2025-11-02 19:33:18,289 - __main__ - INFO - Request Body Summary: {'source_text': 'str', 'requirements': 'str', ...}
2025-11-02 19:33:20,394 - __main__ - INFO - Response Status: 200
2025-11-02 19:33:20,394 - __main__ - INFO - Processing Time: 2.10s
2025-11-02 19:33:20,394 - __main__ - INFO - Response Size: 133 bytes
```

#### 2. 初始化日志
```
2025-11-02 19:32:22,501 - __main__ - INFO - Initializing AI ReWriter...
2025-11-02 19:32:22,506 - __main__ - INFO - Configuration loaded:
2025-11-02 19:32:22,507 - __main__ - INFO -   Qwen Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
2025-11-02 19:32:22,507 - __main__ - INFO -   Qwen Model: qwen3-235b-a22b-instruct-2507
2025-11-02 19:32:22,507 - __main__ - INFO -   Qwen API Key: Configured
```

#### 3. 文本处理日志
```
2025-11-02 19:33:22,739 - __main__ - INFO - Starting text rewrite process
2025-11-02 19:33:22,739 - __main__ - INFO - Mode: cloud
2025-11-02 19:33:22,739 - __main__ - INFO - Source text length: 273 chars
2025-11-02 19:33:22,739 - __main__ - INFO - Requirements length: 27 chars
2025-11-02 19:33:22,739 - __main__ - INFO - Segment size: 200 chars
```

#### 4. 分段处理日志
```
2025-11-02 19:33:22,739 - __main__ - INFO - Splitting text into segments (max size: 200 chars)
2025-11-02 19:33:22,739 - __main__ - INFO - Original text length: 273 chars
2025-11-02 19:33:22,739 - __main__ - INFO - Created 1 segments
2025-11-02 19:33:22,739 - __main__ - INFO -   Segment 1: 274 chars
```

#### 5. API调用日志
```
2025-11-02 19:33:22,740 - __main__ - INFO - Calling Qwen Cloud API...
2025-11-02 19:33:22,740 - __main__ - INFO - Using model: qwen3-235b-a22b-instruct-2507
2025-11-02 19:33:22,740 - __main__ - INFO - Prompt length: 350 chars
2025-11-02 19:33:22,740 - __main__ - INFO - Sending request to: https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
2025-11-02 19:33:34,841 - __main__ - INFO - API Response Time: 12.10s
2025-11-02 19:33:34,841 - __main__ - INFO - Status Code: 200
2025-11-02 19:33:34,841 - __main__ - INFO - Successfully got response from Qwen API
2025-11-02 19:33:34,841 - __main__ - INFO - Response length: 412 chars
2025-11-02 19:33:34,841 - __main__ - INFO - Token usage: {'prompt_tokens': 213, 'completion_tokens': 222, 'total_tokens': 435}
```

#### 6. 错误处理日志
```
2025-11-02 19:33:18,292 - __main__ - INFO - Input validation passed, proceeding with rewrite request
2025-11-02 19:33:18,292 - __main__ - ERROR - Validation failed: Source text is empty
2025-11-02 19:33:18,292 - __main__ - ERROR - Network Error: Network error calling Qwen API: ...
2025-11-02 19:33:18,292 - __main__ - ERROR - Error type: ConnectError
2025-11-02 19:33:18,292 - __main__ - ERROR - Connection troubleshooting:
2025-11-02 19:33:18,292 - __main__ - ERROR -   1. Check internet connection
2025-11-02 19:33:18,292 - __main__ - ERROR -   2. Verify firewall settings
```

## 🚀 如何查看日志

### 方法1: 实时控制台输出
启动后端时，日志会实时显示在终端：
```bash
cd backend
python main.py
```

### 方法2: 查看日志文件
所有日志都会保存到 `backend/app.log` 文件：
```bash
# 查看最新日志
tail -f backend/app.log

# 查看完整日志
cat backend/app.log

# 搜索特定内容
grep "API Response Time" backend/app.log
```

### 方法3: 使用调试工具
我们提供了专门的调试脚本：
```bash
# Qwen API详细调试
python debug_qwen.py

# 后端功能测试
python test_enhanced_backend.py
```

## 🔍 日志分析示例

### 性能监控
```
API Response Time: 2.10s
Processing Time: 2.10s
Token usage: {'prompt_tokens': 79, 'completion_tokens': 14, 'total_tokens': 93}
```

### 错误诊断
```
Network Error: Network error calling Qwen API: ...
Error type: ConnectError
Connection troubleshooting:
  1. Check internet connection
  2. Verify firewall settings
```

### 使用统计
```
Request Body Summary: {'source_text_length': 273, 'requirements_length': 27}
Segments Processed: 1
Result length: 412 chars
```

## 📝 日志级别说明

- **INFO**: 正常操作信息（请求处理、API调用、配置加载）
- **ERROR**: 错误信息（验证失败、API错误、网络问题）
- **WARNING**: 警告信息（非致命问题）
- **DEBUG**: 调试信息（详细的技术细节）

## 🛠️ 自定义日志配置

如需修改日志配置，编辑 `backend/main.py` 中的以下部分：

```python
logging.basicConfig(
    level=logging.INFO,  # 可改为 DEBUG, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

## 📊 监控建议

1. **性能监控**: 关注 `API Response Time` 和 `Processing Time`
2. **错误监控**: 关注 ERROR 级别的日志，特别是网络错误
3. **使用监控**: 关注 `Token usage` 来控制API成本
4. **容量监控**: 关注文本长度和分段数量

## 🔄 日志轮转

对于生产环境，建议添加日志轮转功能：

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10*1024*1024, backupCount=5)
```

这样可以防止单个日志文件过大。