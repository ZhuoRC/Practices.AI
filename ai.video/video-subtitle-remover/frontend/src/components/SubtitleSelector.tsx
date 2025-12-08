import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Plus, Trash2, Move } from 'lucide-react';
import { ProcessConfig, SubtitleArea } from '../types';

interface SubtitleSelectorProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  config: ProcessConfig;
  subtitleAreas: SubtitleArea[];  // 修改：从单个区域改为区域数组
  onSubtitleAreasChange: (areas: SubtitleArea[]) => void;  // 修改：回调函数
}

// 预定义的颜色数组
const PRESET_COLORS = [
  '#22c55e', // 绿色
  '#3b82f6', // 蓝色
  '#f59e0b', // 橙色
  '#ef4444', // 红色
  '#8b5cf6', // 紫色
  '#ec4899', // 粉色
  '#14b8a6', // 青色
  '#f97316', // 橘色
];

// 节流函数
const throttle = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastExecTime = 0;
  
  return (...args: Parameters<T>) => {
    const currentTime = Date.now();
    
    if (currentTime - lastExecTime > delay) {
      func(...args);
      lastExecTime = currentTime;
    } else {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(() => {
        func(...args);
        lastExecTime = Date.now();
        timeoutId = null;
      }, delay - (currentTime - lastExecTime));
    }
  };
};

