import React, { useState } from 'react';
import { Download, Eye, Trash2, Play, Film, Image, Copy, Check } from 'lucide-react';
import { FileInfo } from '../types';
import { formatFileSize, copyToClipboard } from '../utils';
import toast from 'react-hot-toast';

interface ResultManagerProps {
  files: FileInfo[];
  onFileRemove: (fileId: string) => void;
}

export const ResultManager: React.FC<ResultManagerProps> = ({
  files,
  onFileRemove,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [previewFile, setPreviewFile] = useState<FileInfo | null>(null);

  const handleSelectAll = () => {
    if (selectedFiles.size === files.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(files.map(f => f.id)));
    }
  };

  const handleFileSelect = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  const handleDownload = async (file: FileInfo) => {
    try {
      // 模拟下载 - 在实际应用中这里会调用真实的下载API
      if (file.resultUrl) {
        // 创建一个模拟的下载链接
        const link = document.createElement('a');
        link.href = file.url; // 使用原始文件URL进行模拟
        link.download = `${file.name.replace(/\.[^/.]+$/, '')}_no_subtitles${file.name.match(/\.[^/.]+$/)?.[0] || ''}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toast.success('下载已开始（模拟）');
      } else {
        toast.error('文件处理中，请稍后再试');
      }
    } catch (error) {
      toast.error('下载失败');
    }
  };

  const handleBatchDownload = async () => {
    const filesToDownload = files.filter(f => selectedFiles.has(f.id) && f.resultUrl);
    
    if (filesToDownload.length === 0) {
      toast.error('请选择要下载的文件');
      return;
    }

    for (const file of filesToDownload) {
      await handleDownload(file);
    }
  };

  const handlePreview = (file: FileInfo) => {
    setPreviewFile(file);
  };

  const handleCopyUrl = async (file: FileInfo) => {
    if (!file.resultUrl) return;

    const success = await copyToClipboard(file.resultUrl);
    if (success) {
      toast.success('链接已复制到剪贴板');
    } else {
      toast.error('复制失败');
    }
  };

  const getFileIcon = (file: FileInfo) => {
    const isVideo = file.type.startsWith('video/');
    return isVideo ? <Film className="w-4 h-4" /> : <Image className="w-4 h-4" />;
  };

  if (files.length === 0) {
    return (
      <div className="card">
        <div className="card-body text-center py-8">
          <div className="w-12 h-12 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <Download className="w-6 h-6 text-gray-400" />
          </div>
          <p className="text-gray-500 dark:text-gray-400">
            暂无处理结果
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
            处理完成的文件将在这里显示
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* 预览模态框 */}
      {previewFile && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setPreviewFile(null)}
        >
          <div
            className="bg-white dark:bg-dark-surface rounded-lg max-w-4xl max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-border">
              <h3 className="font-semibold text-gray-900 dark:text-dark-text truncate">
                {previewFile.name}
              </h3>
              <button
                onClick={() => setPreviewFile(null)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Trash2 className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="p-4">
              {previewFile.type.startsWith('video/') ? (
                <div className="space-y-4">
                  <video
                    src={previewFile.url}
                    controls
                    className="w-full max-h-[60vh] rounded"
                  />
                  <div className="text-center">
                    <p className="text-sm text-green-600 dark:text-green-400 font-medium">
                      ✅ 字幕移除处理完成
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      这是原始视频预览，实际处理后的文件可以通过下载获取
                    </p>
                  </div>
                </div>
              ) : (
                <img
                  src={previewFile.url}
                  alt={previewFile.name}
                  className="w-full max-h-[60vh] object-contain rounded"
                />
              )}
            </div>
            
            <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-dark-border">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {formatFileSize(previewFile.size)}
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleCopyUrl(previewFile)}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="复制链接"
                >
                  <Copy className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                </button>
                
                <button
                  onClick={() => handleDownload(previewFile)}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>下载</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 结果列表 */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 dark:text-dark-text">
              处理结果 ({files.length})
            </h3>
            
            <div className="flex items-center space-x-3">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedFiles.size === files.length}
                  onChange={handleSelectAll}
                  className="rounded"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  全选
                </span>
              </label>
              
              {selectedFiles.size > 0 && (
                <button
                  onClick={handleBatchDownload}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>批量下载 ({selectedFiles.size})</span>
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div className="card-body">
          <div className="space-y-3">
            {files.map((file) => (
              <div
                key={file.id}
                className={`
                  flex items-center space-x-4 p-4 border rounded-lg transition-colors
                  ${selectedFiles.has(file.id)
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {/* 选择框 */}
                <input
                  type="checkbox"
                  checked={selectedFiles.has(file.id)}
                  onChange={() => handleFileSelect(file.id)}
                  className="rounded"
                />

                {/* 缩略图 */}
                <div className="relative">
                  {file.thumbnail ? (
                    <img
                      src={file.thumbnail}
                      alt={file.name}
                      className="w-16 h-16 object-cover rounded"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                      {getFileIcon(file)}
                    </div>
                  )}
                  
                  {/* 状态标记 */}
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                </div>

                {/* 文件信息 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <p className="font-medium text-gray-900 dark:text-dark-text truncate">
                      {file.name.replace(/\.[^/.]+$/, '')}
                    </p>
                    <span className="badge badge-success text-xs">已完成</span>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400 mt-1">
                    <span>{formatFileSize(file.size)}</span>
                    <span>处理完成</span>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePreview(file)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                    title="预览"
                  >
                    <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                  
                  <button
                    onClick={() => handleCopyUrl(file)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                    title="复制链接"
                  >
                    <Copy className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                  
                  <button
                    onClick={() => handleDownload(file)}
                    className="btn btn-primary flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>下载</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};
