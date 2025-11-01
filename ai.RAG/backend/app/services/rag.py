from typing import List, Dict, Optional
from pathlib import Path
import time
import httpx
import asyncio
from .embeddings import embedding_service
from .vector_store import vector_store
from ..config import settings


class RAGService:
    """RAG (Retrieval-Augmented Generation) service"""

    def __init__(self):
        # Configure LLM provider
        self.provider = settings.llm_provider.lower()
        print(f"LLM Provider: {self.provider}")

        if self.provider == "local":
            # Local Ollama configuration
            self.api_url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
            self.model = settings.ollama_model
            self.api_key = None
            print(f"Local Ollama API URL: {self.api_url}")
            print(f"Local Ollama Model: {self.model}")
        elif self.provider == "cloud":
            # Cloud DashScope/Qwen configuration
            base_url = settings.qwen_api_base_url.rstrip('/')
            if base_url.endswith('/v1') or base_url.endswith('/compatible-mode/v1'):
                self.api_url = f"{base_url}/chat/completions"
            else:
                self.api_url = f"{base_url}/v1/chat/completions"
            self.model = settings.qwen_model
            self.api_key = settings.qwen_api_key
            print(f"Cloud DashScope API URL: {self.api_url}")
            print(f"Cloud DashScope Model: {self.model}")
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}. Use 'cloud' or 'local'")

        # Load prompt template
        self.prompt_template = self._load_prompt_template()
        print(f"Prompt template loaded successfully")

        # Load query reformulation template
        self.reformulation_template = self._load_query_reformulation_template()
        print(f"Query reformulation template loaded successfully")

    async def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        include_sources: bool = True,
        document_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute RAG query: retrieve relevant chunks and generate answer

        Args:
            question: User's question
            top_k: Number of chunks to retrieve (default from settings)
            include_sources: Whether to include source chunks in response
            document_ids: Optional list of document IDs to filter search results

        Returns:
            Dict with answer, optional source chunks, time consumption, and token usage
        """
        try:
            # Start timing
            start_time = time.time()

            # Log original query
            print(f"[RAG Query] Original Question:")
            print(f"{question}")

            # Step 1: Query Reformulation - rewrite question for better retrieval
            reformulated_question, reformulation_tokens = await self._reformulate_query(question)

            # Log reformulated query
            print(f"\n[RAG Query] Reformulated Question:")
            print(f"{reformulated_question}")

            # Step 2: Generate embedding for the reformulated question (run in thread pool to avoid blocking)
            question_embedding = await asyncio.to_thread(embedding_service.embed_text, reformulated_question)

            # Step 3: Search for relevant chunks
            search_results = vector_store.search(
                query_embedding=question_embedding,
                top_k=top_k,
                document_ids=document_ids
            )

            # Step 4: Prepare context from retrieved chunks
            context_chunks = search_results["documents"]

            if not context_chunks:
                end_time = time.time()
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": [],
                    "retrieved_chunks": 0,
                    "time_consumed": round(end_time - start_time, 2),
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "reformulated_question": reformulated_question,
                    "reformulation_tokens": reformulation_tokens.get("total_tokens", 0),
                    "reformulation_prompt_tokens": reformulation_tokens.get("prompt_tokens", 0),
                    "reformulation_completion_tokens": reformulation_tokens.get("completion_tokens", 0)
                }

            # Combine chunks into context
            context = "\n\n".join([f"[Document Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)])

            # Step 5: Build prompt for Qwen (use original question, not reformulated)
            prompt = self._build_prompt(question, context)

            # Step 6: Call LLM API to generate answer
            llm_result = await self._call_llm_api(prompt)
            answer = llm_result["content"]
            token_usage = llm_result.get("usage", {})

            # Calculate time consumed
            end_time = time.time()
            time_consumed = round(end_time - start_time, 2)

            # Step 7: Prepare response
            response = {
                "answer": answer,
                "retrieved_chunks": len(context_chunks),
                "time_consumed": time_consumed,
                "total_tokens": token_usage.get("total_tokens", 0),
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "reformulated_question": reformulated_question,
                "reformulation_tokens": reformulation_tokens.get("total_tokens", 0),
                "reformulation_prompt_tokens": reformulation_tokens.get("prompt_tokens", 0),
                "reformulation_completion_tokens": reformulation_tokens.get("completion_tokens", 0)
            }

            if include_sources:
                sources = []
                for i, (doc, metadata, distance) in enumerate(zip(
                    search_results["documents"],
                    search_results["metadatas"],
                    search_results["distances"]
                )):
                    sources.append({
                        "chunk_index": i,
                        "text": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance  # Convert distance to similarity
                    })
                response["sources"] = sources

            return response

        except Exception as e:
            print(f"Error in query: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _load_prompt_template(self) -> str:
        """
        Load prompt template from file

        Returns:
            Prompt template string with {context} and {question} placeholders
        """
        # Default template as fallback
        default_template = """You are a factual assistant.
Use only the CONTEXT below to answer.
If you don't find the answer, say exactly:
"I don't have enough information to answer that question."

CONTEXT:
{context}

QUESTION:
{question}"""

        try:
            # Get the prompts directory path
            current_file = Path(__file__)
            prompts_dir = current_file.parent.parent / "prompts"
            template_file = prompts_dir / settings.prompt_template_file

            # Load template from file
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = f.read()
                print(f"Loaded prompt template from: {template_file}")
                return template
            else:
                print(f"Prompt template file not found at {template_file}, using default template")
                return default_template

        except Exception as e:
            print(f"Error loading prompt template: {e}. Using default template")
            return default_template

    def _load_query_reformulation_template(self) -> str:
        """
        Load query reformulation template from file

        Returns:
            Query reformulation template string with {question} placeholder
        """
        # Default template as fallback
        default_template = """你是一个专业的查询优化助手。
