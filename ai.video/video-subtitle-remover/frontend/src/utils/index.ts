import { clsx, type ClassValue } from 'clsx';

// 合并 className
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// 格式化文件大小
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化时长
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// 格式化比特率
export function formatBitrate(bitsPerSecond: number): string {
  const kbps = bitsPerSecond / 1000;
  const mbps = kbps / 1000;
  
  if (mbps >= 1) {
    return `${mbps.toFixed(1)} Mbps`;
  }
  return `${kbps.toFixed(0)} kbps`;
}

// 生成唯一 ID
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// 检查文件类型
export function isVideoFile(file: File): boolean {
  const videoTypes = ['video/mp4', 'video/avi', 'video/flv', 'video/wmv', 'video/mov', 'video/mkv'];
  return videoTypes.includes(file.type) || file.name.match(/\.(mp4|avi|flv|wmv|mov|mkv)$/i) !== null;
}

export function isImageFile(file: File): boolean {
  const imageTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/bmp', 'image/tiff'];
  return imageTypes.includes(file.type) || file.name.match(/\.(jpg|jpeg|png|bmp|tiff)$/i) !== null;
}

// 获取文件扩展名
export function getFileExtension(filename: string): string {
  return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
}

// 验证文件格式
export function validateFileFormat(file: File): { valid: boolean; error?: string } {
  const supportedFormats = ['mp4', 'avi', 'flv', 'wmv', 'mov', 'mkv', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'];
  const extension = getFileExtension(file.name).toLowerCase();
  
  if (!supportedFormats.includes(extension)) {
    return {
      valid: false,
      error: `不支持的文件格式: ${extension}。支持的格式: ${supportedFormats.join(', ')}`
    };
  }
  
  return { valid: true };
}

// 验证文件大小
export function validateFileSize(file: File, maxSize: number = 2 * 1024 * 1024 * 1024): { valid: boolean; error?: string } {
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `文件大小超出限制。最大允许: ${formatFileSize(maxSize)}，当前文件: ${formatFileSize(file.size)}`
    };
  }
  
  return { valid: true };
}

// 创建视频缩略图
export function createVideoThumbnail(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      reject(new Error('无法创建 canvas 上下文'));
      return;
    }
    
    video.preload = 'metadata';
    video.src = URL.createObjectURL(file);
    
    video.onloadedmetadata = () => {
      // 设置画布尺寸
      canvas.width = 320;
      canvas.height = (320 / video.videoWidth) * video.videoHeight;
      
      // 跳转到第 2 秒或视频的 10% 位置
      video.currentTime = Math.min(2, video.duration * 0.1);
    };
    
    video.onseeked = () => {
      // 绘制视频帧到画布
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // 转换为 blob URL
      canvas.toBlob((blob) => {
        if (blob) {
          const thumbnailUrl = URL.createObjectURL(blob);
          resolve(thumbnailUrl);
        } else {
          reject(new Error('无法生成缩略图'));
        }
        URL.revokeObjectURL(video.src);
      }, 'image/jpeg', 0.8);
    };
    
    video.onerror = () => {
      reject(new Error('视频加载失败'));
      URL.revokeObjectURL(video.src);
    };
  });
}

// 创建图片缩略图
export function createImageThumbnail(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      reject(new Error('无法创建 canvas 上下文'));
      return;
    }
    
    img.onload = () => {
      // 计算缩略图尺寸
      const maxSize = 320;
      let width = img.width;
      let height = img.height;
      
      if (width > height) {
        if (width > maxSize) {
          height = (maxSize / width) * height;
          width = maxSize;
        }
      } else {
        if (height > maxSize) {
          width = (maxSize / height) * width;
          height = maxSize;
        }
      }
      
      canvas.width = width;
      canvas.height = height;
      
      // 绘制图片
      ctx.drawImage(img, 0, 0, width, height);
      
      // 转换为 blob URL
      canvas.toBlob((blob) => {
        if (blob) {
          const thumbnailUrl = URL.createObjectURL(blob);
          resolve(thumbnailUrl);
        } else {
          reject(new Error('无法生成缩略图'));
        }
      }, 'image/jpeg', 0.8);
    };
    
    img.onerror = () => {
      reject(new Error('图片加载失败'));
    };
    
    img.src = URL.createObjectURL(file);
  });
}

// 下载文件
export function downloadFile(url: string, filename: string): void {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// 复制到剪贴板
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // 降级方案
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const result = document.execCommand('copy');
      document.body.removeChild(textArea);
      return result;
    }
  } catch (error) {
    console.error('复制失败:', error);
    return false;
  }
}

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
