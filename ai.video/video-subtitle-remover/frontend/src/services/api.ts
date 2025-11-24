// API服务配置
const API_BASE_URL = 'http://localhost:8000';

export interface UploadResponse {
  file_id: string;
  filename: string;
  file_path: string;
  size: number;
}

export interface ProcessRequest {
  file_path: string;
  algorithm: string;
  detection_mode: string;
  subtitle_area?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  sttn_params?: any;
  propainter_params?: any;
  lama_params?: any;
  common_params?: any;
}

export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result_url?: string;
  error?: string;
}

export interface TaskListResponse {
  tasks: Array<{
    task_id: string;
    status: string;
    progress: number;
    created_at: string;
  }>;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '文件上传失败');
    }

    return response.json();
  }

  async startProcessing(request: ProcessRequest): Promise<TaskResponse> {
    const response = await fetch(`${this.baseUrl}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '处理请求失败');
    }

    return response.json();
  }

  async getTaskStatus(taskId: string): Promise<TaskResponse> {
    const response = await fetch(`${this.baseUrl}/tasks/${taskId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '获取任务状态失败');
    }

    return response.json();
  }

  async listTasks(): Promise<TaskListResponse> {
    const response = await fetch(`${this.baseUrl}/tasks`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '获取任务列表失败');
    }

    return response.json();
  }

  async deleteTask(taskId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/tasks/${taskId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '删除任务失败');
    }

    return response.json();
  }

  getDownloadUrl(taskId: string): string {
    return `${this.baseUrl}/download/${taskId}`;
  }

  async checkApiHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();
