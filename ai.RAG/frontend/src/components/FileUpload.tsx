import React, { useState } from 'react';
import { Upload, message, Card, Button } from 'antd';
import { InboxOutlined, UploadOutlined } from '@ant-design/icons';
import { documentAPI } from '../services/api';

const { Dragger } = Upload;

interface FileUploadProps {
  onUploadSuccess: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    // Validate file type
    if (!file.name.endsWith('.pdf')) {
      message.error('Only PDF files are supported!');
      return false;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      message.error('File size cannot exceed 50MB!');
      return false;
    }

    setUploading(true);

    try {
      const result = await documentAPI.uploadDocument(file);

      message.success(`File uploaded successfully! Generated ${result.total_chunks} document chunks`);
      onUploadSuccess();
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || 'File upload failed';
      message.error(errorMsg);
    } finally {
      setUploading(false);
    }

    return false; // Prevent default upload behavior
  };

  return (
    <Card title="Upload PDF Document" style={{ marginBottom: 16 }}>
      <Dragger
        name="file"
        accept=".pdf"
        multiple={false}
        beforeUpload={handleUpload}
        showUploadList={false}
        disabled={uploading}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Click or drag PDF file to this area to upload</p>
        <p className="ant-upload-hint">
          Supports single file upload, maximum 50MB
        </p>
      </Dragger>

      {uploading && (
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Button type="primary" loading>
            Uploading...
          </Button>
        </div>
      )}
    </Card>
  );
};

export default FileUpload;
