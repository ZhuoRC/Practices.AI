// 文件类型
export interface FileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  file?: File;
  thumbnail?: string;
  duration?: number;
  width?: number;
  height?: number;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
  resultUrl?: string;
  isOutput?: boolean; // 标记是否为output文件
}

// 字幕区域配置
export interface SubtitleArea {
  id: string;  // 新增：唯一标识符
  x: number;
  y: number;
  width: number;
  height: number;
  name?: string;  // 新增：可选的名称
  color?: string;  // 新增：可选的颜色
}

// 处理配置
export interface ProcessConfig {
  // 修复算法
  algorithm: 'sttn' | 'lama' | 'propainter';
  
  // 字幕检测模式
  detectionMode: 'auto' | 'manual';
  
  // 手动字幕区域 - 修改为支持多个区域
  subtitleAreas?: SubtitleArea[];  // 修改：从单个区域改为区域数组
  
  // STTN 算法参数
  sttnParams?: {
    skipDetection: boolean;
    neighborStride: number;
    referenceLength: number;
    maxLoadNum: number;
  };
  
  // ProPainter 算法参数
  propainterParams?: {
    maxLoadNum: number;
  };
  
  // LAMA 算法参数
  lamaParams?: {
    superFast: boolean;
  };
  
  // 通用参数
  commonParams?: {
    useH264: boolean;
    thresholdHeightWidthDifference: number;
    subtitleAreaDeviationPixel: number;
    thresholdHeightDifference: number;
    pixelToleranceY: number;
    pixelToleranceX: number;
  };
}

// 处理任务状态
export interface TaskStatus {
  id: string;
  fileId: string;
  status: 'pending' | 'processing' | 'completed' | 'error' | 'paused';
  progress: number;
  currentFrame?: number;
  totalFrames?: number;
  speed?: number;
  estimatedTime?: number;
  error?: string;
  startTime?: Date;
  endTime?: Date;
}

// WebSocket 消息类型
export interface WebSocketMessage {
  type: 'progress' | 'status' | 'error' | 'completed';
  data: any;
  taskId: string;
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 系统信息
export interface SystemInfo {
  version: string;
  gpuAvailable: boolean;
  gpuType?: string;
  maxConcurrentTasks: number;
  supportedFormats: string[];
}

// 预设配置
export interface PresetConfig {
  id: string;
  name: string;
  description: string;
  config: ProcessConfig;
  recommended: boolean;
}

// 主题配置
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto';
  primaryColor: string;
}
