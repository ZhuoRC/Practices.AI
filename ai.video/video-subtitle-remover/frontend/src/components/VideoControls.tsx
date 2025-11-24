import React from 'react';
import { Play, Pause, SkipBack, SkipForward, Maximize2 } from 'lucide-react';
import { formatDuration } from '../utils';

interface VideoControlsProps {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  onTogglePlay: () => void;
  onSkip: (seconds: number) => void;
  onSeek: (percent: number) => void;
  onToggleFullscreen: () => void;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  isPlaying,
  currentTime,
  duration,
  onTogglePlay,
  onSkip,
  onSeek,
  onToggleFullscreen,
}) => {
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
