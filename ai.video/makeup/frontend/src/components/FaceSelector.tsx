import React, { useRef, useState, useCallback } from 'react';
import { uploadFile, UploadResponse } from '../services/api';

// Convert filepath to URL for preview
function getPreviewUrl(filepath: string): string {
  const filename = filepath.split(/[/\\]/).pop();
  return `/uploads/${filename}`;
}

interface FaceSelectorProps {
  onUpload: (response: UploadResponse) => void;
  uploadedFile: UploadResponse | null;
  onRemove: () => void;
}

export const FaceSelector: React.FC<FaceSelectorProps> = ({
  onUpload,
  uploadedFile,
  onRemove,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(async (file: File) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp'];

    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(ext)) {
      setError('Please upload a valid image file (JPG, PNG, WebP)');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadFile(file);
      onUpload(response);
    } catch (err) {
      setError('Failed to upload image. Please try again.');
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
        <h2>Source Face</h2>
        <div className="file-info">
          <span className="filename">{uploadedFile.filename}</span>
          <button className="remove-btn" onClick={onRemove}>
            &times;
          </button>
        </div>
        <div className="preview-container">
          <img
            src={getPreviewUrl(uploadedFile.filepath)}
            alt="Source face"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Upload Source Face</h2>
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
          accept="image/*"
          onChange={handleInputChange}
        />
        {isUploading ? (
          <p>Uploading...</p>
        ) : (
          <>
            <p>Drag and drop a face image here</p>
            <p>or click to select</p>
            <p style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
              Supported: JPG, PNG, WebP
            </p>
          </>
        )}
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};
