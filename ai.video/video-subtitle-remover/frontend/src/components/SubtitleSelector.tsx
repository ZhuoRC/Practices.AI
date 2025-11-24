import React, { useState, useEffect } from 'react';
import { ProcessConfig, SubtitleArea } from '../types';

interface SubtitleSelectorProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  config: ProcessConfig;
  subtitleArea: SubtitleArea | null;
  onSubtitleAreaChange: (area: SubtitleArea | null) => void;
}

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

  // 获取视频坐标
  const getVideoCoordinates = (clientX: number, clientY: number) => {
    if (!videoRef.current) return { x: 0, y: 0 };
    
    const rect = videoRef.current.getBoundingClientRect();
    const scaleX = videoRef.current.videoWidth / rect.width;
    const scaleY = videoRef.current.videoHeight / rect.height;
    
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  };

  // 调整字幕区域
  const handleMouseDown = (e: React.MouseEvent, handle?: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!videoRef.current || !subtitleArea) return;
    
    setIsDragging(true);
    setResizeHandle(handle || null);
    setDragStartPos({ x: e.clientX, y: e.clientY });
    setInitialArea({ ...subtitleArea });
  };

  // 处理鼠标移动
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !videoRef.current || !initialArea) return;

    e.preventDefault();

    // 转换为视频坐标
    const videoCoords = getVideoCoordinates(e.clientX, e.clientY);
    const startCoords = getVideoCoordinates(dragStartPos.x, dragStartPos.y);

    requestAnimationFrame(() => {
      if (resizeHandle) {
        // 调整大小
        const videoDeltaX = videoCoords.x - startCoords.x;
        const videoDeltaY = videoCoords.y - startCoords.y;
        
        let newArea = { ...initialArea };
        
        switch (resizeHandle) {
          case 'nw':
            newArea.x = Math.max(0, initialArea.x + videoDeltaX);
            newArea.y = Math.max(0, initialArea.y + videoDeltaY);
            newArea.width = Math.max(50, initialArea.width - videoDeltaX);
            newArea.height = Math.max(20, initialArea.height - videoDeltaY);
            break;
          case 'ne':
            newArea.y = Math.max(0, initialArea.y + videoDeltaY);
            newArea.width = Math.max(50, initialArea.width + videoDeltaX);
            newArea.height = Math.max(20, initialArea.height - videoDeltaY);
            break;
          case 'sw':
            newArea.x = Math.max(0, initialArea.x + videoDeltaX);
            newArea.width = Math.max(50, initialArea.width - videoDeltaX);
            newArea.height = Math.max(20, initialArea.height + videoDeltaY);
            break;
          case 'se':
            newArea.width = Math.max(50, initialArea.width + videoDeltaX);
            newArea.height = Math.max(20, initialArea.height + videoDeltaY);
            break;
        }
        
        // 确保不超出视频边界
        if (videoRef.current) {
          newArea.x = Math.max(0, Math.min(newArea.x, videoRef.current.videoWidth - 50));
          newArea.y = Math.max(0, Math.min(newArea.y, videoRef.current.videoHeight - 20));
          newArea.width = Math.min(newArea.width, videoRef.current.videoWidth - newArea.x);
          newArea.height = Math.min(newArea.height, videoRef.current.videoHeight - newArea.y);
        }
        
        onSubtitleAreaChange(newArea);
      } else {
        // 移动位置
        const videoDeltaX = videoCoords.x - startCoords.x;
        const videoDeltaY = videoCoords.y - startCoords.y;
        
        let newX = Math.max(0, initialArea.x + videoDeltaX);
        let newY = Math.max(0, initialArea.y + videoDeltaY);
        
        // 确保不超出视频边界
        if (videoRef.current) {
          newX = Math.max(0, Math.min(newX, videoRef.current.videoWidth - initialArea.width));
          newY = Math.max(0, Math.min(newY, videoRef.current.videoHeight - initialArea.height));
        }
        
        onSubtitleAreaChange({
          ...initialArea,
          x: newX,
          y: newY,
        });
      }
    });
  };

  // 处理鼠标释放
  const handleMouseUp = () => {
    setIsDragging(false);
    setResizeHandle(null);
    setInitialArea(null);
  };

  // 监听全局鼠标事件
  useEffect(() => {
    const handleGlobalMouseMove = (e: MouseEvent) => {
      if (!isDragging || !videoRef.current || !initialArea) return;
      
      e.preventDefault();

      const videoCoords = getVideoCoordinates(e.clientX, e.clientY);
      const startCoords = getVideoCoordinates(dragStartPos.x, dragStartPos.y);

      requestAnimationFrame(() => {
        if (resizeHandle) {
          const videoDeltaX = videoCoords.x - startCoords.x;
          const videoDeltaY = videoCoords.y - startCoords.y;
          
          let newArea = { ...initialArea };
          
          switch (resizeHandle) {
            case 'nw':
              newArea.x = Math.max(0, initialArea.x + videoDeltaX);
              newArea.y = Math.max(0, initialArea.y + videoDeltaY);
              newArea.width = Math.max(50, initialArea.width - videoDeltaX);
              newArea.height = Math.max(20, initialArea.height - videoDeltaY);
              break;
            case 'ne':
              newArea.y = Math.max(0, initialArea.y + videoDeltaY);
              newArea.width = Math.max(50, initialArea.width + videoDeltaX);
              newArea.height = Math.max(20, initialArea.height - videoDeltaY);
              break;
            case 'sw':
              newArea.x = Math.max(0, initialArea.x + videoDeltaX);
              newArea.width = Math.max(50, initialArea.width - videoDeltaX);
              newArea.height = Math.max(20, initialArea.height + videoDeltaY);
              break;
            case 'se':
              newArea.width = Math.max(50, initialArea.width + videoDeltaX);
              newArea.height = Math.max(20, initialArea.height + videoDeltaY);
              break;
          }
          
          if (videoRef.current) {
            newArea.x = Math.max(0, Math.min(newArea.x, videoRef.current.videoWidth - 50));
            newArea.y = Math.max(0, Math.min(newArea.y, videoRef.current.videoHeight - 20));
            newArea.width = Math.min(newArea.width, videoRef.current.videoWidth - newArea.x);
            newArea.height = Math.min(newArea.height, videoRef.current.videoHeight - newArea.y);
          }
          
          onSubtitleAreaChange(newArea);
        } else {
          const videoDeltaX = videoCoords.x - startCoords.x;
          const videoDeltaY = videoCoords.y - startCoords.y;
          
          let newX = Math.max(0, initialArea.x + videoDeltaX);
          let newY = Math.max(0, initialArea.y + videoDeltaY);
          
          if (videoRef.current) {
            newX = Math.max(0, Math.min(newX, videoRef.current.videoWidth - initialArea.width));
            newY = Math.max(0, Math.min(newY, videoRef.current.videoHeight - initialArea.height));
          }
          
          onSubtitleAreaChange({
            ...initialArea,
            x: newX,
            y: newY,
          });
        }
      });
    };

    const handleGlobalMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
        setResizeHandle(null);
        setInitialArea(null);
      }
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleGlobalMouseMove);
      document.addEventListener('mouseup', handleGlobalMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleGlobalMouseMove);
        document.removeEventListener('mouseup', handleGlobalMouseUp);
      };
    }
  }, [isDragging, resizeHandle, dragStartPos, initialArea, onSubtitleAreaChange]);

  return (
    <>
      {/* 字幕区域选择框 */}
      {config.detectionMode === 'manual' && subtitleArea && (
        <div
          className="subtitle-selection"
          style={{
            position: 'absolute',
            border: '3px solid #22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.3)',
            left: videoRef.current ? `${(subtitleArea.x / videoRef.current.videoWidth) * 100}%` : '10%',
            top: videoRef.current ? `${(subtitleArea.y / videoRef.current.videoHeight) * 100}%` : '70%',
            width: videoRef.current ? `${(subtitleArea.width / videoRef.current.videoWidth) * 100}%` : '80%',
            height: videoRef.current ? `${(subtitleArea.height / videoRef.current.videoHeight) * 100}%` : '20%',
            cursor: 'move',
            zIndex: 1000,
            pointerEvents: videoRef.current ? 'auto' : 'none',
          }}
          onMouseDown={(e) => handleMouseDown(e)}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* 调整大小的手柄 */}
          <div 
            style={{
              position: 'absolute',
              width: '12px',
              height: '12px',
              backgroundColor: '#22c55e',
              borderRadius: '50%',
              top: '-6px',
              left: '-6px',
              cursor: 'nw-resize',
              zIndex: 1001
            }}
            onMouseDown={(e) => handleMouseDown(e, 'nw')} 
          />
          <div 
            style={{
              position: 'absolute',
              width: '12px',
              height: '12px',
              backgroundColor: '#22c55e',
              borderRadius: '50%',
              top: '-6px',
              right: '-6px',
              cursor: 'ne-resize',
              zIndex: 1001
            }}
            onMouseDown={(e) => handleMouseDown(e, 'ne')} 
          />
          <div 
            style={{
              position: 'absolute',
              width: '12px',
              height: '12px',
              backgroundColor: '#22c55e',
              borderRadius: '50%',
              bottom: '-6px',
              left: '-6px',
              cursor: 'sw-resize',
              zIndex: 1001
            }}
            onMouseDown={(e) => handleMouseDown(e, 'sw')} 
          />
          <div 
            style={{
              position: 'absolute',
              width: '12px',
              height: '12px',
              backgroundColor: '#22c55e',
              borderRadius: '50%',
              bottom: '-6px',
              right: '-6px',
              cursor: 'se-resize',
              zIndex: 1001
            }}
            onMouseDown={(e) => handleMouseDown(e, 'se')} 
          />
        </div>
      )}

      {/* 调试信息 */}
      {config.detectionMode === 'manual' && typeof process !== 'undefined' && process.env.NODE_ENV === 'development' && (
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