export const SubtitleSelector: React.FC<SubtitleSelectorProps> = ({
  videoRef,
  config,
  subtitleAreas,
  onSubtitleAreasChange,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [resizeHandle, setResizeHandle] = useState<string | null>(null);
  const [dragStartPos, setDragStartPos] = useState({ x: 0, y: 0 });
  const [initialArea, setInitialArea] = useState<SubtitleArea | null>(null);
  const [activeAreaId, setActiveAreaId] = useState<string | null>(null);
  const [isAddingArea, setIsAddingArea] = useState(false);
  
  // 使用ref来避免频繁的状态更新
  const currentStateRef = useRef({
    isDragging: false,
    resizeHandle: null as string | null,
    dragStartPos: { x: 0, y: 0 },
    initialArea: null as SubtitleArea | null,
    activeAreaId: null as string | null,
  });

  // 生成唯一ID
  const generateId = useCallback(() => {
    return `area-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // 获取视频坐标 - 确保返回整数
  const getVideoCoordinates = useCallback((clientX: number, clientY: number) => {
    if (!videoRef.current) return { x: 0, y: 0 };
    
    const rect = videoRef.current.getBoundingClientRect();
    const scaleX = videoRef.current.videoWidth / rect.width;
    const scaleY = videoRef.current.videoHeight / rect.height;
    
    return {
      x: Math.round((clientX - rect.left) * scaleX),
      y: Math.round((clientY - rect.top) * scaleY),
    };
  }, []);

  // 确保字幕区域坐标为整数
  const ensureIntegerArea = useCallback((area: SubtitleArea): SubtitleArea => {
    return {
      ...area,
      x: Math.round(area.x),
      y: Math.round(area.y),
      width: Math.round(area.width),
      height: Math.round(area.height),
    };
  }, []);

  // 节流后的更新函数
  const throttledUpdate = useCallback(
    throttle((updatedArea: SubtitleArea) => {
      onSubtitleAreasChange(subtitleAreas.map(area => 
        area.id === updatedArea.id ? ensureIntegerArea(updatedArea) : area
      ));
    }, 16), // 约60fps
    [onSubtitleAreasChange, ensureIntegerArea, subtitleAreas]
  );

  // 计算新的字幕区域
  const calculateNewArea = useCallback((
    videoCoords: { x: number; y: number },
    startCoords: { x: number; y: number }
  ): SubtitleArea | null => {
    const { isDragging, resizeHandle, initialArea } = currentStateRef.current;
    
    if (!isDragging || !initialArea || !videoRef.current) return null;

    const videoDeltaX = videoCoords.x - startCoords.x;
    const videoDeltaY = videoCoords.y - startCoords.y;
    
    let newArea = { ...initialArea };
    
    if (resizeHandle) {
      // 调整大小
      switch (resizeHandle) {
        case 'nw':
          newArea.x = Math.max(0, Math.round(initialArea.x + videoDeltaX));
          newArea.y = Math.max(0, Math.round(initialArea.y + videoDeltaY));
          newArea.width = Math.max(50, Math.round(initialArea.width - videoDeltaX));
          newArea.height = Math.max(20, Math.round(initialArea.height - videoDeltaY));
          break;
        case 'ne':
          newArea.y = Math.max(0, Math.round(initialArea.y + videoDeltaY));
          newArea.width = Math.max(50, Math.round(initialArea.width + videoDeltaX));
          newArea.height = Math.max(20, Math.round(initialArea.height - videoDeltaY));
          break;
        case 'sw':
          newArea.x = Math.max(0, Math.round(initialArea.x + videoDeltaX));
          newArea.width = Math.max(50, Math.round(initialArea.width - videoDeltaX));
          newArea.height = Math.max(20, Math.round(initialArea.height + videoDeltaY));
          break;
        case 'se':
          newArea.width = Math.max(50, Math.round(initialArea.width + videoDeltaX));
          newArea.height = Math.max(20, Math.round(initialArea.height + videoDeltaY));
          break;
      }
    } else {
      // 移动位置
      newArea.x = Math.max(0, Math.round(initialArea.x + videoDeltaX));
      newArea.y = Math.max(0, Math.round(initialArea.y + videoDeltaY));
    }
    
    // 确保不超出视频边界
    const videoWidth = videoRef.current.videoWidth;
    const videoHeight = videoRef.current.videoHeight;
    
    newArea.x = Math.max(0, Math.min(newArea.x, videoWidth - 50));
    newArea.y = Math.max(0, Math.min(newArea.y, videoHeight - 20));
    newArea.width = Math.min(newArea.width, videoWidth - newArea.x);
    newArea.height = Math.min(newArea.height, videoHeight - newArea.y);
    
    return newArea;
  }, []);

  // 添加新的字幕区域
  const addSubtitleArea = useCallback(() => {
    if (!videoRef.current) return;
    
    const video = videoRef.current;
    const newArea: SubtitleArea = {
      id: generateId(),
      x: Math.round(video.videoWidth * 0.05),
      y: Math.round(video.videoHeight * 0.78),
      width: Math.round(video.videoWidth * 0.9),
      height: Math.round(video.videoHeight * 0.21),
      name: `字幕区域 ${subtitleAreas.length + 1}`,
      color: PRESET_COLORS[subtitleAreas.length % PRESET_COLORS.length],
    };
    
    onSubtitleAreasChange([...subtitleAreas, newArea]);
    setActiveAreaId(newArea.id);
  }, [subtitleAreas, onSubtitleAreasChange, generateId]);

  // 删除字幕区域
  const deleteSubtitleArea = useCallback((areaId: string) => {
    onSubtitleAreasChange(subtitleAreas.filter(area => area.id !== areaId));
    if (activeAreaId === areaId) {
      setActiveAreaId(null);
    }
  }, [subtitleAreas, onSubtitleAreasChange, activeAreaId]);

  // 更新字幕区域名称
  const updateAreaName = useCallback((areaId: string, name: string) => {
    onSubtitleAreasChange(subtitleAreas.map(area => 
      area.id === areaId ? { ...area, name } : area
    ));
  }, [subtitleAreas, onSubtitleAreasChange]);

  // 处理视频点击（开始添加新区域）
  const handleVideoClick = useCallback((e: React.MouseEvent) => {
    if (!isAddingArea || !videoRef.current) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    const videoCoords = getVideoCoordinates(e.clientX, e.clientY);
    const video = videoRef.current;
    
    // 创建一个默认大小的区域，从点击位置开始
    const newArea: SubtitleArea = {
      id: generateId(),
      x: Math.max(0, videoCoords.x - 100),
      y: Math.max(0, videoCoords.y - 25),
      width: Math.min(200, video.videoWidth - videoCoords.x + 100),
      height: Math.min(50, video.videoHeight - videoCoords.y + 25),
      name: `字幕区域 ${subtitleAreas.length + 1}`,
      color: PRESET_COLORS[subtitleAreas.length % PRESET_COLORS.length],
    };
    
    onSubtitleAreasChange([...subtitleAreas, newArea]);
    setActiveAreaId(newArea.id);
    setIsAddingArea(false);
  }, [isAddingArea, videoRef, getVideoCoordinates, subtitleAreas, onSubtitleAreasChange, generateId]);

  // 调整字幕区域
  const handleMouseDown = useCallback((e: React.MouseEvent, areaId: string, handle?: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    const area = subtitleAreas.find(a => a.id === areaId);
    if (!area || !videoRef.current) return;
    
    setIsDragging(true);
    setResizeHandle(handle || null);
    setDragStartPos({ x: e.clientX, y: e.clientY });
    setInitialArea({ ...area });
    setActiveAreaId(areaId);
    
    // 同时更新ref
    currentStateRef.current = {
      isDragging: true,
      resizeHandle: handle || null,
      dragStartPos: { x: e.clientX, y: e.clientY },
      initialArea: { ...area },
      activeAreaId: areaId,
    };
  }, [subtitleAreas]);

  // 处理鼠标移动
  const handleMouseMove = useCallback((e: MouseEvent) => {
    const { isDragging, dragStartPos, activeAreaId } = currentStateRef.current;
    
    if (!isDragging || !activeAreaId) return;
    
    e.preventDefault();
    
    const videoCoords = getVideoCoordinates(e.clientX, e.clientY);
    const startCoords = getVideoCoordinates(dragStartPos.x, dragStartPos.y);
    
    const newArea = calculateNewArea(videoCoords, startCoords);
    if (newArea) {
      newArea.id = activeAreaId;
      throttledUpdate(newArea);
    }
  }, [getVideoCoordinates, calculateNewArea, throttledUpdate]);

  // 处理鼠标释放
  const handleMouseUp = useCallback(() => {
    if (currentStateRef.current.isDragging) {
      setIsDragging(false);
      setResizeHandle(null);
      setInitialArea(null);
      
      currentStateRef.current = {
        isDragging: false,
        resizeHandle: null,
        dragStartPos: { x: 0, y: 0 },
        initialArea: null,
        activeAreaId: currentStateRef.current.activeAreaId,
      };
    }
  }, []);

  // 监听全局鼠标事件
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <>
      {/* 字幕区域列表控制面板 */}
      {config.detectionMode === 'manual' && (
        <div className="absolute top-2 left-2 bg-black/80 text-white p-3 rounded-lg max-w-xs max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">字幕区域</h3>
            <button
              onClick={addSubtitleArea}
              className="p-1 bg-green-600 hover:bg-green-700 rounded transition-colors"
              title="添加字幕区域"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {subtitleAreas.length === 0 ? (
            <p className="text-xs text-gray-300 mb-2">暂无字幕区域</p>
          ) : (
            <div className="space-y-2">
              {subtitleAreas.map((area, index) => (
                <div
                  key={area.id}
                  className={`p-2 rounded border transition-colors cursor-pointer ${
                    activeAreaId === area.id
                      ? 'bg-white/20 border-white/50'
                      : 'bg-white/10 border-white/20 hover:bg-white/15'
                  }`}
                  onClick={() => setActiveAreaId(area.id)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <input
                      type="text"
                      value={area.name || `字幕区域 ${index + 1}`}
                      onChange={(e) => updateAreaName(area.id, e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="text-xs bg-transparent border-b border-transparent hover:border-white/30 focus:border-white/50 focus:outline-none flex-1 mr-2"
                      placeholder={`字幕区域 ${index + 1}`}
                    />
                    <div className="flex items-center space-x-1">
                      <div
                        className="w-3 h-3 rounded border border-white/50"
                        style={{ backgroundColor: area.color || PRESET_COLORS[index % PRESET_COLORS.length] }}
                      />
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSubtitleArea(area.id);
                        }}
                        className="p-1 hover:bg-red-600 rounded transition-colors"
                        title="删除"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                  <div className="text-xs text-gray-300">
                    {Math.round(area.width)}×{Math.round(area.height)} @ ({Math.round(area.x)}, {Math.round(area.y)})
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-3 pt-2 border-t border-white/20">
            <button
              onClick={() => setIsAddingArea(!isAddingArea)}
              className={`text-xs px-2 py-1 rounded transition-colors w-full ${
                isAddingArea
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'bg-gray-600 hover:bg-gray-700'
              }`}
            >
              {isAddingArea ? '点击视频添加区域' : '点击添加模式'}
            </button>
          </div>
        </div>
      )}

      {/* 字幕区域选择框 */}
      {config.detectionMode === 'manual' && subtitleAreas.map((area, index) => {
        const isActive = activeAreaId === area.id;
        const color = area.color || PRESET_COLORS[index % PRESET_COLORS.length];
        
        if (!videoRef.current) return null;
        
        const video = videoRef.current;
        const selectionStyle = {
          position: 'absolute' as const,
          border: `3px solid ${color}`,
          backgroundColor: `${color}33`, // 添加透明度
          left: `${(area.x / video.videoWidth) * 100}%`,
          top: `${(area.y / video.videoHeight) * 100}%`,
          width: `${(area.width / video.videoWidth) * 100}%`,
          height: `${(area.height / video.videoHeight) * 100}%`,
          cursor: 'move',
          zIndex: isActive ? 1010 : 1000,
          pointerEvents: 'auto' as const,
          transition: isActive ? 'none' : 'border-color 0.2s ease',
        };

        return (
          <div
            key={area.id}
            className={`subtitle-selection ${isActive ? 'active' : ''}`}
            style={selectionStyle}
            onMouseDown={(e) => handleMouseDown(e, area.id)}
            onClick={(e) => {
              e.stopPropagation();
              setActiveAreaId(area.id);
            }}
          >
            {/* 区域标签 */}
            {isActive && (
              <div
                className="absolute -top-6 left-0 text-xs px-1 py-0.5 rounded text-white whitespace-nowrap"
                style={{ backgroundColor: color }}
              >
                {area.name || `字幕区域 ${index + 1}`}
              </div>
            )}

            {/* 调整大小的手柄 - 只在激活状态下显示 */}
            {isActive && (
              <>
                <div 
                  className="resize-handle nw" 
                  onMouseDown={(e) => handleMouseDown(e, area.id, 'nw')}
                  style={{ backgroundColor: color }}
                />
                <div 
                  className="resize-handle ne" 
                  onMouseDown={(e) => handleMouseDown(e, area.id, 'ne')}
                  style={{ backgroundColor: color }}
                />
                <div 
                  className="resize-handle sw" 
                  onMouseDown={(e) => handleMouseDown(e, area.id, 'sw')}
                  style={{ backgroundColor: color }}
                />
                <div 
                  className="resize-handle se" 
                  onMouseDown={(e) => handleMouseDown(e, area.id, 'se')}
                  style={{ backgroundColor: color }}
                />
              </>
            )}
          </div>
        );
      })}

      {/* 视频点击覆盖层（用于添加新区域） */}
      {isAddingArea && videoRef.current && (
        <div
          className="absolute inset-0 cursor-crosshair z-999"
          style={{ zIndex: 999 }}
          onClick={handleVideoClick}
        />
      )}

      {/* 调试信息 */}
      {false && config.detectionMode === 'manual' && (
        <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs p-2 rounded">
          <div>区域数量: {subtitleAreas.length}</div>
          <div>激活区域: {activeAreaId || '无'}</div>
          <div>添加模式: {isAddingArea ? '开启' : '关闭'}</div>
          <div>视频: {videoRef.current ? 'loaded' : 'not loaded'}</div>
          {videoRef.current && (
            <div>Video Size: {videoRef.current.videoWidth}x{videoRef.current.videoHeight}</div>
          )}
        </div>
      )}
    </>
  );
};
