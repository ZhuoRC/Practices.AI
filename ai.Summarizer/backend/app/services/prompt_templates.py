"""Prompt templates for summarization"""

# System messages
CHUNK_SUMMARY_SYSTEM = """你是一个专业的文档摘要助手。请仔细阅读文本，提取关键信息并生成简洁准确的摘要。

输出要求：
- 使用纯文本格式
- 不要使用emoji图标或特殊符号
- 使用清晰的段落结构
- 保持语言专业、简洁"""

FINAL_SUMMARY_SYSTEM = """你是一个专业的文档摘要助手。请综合多个片段的摘要，生成一个连贯完整的总摘要。

输出要求：
- 使用纯文本格式
- 不要使用emoji图标或特殊符号
- 使用清晰的段落结构
- 保持语言专业、简洁
- 如果有多个要点，使用数字编号（1. 2. 3.）而非bullet points"""


def get_chunk_summary_prompt(
    chunk_text: str,
    chunk_id: int,
    total_chunks: int,
    chunk_summary_length: int
) -> str:
    """Generate prompt for chunk summarization"""
    return f"""请为以下文本片段生成摘要。这是第 {chunk_id + 1}/{total_chunks} 个片段。

文本内容：
{chunk_text}

要求：
1. 提取主要观点和关键信息
2. 保持摘要简洁，约{chunk_summary_length}字
3. 使用清晰的语言
4. 保留重要的数据、名称和术语
5. 不要使用emoji图标或特殊符号

摘要："""


def get_final_summary_prompt(
    summaries_text: str,
    original_length: int,
    summary_length: int
) -> str:
    """Generate prompt for final summary generation"""
    return f"""请综合以下各个片段的摘要，生成一个完整、连贯的总摘要。

原文长度：约 {original_length} 字

各片段摘要：
{summaries_text}

要求：
1. 整合所有片段的关键信息
2. 生成逻辑连贯、结构清晰的总摘要
3. 总摘要长度约{summary_length}字
4. 突出文档的主题和核心观点
5. 如果有明显的结构（如引言、正文、结论），请体现出来
6. 不要使用emoji图标或特殊符号
7. 使用专业、客观的语言

总摘要："""
