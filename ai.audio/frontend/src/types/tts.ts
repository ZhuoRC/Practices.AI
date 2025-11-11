export interface VoiceInfo {
  voice_id: string;
  name: string;
  language: string;
  gender?: string;
  description?: string;
  sample_rate?: number;
  is_neural: boolean;
}

export interface TTSRequest {
  text: string;
  provider: string;
  voice_id: string;
  speed: number;
  pitch: number;
  volume: number;
  output_format: 'mp3' | 'wav' | 'ogg' | 'flac';
  sample_rate?: number;
}

export interface TTSResponse {
  audio_id: string;
  duration: number;
  file_size: number;
  format: string;
  provider_used: string;
  voice_used: string;
  sample_rate: number;
  metadata?: Record<string, any>;
  download_url: string;
}

export interface ProviderInfo {
  name: string;
  description: string;
  capabilities: string[];
  max_text_length: number;
  supported_formats: string[];
  is_configured: boolean;
}

export interface ProviderVoicesResponse {
  provider: string;
  voices: VoiceInfo[];
}

export interface HealthResponse {
  status: string;
  available_providers: string[];
  total_providers: number;
}
