import React, { useState, useCallback } from 'react';
import { VideoUploader } from '../components/VideoUploader';
import { FaceSelector } from '../components/FaceSelector';
import { ProcessingStatus } from '../components/ProcessingStatus';
import { VideoPreview } from '../components/VideoPreview';
import {
  UploadResponse,
  TaskResponse,
  startFaceSwap,
  pollTaskStatus,
} from '../services/api';

export const Home: React.FC = () => {
  const [videoFile, setVideoFile] = useState<UploadResponse | null>(null);
  const [faceFile, setFaceFile] = useState<UploadResponse | null>(null);
  const [currentTask, setCurrentTask] = useState<TaskResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVideoUpload = useCallback((response: UploadResponse) => {
    setVideoFile(response);
    setError(null);
  }, []);

  const handleFaceUpload = useCallback((response: UploadResponse) => {
    setFaceFile(response);
    setError(null);
  }, []);

  const handleRemoveVideo = useCallback(() => {
    setVideoFile(null);
  }, []);

  const handleRemoveFace = useCallback(() => {
    setFaceFile(null);
  }, []);

  const handleStartProcessing = async () => {
    if (!videoFile || !faceFile) {
      setError('Please upload both a video and a face image');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setCurrentTask(null);

    try {
      // Start the face swap process
      const response = await startFaceSwap(
        faceFile.filepath,
        videoFile.filepath
      );

      // Poll for task status
      await pollTaskStatus(
        response.task_id,
        (task) => {
          setCurrentTask(task);
        },
        1000
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setVideoFile(null);
    setFaceFile(null);
    setCurrentTask(null);
    setError(null);
    setIsProcessing(false);
  };

  const canStartProcessing = videoFile && faceFile && !isProcessing;
  const showResult = currentTask?.status === 'completed';

  return (
    <div className="container">
      <h1>FaceFusion - Video Face Swap</h1>

      <div className="grid">
        <VideoUploader
          onUpload={handleVideoUpload}
          uploadedFile={videoFile}
          onRemove={handleRemoveVideo}
        />
        <FaceSelector
          onUpload={handleFaceUpload}
          uploadedFile={faceFile}
          onRemove={handleRemoveFace}
        />
      </div>

      {error && (
        <div className="card">
          <div className="error-message">{error}</div>
        </div>
      )}

      <div className="card" style={{ textAlign: 'center' }}>
        <button
          className="btn btn-primary"
          onClick={handleStartProcessing}
          disabled={!canStartProcessing}
          style={{ marginRight: '12px' }}
        >
          {isProcessing ? 'Processing...' : 'Start Face Swap'}
        </button>
        <button className="btn btn-secondary" onClick={handleReset}>
          Reset
        </button>
      </div>

      <ProcessingStatus task={currentTask} isProcessing={isProcessing} />

      {showResult && <VideoPreview task={currentTask} />}
    </div>
  );
};
