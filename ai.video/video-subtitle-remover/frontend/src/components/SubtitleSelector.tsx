import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ProcessConfig, SubtitleArea } from '../types';

interface SubtitleSelectorProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  config: ProcessConfig;
  subtitleArea: SubtitleArea | null;
  onSubtitleAreaChange: (area: SubtitleArea | null) => void;
}

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
  subtitleArea,
  onSubtitleAreaChange,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [resizeHandle, setResizeHandle] = useState<string | null>(null);
  const [dragStartPos, setDragStartPos] = useState({ x: 0, y: 0 });
  const [initialArea, setInitialArea] = useState<SubtitleArea | null>(null);
  
  // 使用ref来避免频繁的状态更新
  const currentStateRef = useRef({
    isDragging: false,
    resizeHandle: null as string | null,
    dragStartPos: { x: 0, y: 0 },
    initialArea: null as SubtitleArea | null,
  });

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
      x: Math.round(area.x),
      y: Math.round(area.y),
      width: Math.round(area.width),
      height: Math.round(area.height),
    };
  }, []);

  // 节流后的更新函数
  const throttledUpdate = useCallback(
    throttle((newArea: SubtitleArea) => {
      onSubtitleAreaChange(ensureIntegerArea(newArea));
    }, 16), // 约60fps
    [onSubtitleAreaChange, ensureIntegerArea]
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

  // 调整字幕区域
  const handleMouseDown = useCallback((e: React.MouseEvent, handle?: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!videoRef.current || !subtitleArea) return;
    
    setIsDragging(true);
    setResizeHandle(handle || null);
    setDragStartPos({ x: e.clientX, y: e.clientY });
    setInitialArea({ ...subtitleArea });
    
    // 同时更新ref
    currentStateRef.current = {
      isDragging: true,
      resizeHandle: handle || null,
      dragStartPos: { x: e.clientX, y: e.clientY },
      initialArea: { ...subtitleArea },
    };
  }, [subtitleArea]);

  // 处理鼠标移动
  const handleMouseMove = useCallback((e: MouseEvent) => {
    const { isDragging, dragStartPos } = currentStateRef.current;
    
    if (!isDragging) return;
    
    e.preventDefault();
    
    const videoCoords = getVideoCoordinates(e.clientX, e.clientY);
    const startCoords = getVideoCoordinates(dragStartPos.x, dragStartPos.y);
    
    const newArea = calculateNewArea(videoCoords, startCoords);
    if (newArea) {
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

  // 计算样式
  const selectionStyle = React.useMemo(() => {
    if (config.detectionMode !== 'manual' || !subtitleArea || !videoRef.current) {
      return {};
    }
    
    const video = videoRef.current;
    return {
      position: 'absolute' as const,
      border: '3px solid #22c55e',
      backgroundColor: 'rgba(34, 197, 94, 0.3)',
      left: `${(subtitleArea.x / video.videoWidth) * 100}%`,
      top: `${(subtitleArea.y / video.videoHeight) * 100}%`,
      width: `${(subtitleArea.width / video.videoWidth) * 100}%`,
      height: `${(subtitleArea.height / video.videoHeight) * 100}%`,
      cursor: 'move',
      zIndex: 1000,
      pointerEvents: 'auto' as const,
    };
  }, [config.detectionMode, subtitleArea]);

  return (
    <>
      {/* 字幕区域选择框 */}
      {config.detectionMode === 'manual' && subtitleArea && (
        <div
          className="subtitle-selection"
          style={selectionStyle}
          onMouseDown={(e) => handleMouseDown(e)}
        >
          {/* 调整大小的手柄 */}
          <div className="resize-handle nw" onMouseDown={(e) => handleMouseDown(e, 'nw')} />
          <div className="resize-handle ne" onMouseDown={(e) => handleMouseDown(e, 'ne')} />
          <div className="resize-handle sw" onMouseDown={(e) => handleMouseDown(e, 'sw')} />
          <div className="resize-handle se" onMouseDown={(e) => handleMouseDown(e, 'se')} />
        </div>
      )}

      {/* 调试信息 */}
      {config.detectionMode === 'manual' && subtitleArea && (
        <div className="absolute top-2 left-2 bg-black/50 text-white text-xs p-2 rounded">
          <div>Mode: {config.detectionMode}</div>
          <div>SubtitleArea: {subtitleArea ? 'exists' : 'null'}</div>
          <div>Video: {videoRef.current ? 'loaded' : 'not loaded'}</div>
          {videoRef.current && (
            <div>Video Size: {videoRef.current.videoWidth}x{videoRef.current.videoHeight}</div>
          )}
          {subtitleArea && (
            <>
              <div>X: {Math.round(subtitleArea.x)}</div>
              <div>Y: {Math.round(subtitleArea.y)}</div>
              <div>W: {Math.round(subtitleArea.width)}</div>
              <div>H: {Math.round(subtitleArea.height)}</div>
            </>
          )}
        </div>
      )}
    </>
  );
};
