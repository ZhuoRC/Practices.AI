// API服务配置
const API_BASE_URL = 'http://localhost:8000';

export interface UploadResponse {
  file_id: string;
  filename: string;
  file_path: string;
  size: number;
}

export interface ProcessRequest {
  filePath: string;
  algorithm: string;
  detectionMode: string;
  subtitleArea?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  sttnParams?: any;
  propainterParams?: any;
  lamaParams?: any;
  commonParams?: any;
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

export interface UploadedFile {
  id: string;
  name: string;
  url: string;
  size: number;
  created_at: string;
}

export interface OutputFile {
  id: string;
  name: string;
  url: string;
  size: number;
  created_at: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();
      
      // 监听上传进度
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            onProgress(progress);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('解析响应失败'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || '文件上传失败'));
          } catch {
            reject(new Error(`上传失败: ${xhr.statusText}`));
          }
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('网络错误，上传失败'));
      });

      xhr.addEventListener('timeout', () => {
        reject(new Error('上传超时'));
      });

      xhr.open('POST', `${this.baseUrl}/upload`);
      xhr.timeout = 300000; // 5分钟超时
      xhr.send(formData);
    });
  }

  async startProcessing(request: ProcessRequest): Promise<TaskResponse> {
    console.log('Sending request:', request);
    
    const response = await fetch(`${this.baseUrl}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);

    if (!response.ok) {
      let errorMessage = '处理请求失败';
      try {
        const error = await response.json();
        console.log('Error response:', error);
        
        // 处理FastAPI的验证错误
        if (error.detail && Array.isArray(error.detail)) {
          errorMessage = error.detail.map((err: any) => {
            return `${err.loc ? err.loc.join('.') + ': ' : ''}${err.msg}`;
          }).join('; ');
        } else if (error.detail) {
          errorMessage = typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail);
        } else {
          errorMessage = JSON.stringify(error) || '处理请求失败';
        }
      } catch (e) {
        console.log('Failed to parse error:', e);
        const errorText = await response.text();
        errorMessage = errorText || '处理请求失败';
      }
      throw new Error(errorMessage);
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

  async getUploadedFiles(): Promise<UploadedFile[]> {
    const response = await fetch(`${this.baseUrl}/files`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '获取文件列表失败');
    }

    return response.json();
  }

  async getOutputFiles(): Promise<OutputFile[]> {
    const response = await fetch(`${this.baseUrl}/outputs`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '获取输出文件列表失败');
    }

    return response.json();
  }

  async deleteFile(fileId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/files/${fileId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '删除文件失败');
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
