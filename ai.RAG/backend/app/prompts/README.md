# Prompt Templates

This directory contains prompt templates for the RAG system.

## Available Templates

### 1. `rag_system.txt` (Default)
Simple, factual prompt template focused on accuracy.
- Best for: General Q&A, factual queries
- Language: English
- Style: Concise

### 2. `rag_detailed.txt`
More detailed template with explicit instructions.
- Best for: Complex queries, detailed explanations
- Language: English
- Style: Detailed with citations

### 3. `rag_chinese.txt`
Chinese language template.
- Best for: Chinese documents and queries
- Language: Chinese (Simplified)
- Style: Professional

## Usage

### Switch Templates

**Method 1: Via Environment Variable**
Edit `backend/.env`:
```bash
# Use default template
PROMPT_TEMPLATE_FILE=rag_system.txt

# Use detailed template
PROMPT_TEMPLATE_FILE=rag_detailed.txt

# Use Chinese template
PROMPT_TEMPLATE_FILE=rag_chinese.txt
```

**Method 2: Create Custom Template**
1. Create a new `.txt` file in this directory (e.g., `my_custom.txt`)
2. Use `{context}` and `{question}` as placeholders
3. Update `.env` to point to your file
4. Restart the server

### Available Variables

All templates must include these placeholders:
- `{context}` - Retrieved document chunks (auto-injected)
- `{question}` - User's question (auto-injected)

### Example Custom Template

```
You are an expert analyst.
Analyze the CONTEXT and provide insights about the QUESTION.

CONTEXT:
{context}

QUESTION:
{question}

Analysis:
```

## Tips

✓ Keep prompts clear and specific
✓ Always include `{context}` and `{question}` placeholders
✓ Test changes with various query types
✓ Restart server after modifications
✓ Consider your document language and domain
✗ Don't remove the required placeholders
✗ Don't make prompts too complex
