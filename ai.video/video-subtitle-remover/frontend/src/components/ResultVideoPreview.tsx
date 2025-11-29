import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Maximize2 } from 'lucide-react';
import { FileInfo } from '../types';
import { formatDuration } from '../utils';
import { VideoControls } from './VideoControls';

interface ResultVideoPreviewProps {
  file: FileInfo | null;
  isModalOpen?: boolean;
}

export const ResultVideoPreview: React.FC<ResultVideoPreviewProps> = ({
  file,
  isModalOpen = false,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 获取完整的视频URL - 与源视图相同的逻辑
  const getVideoUrl = (file: FileInfo) => {
    if (!file.url) return '';
    
    // 如果是blob URL，直接使用
    if (file.url.startsWith('blob:')) {
      return file.url;
    }
    
    // 如果是完整的URL（以http开头），直接返回
    if (file.url.startsWith('http://') || file.url.startsWith('https://')) {
      return file.url;
    }
    
    // 处理相对路径
    let normalizedPath = file.url.replace(/\\/g, '/');
    
    // 确保路径以/开头
    if (!normalizedPath.startsWith('/')) {
      normalizedPath = '/' + normalizedPath;
    }
    
    // 根据路径类型构建完整URL
    if (normalizedPath.startsWith('/uploads/')) {
      return `http://localhost:8000${normalizedPath}`;
    } else if (normalizedPath.startsWith('/outputs/')) {
      return `http://localhost:8000${normalizedPath}`;
    } else if (normalizedPath.startsWith('/')) {
      // 其他根路径，也尝试直接访问
      return `http://localhost:8000${normalizedPath}`;
    }
    
    // 默认情况下，构建uploads URL
    return `http://localhost:8000/uploads/${normalizedPath}`;
  };

  // 处理视频元数据加载
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  // 处理时间更新
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  // 播放控制
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(error => {
          console.error('视频播放失败:', error);
        });
      }
      setIsPlaying(!isPlaying);
    }
  };

  // 跳转
  const skip = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(0, Math.min(duration, currentTime + seconds));
    }
  };

  // 全屏切换
  const toggleFullscreen = () => {
    if (!containerRef.current) return;

    if (!isFullscreen) {
      containerRef.current.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
    setIsFullscreen(!isFullscreen);
  };

  // 音量控制
  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  // 处理视频加载错误
  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    console.error('结果视频加载错误:', e);
    const video = e.currentTarget;
    console.error('视频元素错误码:', video.error?.code);
    console.error('视频元素错误信息:', video.error?.message);
    console.error('视频源URL:', video.src);
    
    // 如果是404错误，尝试添加下载链接
    if (video.error?.code === 4) {
      console.log('检测到404错误，可能是路径问题');
      console.log('原始file.url:', file?.url);
      console.log('处理后URL:', getVideoUrl(file!));
    }
  };

  if (!file) {
    return (
      <div className="card">
        <div className="card-body">
          <div className="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">
              请选择要预览的结果文件
            </p>
          </div>
        </div>
      </div>
    );
  }

  const videoUrl = getVideoUrl(file);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="font-semibold text-gray-900 dark:text-dark-text">
          结果预览
        </h3>
        <div className="flex items-center space-x-2">
          <span className="badge badge-success">处理完成</span>
          {file.status === 'processing' && (
            <span className="badge badge-warning">处理中 {file.progress}%</span>
          )}
          {file.status === 'error' && (
            <span className="badge badge-danger">处理失败</span>
          )}
        </div>
      </div>
      
      <div className="card-body space-y-4">
        {/* 视频预览区域 - 结果视图不需要字幕选择器 */}
        <div
          ref={containerRef}
          className="video-preview aspect-video relative"
        >
          <video
            ref={videoRef}
            src={videoUrl}
            className="w-full h-full"
            onLoadedMetadata={handleLoadedMetadata}
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onError={handleVideoError}
            // 添加跨域属性，以防后端需要
            crossOrigin="anonymous"
            // 添加一些额外的属性来帮助调试
            controls={false}
            preload="metadata"
          />
        </div>

        {/* 视频控制栏 */}
        <VideoControls
          isPlaying={isPlaying}
          currentTime={currentTime}
          duration={duration}
          volume={volume}
          onTogglePlay={togglePlay}
          onSkip={skip}
          onSeek={(percent) => {
            if (videoRef.current) {
              videoRef.current.currentTime = duration * percent;
            }
          }}
          onToggleFullscreen={toggleFullscreen}
          onVolumeChange={handleVolumeChange}
        />

        {/* 调试信息 */}
        {true && (
          <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs">
            <p className="font-medium text-gray-700 dark:text-gray-300 mb-2">调试信息:</p>
            <div className="space-y-1 text-gray-600 dark:text-gray-400">
              <div>原始URL: {file.url}</div>
              <div>处理后URL: {videoUrl}</div>
              <div>文件状态: {file.status}</div>
              {file.progress !== undefined && <div>进度: {file.progress}%</div>}
              <div>Modal状态: {isModalOpen ? '打开' : '关闭'}</div>
              <div>视图类型: 结果预览（无字幕选择）</div>
              <div>当前音量: {Math.round(volume * 100)}%</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
