import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Play, Pause, SkipBack, SkipForward, Maximize2, Settings } from 'lucide-react';
import { FileInfo, ProcessConfig, SubtitleArea } from '../types';
import { formatDuration } from '../utils';
import { VideoControls } from './VideoControls';
import { SubtitleSelector } from './SubtitleSelector';

interface VideoPreviewProps {
  file: FileInfo | null;
  config: ProcessConfig;
  onConfigChange: (config: ProcessConfig) => void;
  isModalOpen?: boolean; // modal状态
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({
  file,
  config,
  onConfigChange,
  isModalOpen = false, // 默认为false
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [subtitleAreas, setSubtitleAreas] = useState<SubtitleArea[]>(
    config.subtitleAreas || []
  );
  const [showSubtitlePanel, setShowSubtitlePanel] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const onConfigChangeRef = useRef(onConfigChange);
  
  // 更新ref以避免useEffect依赖问题
  useEffect(() => {
    onConfigChangeRef.current = onConfigChange;
  }, [onConfigChange]);

  // 当检测模式改变时，初始化字幕区域
  useEffect(() => {
    if (config.detectionMode === 'manual' && subtitleAreas.length === 0) {
      if (videoRef.current) {
        const video = videoRef.current;
        const defaultArea: SubtitleArea = {
          id: `area-${Date.now()}`,
          x: Math.round(video.videoWidth * 0.05),
          y: Math.round(video.videoHeight * 0.78),
          width: Math.round(video.videoWidth * 0.9),
          height: Math.round(video.videoHeight * 0.21),
          name: '字幕区域 1',
          color: '#22c55e',
        };
        setSubtitleAreas([defaultArea]);
      }
    } else if (config.detectionMode === 'auto') {
      setSubtitleAreas([]);
    }
  }, [config.detectionMode, subtitleAreas.length]);

  // 更新配置中的字幕区域 - 使用useCallback避免无限循环
  const updateConfigWithSubtitleAreas = useCallback(() => {
    if (config.detectionMode === 'manual') {
      onConfigChangeRef.current({
        ...config,
        subtitleAreas,
        detectionMode: 'manual',
      });
    }
  }, [subtitleAreas, config.detectionMode, config.subtitleAreas]);

  useEffect(() => {
    updateConfigWithSubtitleAreas();
  }, [updateConfigWithSubtitleAreas]);

  // 获取完整的视频URL - 修复URL路径问题
  const getVideoUrl = (file: FileInfo | null) => {
    if (!file?.url) return '';
    
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
      
      if (config.detectionMode === 'manual' && subtitleAreas.length === 0) {
        const video = videoRef.current;
        const defaultArea: SubtitleArea = {
          id: `area-${Date.now()}`,
          x: Math.round(video.videoWidth * 0.05),
          y: Math.round(video.videoHeight * 0.78),
          width: Math.round(video.videoWidth * 0.9),
          height: Math.round(video.videoHeight * 0.21),
          name: '字幕区域 1',
          color: '#22c55e',
        };
        setSubtitleAreas([defaultArea]);
      }
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

  // 处理字幕区域变化
  const handleSubtitleAreasChange = (areas: SubtitleArea[]) => {
    setSubtitleAreas(areas);
  };

  // 处理视频加载错误
  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    console.error('视频加载错误:', e);
    const video = e.currentTarget;
    console.error('视频元素错误码:', video.error?.code);
    console.error('视频元素错误信息:', video.error?.message);
    console.error('视频源URL:', video.src);
    
    // 如果是404错误，尝试添加下载链接
    if (video.error?.code === 4) {
      console.log('检测到404错误，可能是路径问题');
      console.log('原始file.url:', file?.url);
      console.log('处理后URL:', getVideoUrl(file));
    }
  };

  if (!file) {
    return (
      <div className="card">
        <div className="card-body">
          <div className="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">
              请选择要预览的文件
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
          视频预览
        </h3>
        <div className="flex items-center space-x-2">
          <span className={`badge ${config.detectionMode === 'auto' ? 'badge-primary' : 'badge-secondary'}`}>
            {config.detectionMode === 'auto' ? '自动检测' : '手动选择'}
          </span>
          {file.status === 'processing' && (
            <span className="badge badge-warning">上传中 {file.progress}%</span>
          )}
          {file.status === 'error' && (
            <span className="badge badge-danger">上传失败</span>
          )}
        </div>
      </div>
      
      <div className="card-body">
        {/* 字幕控制按钮和模式选择 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            {/* 模式选择 */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                字幕检测模式
              </label>
              <select
                value={config.detectionMode}
                onChange={(e) => onConfigChange({
                  ...config,
                  detectionMode: e.target.value as 'auto' | 'manual',
                })}
                className="select"
              >
                <option value="auto">自动检测</option>
                <option value="manual">手动选择</option>
              </select>
            </div>

            {/* 字幕控制面板开关 */}
            {config.detectionMode === 'manual' && (
              <button
                onClick={() => setShowSubtitlePanel(!showSubtitlePanel)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  showSubtitlePanel
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span>字幕区域管理</span>
                {subtitleAreas.length > 0 && (
                  <span className="ml-1 px-2 py-1 bg-blue-500 text-white text-xs rounded-full">
                    {subtitleAreas.length}
                  </span>
                )}
              </button>
            )}
          </div>
        </div>

        {/* 视频预览区域 - 独立容器，不会被字幕控制面板遮挡 */}
        <div className="relative">
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

            {/* 简化的字幕区域显示 - 只在视频内显示边界框 */}
            {config.detectionMode === 'manual' && !isModalOpen && subtitleAreas.map((area) => (
              <div
                key={area.id}
                className="absolute border-2 border-dashed border-blue-500 bg-blue-100 bg-opacity-20"
                style={{
                  left: `${area.x}px`,
                  top: `${area.y}px`,
                  width: `${area.width}px`,
                  height: `${area.height}px`,
                  backgroundColor: area.color ? `${area.color}20` : undefined,
                  borderColor: area.color || '#22c55e',
                }}
              />
            ))}
          </div>
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

        {/* 字幕区域控制面板 - 独立区域，不遮挡视频 */}
        {showSubtitlePanel && config.detectionMode === 'manual' && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <SubtitleSelector
              videoRef={videoRef}
              config={config}
              subtitleAreas={subtitleAreas}
              onSubtitleAreasChange={handleSubtitleAreasChange}
            />
          </div>
        )}

        {/* 调试信息 */}
        {false && (
          <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs">
            <p className="font-medium text-gray-700 dark:text-gray-300 mb-2">调试信息:</p>
            <div className="space-y-1 text-gray-600 dark:text-gray-400">
              <div>原始URL: {file?.url || ''}</div>
              <div>处理后URL: {videoUrl}</div>
              <div>文件状态: {file?.status || 'unknown'}</div>
              {file?.progress !== undefined && <div>进度: {file.progress}%</div>}
              <div>Modal状态: {isModalOpen ? '打开' : '关闭'}</div>
              <div>字幕面板: {showSubtitlePanel ? '显示' : '隐藏'}</div>
              <div>当前音量: {Math.round(volume * 100)}%</div>
              <div>字幕区域数量: {subtitleAreas.length}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
