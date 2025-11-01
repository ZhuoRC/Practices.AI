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
  upload_time: string;  // Format: yyyy-mm-dd (for display)
  upload_time_iso: string;  // ISO timestamp (for sorting)
  total_chunks: number;
}

export interface QueryResponse {
  success: boolean;
  question: string;
  reformulated_question: string;
  answer: string;
  retrieved_chunks: number;
  time_consumed: number;  // Time in seconds
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  reformulation_tokens: number;
  reformulation_prompt_tokens: number;
  reformulation_completion_tokens: number;
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
  task_id: string;
  filename: string;
}

export interface TaskStatus {
  task_id: string;
  task_type: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
  result?: {
    document_id: string;
    original_filename: string;
    total_chunks: number;
    file_size: number;
  };
  error?: string;
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

  // Get task status
  getTaskStatus: async (taskId: string): Promise<TaskStatus> => {
    const response = await api.get(`/api/documents/tasks/${taskId}`);
    return response.data;
  },

  // List all tasks
  listTasks: async (): Promise<TaskStatus[]> => {
    const response = await api.get('/api/documents/tasks');
    return response.data.tasks;
  },

  // Delete task
  deleteTask: async (taskId: string): Promise<void> => {
    await api.delete(`/api/documents/tasks/${taskId}`);
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
