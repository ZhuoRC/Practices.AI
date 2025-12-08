# Gemini Workspace Context: Practices.AI

This document provides a comprehensive overview of the `Practices.AI` workspace for AI-powered analysis and development.

## 1. Project Overview

This repository, `Practices.AI`, is a **monorepo** containing a collection of independent AI-powered applications, experiments, and local model deployments. The projects primarily focus on leveraging Large Language Models (LLMs) and other AI technologies for practical tasks.

A common architectural pattern is observed across the web applications:
- **Backend**: Python with the **FastAPI** framework.
- **Frontend**: JavaScript/TypeScript with the **React** framework and **Ant Design** for the UI.
- **Configuration**: Environment variables managed via `.env` files in the backend directories.
- **Startup**: Convenience scripts (`start.bat`, `start.py`) are often provided for easy, one-click application startup on Windows.

## 2. Workspace Structure

The root directory is organized into several sub-projects, each housed in a directory prefixed with `ai.` or `api.`. Each of these directories functions as a standalone project.

```
Practices.AI/
├── ai.audio/         # Text-to-Speech (TTS) Service
├── ai.RAG/           # Retrieval-Augmented Generation Q&A System
├── ai.rewriter/      # AI Text Rewriter/Paraphraser
├── ai.summarizer/    # Document and Webpage Summarizer
├── ai.huggingface/   # Local deployment for DeepSeek-OCR
├── ai.ComfyUI/       # Documentation and tutorials for ComfyUI
├── ai.qwen-image-local/ # Local deployment for Qwen Image Models
└── ... and other projects
```

## 3. Key Projects & Quick Start Guides

Below are summaries and quick-start instructions for the key projects within this workspace.

---

### 3.1. `ai.audio`: AI Text-to-Speech (TTS) Service

- **Purpose**: A web application for generating speech from text using various cloud (Azure, Google, ElevenLabs) and local TTS engines.
- **Tech Stack**:
    - Backend: FastAPI
    - Frontend: React, Ant Design
- **Quick Start**:
    1.  Navigate to `ai.audio/`.
    2.  Configure API keys in `backend/.env`.
    3.  Run `start.bat` to launch both backend and frontend services.
    4.  Access UI at `http://localhost:3000`.

---

### 3.2. `ai.RAG`: Intelligent Q&A System

- **Purpose**: A Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and ask questions about their content.
- **Tech Stack**:
    - Backend: FastAPI, ChromaDB (vector store), `sentence-transformers`
    - Frontend: React, Ant Design, Vite
    - LLM: Qwen API (cloud or local)
- **Quick Start**:
    1.  Navigate to `ai.RAG/`.
    2.  Install dependencies: `cd backend && pip install -r requirements.txt` and `cd frontend && npm install`.
    3.  Configure the LLM provider in `backend/.env`.
    4.  Start services: `cd backend && python run.py` and `cd frontend && npm run dev`.
    5.  Access UI at `http://localhost:5173`.

---

### 3.3. `ai.rewriter`: AI Text Rewriter

- **Purpose**: A web tool for paraphrasing and rewriting text using either a cloud-based (Qwen) or a local (Mistral via Ollama) LLM. It supports chunking for long texts.
- **Tech Stack**:
    - Backend: FastAPI
    - Frontend: React, Ant Design
    - LLM: Qwen API or Ollama
- **Quick Start**:
    1.  Navigate to `ai.rewriter/`.
    2.  Configure the desired LLM in `backend/.env`.
    3.  Run `start.bat` or `start_clean.bat` for a complete, automated startup.
    4.  Access UI at `http://localhost:3000`.

---

### 3.4. `ai.summarizer`: AI Document Summarizer

- **Purpose**: An application that generates summaries from uploaded documents (PDF, DOCX, etc.) or webpages using a Map-Reduce approach with LLMs.
- **Tech Stack**:
    - Backend: FastAPI, PyPDF2, BeautifulSoup4
    - Frontend: React, Ant Design, Vite
    - LLM: Qwen API or Ollama
- **Quick Start**:
    1.  Navigate to `ai.summarizer/`.
    2.  Configure the LLM provider in `backend/.env`.
    3.  Run `start.bat` to launch both services.
    4.  Access UI at `http://localhost:5173`.

---

### 3.5. `ai.huggingface`: DeepSeek-OCR Local API

- **Purpose**: Provides a local, RESTful API for the DeepSeek-OCR model, optimized to run on GPUs with lower VRAM (6GB+).
- **Tech Stack**:
    - Backend: FastAPI, PyTorch, Flash Attention
- **Quick Start**:
    1.  Navigate to `ai.huggingface/`.
    2.  Create a Python virtual environment and install dependencies from `requirements.txt`, paying close attention to the specific PyTorch and Flash Attention installation steps in the README.
    3.  Run `python check_gpu.py` to verify the setup.
    4.  Start the server: `python deepseek_ocr/deepseek_ocr_api_low_vram.py`.
    5.  Access interactive API docs at `http://localhost:8031/docs`.

---

### 3.6. `ai.ComfyUI`: ComfyUI Learning Tutorials

- **Purpose**: This directory contains a comprehensive set of Markdown documents serving as a learning tutorial for ComfyUI, a node-based GUI for Stable Diffusion.
- **Usage**: This is a non-code, documentation-only project. To use it, simply browse the `docs/` directory to learn about ComfyUI.
