import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import {
  TTSRequest,
  TTSResponse,
  ProviderInfo,
  ProviderVoicesResponse,
  HealthResponse,
  VoiceInfo
} from '../types/tts';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

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
  (error: any) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    console.error('API Error:', error);

    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      switch (status) {
        case 400:
          throw new Error((data as any)?.detail || '请求参数错误');
        case 404:
          throw new Error((data as any)?.detail || '资源未找到');
        case 500:
          throw new Error((data as any)?.detail || '服务器内部错误');
        case 503:
          throw new Error((data as any)?.detail || '服务暂时不可用');
        default:
          throw new Error((data as any)?.detail || `请求失败 (${status})`);
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

export const ttsApi = {
  // Health check
  async healthCheck(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },

  // Get available providers
  async getProviders(): Promise<string[]> {
    const response = await api.get<string[]>('/providers');
    return response.data;
  },

  // Get provider information
  async getProviderInfo(provider: string): Promise<ProviderInfo> {
    const response = await api.get<ProviderInfo>(`/providers/${provider}/info`);
    return response.data;
  },

  // Get voices for a provider
  async getProviderVoices(provider: string): Promise<ProviderVoicesResponse> {
    const response = await api.get<ProviderVoicesResponse>(`/providers/${provider}/voices`);
    return response.data;
  },

  // Generate speech
  async generateSpeech(request: TTSRequest): Promise<TTSResponse> {
    const response = await api.post<TTSResponse>('/generate', request);
    return response.data;
  },

  // Get audio file
  async getAudio(audioId: string): Promise<Blob> {
    const response = await api.get(`/audio/${audioId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get voice preview
  async getVoicePreview(provider: string, voiceId: string): Promise<Blob> {
    const response = await api.get(`/voices/${provider}/${voiceId}/preview`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get download URL for audio
  getAudioDownloadUrl(audioId: string): string {
    return `${API_BASE_URL}/audio/${audioId}`;
  },

  // Get voice preview URL
  getVoicePreviewUrl(provider: string, voiceId: string): string {
    return `${API_BASE_URL}/voices/${provider}/${voiceId}/preview`;
  }
};

export default api;
