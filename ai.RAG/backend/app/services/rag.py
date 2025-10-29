from typing import List, Dict, Optional
from pathlib import Path
import httpx
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

    async def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        include_sources: bool = True
    ) -> Dict:
        """
        Execute RAG query: retrieve relevant chunks and generate answer

        Args:
            question: User's question
            top_k: Number of chunks to retrieve (default from settings)
            include_sources: Whether to include source chunks in response

        Returns:
            Dict with answer and optional source chunks
        """
        try:
            # Step 1: Generate embedding for the question
            print(f"Generating embedding for question: {question[:50]}...")
            question_embedding = embedding_service.embed_text(question)
            print(f"Embedding generated successfully. Dimension: {len(question_embedding)}")

            # Step 2: Search for relevant chunks
            print(f"Searching vector store for top {top_k or settings.top_k} chunks...")
            search_results = vector_store.search(
                query_embedding=question_embedding,
                top_k=top_k
            )
            print(f"Found {len(search_results['documents'])} chunks")

            # Step 3: Prepare context from retrieved chunks
            context_chunks = search_results["documents"]

            if not context_chunks:
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": [],
                    "retrieved_chunks": 0
                }

            # Combine chunks into context
            context = "\n\n".join([f"[Document Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)])
            print(f"Context prepared. Total length: {len(context)} characters")

            # Step 4: Build prompt for Qwen
            prompt = self._build_prompt(question, context)

            # Step 5: Call LLM API to generate answer
            print(f"Calling {self.provider} API at {self.api_url}...")
            answer = await self._call_llm_api(prompt)
            print(f"Answer generated successfully. Length: {len(answer)} characters")

            # Step 6: Prepare response
            response = {
                "answer": answer,
                "retrieved_chunks": len(context_chunks)
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

    async def _call_llm_api(self, prompt: str) -> str:
        """
        Call LLM API to generate response (supports both local and cloud)

        Args:
            prompt: Prompt to send to LLM

        Returns:
            Generated response text
        """
        if self.provider == "local":
            return await self._call_ollama_api(prompt)
        elif self.provider == "cloud":
            return await self._call_dashscope_api(prompt)
        else:
            raise Exception(f"Unknown provider: {self.provider}")

    async def _call_ollama_api(self, prompt: str) -> str:
        """
        Call Ollama API to generate response

        Args:
            prompt: Prompt to send to Ollama

        Returns:
            Generated response text
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

                print(f"Sending request to Ollama API: {self.api_url}")
                print(f"Using model: {self.model}")

                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

                print(f"Ollama API response status: {response.status_code}")

                response.raise_for_status()
                result = response.json()

                # Extract answer from Ollama response
                if "message" in result and "content" in result["message"]:
                    answer = result["message"]["content"]
                    return answer.strip()
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

    async def _call_dashscope_api(self, prompt: str) -> str:
        """
        Call DashScope API to generate response

        Args:
            prompt: Prompt to send to DashScope

        Returns:
            Generated response text
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

                print(f"Sending request to DashScope API: {self.api_url}")
                print(f"Using model: {self.model}")

                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

                print(f"DashScope API response status: {response.status_code}")

                response.raise_for_status()
                result = response.json()

                # Extract answer from response
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"]
                    return answer.strip()
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
