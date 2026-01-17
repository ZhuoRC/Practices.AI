import React, { useRef, useState, useCallback } from 'react';
import { uploadFile, UploadResponse } from '../services/api';

// Convert filepath to URL for preview
function getPreviewUrl(filepath: string): string {
  const filename = filepath.split(/[/\\]/).pop();
  return `/uploads/${filename}`;
}

interface VideoUploaderProps {
  onUpload: (response: UploadResponse) => void;
  uploadedFile: UploadResponse | null;
  onRemove: () => void;
}

export const VideoUploader: React.FC<VideoUploaderProps> = ({
  onUpload,
  uploadedFile,
  onRemove,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(async (file: File) => {
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm'];
    const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];

    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(ext)) {
      setError('Please upload a valid video file (MP4, AVI, MOV, MKV, WebM)');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadFile(file);
      onUpload(response);
    } catch (err) {
      setError('Failed to upload video. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  }, [onUpload]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  if (uploadedFile) {
    return (
      <div className="card">
        <h2>Target Video</h2>
        <div className="file-info">
          <span className="filename">{uploadedFile.filename}</span>
          <button className="remove-btn" onClick={onRemove}>
            &times;
          </button>
        </div>
        <div className="preview-container">
          <video
            src={getPreviewUrl(uploadedFile.filepath)}
            controls
            style={{ maxHeight: '300px' }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Upload Target Video</h2>
      <div
        className={`upload-area ${isDragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          accept="video/*"
          onChange={handleInputChange}
        />
        {isUploading ? (
          <p>Uploading...</p>
        ) : (
          <>
            <p>Drag and drop a video file here</p>
            <p>or click to select</p>
            <p style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
              Supported: MP4, AVI, MOV, MKV, WebM
            </p>
          </>
        )}
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};
