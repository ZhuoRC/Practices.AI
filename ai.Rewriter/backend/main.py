from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
import httpx
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="AI Rewriter API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request details
    logger.info(f"Incoming Request: {request.method} {request.url}")
    logger.info(f"Client IP: {request.client.host if request.client else 'unknown'}")
    logger.info(f"Headers: {dict(request.headers)}")

    # Get request body for POST requests - IMPORTANT: Cache the body so FastAPI can read it again
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            # Read the body
            body = await request.body()
            if body:
                # Try to parse as JSON for logging
                try:
                    body_json = json.loads(body.decode())
                    # Log detailed payload information
                    if isinstance(body_json, dict):
                        summary = {k: type(v).__name__ for k, v in body_json.items()}
                        if 'source_text' in body_json:
                            summary['source_text_length'] = len(body_json['source_text'])
                            summary['source_text_preview'] = body_json['source_text'][:100] + "..." if len(body_json['source_text']) > 100 else body_json['source_text']
                        if 'requirements' in body_json:
                            summary['requirements_length'] = len(body_json['requirements'])
                            summary['requirements_preview'] = body_json['requirements'][:100] + "..." if len(body_json['requirements']) > 100 else body_json['requirements']
                        summary['mode'] = body_json.get('mode', 'unknown')
                        summary['segment_size'] = body_json.get('segment_size', 'default')
                        logger.info(f"Request Body Summary: {summary}")
                        logger.info(f"Full Payload: {body_json}")
                except:
                    logger.info(f"Request Body Size: {len(body)} bytes")

            # CRITICAL FIX: Create a new receive function that replays the body
            async def receive():
                return {"type": "http.request", "body": body}

            # Replace the request's receive with our cached version
            request._receive = receive

        except Exception as e:
            logger.warning(f"Could not log request body: {e}")

    # Process request
    response = await call_next(request)

    # Log response details
    process_time = time.time() - start_time
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Processing Time: {process_time:.2f}s")
    logger.info(f"Response Size: {response.headers.get('content-length', 'unknown')} bytes")
    logger.info("=" * 80)

    return response

class RewriteRequest(BaseModel):
    source_text: str
    requirements: str
    mode: str = "cloud"  # "cloud" or "local"
    segment_size: Optional[int] = 500  # For segmented rewriting

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

class RewriteResponse(BaseModel):
    rewritten_text: str
    mode_used: str
    segments_processed: int
    token_usage: Optional[TokenUsage] = None

