"""
Simple API test script
Run this after starting the backend to verify everything works
"""
import requests
import sys

BASE_URL = "http://localhost:8001"


def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Health check passed: {data.get('status')}")
        print(f"  - Vector store chunks: {data.get('vector_store', {}).get('total_chunks', 0)}")
        print(f"  - Vector store documents: {data.get('vector_store', {}).get('total_documents', 0)}")
        print(f"  - Qwen API: {data.get('qwen_api')}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_list_documents():
    """Test list documents endpoint"""
    print("\nTesting /api/documents/...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents/")
        response.raise_for_status()
        data = response.json()
        print(f"✓ List documents passed")
        print(f"  - Total documents: {data.get('total_documents', 0)}")
        return True
    except Exception as e:
        print(f"✗ List documents failed: {e}")
        return False


def test_upload_document(file_path):
    """Test document upload"""
    print(f"\nTesting /api/documents/upload with {file_path}...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
            response.raise_for_status()
            data = response.json()
            print(f"✓ Upload passed")
            print(f"  - Document ID: {data.get('document_id')}")
            print(f"  - Total chunks: {data.get('total_chunks')}")
            return data.get('document_id')
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return None


def test_query(question):
    """Test query endpoint"""
    print(f"\nTesting /api/query with question: '{question}'...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"question": question, "include_sources": True}
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ Query passed")
        print(f"  - Answer: {data.get('answer')[:100]}...")
        print(f"  - Retrieved chunks: {data.get('retrieved_chunks')}")
        if data.get('sources'):
            print(f"  - Sources: {len(data.get('sources'))} chunks")
        return True
    except Exception as e:
        print(f"✗ Query failed: {e}")
        return False


def main():
    print("=" * 60)
    print("RAG System API Test")
    print("=" * 60)

    # Test health
    if not test_health():
        print("\n⚠ Backend may not be running properly")
        sys.exit(1)

    # Test list documents
    test_list_documents()

    # Test upload (optional - provide a PDF file path)
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        doc_id = test_upload_document(pdf_path)

        if doc_id:
            # Test query if we uploaded a document
            test_query("What is the main content of this document?")

    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
