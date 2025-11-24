import React from 'react';
import { Clock, CheckCircle, AlertCircle, X, Pause, Play } from 'lucide-react';
import { TaskStatus } from '../types';
import { formatDuration } from '../utils';

interface ProcessingQueueProps {
  tasks: TaskStatus[];
}

export const ProcessingQueue: React.FC<ProcessingQueueProps> = ({ tasks }) => {
  const getStatusIcon = (status: TaskStatus['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'processing':
        return <div className="loading-spinner w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'paused':
        return <Pause className="w-4 h-4 text-blue-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: TaskStatus['status']) => {
    switch (status) {
      case 'pending':
        return '等待中';
      case 'processing':
        return '处理中';
      case 'completed':
        return '已完成';
      case 'error':
        return '错误';
      case 'paused':
        return '已暂停';
      default:
        return '未知';
    }
  };

  const getProgressColor = (status: TaskStatus['status']) => {
    switch (status) {
      case 'processing':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="card">
        <div className="card-body text-center py-8">
          <div className="w-12 h-12 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <Clock className="w-6 h-6 text-gray-400" />
          </div>
          <p className="text-gray-500 dark:text-gray-400">
            暂无处理任务
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
            上传文件并点击"开始处理"来添加任务
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900 dark:text-dark-text">
            处理队列 ({tasks.length})
          </h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {tasks.filter(t => t.status === 'processing').length} 正在处理
            </span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {tasks.filter(t => t.status === 'completed').length} 已完成
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-body space-y-3 max-h-96 overflow-y-auto">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3"
          >
            {/* 任务头部 */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getStatusIcon(task.status)}
                <div>
                  <p className="font-medium text-gray-900 dark:text-dark-text">
                    任务 #{task.id.slice(-6)}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {getStatusText(task.status)}
                  </p>
                </div>
              </div>
              
              {/* 控制按钮 */}
              <div className="flex items-center space-x-2">
                {task.status === 'processing' && (
                  <button
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                    title="暂停"
                  >
                    <Pause className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                )}
                
                {task.status === 'paused' && (
                  <button
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                    title="继续"
                  >
                    <Play className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                )}
                
                {(task.status === 'pending' || task.status === 'error') && (
                  <button
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                    title="取消"
                  >
                    <X className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                )}
              </div>
            </div>

            {/* 进度条 */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  处理进度
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {Math.round(task.progress)}%
                </span>
              </div>
              <div className="progress-bar h-2">
                <div
                  className={`progress-fill ${getProgressColor(task.status)}`}
                  style={{ width: `${task.progress}%` }}
                />
              </div>
            </div>

            {/* 详细信息 */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              {task.currentFrame && task.totalFrames && (
                <>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">当前帧:</span>
                    <span className="ml-2 font-medium text-gray-900 dark:text-dark-text">
                      {task.currentFrame.toLocaleString()} / {task.totalFrames.toLocaleString()}
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">处理速度:</span>
                    <span className="ml-2 font-medium text-gray-900 dark:text-dark-text">
                      {task.speed ? `${task.speed.toFixed(1)} FPS` : '--'}
                    </span>
                  </div>
                </>
              )}
              
              {task.estimatedTime && (
                <div>
                  <span className="text-gray-500 dark:text-gray-400">预计剩余:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-dark-text">
                    {formatDuration(task.estimatedTime)}
                  </span>
                </div>
              )}
              
              {task.startTime && (
                <div>
                  <span className="text-gray-500 dark:text-gray-400">开始时间:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-dark-text">
                    {new Date(task.startTime).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>

            {/* 错误信息 */}
            {task.error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 text-red-500 mt-0.5" />
                  <p className="text-sm text-red-800 dark:text-red-200">
                    {task.error}
                  </p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