class AIReWriter:
    def __init__(self):
        logger.info("Initializing AI ReWriter...")

        self.qwen_api_key = os.getenv("QWEN_API_KEY")
        self.qwen_base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.qwen_model = os.getenv("QWEN_MODEL", "qwen-plus")
        self.local_model_host = os.getenv("LOCAL_MODEL_HOST", "localhost")
        self.local_model_port = os.getenv("LOCAL_MODEL_PORT", "11434")
        self.local_model_name = os.getenv("LOCAL_MODEL_NAME", "mistral:7b-instruct")

        # Log configuration (without sensitive data)
        logger.info("Configuration loaded:")
        logger.info(f"  Qwen Base URL: {self.qwen_base_url}")
        logger.info(f"  Qwen Model: {self.qwen_model}")
        logger.info(f"  Qwen API Key: {'Configured' if self.qwen_api_key else 'Not configured'}")
        logger.info(f"  Local Model Host: {self.local_model_host}")
        logger.info(f"  Local Model Port: {self.local_model_port}")
        logger.info(f"  Local Model Name: {self.local_model_name}")

        logger.info("AI ReWriter initialization complete!")

    def split_text_into_segments(self, text: str, segment_size: int) -> List[str]:
        """Split text into segments while preserving sentence boundaries."""
        logger.info(f"Splitting text into segments (max size: {segment_size} chars)")
        logger.info(f"Original text length: {len(text)} chars")

        sentences = re.split(r'[.!?]+', text)
        segments = []
        current_segment = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_segment + sentence) < segment_size:
                current_segment += sentence + ". "
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + ". "

        if current_segment:
            segments.append(current_segment.strip())

        logger.info(f"Created {len(segments)} segments")
        for i, segment in enumerate(segments):
            logger.info(f"  Segment {i+1}: {len(segment)} chars")

        return segments

    async def call_qwen_api(self, prompt: str) -> tuple[str, dict]:
        """Call Qwen cloud API. Returns (content, usage_dict)."""
        logger.info("Calling Qwen Cloud API...")
        logger.info(f"Using model: {self.qwen_model}")
        logger.info(f"Prompt length: {len(prompt)} chars")

        headers = {
            "Authorization": f"Bearer {self.qwen_api_key}",
            "Content-Type": "application/json"
        }

        # Prepare data based on API version
        if "/compatible-mode/v1" in self.qwen_base_url:
            # OpenAI compatible format
            data = {
                "model": self.qwen_model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的文本改写助手，根据用户的要求对文本进行改写。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 3000  # Increased for longer responses
            }
        else:
            # Native DashScope API format
            data = {
                "model": self.qwen_model,
                "input": {
                    "messages": [
                        {"role": "system", "content": "你是一个专业的文本改写助手，根据用户的要求对文本进行改写。"},
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 3000,  # Increased for longer responses
                    "enable_thinking": False,
                    "result_format": "message"
                }
            }

        try:
            start_time = time.time()

            # Determine API format and construct endpoint
            if "/compatible-mode/v1" in self.qwen_base_url:
                endpoint = f"{self.qwen_base_url}/chat/completions"
                api_format = "Compatible Mode (OpenAI-like)"
            else:
                endpoint = f"{self.qwen_base_url}/services/aigc/text-generation/generation"
                api_format = "Native DashScope API"

            # Log detailed request information
            logger.info("=" * 80)
            logger.info("QWEN API REQUEST DETAILS")
            logger.info("=" * 80)
            logger.info(f"API Format: {api_format}")
            logger.info(f"Base URL: {self.qwen_base_url}")
            logger.info(f"Full Endpoint URL: {endpoint}")
            logger.info(f"API Model: {self.qwen_model}")
            logger.info(f"Request Headers: {headers}")
            logger.info(f"Request Payload:")
            logger.info(f"  {json.dumps(data, indent=2, ensure_ascii=False)}")

            # Use longer timeout for large texts
            timeout = 300.0 if len(prompt) > 1000 else 120.0
            logger.info(f"Timeout: {timeout}s (prompt length: {len(prompt)})")
            logger.info("=" * 80)

            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info(f"Sending HTTP POST request to: {endpoint}")

                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=data
                )

                api_time = time.time() - start_time
                logger.info("=" * 80)
                logger.info("QWEN API RESPONSE DETAILS")
                logger.info("=" * 80)
                logger.info(f"Response Time: {api_time:.2f}s")
                logger.info(f"Status Code: {response.status_code}")
                logger.info(f"Response Headers: {dict(response.headers)}")
                logger.info(f"Response Body:")
                try:
                    response_json = response.json()
                    logger.info(f"  {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                except:
                    logger.info(f"  {response.text}")
                logger.info("=" * 80)

                if response.status_code != 200:
                    error_detail = f"Qwen API error: {response.status_code} - {response.text}"
                    logger.error(f"API Error: {error_detail}")
                    raise HTTPException(
                        status_code=500,
                        detail=error_detail
                    )

                result = response.json()
                logger.info(f"Response keys: {list(result.keys())}")

                # Handle different response formats
                usage = result.get("usage", {})

                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"Successfully got response from Qwen API")
                    logger.info(f"Response length: {len(content)} chars")
                    if usage:
                        logger.info(f"Token usage: {usage}")
                    return content, usage
                elif "output" in result and "choices" in result["output"] and len(result["output"]["choices"]) > 0:
                    # Native DashScope API format
                    content = result["output"]["choices"][0]["message"]["content"]
                    logger.info(f"Successfully got response from Qwen API (native format)")
                    logger.info(f"Response length: {len(content)} chars")
                    if usage:
                        logger.info(f"Token usage: {usage}")
                    return content, usage
                elif "output" in result and "text" in result["output"]:
                    content = result["output"]["text"]
                    logger.info(f"Successfully got response from Qwen API (alternative format)")
                    logger.info(f"Response length: {len(content)} chars")
                    return content, usage
                else:
                    logger.error(f"Unexpected response format: {result}")
                    raise HTTPException(status_code=500, detail="Unexpected API response format")

        except httpx.RequestError as e:
            error_detail = f"Network error calling Qwen API: {str(e)}"
            logger.error(f"Network Error: {error_detail}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Detailed error info: {repr(e)}")

            # Provide more helpful troubleshooting information
            if "connect" in str(e).lower():
                logger.error("Connection troubleshooting:")
                logger.error("  1. Check internet connection")
                logger.error("  2. Verify firewall settings")
                logger.error("  3. Check if the API endpoint is accessible")
                logger.error(f"  4. Try accessing {self.qwen_base_url} in browser")
            elif "timeout" in str(e).lower():
                logger.error("Timeout troubleshooting:")
                logger.error("  1. Check network speed")
                logger.error("  2. Try again (API might be slow)")
                logger.error("  3. Consider reducing request complexity")
                logger.error("  4. Try using smaller text segments")
                logger.error(f"  5. Current timeout settings: {timeout}s API timeout")

            raise HTTPException(status_code=503, detail=error_detail)
        except Exception as e:
            error_detail = f"Unexpected error calling Qwen API: {str(e)}"
            logger.error(f"Unexpected Error: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

    async def call_local_model(self, prompt: str) -> tuple[str, dict]:
        """Call local Mistral model via Ollama. Returns (content, usage_dict)."""
        logger.info("Calling Local Model (Ollama)...")
        logger.info(f"Using model: {self.local_model_name}")
        logger.info(f"Local endpoint: {self.local_model_host}:{self.local_model_port}")

        url = f"http://{self.local_model_host}:{self.local_model_port}/api/generate"

        data = {
            "model": self.local_model_name,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "1h",  # Keep model loaded for 1 hour after last request
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }

        try:
            start_time = time.time()
            logger.info(f"Sending request to local model: {url}")
            logger.info(f"Prompt length: {len(prompt)} chars")

            # Increased timeout to handle model loading + long text processing
            timeout = 300.0  # 5 minutes for local model (loading + generation)
            logger.info(f"Request timeout: {timeout}s")
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=data)

                api_time = time.time() - start_time
                logger.info(f"Local Model Response Time: {api_time:.2f}s")
                logger.info(f"Status Code: {response.status_code}")

                if response.status_code != 200:
                    error_detail = f"Local model error: {response.status_code} - {response.text}"
                    logger.error(f"Local Model Error: {error_detail}")
                    raise HTTPException(status_code=500, detail=error_detail)

                result = response.json()
                content = result.get("response", "")

                # Ollama returns token counts in different format
                usage = {}
                if "prompt_eval_count" in result:
                    usage["input_tokens"] = result.get("prompt_eval_count", 0)
                if "eval_count" in result:
                    usage["output_tokens"] = result.get("eval_count", 0)
                if usage:
                    usage["total_tokens"] = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                    logger.info(f"Token usage: {usage}")

                logger.info(f"Successfully got response from local model")
                logger.info(f"Response length: {len(content)} chars")
                return content, usage

        except httpx.TimeoutException as e:
            api_time = time.time() - start_time
            error_detail = f"Local model request timeout after {api_time:.2f}s (limit: {timeout}s)"
            logger.error(f"Local Model Timeout: {error_detail}")
            logger.error("Troubleshooting tips:")
            logger.error("  1. Model may need time to load (first request is slower)")
            logger.error("  2. Consider using smaller text segments")
            logger.error("  3. Ensure Ollama service is running: 'ollama serve'")
            logger.error("  4. Check if model is loaded: curl http://localhost:11434/api/tags")
            raise HTTPException(status_code=504, detail=error_detail)
        except httpx.RequestError as e:
            api_time = time.time() - start_time
            error_detail = f"Network error calling local model after {api_time:.2f}s: {str(e)}"
            logger.error(f"Local Model Network Error: {error_detail}")
            raise HTTPException(status_code=503, detail=error_detail)
        except Exception as e:
            error_detail = f"Unexpected error calling local model: {str(e)}"
            logger.error(f"Local Model Unexpected Error: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

    def create_rewrite_prompt(self, segment: str, requirements: str, context: str = "") -> str:
        """Create a prompt for text rewriting."""
        logger.info("Creating rewrite prompt...")
        logger.info(f"Segment length: {len(segment)} chars")
        logger.info(f"Requirements: {requirements[:100]}{'...' if len(requirements) > 100 else ''}")
        logger.info(f"Context length: {len(context)} chars")

        prompt = f"请根据以下要求改写文本：\n\n改写要求：{requirements}\n\n"

        if context:
            prompt += f"上下文信息：{context}\n\n"

        prompt += f"原文：\n{segment}\n\n请改写上述文本，保持原意的同时满足改写要求："

        logger.info(f"Prompt created successfully, length: {len(prompt)} chars")
        logger.info(f"Prompt preview: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")

        return prompt

    async def rewrite_segment_cloud(self, segment: str, requirements: str, context: str = "") -> tuple[str, dict]:
        """Rewrite a single segment using cloud API. Returns (content, usage_dict)."""
        logger.info("Rewrite segment using cloud API...")
        prompt = self.create_rewrite_prompt(segment, requirements, context)
        logger.info("Calling Qwen API with generated prompt...")
        return await self.call_qwen_api(prompt)

    async def rewrite_segment_local(self, segment: str, requirements: str, context: str = "") -> tuple[str, dict]:
        """Rewrite a single segment using local model. Returns (content, usage_dict)."""
        prompt = self.create_rewrite_prompt(segment, requirements, context)
        return await self.call_local_model(prompt)

    async def rewrite_text(self, source_text: str, requirements: str, mode: str, segment_size: int = 500) -> tuple[str, int, dict]:
        """Main rewrite function with support for segmented processing. Returns (text, segments_count, total_usage)."""
        logger.info(f"Starting text rewrite process")
        logger.info(f"Mode: {mode}")
        logger.info(f"Source text length: {len(source_text)} chars")
        logger.info(f"Requirements length: {len(requirements)} chars")
        logger.info(f"Segment size: {segment_size} chars")

        # Initialize token usage tracking
        total_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

        if len(source_text) <= segment_size:
            # Text is short enough, process as single segment
            logger.info("Processing as single segment")
            if mode == "cloud":
                result, usage = await self.rewrite_segment_cloud(source_text, requirements)
            else:
                result, usage = await self.rewrite_segment_local(source_text, requirements)

            # Aggregate token usage
            if usage:
                total_usage["input_tokens"] = usage.get("input_tokens", 0)
                total_usage["output_tokens"] = usage.get("output_tokens", 0)
                total_usage["total_tokens"] = usage.get("total_tokens", 0)

            logger.info(f"Single segment rewrite completed, result length: {len(result)} chars")
            logger.info(f"Token usage: {total_usage}")
            return result, 1, total_usage

        # Split into segments for longer texts
        logger.info("Processing multiple segments")
        segments = self.split_text_into_segments(source_text, segment_size)
        rewritten_segments = []

        for i, segment in enumerate(segments):
            logger.info(f"Processing segment {i+1}/{len(segments)}")

            # Provide context from previous segments
            context = ""
            if i > 0:
                context = "前文改写结果：" + " ".join(rewritten_segments[-1:])  # Only use immediate previous segment as context
                logger.info(f"Providing context from previous segment: {len(context)} chars")

            if mode == "cloud":
                rewritten_segment, usage = await self.rewrite_segment_cloud(segment, requirements, context)
            else:
                rewritten_segment, usage = await self.rewrite_segment_local(segment, requirements, context)

            # Aggregate token usage
            if usage:
                total_usage["input_tokens"] += usage.get("input_tokens", 0)
                total_usage["output_tokens"] += usage.get("output_tokens", 0)
                total_usage["total_tokens"] += usage.get("total_tokens", 0)

            rewritten_segments.append(rewritten_segment)
            logger.info(f"Segment {i+1} rewrite completed, result length: {len(rewritten_segment)} chars")

        final_result = " ".join(rewritten_segments)
        logger.info(f"All segments processed, final result length: {len(final_result)} chars")
        logger.info(f"Total token usage across all segments: {total_usage}")
        return final_result, len(segments), total_usage

# Initialize the rewriter
rewriter = AIReWriter()

@app.get("/")
async def root():
    return {"message": "AI Rewriter API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "modes": ["cloud", "local"]}

@app.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    """Rewrite text according to requirements."""
    request_start_time = time.time()
    logger.info("Received rewrite request")

    try:
        # Validate input
        if not request.source_text.strip():
            logger.error("Validation failed: Source text is empty")
            raise HTTPException(status_code=400, detail="Source text cannot be empty")

        if not request.requirements.strip():
            logger.error("Validation failed: Requirements are empty")
            raise HTTPException(status_code=400, detail="Requirements cannot be empty")

        if request.mode not in ["cloud", "local"]:
            logger.error(f"Validation failed: Invalid mode '{request.mode}'")
            raise HTTPException(status_code=400, detail="Mode must be 'cloud' or 'local'")

        if request.mode == "cloud" and not rewriter.qwen_api_key:
            logger.error("Validation failed: Qwen API key not configured for cloud mode")
            raise HTTPException(
                status_code=500,
                detail="Qwen API key not configured for cloud mode"
            )

        logger.info(f"Input validation passed, proceeding with rewrite request")

        rewritten_text, segments_processed, token_usage = await rewriter.rewrite_text(
            request.source_text,
            request.requirements,
            request.mode,
            request.segment_size or 500
        )

        total_time = time.time() - request_start_time
        logger.info(f"Rewrite request completed successfully in {total_time:.2f}s")
        logger.info(f"Returning response: mode={request.mode}, segments={segments_processed}, result_length={len(rewritten_text)}, tokens={token_usage}")

        # Create TokenUsage model if we have token data
        token_usage_model = None
        if token_usage and token_usage.get("total_tokens", 0) > 0:
            token_usage_model = TokenUsage(**token_usage)

        return RewriteResponse(
            rewritten_text=rewritten_text,
            mode_used=request.mode,
            segments_processed=segments_processed,
            token_usage=token_usage_model
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except httpx.RequestError as e:
        total_time = time.time() - request_start_time
        logger.error(f"Request error after {total_time:.2f}s: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        total_time = time.time() - request_start_time
        logger.error(f"Unexpected error after {total_time:.2f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=600,  # 10 minutes keep-alive
        timeout_graceful_shutdown=30  # 30 seconds graceful shutdown
    )