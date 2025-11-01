# Prompt Templates 说明

## 文件位置
`app/services/prompt_templates.py`

## 如何自定义输出要求

所有的摘要生成prompt都已经抽取到 `prompt_templates.py` 中，你可以轻松修改输出要求。

### 1. 全局输出要求

在 `CHUNK_SUMMARY_SYSTEM` 和 `FINAL_SUMMARY_SYSTEM` 中定义：

```python
CHUNK_SUMMARY_SYSTEM = """你是一个专业的文档摘要助手。...

输出要求：
- 使用纯文本格式
- 不要使用emoji图标或特殊符号
- 使用清晰的段落结构
- 保持语言专业、简洁"""
```

**可以添加的要求示例：**
- ✅ 不要使用emoji图标或特殊符号
- ✅ 使用中文/英文输出
- ✅ 使用客观/主观语气
- ✅ 包含/不包含引用
- ✅ 使用markdown格式/纯文本格式
- ✅ 突出重点使用**加粗**/普通文本

### 2. 具体任务要求

在 `get_chunk_summary_prompt()` 和 `get_final_summary_prompt()` 函数中定义：

```python
要求：
1. 提取主要观点和关键信息
2. 保持摘要简洁，约{chunk_summary_length}字
3. 使用清晰的语言
4. 保留重要的数据、名称和术语
5. 不要使用emoji图标或特殊符号  # 👈 在这里添加更多要求
```

### 3. 常见自定义场景

#### 场景1: 禁止使用特殊符号和emoji
```python
5. 不要使用emoji图标或特殊符号
6. 不要使用bullet points（•、●、○）
7. 使用数字编号（1. 2. 3.）而非其他标记
```

#### 场景2: 要求特定格式
```python
5. 使用markdown格式输出
6. 重要概念使用**加粗**标记
7. 每个段落之间空一行
```

#### 场景3: 特定领域要求
```python
5. 保留所有技术术语的英文原文
6. 突出数据和统计结果
7. 按时间顺序组织内容
```

#### 场景4: 语言风格要求
```python
5. 使用正式、学术的语言风格
6. 避免使用口语化表达
7. 保持客观中立的叙述
```

## 修改步骤

1. 打开 `app/services/prompt_templates.py`
2. 根据需求修改 `CHUNK_SUMMARY_SYSTEM` 或 `FINAL_SUMMARY_SYSTEM`
3. 或者修改 `get_chunk_summary_prompt()` 或 `get_final_summary_prompt()` 中的"要求"部分
4. 保存文件
5. 重启backend服务

**不需要修改** `summarizer.py`，所有的prompt逻辑都已经封装在template模块中。

## 示例：添加"不要使用图标"的要求

修改前：
```python
要求：
1. 提取主要观点和关键信息
2. 保持摘要简洁，约{chunk_summary_length}字
```

修改后：
```python
要求：
1. 提取主要观点和关键信息
2. 保持摘要简洁，约{chunk_summary_length}字
3. 不要使用emoji图标、表情符号或特殊符号
4. 使用纯文本格式，便于阅读和复制
```

## 高级用法

如果需要为不同类型的文档使用不同的prompt，可以：

1. 在 `prompt_templates.py` 中添加新的prompt函数
2. 在 `summarizer.py` 中根据文档类型选择不同的prompt函数

例如：
```python
# prompt_templates.py
def get_technical_doc_prompt(...):
    """For technical documentation"""
    ...

def get_news_article_prompt(...):
    """For news articles"""
    ...
```
