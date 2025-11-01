from typing import List, Dict, Optional
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings

# Disable ChromaDB telemetry to avoid errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"


class VectorStore:
    """ChromaDB vector store for document embeddings"""

    def __init__(self):
        """Initialize ChromaDB client and collection"""
        persist_dir = str(settings.get_chroma_persist_directory())

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "RAG document chunks"}
        )

        print(f"ChromaDB initialized. Collection: {settings.chroma_collection_name}")
        print(f"Total documents in collection: {self.collection.count()}")

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store

        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of unique IDs for each document
        """
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to vector store")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        document_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            document_ids: Optional list of document IDs to filter results

        Returns:
            Search results with documents, distances, and metadata
        """
        if top_k is None:
            top_k = settings.top_k

        # Get total chunks count
        total_chunks_in_db = self.collection.count()

        # Build where clause for filtering by document_ids
        where_clause = None
        if document_ids:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}

            # Count filtered chunks
            try:
                filtered_results = self.collection.get(where=where_clause)
                filtered_count = len(filtered_results["ids"]) if filtered_results["ids"] else 0
                print(f"[VectorSearch] Filter: {len(document_ids)} docs | {filtered_count}/{total_chunks_in_db} chunks | top_k={top_k}")
            except Exception as e:
                print(f"[VectorSearch] Filter: {len(document_ids)} docs | top_k={top_k}")
        else:
            print(f"[VectorSearch] No filter | {total_chunks_in_db} chunks | top_k={top_k}")

        # IMPORTANT: ChromaDB applies the where filter BEFORE similarity search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )

        # Log results
        results_count = len(results["ids"][0]) if results["ids"] else 0
        if results_count > 0:
            print(f"[VectorSearch] Found {results_count} chunks | Top similarity: {1 - results['distances'][0][0]:.4f}")
        else:
            print(f"[VectorSearch] No results found")

        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }

    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all chunks belonging to a document

        Args:
            document_id: Document ID to delete

        Returns:
            Number of chunks deleted
        """
        try:
            # Query for all chunks with this document_id
            print(f"Querying ChromaDB for document_id: {document_id}")
            results = self.collection.get(
                where={"document_id": document_id}
            )

            print(f"Query results: found {len(results['ids']) if results['ids'] else 0} chunks")

            if results["ids"]:
                print(f"Deleting chunk IDs: {results['ids'][:5]}...")  # Show first 5
                self.collection.delete(ids=results["ids"])
                print(f"Successfully deleted {len(results['ids'])} chunks for document {document_id}")
                return len(results["ids"])
            else:
                print(f"No chunks found for document {document_id}")
                return 0

        except Exception as e:
            print(f"Error in delete_by_document_id: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def get_document_chunks(self, document_id: str) -> List[Dict]:
        """
        Get all chunks for a specific document

        Args:
            document_id: Document ID

        Returns:
            List of chunks with metadata
        """
        try:
            print(f"Getting chunks for document_id: {document_id}")
            results = self.collection.get(
                where={"document_id": document_id}
            )

            print(f"Get results: found {len(results['ids']) if results['ids'] else 0} chunks")

            chunks = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    chunks.append({
                        "id": results["ids"][i],
                        "text": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    })
                print(f"Returning {len(chunks)} chunks")
            else:
                print(f"No chunks found for document {document_id}")

            return chunks

        except Exception as e:
            print(f"Error in get_document_chunks: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def list_documents(self) -> List[str]:
        """
        List all unique document IDs in the collection

        Returns:
            List of document IDs
        """
        # Get all documents
        results = self.collection.get()

        # Extract unique document IDs from metadata
        document_ids = set()
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                if "document_id" in metadata:
                    document_ids.add(metadata["document_id"])

        return list(document_ids)

    def count(self) -> int:
        """Get total number of chunks in collection"""
        return self.collection.count()

    def reset(self) -> None:
        """Reset the collection (delete all data)"""
        self.client.delete_collection(name=settings.chroma_collection_name)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "RAG document chunks"}
        )
        print("Collection reset successfully")


# Global instance
vector_store = VectorStore()
