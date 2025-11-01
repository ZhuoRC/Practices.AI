"""Code snippet to add checkpoint support to summarizer"""

# This is the modified section for the summarize_document method

CHECKPOINT_CODE_AFTER_CHUNKING = '''
        # Step 2.5: Check for checkpoint and resume if available
        checkpoint_mgr = get_checkpoint_manager()
        task_id = checkpoint_mgr.find_checkpoint_by_content(content)

        checkpoint = None
        start_chunk_idx = 0

        if task_id:
            checkpoint = checkpoint_mgr.load_checkpoint(task_id)

        if checkpoint:
            # Resume from checkpoint
            chunk_summaries = checkpoint["chunk_summaries"]
            chunk_details = checkpoint["chunk_details"]
            total_tokens = checkpoint["total_tokens"]
            start_chunk_idx = len(chunk_summaries)
            print(f"  ⏭ Resuming from checkpoint: {start_chunk_idx}/{len(chunks)} chunks already completed")
            print(f"  💰 Saved tokens so far: {total_tokens['total_tokens']} tokens")
        else:
            # Fresh start - generate new task_id
            task_id = checkpoint_mgr.generate_task_id(content, filename)
            chunk_summaries = []
            chunk_details = []
            total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            print(f"  🆕 Starting fresh summarization (task_id: {task_id})")
'''

CHECKPOINT_SAVE_AFTER_CHUNK = '''
                # Save checkpoint after each chunk
                checkpoint_mgr.save_checkpoint(
                    task_id=task_id,
                    chunk_summaries=chunk_summaries,
                    chunk_details=chunk_details,
                    total_tokens=total_tokens,
                    total_chunks=len(chunks),
                    metadata={
                        "filename": filename,
                        "original_length": original_length,
                        "summary_length": summary_length
                    }
                )
'''

CHECKPOINT_DELETE_AT_END = '''
        # Clean up checkpoint after successful completion
        checkpoint_mgr.delete_checkpoint(task_id)
'''

# Instructions:
# 1. After "Failed to create chunks from document" (line 65), add CHECKPOINT_CODE_AFTER_CHUNKING
# 2. Change "for i, chunk in enumerate(chunks):" to "for i, chunk in enumerate(chunks[start_chunk_idx:], start=start_chunk_idx):"
# 3. After chunk_details.append(...), add CHECKPOINT_SAVE_AFTER_CHUNK
# 4. Before final return statement, add CHECKPOINT_DELETE_AT_END