将用户的问题改写为更适合文档检索的形式。
保持问题的核心意图，使用更明确的关键词。
只输出改写后的问题，不要添加任何解释。

原始问题：{question}

改写后的问题："""

        try:
            # Get the prompts directory path
            current_file = Path(__file__)
            prompts_dir = current_file.parent.parent / "prompts"
            template_file = prompts_dir / "query_reformulation.txt"

            # Load template from file
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = f.read()
                print(f"Loaded query reformulation template from: {template_file}")
                return template
            else:
                print(f"Query reformulation template not found at {template_file}, using default")
                return default_template

        except Exception as e:
            print(f"Error loading query reformulation template: {e}. Using default")
            return default_template

    async def _reformulate_query(self, question: str) -> tuple:
        """
        Reformulate user's question for better retrieval

        Args:
            question: Original user question

        Returns:
            Tuple of (reformulated_question, token_usage_dict)
        """
        try:
            # Build reformulation prompt
            prompt = self.reformulation_template.format(question=question)

            # Call LLM to reformulate
            llm_result = await self._call_llm_api(prompt)
            reformulated = llm_result["content"].strip()
            token_usage = llm_result.get("usage", {})

            # If reformulation failed or is empty, use original question
            if not reformulated or len(reformulated) < 3:
                return question, {}

            return reformulated, token_usage

        except Exception as e:
            return question, {}

    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for LLM with context and question

        Args:
            question: User's question
            context: Retrieved context chunks

        Returns:
            Formatted prompt
        """
        # Use the loaded template and replace placeholders
        prompt = self.prompt_template.format(context=context, question=question)
        return prompt

    async def _call_llm_api(self, prompt: str) -> Dict:
        """
        Call LLM API to generate response (supports both local and cloud)

        Args:
            prompt: Prompt to send to LLM

        Returns:
            Dict with content and usage information
        """
        if self.provider == "local":
            return await self._call_ollama_api(prompt)
        elif self.provider == "cloud":
            return await self._call_dashscope_api(prompt)
        else:
            raise Exception(f"Unknown provider: {self.provider}")

    async def _call_ollama_api(self, prompt: str) -> Dict:
        """
        Call Ollama API to generate response

        Args:
            prompt: Prompt to send to Ollama

        Returns:
            Dict with content and usage information
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000
                    }
                }

                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

                # Extract answer from Ollama response
                if "message" in result and "content" in result["message"]:
                    answer = result["message"]["content"]

                    # Extract token usage if available
                    usage = {}
                    if "prompt_eval_count" in result:
                        usage["prompt_tokens"] = result["prompt_eval_count"]
                    if "eval_count" in result:
                        usage["completion_tokens"] = result["eval_count"]
                    if usage:
                        usage["total_tokens"] = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)

                    return {
                        "content": answer.strip(),
                        "usage": usage
                    }
                else:
                    print(f"Unexpected response format: {result}")
                    raise Exception("Unexpected response format from Ollama API")

        except httpx.ConnectError as e:
            error_msg = f"Cannot connect to Ollama at {self.api_url}. Is Ollama running? Error: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.TimeoutException as e:
            error_msg = f"Timeout connecting to Ollama at {self.api_url}. Error: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Ollama: {e.response.status_code} - {e.response.text}"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"HTTP error calling Ollama: {type(e).__name__}: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error generating answer: {type(e).__name__}: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    async def _call_dashscope_api(self, prompt: str) -> Dict:
        """
        Call DashScope API to generate response

        Args:
            prompt: Prompt to send to DashScope

        Returns:
            Dict with content and usage information
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Content-Type": "application/json"
                }

                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "enable_thinking": False  # Required for non-streaming calls
                }

                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

                # Extract answer from response
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"]

                    # Extract token usage
                    usage = {}
                    if "usage" in result:
                        usage["prompt_tokens"] = result["usage"].get("prompt_tokens", 0)
                        usage["completion_tokens"] = result["usage"].get("completion_tokens", 0)
                        usage["total_tokens"] = result["usage"].get("total_tokens", 0)

                    return {
                        "content": answer.strip(),
                        "usage": usage
                    }
                else:
                    print(f"Unexpected response format: {result}")
                    raise Exception("Unexpected response format from DashScope API")

        except httpx.ConnectError as e:
            error_msg = f"Cannot connect to DashScope at {self.api_url}. Error: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.TimeoutException as e:
            error_msg = f"Timeout connecting to DashScope at {self.api_url}. Error: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from DashScope: {e.response.status_code} - {e.response.text}"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"HTTP error calling DashScope: {type(e).__name__}: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error generating answer: {type(e).__name__}: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    async def health_check(self) -> Dict:
        """
        Check RAG system health

        Returns:
            System health status
        """
        try:
            # Check vector store
            total_chunks = vector_store.count()
            total_documents = len(vector_store.list_documents())

            # Try a simple LLM API call
            test_prompt = "Hello"
            try:
                await self._call_llm_api(test_prompt)
                llm_status = "healthy"
            except Exception as e:
                llm_status = f"error: {str(e)}"

            return {
                "status": "healthy" if llm_status == "healthy" else "degraded",
                "vector_store": {
                    "total_chunks": total_chunks,
                    "total_documents": total_documents
                },
                "llm_provider": self.provider,
                "llm_model": self.model,
                "llm_status": llm_status,
                "embedding_model": settings.embedding_model
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance
rag_service = RAGService()
