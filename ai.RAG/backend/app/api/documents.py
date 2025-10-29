from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ..services.pdf_processor import pdf_processor
from ..services.embeddings import embedding_service
from ..services.vector_store import vector_store

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document and process it for RAG

    Args:
        file: PDF file to upload

    Returns:
        Document information and processing status
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Read file content
        content = await file.read()

        # Save PDF file
        save_result = await pdf_processor.save_pdf(content, file.filename)
        document_id = save_result["document_id"]
        file_path = save_result["file_path"]

        # Process PDF: extract text and create chunks
        chunks = await pdf_processor.process_pdf(file_path, document_id)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text content found in PDF")

        # Generate embeddings for all chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)

        # Prepare data for vector store
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        metadatas = [
            {
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "total_chunks": chunk["total_chunks"],
                "original_filename": save_result["original_filename"]
            }
            for chunk in chunks
        ]

        # Store in vector database
        vector_store.add_documents(
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=chunk_ids
        )

        return {
            "success": True,
            "message": "Document uploaded and processed successfully",
            "document_id": document_id,
            "original_filename": save_result["original_filename"],
            "total_chunks": len(chunks),
            "file_size": len(content)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/_cleanup/orphaned")
async def cleanup_orphaned_documents():
    """
    Cleanup orphaned documents (PDF files without vector store data or vice versa)

    Returns:
        Cleanup report
    """
    try:
        print("Starting orphaned documents cleanup...")

        # Get all PDF files
        pdf_files = pdf_processor.list_pdfs()
        pdf_doc_ids = {pdf["document_id"] for pdf in pdf_files}
        print(f"Found {len(pdf_doc_ids)} PDF files")

        # Get all document IDs from vector store
        vector_doc_ids = set(vector_store.list_documents())
        print(f"Found {len(vector_doc_ids)} unique documents in vector store")

        # Find orphaned PDFs (PDF exists but no vector data)
        orphaned_pdfs = pdf_doc_ids - vector_doc_ids
        print(f"Found {len(orphaned_pdfs)} orphaned PDF files")

        # Find orphaned vector data (vector data exists but no PDF)
        orphaned_vectors = vector_doc_ids - pdf_doc_ids
        print(f"Found {len(orphaned_vectors)} orphaned vector store entries")

        cleanup_report = {
            "total_pdfs": len(pdf_doc_ids),
            "total_vectors": len(vector_doc_ids),
            "orphaned_pdfs": list(orphaned_pdfs),
            "orphaned_vectors": list(orphaned_vectors),
            "pdfs_deleted": 0,
            "vector_entries_deleted": 0
        }

        # Optionally delete orphaned data (for now just report)
        # Uncomment below to actually delete orphaned data
        """
        for doc_id in orphaned_pdfs:
            filename = f"{doc_id}.pdf"
            if pdf_processor.delete_pdf(filename):
                cleanup_report["pdfs_deleted"] += 1

        for doc_id in orphaned_vectors:
            chunks_deleted = vector_store.delete_by_document_id(doc_id)
            if chunks_deleted > 0:
                cleanup_report["vector_entries_deleted"] += 1
        """

        return {
            "success": True,
            "message": "Cleanup scan completed (use /_cleanup/orphaned/delete to remove orphaned data)",
            **cleanup_report
        }

    except Exception as e:
        print(f"Error during cleanup: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.post("/_cleanup/orphaned/delete")
async def cleanup_orphaned_documents_delete():
    """
    Cleanup orphaned documents with actual deletion

    Returns:
        Cleanup report with deletion results
    """
    try:
        print("Starting orphaned documents cleanup with deletion...")

        # Get all PDF files
        pdf_files = pdf_processor.list_pdfs()
        pdf_doc_ids = {pdf["document_id"] for pdf in pdf_files}
        print(f"Found {len(pdf_doc_ids)} PDF files")

        # Get all document IDs from vector store
        vector_doc_ids = set(vector_store.list_documents())
        print(f"Found {len(vector_doc_ids)} unique documents in vector store")

        # Find orphaned PDFs (PDF exists but no vector data)
        orphaned_pdfs = pdf_doc_ids - vector_doc_ids
        print(f"Found {len(orphaned_pdfs)} orphaned PDF files")

        # Find orphaned vector data (vector data exists but no PDF)
        orphaned_vectors = vector_doc_ids - pdf_doc_ids
        print(f"Found {len(orphaned_vectors)} orphaned vector store entries")

        cleanup_report = {
            "total_pdfs": len(pdf_doc_ids),
            "total_vectors": len(vector_doc_ids),
            "orphaned_pdfs": list(orphaned_pdfs),
            "orphaned_vectors": list(orphaned_vectors),
            "pdfs_deleted": 0,
            "vector_entries_deleted": 0
        }

        # Delete orphaned PDFs
        for doc_id in orphaned_pdfs:
            filename = f"{doc_id}.pdf"
            if pdf_processor.delete_pdf(filename):
                cleanup_report["pdfs_deleted"] += 1
                print(f"Deleted orphaned PDF: {filename}")

        # Delete orphaned vector data
        for doc_id in orphaned_vectors:
            chunks_deleted = vector_store.delete_by_document_id(doc_id)
            if chunks_deleted > 0:
                cleanup_report["vector_entries_deleted"] += 1
                print(f"Deleted orphaned vector data for: {doc_id} ({chunks_deleted} chunks)")

        return {
            "success": True,
            "message": f"Cleanup completed: deleted {cleanup_report['pdfs_deleted']} PDFs and {cleanup_report['vector_entries_deleted']} vector entries",
            **cleanup_report
        }

    except Exception as e:
        print(f"Error during cleanup: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.get("/_debug/vector-store")
async def debug_vector_store():
    """
    Debug endpoint to inspect vector store contents

    Returns:
        Sample of vector store data for debugging
    """
    try:
        # Get all data from vector store
        results = vector_store.collection.get()

        # Get first few items as sample
        sample_size = min(5, len(results["ids"]) if results["ids"] else 0)

        sample_data = {
            "total_items": len(results["ids"]) if results["ids"] else 0,
            "sample_ids": results["ids"][:sample_size] if results["ids"] else [],
            "sample_metadatas": results["metadatas"][:sample_size] if results["metadatas"] else [],
        }

        # Get unique document IDs
        doc_ids = set()
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                if "document_id" in metadata:
                    doc_ids.add(metadata["document_id"])

        sample_data["unique_document_ids"] = list(doc_ids)

        return {
            "success": True,
            **sample_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error debugging vector store: {str(e)}")


@router.get("/")
async def list_documents():
    """
    List all uploaded documents

    Returns:
        List of documents with metadata
    """
    try:
        # Get document IDs from vector store
        document_ids = vector_store.list_documents()

        # Get PDF file information
        pdf_files = pdf_processor.list_pdfs()

        # Combine information
        documents = []
        for pdf in pdf_files:
            doc_id = pdf["document_id"]

            # Get chunks for this document
            chunks = vector_store.get_document_chunks(doc_id)

            documents.append({
                "document_id": doc_id,
                "filename": pdf["filename"],
                "file_size": pdf["file_size"],
                "modified_time": pdf["modified_time"],
                "total_chunks": len(chunks)
            })

        return {
            "success": True,
            "total_documents": len(documents),
            "documents": documents
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get details of a specific document

    Args:
        document_id: Document ID

    Returns:
        Document details with all chunks
    """
    try:
        # Get chunks from vector store
        chunks = vector_store.get_document_chunks(document_id)

        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get PDF file info
        pdf_files = pdf_processor.list_pdfs()
        pdf_info = next((pdf for pdf in pdf_files if pdf["document_id"] == document_id), None)

        return {
            "success": True,
            "document_id": document_id,
            "file_info": pdf_info,
            "total_chunks": len(chunks),
            "chunks": chunks
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")


@router.post("/_reset/all")
async def reset_all_data():
    """
    Reset all data (vector store and PDF files)
    WARNING: This will delete ALL documents and embeddings!

    Returns:
        Reset status
    """
    try:
        print("Resetting all data...")

        # Reset vector store
        vector_store.reset()
        print("Vector store reset successfully")

        # Delete all PDF files
        deleted_count = 0
        pdf_files = pdf_processor.list_pdfs()
        for pdf in pdf_files:
            if pdf_processor.delete_pdf(pdf["filename"]):
                deleted_count += 1

        print(f"Deleted {deleted_count} PDF files")

        return {
            "success": True,
            "message": "All data reset successfully",
            "pdfs_deleted": deleted_count,
            "vector_store_reset": True
        }

    except Exception as e:
        print(f"Error resetting data: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error resetting data: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks

    Args:
        document_id: Document ID to delete

    Returns:
        Deletion status
    """
    try:
        print(f"Attempting to delete document: {document_id}")

        # Check PDF file exists
        filename = f"{document_id}.pdf"
        pdf_path = pdf_processor.storage_path / filename
        pdf_exists = pdf_path.exists()
        print(f"PDF file exists: {pdf_exists}")

        # Check vector store
        chunks = vector_store.get_document_chunks(document_id)
        print(f"Found {len(chunks)} chunks in vector store")

        # If neither exists, return 404
        if not pdf_exists and not chunks:
            print(f"Document not found anywhere: {document_id}")
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

        # Delete from vector store (if exists)
        chunks_deleted = 0
        if chunks:
            chunks_deleted = vector_store.delete_by_document_id(document_id)
            print(f"Deleted {chunks_deleted} chunks from vector store")
        else:
            print(f"No chunks to delete from vector store (orphaned PDF file)")

        # Delete PDF file (if exists)
        pdf_deleted = False
        if pdf_exists:
            pdf_deleted = pdf_processor.delete_pdf(filename)
            print(f"PDF file deletion status: {pdf_deleted}")
        else:
            print(f"PDF file not found: {filename} (orphaned vector store data)")

        return {
            "success": True,
            "message": "Document deleted successfully",
            "document_id": document_id,
            "chunks_deleted": chunks_deleted,
            "file_deleted": pdf_deleted,
            "was_orphaned": (pdf_exists and not chunks) or (not pdf_exists and chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting document {document_id}: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
