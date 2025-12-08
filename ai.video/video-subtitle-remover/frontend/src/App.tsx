import React, { useState, useEffect } from 'react';
import { FileUploader } from './components/FileUploader';
import { VideoPreview } from './components/VideoPreview';
import { ResultVideoPreview } from './components/ResultVideoPreview';
import { ParameterConfig } from './components/ParameterConfig';
import { ProcessingQueue } from './components/ProcessingQueue';
import { Modal } from './components/Modal';
import { Settings, Upload } from 'lucide-react';
import { FileInfo, ProcessConfig, TaskStatus } from './types';
import { apiService, TaskResponse } from './services/api';

// localStorage键名常量
const STORAGE_KEYS = {
  SELECTED_FILE: 'video-subtitle-selected-file',
  TASKS: 'video-subtitle-tasks',
  FILES: 'video-subtitle-files',
};

function App() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [config, setConfig] = useState<ProcessConfig>({
    algorithm: 'sttn',
    detectionMode: 'auto',
    sttnParams: {
      skipDetection: true,
      neighborStride: 5,
      referenceLength: 10,
      maxLoadNum: 50,
    },
    propainterParams: {
      maxLoadNum: 70,
    },
    lamaParams: {
      superFast: false,
    },
    commonParams: {
      useH264: true,
      thresholdHeightWidthDifference: 10,
      subtitleAreaDeviationPixel: 20,
      thresholdHeightDifference: 20,
      pixelToleranceY: 20,
      pixelToleranceX: 20,
    },
  });
  const [tasks, setTasks] = useState<TaskStatus[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [resultFile, setResultFile] = useState<FileInfo | null>(null);

  // 从localStorage和后端恢复状态
  useEffect(() => {
    const loadFiles = async () => {
      try {
        let combinedFiles: FileInfo[] = [];
        
        // 首先从localStorage恢复已保存的文件列表
        const savedFiles = localStorage.getItem(STORAGE_KEYS.FILES);
        if (savedFiles) {
          const parsedFiles = JSON.parse(savedFiles);
          // 过滤掉正在上传中的文件（刷新后这些文件状态已经无效）
          const validFiles = parsedFiles.filter((file: FileInfo) => 
            file.status === 'completed'
          );
          combinedFiles = validFiles;
          console.log('恢复文件列表:', validFiles.length, '个文件');
        }

        // 然后从后端uploads目录获取所有视频文件
        try {
          const uploadedFiles = await apiService.getUploadedFiles();
          console.log('从后端获取的文件:', uploadedFiles);
          
          // 将后端文件转换为前端FileInfo格式
          const backendFiles: FileInfo[] = uploadedFiles.map(file => ({
            id: file.id,
            name: file.name,
            url: file.url,
            file: undefined, // 后端文件没有File对象
            status: 'completed' as const,
            progress: 100,
            size: file.size,
            type: 'video/mp4', // 后端文件默认为video/mp4类型
          }));

          // 合并本地保存的文件和后端文件，去重
          backendFiles.forEach(backendFile => {
            // 检查是否已存在（通过URL或ID比较）
            const exists = combinedFiles.some(existingFile => 
              existingFile.url === backendFile.url || existingFile.id === backendFile.id
            );
            if (!exists) {
              combinedFiles.push(backendFile);
            }
          });

          // 获取output文件
          try {
            const outputFiles = await apiService.getOutputFiles();
            const backendOutputFiles: FileInfo[] = outputFiles.map(file => ({
              id: file.id,
              name: file.name,
              url: file.url,
              file: undefined,
              status: 'completed' as const,
              progress: 100,
              size: file.size,
              type: 'video/mp4',
              isOutput: true, // 标记为output文件
            }));

            // 合并output文件
            backendOutputFiles.forEach(backendFile => {
              const exists = combinedFiles.some(existingFile => 
                existingFile.url === backendFile.url || existingFile.id === backendFile.id
              );
              if (!exists) {
                combinedFiles.push(backendFile);
              }
            });
          } catch (error) {
            console.warn('获取output文件失败:', error);
          }

          setFiles(combinedFiles);
          console.log('合并后的文件列表:', combinedFiles.length, '个文件');
        } catch (error) {
          console.error('获取后端文件列表失败:', error);
          // 如果获取后端文件失败，仍然使用本地保存的文件
          setFiles(combinedFiles);
        }

        // 恢复选中的文件 - 支持同时选择源文件和结果文件
        const savedSelectedFile = localStorage.getItem(STORAGE_KEYS.SELECTED_FILE);
        if (savedSelectedFile) {
          const parsedState = JSON.parse(savedSelectedFile);
          if (parsedState.selectedFile) {
            const selectedFile = combinedFiles.find((file: FileInfo) => 
              file.id === parsedState.selectedFile.id || file.url === parsedState.selectedFile.url
            );
            if (selectedFile && !selectedFile.isOutput) {
              setSelectedFile(selectedFile);
              console.log('恢复选中的源文件:', selectedFile.name);
            }
          }
          
          if (parsedState.resultFile) {
            const resultFile = combinedFiles.find((file: FileInfo) => 
              file.id === parsedState.resultFile.id || file.url === parsedState.resultFile.url
            );
            if (resultFile && resultFile.isOutput) {
              setResultFile(resultFile);
              console.log('恢复选中的结果文件:', resultFile.name);
            }
          }
        }

        // 恢复任务列表
        const savedTasks = localStorage.getItem(STORAGE_KEYS.TASKS);
        if (savedTasks) {
          const parsedTasks = JSON.parse(savedTasks);
          // 过滤掉未完成的任务（重启后这些任务已经无效）
          const validTasks = parsedTasks.filter((task: TaskStatus) => 
            task.status === 'completed'
          );
          setTasks(validTasks);
        }
      } catch (error) {
        console.error('恢复状态失败:', error);
      }
    };

    loadFiles();
  }, []); // 只在组件挂载时执行一次

  // 自动保存文件列表到localStorage
  useEffect(() => {
    try {
      // 只保存已完成的文件，避免保存正在上传的临时状态
      const completedFiles = files.filter(file => file.status === 'completed');
      localStorage.setItem(STORAGE_KEYS.FILES, JSON.stringify(completedFiles));
      console.log('保存文件列表:', completedFiles.length, '个文件');
    } catch (error) {
      console.error('保存文件列表失败:', error);
    }
  }, [files]);

  // 自动保存任务列表到localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(tasks));
    } catch (error) {
      console.error('保存任务列表失败:', error);
    }
  }, [tasks]);

  // 添加文件
  const handleFilesAdded = async (newFiles: FileInfo[]) => {
    console.log('handleFilesAdded called with:', newFiles.map(f => ({ 
      name: f.name, 
      hasFile: !!f.file,
      fileSize: f.file?.size,
      fileType: f.file?.type
    })));
    
    // 先将文件添加到状态中，状态为uploading
    const initialFiles = newFiles.map(file => ({
      ...file,
      status: 'processing' as const,
      progress: 0,
    }));
    
    setFiles(prev => [...prev, ...initialFiles]);
    
    // 上传文件到后端
    const uploadedFiles: FileInfo[] = [];
    for (let i = 0; i < newFiles.length; i++) {
      const file = newFiles[i];
      const initialFile = initialFiles[i];
      
      try {
        if (file.file instanceof File) {
          console.log('Starting upload for file:', file.name, 'size:', file.file.size);
          
          const uploadResponse = await apiService.uploadFile(file.file, (progress) => {
            // 更新上传进度
            setFiles(prev => prev.map(f => 
              f.id === initialFile.id 
                ? { ...f, progress }
                : f
            ));
          });
          
          console.log('Upload successful:', uploadResponse);
          
          // 修复：使用正确的URL格式 - 构建相对路径而不是使用绝对路径
          const fileExtension = file.name.split('.').pop();
          const updatedFile = {
            ...file,
            url: `/uploads/${uploadResponse.file_id}.${fileExtension}`, // 修复：使用相对路径
            status: 'completed' as const,
            progress: 100,
          };
          uploadedFiles.push(updatedFile);
          
          // 更新文件状态为完成
          setFiles(prev => prev.map(f => 
            f.id === initialFile.id 
              ? updatedFile
              : f
          ));
          
          // 如果这个文件是当前选中的文件，更新selectedFile
          if (selectedFile?.id === file.id) {
            console.log('Updating selectedFile from blob to backend path');
            setSelectedFile(updatedFile);
          }
        } else {
          console.error('File has no file object, cannot upload:', file.name);
          // 标记文件为错误状态
          setFiles(prev => prev.map(f => 
            f.id === initialFile.id 
              ? { ...f, status: 'error' as const, error: '文件无效' }
              : f
          ));
          continue;
        }
      } catch (error) {
        console.error('文件上传失败:', error);
        const errorMessage = error instanceof Error ? error.message : '未知错误';
        
        // 标记文件上传失败
        setFiles(prev => prev.map(f => 
          f.id === initialFile.id 
            ? { ...f, status: 'error' as const, error: errorMessage }
            : f
        ));
      }
    }

    // 自动选择第一个成功上传的文件
    if (!selectedFile && uploadedFiles.length > 0) {
      console.log('Auto-selecting first successful uploaded file:', uploadedFiles[0].name);
      setSelectedFile(uploadedFiles[0]);
    }
  };

  // 删除文件
  const handleFileRemove = async (fileId: string) => {
    try {
      // 调用后端API删除文件
      await apiService.deleteFile(fileId);
      
      // 从前端状态中删除文件
      setFiles(prev => prev.filter(f => f.id !== fileId));
      
      // 如果删除的是当前选中的源文件，清除选择
      if (selectedFile?.id === fileId) {
        setSelectedFile(null);
      }
      
      // 如果删除的是结果文件，清除结果
      if (resultFile?.id === fileId) {
        setResultFile(null);
      }
      
      // 更新localStorage中的选择状态
      try {
        const currentState = {
          selectedFile: selectedFile?.id === fileId ? null : (selectedFile ? {
            id: selectedFile.id,
            name: selectedFile.name,
            url: selectedFile.url,
            isOutput: selectedFile.isOutput,
          } : null),
          resultFile: resultFile?.id === fileId ? null : (resultFile ? {
            id: resultFile.id,
            name: resultFile.name,
            url: resultFile.url,
            isOutput: resultFile.isOutput,
          } : null)
        };
        localStorage.setItem(STORAGE_KEYS.SELECTED_FILE, JSON.stringify(currentState));
      } catch (error) {
        console.error('保存选中文件状态失败:', error);
      }
      
      console.log('文件删除成功');
    } catch (error) {
      console.error('删除文件失败:', error);
      alert(`删除文件失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  // 选择文件 - 修改为允许同时选择源文件和结果文件
  const handleFileSelect = (file: FileInfo) => {
    console.log('Selecting file:', file.name, 'URL:', file.url);
    
    // 检查文件是否已上传完成
    if (!file.url) {
      alert('文件尚未上传完成，请等待上传完成后再选择');
      return;
    }
    
    // 检查文件状态
    if (file.status === 'processing') {
      alert('文件正在上传中，请等待上传完成后再选择');
      return;
    }
    
    if (file.status === 'error') {
      alert('文件上传失败，请重新上传');
      return;
    }
    
    // 检查是否是blob URL（表示还未上传完成）
    if (file.url.startsWith('blob:')) {
      alert('文件尚未上传完成，请等待上传完成后再选择');
      return;
    }
    
    // 文件已上传完成，可以根据类型设置到对应的状态
    if (file.isOutput) {
      // 如果是output文件，设置为结果文件（不影响源文件选择）
      setResultFile(file);
    } else {
      // 如果是源文件，设置为选中文件（不影响结果文件选择）
      setSelectedFile(file);
    }
    
    // 保存当前选择状态到localStorage - 支持同时保存两种文件
    try {
      const currentState = {
        selectedFile: file.isOutput ? (selectedFile ? {
          id: selectedFile.id,
          name: selectedFile.name,
          url: selectedFile.url,
          isOutput: selectedFile.isOutput,
        } : null) : {
          id: file.id,
          name: file.name,
          url: file.url,
          isOutput: false,
        },
        resultFile: file.isOutput ? {
          id: file.id,
          name: file.name,
          url: file.url,
          isOutput: true,
        } : (resultFile ? {
          id: resultFile.id,
          name: resultFile.name,
          url: resultFile.url,
          isOutput: true,
        } : null)
      };
      localStorage.setItem(STORAGE_KEYS.SELECTED_FILE, JSON.stringify(currentState));
    } catch (error) {
      console.error('保存选中文件失败:', error);
    }
  };

  // 开始处理
  const handleStartProcessing = async () => {
    if (!selectedFile) return;

    try {
      setIsProcessing(true);
      
      // 修复：验证文件路径格式，确保不是blob URL
      const filePath = selectedFile.url;
      console.log('Using file path for processing:', filePath);
      console.log('Selected file details:', selectedFile);
      
      // 修复：检查文件路径是否有效
      if (!filePath || filePath.startsWith('blob:')) {
        throw new Error('文件尚未正确上传，请重新上传文件');
      }
      
      // 修复：使用相对路径，后端会自动拼接完整路径
      let processFilePath = filePath;
      if (filePath.startsWith('/uploads/')) {
        // 对于相对路径，直接使用
        processFilePath = filePath;
      } else if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        // 如果是完整URL，提取路径部分
        const url = new URL(filePath);
        processFilePath = url.pathname;
      }
      
      console.log('Final process file path:', processFilePath);
      
      // 创建处理请求 - 添加多字幕区域支持
      const processRequest = {
        filePath: processFilePath, // 修复：使用正确的路径格式
        algorithm: config.algorithm,
        detectionMode: config.detectionMode,
        subtitleAreas: config.subtitleAreas, // 修复：发送多字幕区域数组
        subtitleArea: config.subtitleAreas && config.subtitleAreas.length > 0 ? {
          x: config.subtitleAreas[0].x,
          y: config.subtitleAreas[0].y,
          width: config.subtitleAreas[0].width,
          height: config.subtitleAreas[0].height,
        } : undefined,
        sttnParams: config.sttnParams,
        propainterParams: config.propainterParams,
        lamaParams: config.lamaParams,
        commonParams: config.commonParams,
      };

      console.log('Sending process request:', processRequest);

      // 调用API开始处理
      const taskResponse = await apiService.startProcessing(processRequest);

      // 创建本地任务状态
      const task: TaskStatus = {
        id: taskResponse.task_id,
        fileId: selectedFile.id,
        status: 'pending',
        progress: 0,
        startTime: new Date(),
      };

      setTasks(prev => [...prev, task]);

      // 开始轮询任务状态
      pollTaskStatus(taskResponse.task_id, selectedFile.id);

    } catch (error) {
      console.error('处理失败:', error);
      alert(`处理失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // 轮询任务状态
  const pollTaskStatus = async (taskId: string, fileId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const taskResponse = await apiService.getTaskStatus(taskId);

        setTasks(prev => prev.map(task => {
          if (task.id === taskId) {
            return {
              ...task,
              status: taskResponse.status as any,
              progress: taskResponse.progress,
              error: taskResponse.error,
            };
          }
          return task;
        }));

        // 如果任务完成或失败，停止轮询
        if (taskResponse.status === 'completed') {
          clearInterval(pollInterval);
          setIsProcessing(false);
          
          // 创建结果文件对象
          const resultFileInfo: FileInfo = {
            id: `result-${taskId}`,
            name: `${selectedFile?.name.replace(/\.[^/.]+$/, '')}_processed${selectedFile?.name.match(/\.[^/.]+$/)?.[0] || ''}`,
            url: apiService.getDownloadUrl(taskId),
            status: 'completed',
            progress: 100,
            size: selectedFile?.size || 0,
            type: selectedFile?.type || 'video/mp4',
            isOutput: true,
          };

          // 更新文件状态
          setFiles(prev => prev.map(file => {
            if (file.id === fileId) {
              return {
                ...file,
                status: 'completed',
                progress: 100,
                resultUrl: apiService.getDownloadUrl(taskId),
              };
            }
            return file;
          }));

          // 添加结果文件到文件列表
          setFiles(prev => [...prev, resultFileInfo]);

          // 自动在结果视图显示结果（不影响源文件选择）
          setResultFile(resultFileInfo);
          console.log('任务完成，结果文件已自动显示:', resultFileInfo.name);

        } else if (taskResponse.status === 'failed') {
          clearInterval(pollInterval);
          setIsProcessing(false);
          console.error('任务失败:', taskResponse.error);
        }

      } catch (error) {
        console.error('获取任务状态失败:', error);
        clearInterval(pollInterval);
        setIsProcessing(false);
      }
    }, 2000); // 每2秒轮询一次
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 全屏顶部标题栏 */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Video Subtitle Remover</h1>
        </div>
      </header>

      {/* 全屏内容区 */}
      <div className="flex h-[calc(100vh-73px)]">
          {/* 左侧栏 */}
          <aside className="w-80 border-r border-gray-200 p-6 bg-gray-50 flex flex-col gap-6">
            {/* 文件管理 */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-base font-semibold text-gray-700">文件管理</div>
                <FileUploader 
                  onFilesAdded={handleFilesAdded}
                  files={files}
                  selectedFileId={selectedFile?.id}
                  onFileSelect={handleFileSelect}
                  onFileRemove={handleFileRemove}
                  compactMode={true}
                />
              </div>
              
              {/* 文件列表 - 只显示上传的文件，不显示output文件 */}
              {files.filter(file => !file.isOutput).length > 0 && (
                <div className="border border-gray-200 rounded-lg bg-white max-h-64 overflow-y-auto">
                  {files.filter(file => !file.isOutput).map((file) => (
                    <div
                      key={file.id}
                      className={`
                        flex items-center space-x-3 p-3 border-b border-gray-100 last:border-b-0 cursor-pointer transition-colors
                        ${selectedFile?.id === file.id
                          ? 'bg-blue-50 border-l-4 border-l-blue-500' 
                          : 'hover:bg-gray-50'
                        }
                      `}
                      onClick={() => handleFileSelect(file)}
                    >
                      {/* 文件图标 */}
                      <div className="w-8 h-8 rounded flex items-center justify-center flex-shrink-0 bg-blue-100">
                        <Upload className="w-4 h-4 text-blue-600" />
                      </div>

                      {/* 文件信息 */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {file.name}
                          </p>
                          {file.status === 'completed' && (
                            <span className="text-xs text-green-500">✓</span>
                          )}
                          {file.status === 'processing' && (
                            <span className="text-xs text-blue-500">⟳</span>
                          )}
                          {file.status === 'error' && (
                            <span className="text-xs text-red-500">✗</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          {file.status === 'processing' ? `上传中... ${file.progress}%` : 
                           file.status === 'completed' ? '已上传' :
                           file.status === 'error' ? '上传失败' : '等待中'}
                        </div>
                        {file.progress > 0 && file.status === 'processing' && (
                          <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                            <div
                              className="bg-blue-600 h-1 rounded-full transition-all"
                              style={{ width: `${file.progress}%` }}
                            />
                          </div>
                        )}
                      </div>

                      {/* 删除按钮 */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFileRemove(file.id);
                        }}
                        className="p-1 rounded hover:bg-red-100 text-red-500 flex-shrink-0"
                        title="删除文件"
                      >
                        <span className="w-4 h-4 text-sm">×</span>
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="border border-dashed border-gray-300 rounded-lg p-4 bg-white min-h-[80px]">
                <div className="text-sm text-gray-600 p-2">
                  <div className="font-medium text-gray-900 mb-2">当前选择:</div>
                  {selectedFile ? (
                    <div className="text-xs text-gray-500">
                      <div>📹 源文件: {selectedFile.name}</div>
                      <div>
                        {selectedFile.url?.startsWith('blob:') ? (
                          <span className="text-yellow-600">⚠️ 文件上传中...</span>
                        ) : selectedFile.status === 'error' ? (
                          <span className="text-red-500">❌ 上传失败</span>
                        ) : selectedFile.status === 'processing' ? (
                          <span className="text-blue-500">🔄 正在上传...</span>
                        ) : (
                          <span className="text-green-500">✅ 文件已上传</span>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-gray-400">未选择源文件</div>
                  )}
                  {resultFile ? (
                    <div className="text-xs text-gray-500 mt-1">
                      <div>🎯 结果文件: {resultFile.name}</div>
                      <div>
                        {resultFile.status === 'error' ? (
                          <span className="text-red-500">❌ 处理失败</span>
                        ) : resultFile.status === 'processing' ? (
                          <span className="text-blue-500">🔄 处理中...</span>
                        ) : (
                          <span className="text-green-500">✅ 处理完成</span>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-gray-400 mt-1">未选择结果文件</div>
                  )}
                </div>
              </div>
            </div>

            {/* 配置管理按钮 */}
            <div className="space-y-2">
              <button
                onClick={() => setIsConfigModalOpen(true)}
                className="flex items-center gap-2 w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 px-4 rounded-lg transition-colors text-base font-medium"
              >
                <Settings className="w-5 h-5" />
                参数配置
              </button>
            </div>

            {/* 处理按钮 */}
            <button
              onClick={handleStartProcessing}
              disabled={!selectedFile || isProcessing || selectedFile?.status === 'processing' || selectedFile?.status === 'error'}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-base font-medium"
            >
              {isProcessing ? '处理中...' : selectedFile?.status === 'processing' ? '等待上传完成...' : selectedFile?.status === 'error' ? '文件上传失败' : '开始处理'}
            </button>

            {/* 任务列表 */}
            <div className="space-y-3 flex-1">
              <div className="text-base font-semibold text-gray-700">任务列表</div>
              <div className="flex-1">
                <ProcessingQueue tasks={tasks} />
              </div>
            </div>
          </aside>

          {/* 主视图区 */}
          <main className="flex-1 p-6 flex flex-col gap-6">
            <div className="flex gap-6 flex-1 min-h-0">
              {/* 源视图 */}
              <section className="flex-1 border border-dashed border-gray-300 rounded-xl p-6 flex flex-col gap-4 bg-white shadow-sm">
                <div className="text-base font-semibold text-gray-700">源视图</div>
                <div className="flex-1 border border-gray-200 rounded-lg bg-gray-50 relative overflow-hidden">
                  <VideoPreview 
                    file={selectedFile}
                    config={config}
                    onConfigChange={setConfig}
                    isModalOpen={isConfigModalOpen}
                  />
                </div>
              </section>

              {/* 结果视图 */}
              <section className="flex-1 border border-dashed border-gray-300 rounded-xl p-6 flex flex-col gap-4 bg-white shadow-sm">
                <div className="text-base font-semibold text-gray-700">结果视图</div>
                <div className="flex gap-4 flex-1 min-h-0">
                  {/* 结果预览区域 - 使用专门的ResultVideoPreview组件 */}
                  <div className="flex-1 border border-gray-200 rounded-lg bg-gray-50 relative overflow-hidden">
                    {resultFile ? (
                      <ResultVideoPreview 
                        file={resultFile}
                        isModalOpen={isConfigModalOpen}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400 text-base">
                        {isProcessing ? '处理中...' : '请选择已处理的文件进行预览'}
                      </div>
                    )}
                  </div>
                  
                  {/* Output文件列表 */}
                  <div className="w-64 border border-gray-200 rounded-lg bg-white p-4">
                    <div className="text-sm font-medium text-gray-700 mb-3">已处理的文件</div>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {files.filter(file => file.isOutput).length > 0 ? (
                        files.filter(file => file.isOutput).map((file) => (
                          <div
                            key={file.id}
                            className={`
                              flex items-center space-x-2 p-2 border border-gray-100 rounded cursor-pointer transition-colors
                              ${resultFile?.id === file.id
                                ? 'bg-green-50 border-green-300' 
                                : 'hover:bg-gray-50'
                              }
                            `}
                            onClick={() => {
                              setResultFile(file);
                              // 保存到localStorage
                              try {
                                const currentState = {
                                  selectedFile: selectedFile ? {
                                    id: selectedFile.id,
                                    name: selectedFile.name,
                                    url: selectedFile.url,
                                    isOutput: selectedFile.isOutput,
                                  } : null,
                                  resultFile: {
                                    id: file.id,
                                    name: file.name,
                                    url: file.url,
                                    isOutput: true,
                                  }
                                };
                                localStorage.setItem(STORAGE_KEYS.SELECTED_FILE, JSON.stringify(currentState));
                              } catch (error) {
                                console.error('保存选中文件失败:', error);
                              }
                            }}
                          >
                            {/* 文件图标 */}
                            <div className="w-6 h-6 rounded flex items-center justify-center flex-shrink-0 bg-green-100">
                              <Upload className="w-3 h-3 text-green-600" />
                            </div>

                            {/* 文件信息 */}
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-gray-900 truncate">
                                {file.name}
                              </p>
                              <div className="text-xs text-gray-500">
                                {file.size ? `${(file.size / 1024 / 1024).toFixed(1)} MB` : ''}
                              </div>
                            </div>

                            {/* 删除按钮 */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleFileRemove(file.id);
                              }}
                              className="p-1 rounded hover:bg-red-100 text-red-500 flex-shrink-0"
                              title="删除文件"
                            >
                              <span className="w-3 h-3 text-sm">×</span>
                            </button>
                          </div>
                        ))
                      ) : (
                        <div className="text-xs text-gray-400 text-center py-8">
                          暂无已处理的文件
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </section>
            </div>

            {/* 底部控制区 */}
            <div className="border-t border-gray-200 pt-6 flex flex-col gap-4 text-base">
              <div className="flex items-center gap-4">
                <span className="min-w-[80px] text-gray-700 font-medium">Frame输入：</span>
                <input 
                  type="text" 
                  placeholder="例如：100 或 00:01:23"
                  className="px-4 py-2 text-base border border-gray-300 rounded-lg min-w-[200px] focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center gap-6">
                {config.subtitleAreas && config.subtitleAreas.length > 0 && (
                  <>
                    <div className="flex items-center gap-2">
                      <span className="min-w-[30px] text-gray-700 font-medium">X：</span>
                      <input 
                        type="text" 
                        value={config.subtitleAreas[0].x}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          subtitleAreas: prev.subtitleAreas ? [
                            { ...prev.subtitleAreas[0], x: parseInt(e.target.value) || 0 },
                            ...prev.subtitleAreas.slice(1)
                          ] : undefined
                        }))}
                        className="w-24 px-3 py-2 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="min-w-[30px] text-gray-700 font-medium">Y：</span>
                      <input 
                        type="text" 
                        value={config.subtitleAreas[0].y}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          subtitleAreas: prev.subtitleAreas ? [
                            { ...prev.subtitleAreas[0], y: parseInt(e.target.value) || 0 },
                            ...prev.subtitleAreas.slice(1)
                          ] : undefined
                        }))}
                        className="w-24 px-3 py-2 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>
          </main>
      </div>

      {/* 参数配置Modal */}
      <Modal
        isOpen={isConfigModalOpen}
        onClose={() => setIsConfigModalOpen(false)}
        title="参数配置"
      >
        <ParameterConfig 
          config={config}
          onChange={setConfig}
        />
      </Modal>
    </div>
  );
}

export default App;
