import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for long texts
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);

    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      switch (status) {
        case 400:
          throw new Error(data.detail || '请求参数错误');
        case 500:
          throw new Error(data.detail || '服务器内部错误');
        case 503:
          throw new Error(data.detail || '服务暂时不可用');
        default:
          throw new Error(data.detail || `请求失败 (${status})`);
      }
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('无法连接到服务器，请检查后端服务是否运行');
    } else {
      // Something else happened
      throw new Error('请求失败，请稍后重试');
    }
  }
);

export interface RewriteRequest {
  source_text: string;
  requirements: string;
  mode: string;
  segment_size?: number;
}

export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface RewriteResponse {
  rewritten_text: string;
  mode_used: string;
  segments_processed: number;
  token_usage?: TokenUsage;
}

export const rewriteText = async (request: RewriteRequest): Promise<RewriteResponse> => {
  try {
    const response = await api.post<RewriteResponse>('/rewrite', request);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;