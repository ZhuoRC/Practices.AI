# RAG Query Filter Process Explanation

## Quick Answer

**Filter happens BEFORE top_k selection.**

## Execution Order

```
1. Apply document_ids filter (if provided)
   └─> Narrows down the search space to specific documents

2. Compute similarity scores for filtered chunks
   └─> Only calculates embeddings for chunks that passed the filter

3. Sort by similarity (distance)
   └─> Lower distance = higher similarity

4. Select top_k results
   └─> Returns the K most similar chunks from filtered set
```

## Example Scenario

### Database State
```
Total chunks in database: 1000 chunks across 10 documents
- doc_1: 100 chunks
- doc_2: 100 chunks
- doc_3: 100 chunks
- ... (7 more documents)
```

### Case 1: No Filter (Search All Documents)

```python
# Query with no filter
query(question="What is AI?", document_ids=None, top_k=5)

# Process:
1. Search Space: ALL 1000 chunks
2. Compute similarity for: 1000 chunks
3. Sort by similarity
4. Return: Top 5 most similar chunks (from any document)
```

**Log Output:**
```
🌐 NO FILTER APPLIED:
   - Searching across ALL documents
   - All 1000 chunks will be searched

⚙️  EXECUTION ORDER:
   1. Apply where filter (document_ids) → Narrow down search space
   2. Compute similarity scores for filtered chunks
   3. Sort by similarity (lowest distance = highest similarity)
   4. Return top 5 most similar chunks

✅ RESULTS:
   - Found 5 chunks

📄 Result Details:
   [1] Chunk: doc_1_chunk_5
       Document: doc_1 (machine_learning.pdf)
       Distance: 0.1234 | Similarity: 0.8766
   [2] Chunk: doc_7_chunk_23
       Document: doc_7 (neural_networks.pdf)
       Distance: 0.1456 | Similarity: 0.8544
   ...
```

### Case 2: With Filter (Search Specific Documents)

```python
# Query with filter
query(
    question="What is AI?",
    document_ids=["doc_1", "doc_2"],  # Only search in 2 documents
    top_k=5
)

# Process:
1. Apply Filter: doc_1, doc_2
   └─> Search Space: 200 chunks (100 + 100)
   └─> Filtered Out: 800 chunks
2. Compute similarity for: 200 chunks ONLY
3. Sort by similarity
4. Return: Top 5 most similar chunks (only from doc_1 or doc_2)
```

**Log Output:**
```
📊 Total chunks in database: 1000

🎯 FILTER APPLIED:
   - Filter type: document_ids
   - Filtering to 2 document(s): ['doc_1', 'doc_2']
   - Where clause: {'document_id': {'$in': ['doc_1', 'doc_2']}}
   - Chunks matching filter: 200
   - Chunks filtered out: 800

🎯 SEARCH PARAMETERS:
   - Requesting top_k: 5 results
   - Embedding dimension: 1024

⚙️  EXECUTION ORDER:
   1. Apply where filter (document_ids) → Narrow down search space
   2. Compute similarity scores for filtered chunks
   3. Sort by similarity (lowest distance = highest similarity)
   4. Return top 5 most similar chunks

✅ RESULTS:
   - Found 5 chunks

📄 Result Details:
   [1] Chunk: doc_1_chunk_12
       Document: doc_1 (machine_learning.pdf)
       Distance: 0.1567 | Similarity: 0.8433
   [2] Chunk: doc_2_chunk_8
       Document: doc_2 (deep_learning.pdf)
       Distance: 0.1678 | Similarity: 0.8322
   ...
```

## Key Points

### 1. Filter is Pre-Search
- Filter is applied **BEFORE** similarity computation
- This is more efficient than post-filtering because:
  - Fewer embeddings to compare
  - Less memory usage
  - Faster computation

### 2. ChromaDB Implementation
```python
# In vector_store.py
results = self.collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,           # Maximum results to return
    where=where_clause         # Filter applied FIRST
)
```

ChromaDB's `where` parameter:
- Filters at the database level
- Applied before vector similarity search
- Uses metadata filtering (document_id field)

### 3. Performance Impact

**Without Filter:**
```
Search 1000 chunks → Find top 5
Time: ~100ms (depends on hardware)
```

**With Filter (200 chunks):**
```
Filter to 200 chunks → Search 200 chunks → Find top 5
Time: ~20ms (5x faster)
```

## Why This Order Matters

### Scenario: Looking for AI information in specific papers

**User selects 2 documents from UI**
```
Selected: ["paper_1", "paper_2"]
Question: "Explain neural networks"
```

**What happens:**
1. ✅ System filters to only paper_1 and paper_2 chunks
2. ✅ Searches within those 2 papers
3. ✅ Returns most relevant chunks from those papers
4. ❌ Does NOT search other papers at all
5. ❌ Does NOT return chunks from unselected papers

**Result:** User gets answers ONLY from the documents they selected, which is the intended behavior.

## Code Flow

```
User Query → RAG Service → Vector Store
                              ↓
                    [Filter Applied Here]
                              ↓
                    ChromaDB Query with where clause
                              ↓
                    1. Filter by document_ids
                    2. Compute similarity (filtered set only)
                    3. Sort by similarity
                    4. Return top_k
                              ↓
                    Results → RAG Service → LLM → User
```

## Testing

To see the detailed logs, simply run a query:

### Test 1: Query without filter
```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "document_ids": null}'
```

### Test 2: Query with filter
```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "document_ids": ["doc_id_1", "doc_id_2"]}'
```

Watch the backend console for detailed logs showing:
- Total chunks before filter
- Chunks after filter
- Execution order
- Results with similarity scores

## Summary

| Aspect | Details |
|--------|---------|
| **Filter Timing** | BEFORE top_k selection |
| **Implementation** | ChromaDB `where` clause |
| **Performance** | More efficient (fewer comparisons) |
| **Use Case** | Search within specific documents |
| **Result** | Only returns chunks from filtered documents |
