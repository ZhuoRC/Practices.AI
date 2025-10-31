import axios from 'axios';

export const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Document {
  document_id: string;
  filename: string;
  file_size: number;
  upload_time: string;  // Format: yyyy-mm-dd
  total_chunks: number;
}

export interface QueryResponse {
  success: boolean;
  question: string;
  answer: string;
  retrieved_chunks: number;
  time_consumed: number;  // Time in seconds
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  sources?: Array<{
    chunk_index: number;
    text: string;
    metadata: any;
    similarity_score: number;
  }>;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  document_id: string;
  original_filename: string;
  total_chunks: number;
  file_size: number;
}

export const documentAPI = {
  // Upload PDF document
  uploadDocument: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // List all documents
  listDocuments: async (): Promise<Document[]> => {
    const response = await api.get('/api/documents/');
    return response.data.documents;
  },

  // Delete document
  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/api/documents/${documentId}`);
  },
};

export const queryAPI = {
  // Query RAG system
  query: async (
    question: string,
    includeSources: boolean = true,
    documentIds?: string[]
  ): Promise<QueryResponse> => {
    const response = await api.post('/api/query', {
      question,
      include_sources: includeSources,
      document_ids: documentIds && documentIds.length > 0 ? documentIds : undefined,
    });

    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;
