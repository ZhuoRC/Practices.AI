import React, { useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Maximize2, Volume2, VolumeX } from 'lucide-react';
import { formatDuration } from '../utils';

interface VideoControlsProps {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  onTogglePlay: () => void;
  onSkip: (seconds: number) => void;
  onSeek: (percent: number) => void;
  onToggleFullscreen: () => void;
  onVolumeChange: (volume: number) => void;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  isPlaying,
  currentTime,
  duration,
  volume,
  onTogglePlay,
  onSkip,
  onSeek,
  onToggleFullscreen,
  onVolumeChange,
}) => {
  const [isVolumeSliderVisible, setIsVolumeSliderVisible] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [previousVolume, setPreviousVolume] = useState(volume);

  const handleVolumeToggle = () => {
    if (isMuted) {
      // 取消静音，恢复之前的音量
      onVolumeChange(previousVolume);
      setIsMuted(false);
    } else {
      // 静音，保存当前音量
      setPreviousVolume(volume);
      onVolumeChange(0);
      setIsMuted(true);
    }
  };

  const handleVolumeChange = (newVolume: number) => {
    onVolumeChange(newVolume);
    if (newVolume > 0 && isMuted) {
      setIsMuted(false);
    }
  };

  return (
    <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
      <div className="flex items-center space-x-4">
        {/* 播放控制 */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onTogglePlay}
            className="p-2 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            {isPlaying ? <Pause className="w-4 h-4 text-gray-700 dark:text-gray-300" /> : <Play className="w-4 h-4 text-gray-700 dark:text-gray-300" />}
          </button>
          
          <button
            onClick={() => onSkip(-10)}
            className="p-2 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <SkipBack className="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>
          
          <button
            onClick={() => onSkip(10)}
            className="p-2 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <SkipForward className="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          {/* 音量控制 */}
          <div className="relative">
            <button
              onClick={handleVolumeToggle}
              onMouseEnter={() => setIsVolumeSliderVisible(true)}
              onMouseLeave={() => setIsVolumeSliderVisible(false)}
              className="p-2 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              {isMuted || volume === 0 ? (
                <VolumeX className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              ) : (
                <Volume2 className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              )}
            </button>

            {/* 音量滑块 */}
            <div
              className={`absolute bottom-full left-1/2 -translate-x-1/2 mb-2 transition-all duration-200 ${
                isVolumeSliderVisible ? 'opacity-100 visible' : 'opacity-0 invisible'
              }`}
              onMouseEnter={() => setIsVolumeSliderVisible(true)}
              onMouseLeave={() => setIsVolumeSliderVisible(false)}
            >
              <div className="bg-black/90 rounded-lg p-3 shadow-lg border border-white/10 min-w-[120px]">
                <div className="flex items-center space-x-2">
                  <Volume2 className="w-3 h-3 text-white flex-shrink-0" />
                  <div className="relative w-20 h-1 bg-white/30 rounded-full">
                    <div
                      className="absolute h-full bg-white rounded-full"
                      style={{ width: `${isMuted ? 0 : volume * 100}%` }}
                    />
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={isMuted ? 0 : volume}
                    onChange={(e) => handleVolumeChange(Number(e.target.value))}
                    className="absolute inset-0 w-full h-6 opacity-0 cursor-pointer"
                    style={{ left: 0, top: '-10px' }}
                  />
                  <span className="text-xs text-white min-w-[30px] text-right">
                    {Math.round((isMuted ? 0 : volume) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 进度条 */}
        <div className="flex-1">
          <div className="bg-gray-300 dark:bg-gray-600 rounded-full h-2 cursor-pointer" onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            onSeek(percent);
          }}>
            <div
              className="bg-primary-500 h-2 rounded-full transition-all"
              style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
            />
          </div>
        </div>

        {/* 时间显示 */}
        <div className="text-gray-700 dark:text-gray-300 text-sm font-mono min-w-[100px] text-right">
          {formatDuration(currentTime)} / {formatDuration(duration)}
        </div>

        {/* 全屏按钮 */}
        <button
          onClick={onToggleFullscreen}
          className="p-2 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        >
          <Maximize2 className="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>
      </div>
    </div>
  );
};
