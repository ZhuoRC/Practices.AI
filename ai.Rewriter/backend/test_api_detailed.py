#!/usr/bin/env python3
"""
Test script to verify Qwen API call with detailed logging
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import AIReWriter

async def test_qwen_api():
    """Test Qwen API call with detailed logging"""

    # Initialize AI ReWriter
    rewriter = AIReWriter()

    # Test data
    test_text = "这是一个测试文本，用于验证Qwen API的调用是否正常工作。"
    requirements = "请将这个文本改写得更正式一些"

    # Build prompt as done in rewrite_text method
    prompt = f"""请根据以下要求改写文本：

原始文本：
{test_text}

改写要求：
{requirements}

请提供改写后的文本："""

    print("=" * 80)
    print("TESTING QWEN API CALL")
    print("=" * 80)
    print(f"Test Text: {test_text}")
    print(f"Requirements: {requirements}")
    print(f"Built Prompt Length: {len(prompt)}")

    try:
        # Call Qwen API
        result = await rewriter.call_qwen_api(prompt)
        print(f"SUCCESS! Result: {result}")
    except Exception as e:
        print(f"ERROR: {e}")

    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_qwen_api())