import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Maximize2 } from 'lucide-react';
import { FileInfo, ProcessConfig, SubtitleArea } from '../types';
import { formatDuration } from '../utils';
import { VideoControls } from './VideoControls';
import { SubtitleSelector } from './SubtitleSelector';

interface VideoPreviewProps {
  file: FileInfo | null;
  config: ProcessConfig;
  onConfigChange: (config: ProcessConfig) => void;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({
  file,
  config,
  onConfigChange,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [subtitleArea, setSubtitleArea] = useState<SubtitleArea | null>(
    config.subtitleArea || null
  );

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 当检测模式改变时，初始化字幕区域
  useEffect(() => {
    if (config.detectionMode === 'manual' && !subtitleArea) {
      const defaultArea: SubtitleArea = {
        x: 100,
        y: 400,
        width: 800,
        height: 200,
      };
      setSubtitleArea(defaultArea);
    } else if (config.detectionMode === 'auto') {
      setSubtitleArea(null);
    }
  }, [config.detectionMode, subtitleArea]);

  // 更新配置中的字幕区域
  useEffect(() => {
    if (subtitleArea && config.detectionMode === 'manual') {
      onConfigChange({
        ...config,
        subtitleArea,
        detectionMode: 'manual',
      });
    }
  }, [subtitleArea, config, onConfigChange]);

  // 处理视频元数据加载
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
      
      if (config.detectionMode === 'manual') {
        const defaultArea: SubtitleArea = {
          x: videoRef.current.videoWidth * 0.05,
          y: videoRef.current.videoHeight * 0.78,
          width: videoRef.current.videoWidth * 0.9,
          height: videoRef.current.videoHeight * 0.21,
        };
        setSubtitleArea(defaultArea);
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
        videoRef.current.play();
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

  // 处理字幕区域变化
  const handleSubtitleAreaChange = (area: SubtitleArea | null) => {
    setSubtitleArea(area);
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
        </div>
      </div>
      
      <div className="card-body space-y-4">
        {/* 视频预览区域 */}
        <div
          ref={containerRef}
          className="video-preview aspect-video relative"
        >
          <video
            ref={videoRef}
            src={file.url}
            className="w-full h-full"
            onLoadedMetadata={handleLoadedMetadata}
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />

          {/* 字幕选择器 */}
          <SubtitleSelector
            videoRef={videoRef}
            config={config}
            subtitleArea={subtitleArea}
            onSubtitleAreaChange={handleSubtitleAreaChange}
          />
        </div>

        {/* 视频控制栏 */}
        <VideoControls
          isPlaying={isPlaying}
          currentTime={currentTime}
          duration={duration}
          onTogglePlay={togglePlay}
          onSkip={skip}
          onSeek={(percent) => {
            if (videoRef.current) {
              videoRef.current.currentTime = duration * percent;
            }
          }}
          onToggleFullscreen={toggleFullscreen}
        />

        {/* 字幕区域控制 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              字幕检测模式
            </label>
            <select
              value={config.detectionMode}
              onChange={(e) => onConfigChange({
                ...config,
                detectionMode: e.target.value as 'auto' | 'manual',
              })}
              className="select w-32"
            >
              <option value="auto">自动检测</option>
              <option value="manual">手动选择</option>
            </select>
          </div>

          {config.detectionMode === 'manual' && subtitleArea && (
            <div className="space-y-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                字幕区域位置
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
                <div>X: {Math.round(subtitleArea.x)}px</div>
                <div>Y: {Math.round(subtitleArea.y)}px</div>
                <div>宽度: {Math.round(subtitleArea.width)}px</div>
                <div>高度: {Math.round(subtitleArea.height)}px</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
