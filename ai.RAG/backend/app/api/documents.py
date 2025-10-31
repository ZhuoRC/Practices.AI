from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
import asyncio
from ..services.pdf_processor import pdf_processor
from ..services.embeddings import embedding_service
from ..services.vector_store import vector_store

router = APIRouter(prefix="/api/documents", tags=["documents"])


# Response Models
class UploadDocumentResponse(BaseModel):
    """Response model for document upload"""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Success or error message")
    document_id: str = Field(..., description="Unique document identifier")
    original_filename: str = Field(..., description="Original filename of the uploaded PDF")
    total_chunks: int = Field(..., description="Number of text chunks created from the document")
    file_size: int = Field(..., description="File size in bytes")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Document uploaded and processed successfully",
                "document_id": "doc_20240101_120000_abc123",
                "original_filename": "sample.pdf",
                "total_chunks": 15,
                "file_size": 245678
            }
        }


class DocumentInfo(BaseModel):
    """Document information model"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    upload_time: str = Field(..., description="Upload timestamp (YYYY-MM-DD)")
    total_chunks: int = Field(..., description="Number of text chunks")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_20240101_120000_abc123",
                "filename": "sample.pdf",
                "file_size": 245678,
                "upload_time": "2024-01-01",
                "total_chunks": 15
            }
        }


class ListDocumentsResponse(BaseModel):
    """Response model for listing documents"""
    success: bool = Field(True, description="Whether the operation was successful")
    total_documents: int = Field(..., description="Total number of documents")
    documents: List[DocumentInfo] = Field(..., description="List of documents")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_documents": 2,
                "documents": [
                    {
                        "document_id": "doc_20240101_120000_abc123",
                        "filename": "sample.pdf",
                        "file_size": 245678,
                        "upload_time": "2024-01-01",
                        "total_chunks": 15
                    }
                ]
            }
        }


class DeleteDocumentResponse(BaseModel):
    """Response model for document deletion"""
    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Success or error message")
    document_id: str = Field(..., description="ID of the deleted document")
    chunks_deleted: int = Field(..., description="Number of chunks deleted from vector store")
    file_deleted: bool = Field(..., description="Whether the PDF file was deleted")
    was_orphaned: bool = Field(..., description="Whether the document had missing data (PDF or vectors)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Document deleted successfully",
                "document_id": "doc_20240101_120000_abc123",
                "chunks_deleted": 15,
                "file_deleted": True,
                "was_orphaned": False
            }
        }


@router.post("/upload", response_model=UploadDocumentResponse, summary="Upload PDF Document")
async def upload_document(file: UploadFile = File(..., description="PDF file to upload and process")):
    """
    Upload a PDF document and process it for RAG.

    The document will be:
    1. Validated as a PDF file
    2. Saved to the storage directory
    3. Split into text chunks
    4. Converted to embeddings
    5. Stored in the vector database for similarity search

    **Note**: Only PDF files are supported.
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

        # Generate embeddings for all chunks (run in thread pool to avoid blocking)
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = await asyncio.to_thread(embedding_service.embed_texts, chunk_texts)

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


@router.get("/", response_model=ListDocumentsResponse, summary="List All Documents")
async def list_documents():
    """
    Get a list of all uploaded documents with their metadata.

    Returns information including:
    - Document ID
    - Original filename
    - File size
    - Upload timestamp
    - Number of text chunks
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
                "filename": pdf["filename"],  # Original filename
                "file_size": pdf["file_size"],
                "upload_time": pdf.get("upload_time", ""),  # Formatted as yyyy-mm-dd
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


@router.delete("/{document_id}", response_model=DeleteDocumentResponse, summary="Delete Document")
async def delete_document(document_id: str):
    """
    Delete a document and all its associated data.

    This will:
    1. Remove all text chunks from the vector database
    2. Delete the PDF file from storage
    3. Remove all metadata

    **Parameters**:
    - **document_id**: Unique identifier of the document to delete

    **Note**: This operation cannot be undone.
    """
    try:
        print(f"Attempting to delete document: {document_id}")

        # Check if document exists in metadata or as legacy file
        pdf_exists = False
        if document_id in pdf_processor.metadata:
            stored_filename = pdf_processor.metadata[document_id]["stored_filename"]
            pdf_path = pdf_processor.storage_path / stored_filename
            pdf_exists = pdf_path.exists()
        else:
            # Try legacy format
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
            pdf_deleted = pdf_processor.delete_pdf(document_id)  # Pass document_id instead of filename
            print(f"PDF file deletion status: {pdf_deleted}")
        else:
            print(f"PDF file not found for document: {document_id} (orphaned vector store data)")

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
