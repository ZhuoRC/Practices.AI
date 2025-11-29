import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Film, Image, File, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { FileInfo } from '../types';
import { formatFileSize, generateId, isVideoFile, isImageFile, validateFileFormat, validateFileSize, createVideoThumbnail, createImageThumbnail } from '../utils';
import toast from 'react-hot-toast';

interface FileUploaderProps {
  onFilesAdded: (files: FileInfo[]) => void;
  files: FileInfo[];
  selectedFileId?: string;
  onFileSelect: (file: FileInfo) => void;
  onFileRemove: (fileId: string) => void;
  compactMode?: boolean;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  onFilesAdded,
  files,
  selectedFileId,
  onFileSelect,
  onFileRemove,
  compactMode = false,
}) => {
  const [isDragActive, setIsDragActive] = useState(false);

  const processFiles = useCallback(async (acceptedFiles: File[]) => {
    const validFiles: FileInfo[] = [];
    
    for (const file of acceptedFiles) {
      // 验证文件格式
      const formatValidation = validateFileFormat(file);
      if (!formatValidation.valid) {
        toast.error(`${file.name}: ${formatValidation.error}`);
        continue;
      }

      // 验证文件大小
      const sizeValidation = validateFileSize(file);
      if (!sizeValidation.valid) {
        toast.error(`${file.name}: ${sizeValidation.error}`);
        continue;
      }

      // 创建文件信息
      const fileInfo: FileInfo = {
        id: generateId(),
        name: file.name,
        size: file.size,
        type: file.type,
        url: URL.createObjectURL(file),
        status: 'pending',
        progress: 0,
        file: file, // 添加实际的 File 对象，这是修复的关键
      };

      // 生成缩略图
      try {
        if (isVideoFile(file)) {
          fileInfo.thumbnail = await createVideoThumbnail(file);
        } else if (isImageFile(file)) {
          fileInfo.thumbnail = await createImageThumbnail(file);
        }
      } catch (error) {
        console.warn('Failed to create thumbnail:', error);
      }

      validFiles.push(fileInfo);
    }

    if (validFiles.length > 0) {
      onFilesAdded(validFiles);
      toast.success(`成功添加 ${validFiles.length} 个文件`);
    }
  }, [onFilesAdded]);

  const { getRootProps, getInputProps, isDragAccept, isDragReject } = useDropzone({
    onDrop: processFiles,
    accept: {
      'video/*': ['.mp4', '.avi', '.flv', '.wmv', '.mov', '.mkv'],
      'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
    },
    multiple: true,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    onDropAccepted: () => setIsDragActive(false),
    onDropRejected: () => setIsDragActive(false),
  });

  const getFileIcon = (file: FileInfo) => {
    if (isVideoFile({ name: file.name, type: file.type } as File)) {
      return <Film className="w-4 h-4" />;
    } else if (isImageFile({ name: file.name, type: file.type } as File)) {
      return <Image className="w-4 h-4" />;
    }
    return <File className="w-4 h-4" />;
  };

  const getStatusIcon = (status: FileInfo['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: FileInfo['status']) => {
    switch (status) {
      case 'completed':
        return <span className="badge badge-success">已完成</span>;
      case 'processing':
        return <span className="badge badge-primary">处理中</span>;
      case 'error':
        return <span className="badge badge-danger">错误</span>;
      default:
        return <span className="badge badge-warning">等待中</span>;
    }
  };

  // Compact模式：只显示上传按钮
  if (compactMode) {
    return (
      <div
        {...getRootProps()}
        className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg cursor-pointer transition-colors text-sm font-medium"
      >
        <input {...getInputProps()} />
        <Upload className="w-4 h-4" />
        <span>上传文件</span>
      </div>
    );
  }

  // 完整模式：显示拖拽区域和文件列表
  return (
    <div className="space-y-4">
      {/* 拖拽上传区域 */}
      <div
        {...getRootProps()}
        className={`
          dropzone p-8 text-center cursor-pointer transition-all
          ${isDragActive ? 'active' : ''}
          ${isDragReject ? 'reject' : ''}
          ${isDragAccept ? 'border-primary-500' : 'border-gray-300'}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-lg font-medium text-gray-900 dark:text-dark-text mb-2">
          {isDragActive ? '释放文件到这里' : '拖拽文件到这里上传'}
        </p>
        <p className="text-sm text-gray-500 dark:text-dark-text-secondary mb-4">
          或点击选择文件
        </p>
        <p className="text-xs text-gray-400">
          支持格式: MP4, AVI, FLV, WMV, MOV, MKV, JPG, PNG, BMP, TIFF
        </p>
      </div>

      {/* 文件列表 */}
      {files.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 dark:text-dark-text">
              文件列表 ({files.length})
            </h3>
          </div>
          <div className="card-body space-y-2 max-h-96 overflow-y-auto">
            {files.map((file) => (
              <div
                key={file.id}
                className={`
                  flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-colors
                  ${selectedFileId === file.id 
                    ? 'bg-primary-50 dark:bg-primary-900/20 border border-primary-300' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                  }
                `}
                onClick={() => onFileSelect(file)}
              >
                {/* 缩略图 */}
                {file.thumbnail ? (
                  <img
                    src={file.thumbnail}
                    alt={file.name}
                    className="w-12 h-12 object-cover rounded"
                  />
                ) : (
                  <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                    {getFileIcon(file)}
                  </div>
                )}

                {/* 文件信息 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <p className="text-sm font-medium text-gray-900 dark:text-dark-text truncate">
                      {file.name}
                    </p>
                    {getStatusIcon(file.status)}
                  </div>
                  <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-dark-text-secondary">
                    <span>{formatFileSize(file.size)}</span>
                    {getStatusBadge(file.status)}
                  </div>
                  {file.progress > 0 && file.status === 'processing' && (
                    <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                      <div
                        className="bg-primary-600 h-1 rounded-full transition-all"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  )}
                </div>

                {/* 删除按钮 */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onFileRemove(file.id);
                  }}
                  className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/20 text-red-500"
                  title="删除文件"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
