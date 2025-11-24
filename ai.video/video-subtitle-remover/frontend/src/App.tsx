import React, { useState } from 'react';
import { FileUploader } from './components/FileUploader';
import { VideoPreview } from './components/VideoPreview';
import { ParameterConfig } from './components/ParameterConfig';
import { ProcessingQueue } from './components/ProcessingQueue';
import { Modal } from './components/Modal';
import { Settings } from 'lucide-react';
import { FileInfo, ProcessConfig, TaskStatus } from './types';
import { apiService, TaskResponse } from './services/api';

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

  // 添加文件
  const handleFilesAdded = async (newFiles: FileInfo[]) => {
    // 上传文件到后端
    const uploadedFiles: FileInfo[] = [];
    for (const file of newFiles) {
      try {
        if (file.file instanceof File) {
          const uploadResponse = await apiService.uploadFile(file.file);
          uploadedFiles.push({
            ...file,
            url: uploadResponse.file_path,
          });
        } else {
          uploadedFiles.push(file);
        }
      } catch (error) {
        console.error('文件上传失败:', error);
        alert(`文件上传失败: ${error instanceof Error ? error.message : '未知错误'}`);
      }
    }

    setFiles(prev => [...prev, ...uploadedFiles]);
    if (!selectedFile && uploadedFiles.length > 0) {
      setSelectedFile(uploadedFiles[0]);
    }
  };

  // 删除文件
  const handleFileRemove = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    if (selectedFile?.id === fileId) {
      setSelectedFile(null);
    }
  };

  // 选择文件
  const handleFileSelect = (file: FileInfo) => {
    setSelectedFile(file);
  };

  // 开始处理
  const handleStartProcessing = async () => {
    if (!selectedFile) return;

    try {
      setIsProcessing(true);
      
      // 创建处理请求
      const processRequest = {
        file_path: selectedFile.url || '',
        algorithm: config.algorithm,
        detection_mode: config.detectionMode,
        subtitle_area: config.subtitleArea ? {
          x: config.subtitleArea.x,
          y: config.subtitleArea.y,
          width: config.subtitleArea.width,
          height: config.subtitleArea.height,
        } : undefined,
        sttn_params: config.sttnParams,
        propainter_params: config.propainterParams,
        lama_params: config.lamaParams,
        common_params: config.commonParams,
      };

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
              <div className="text-base font-semibold text-gray-700">文件管理</div>
              <FileUploader 
                onFilesAdded={handleFilesAdded}
                files={files}
                selectedFileId={selectedFile?.id}
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
              />
              <div className="border border-dashed border-gray-300 rounded-lg p-4 bg-white min-h-[100px]">
                {selectedFile ? (
                  <div className="text-sm text-gray-600 p-2">{selectedFile.name}</div>
                ) : (
                  <div className="text-sm text-gray-400">未选择文件</div>
                )}
              </div>
            </div>

            {/* 参数配置按钮 */}
            <button
              onClick={() => setIsConfigModalOpen(true)}
              className="flex items-center gap-2 w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 px-4 rounded-lg transition-colors text-base font-medium"
            >
              <Settings className="w-5 h-5" />
              参数配置
            </button>

            {/* 处理按钮 */}
            <button
              onClick={handleStartProcessing}
              disabled={!selectedFile || isProcessing}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-base font-medium"
            >
              {isProcessing ? '处理中...' : '开始处理'}
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
                  />
                </div>
              </section>

              {/* 结果视图 */}
              <section className="flex-1 border border-dashed border-gray-300 rounded-xl p-6 flex flex-col gap-4 bg-white shadow-sm">
                <div className="text-base font-semibold text-gray-700">结果视图</div>
                <div className="flex-1 border border-gray-200 rounded-lg bg-gray-50 relative overflow-hidden">
                  {/* 结果预览区域 */}
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-base">
                    {isProcessing ? '处理中...' : '等待处理结果'}
                  </div>
                </div>
                <div className="flex justify-center">
                  <button className="w-12 h-12 rounded-full border border-gray-400 bg-white flex items-center justify-center cursor-pointer hover:bg-gray-50 transition-colors shadow-sm">
                    <span className="ml-1 text-lg">▶</span>
                  </button>
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
                {config.subtitleArea && (
                  <>
                    <div className="flex items-center gap-2">
                      <span className="min-w-[30px] text-gray-700 font-medium">X：</span>
                      <input 
                        type="text" 
                        value={config.subtitleArea.x}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          subtitleArea: prev.subtitleArea ? {
                            ...prev.subtitleArea,
                            x: parseInt(e.target.value) || 0
                          } : undefined
                        }))}
                        className="w-24 px-3 py-2 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="min-w-[30px] text-gray-700 font-medium">Y：</span>
                      <input 
                        type="text" 
                        value={config.subtitleArea.y}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          subtitleArea: prev.subtitleArea ? {
                            ...prev.subtitleArea,
                            y: parseInt(e.target.value) || 0
                          } : undefined
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
