import React, { useEffect, useState, useRef } from 'react';
import { Card, Table, Button, Popconfirm, message, Tag, Checkbox, Modal, Upload, Input, Progress, Tooltip } from 'antd';
import { DeleteOutlined, ReloadOutlined, FileTextOutlined, UploadOutlined, InboxOutlined } from '@ant-design/icons';
import { documentAPI, Document, TaskStatus } from '../services/api';

const { Dragger } = Upload;

interface DocumentListProps {
  selectedDocIds: string[];
  onSelectionChange: (docIds: string[]) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  selectedDocIds,
  onSelectionChange
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filename, setFilename] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Background tasks (tasks being monitored after modal is closed)
  const [backgroundTasks, setBackgroundTasks] = useState<Map<string, { filename: string; progress: number }>>(new Map());
  const backgroundPollRef = useRef<NodeJS.Timeout | null>(null);

  // Filename filter
  const [filenameFilter, setFilenameFilter] = useState('');

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const docs = await documentAPI.listDocuments();

      // Debug: log first 3 documents to check data
      console.log('📄 First 3 documents (before sort):', docs.slice(0, 3).map(d => ({
        filename: d.filename,
        upload_time: d.upload_time,
        upload_time_iso: d.upload_time_iso
      })));

      // Sort by upload time ISO timestamp (newest first)
      const sortedDocs = docs.sort((a, b) => {
        // Use upload_time_iso for accurate sorting
        const timeA = new Date(a.upload_time_iso).getTime();
        const timeB = new Date(b.upload_time_iso).getTime();

        // Debug: log comparison
        if (docs.indexOf(a) < 3 || docs.indexOf(b) < 3) {
          console.log(`Comparing: ${a.filename} (${a.upload_time_iso}, ${timeA}) vs ${b.filename} (${b.upload_time_iso}, ${timeB}) = ${timeB - timeA}`);
        }

        return timeB - timeA; // Descending order (newest first)
      });

      // Debug: log first 3 after sort
      console.log('📄 First 3 documents (after sort):', sortedDocs.slice(0, 3).map(d => ({
        filename: d.filename,
        upload_time: d.upload_time,
        upload_time_iso: d.upload_time_iso
      })));

      setDocuments(sortedDocs);
    } catch (error) {
      message.error('Failed to load document list');
      console.error('Load documents error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleDelete = async (documentId: string) => {
    try {
      await documentAPI.deleteDocument(documentId);
      message.success('Document deleted successfully');
      loadDocuments();
    } catch (error) {
      message.error('Failed to delete document');
      console.error('Delete document error:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const handleSelectChange = (docId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedDocIds, docId]);
    } else {
      onSelectionChange(selectedDocIds.filter(id => id !== docId));
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(filteredDocuments.map(doc => doc.document_id));
    } else {
      onSelectionChange([]);
    }
  };

  // Filter documents by filename
  const filteredDocuments = documents.filter(doc =>
    doc.filename.toLowerCase().includes(filenameFilter.toLowerCase())
  );

  const isAllSelected = filteredDocuments.length > 0 && selectedDocIds.length === filteredDocuments.length;
  const isIndeterminate = selectedDocIds.length > 0 && selectedDocIds.length < filteredDocuments.length;

  const handleFileSelect = (file: File) => {
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

    setSelectedFile(file);
    setFilename(file.name);
    return false; // Prevent default upload behavior
  };

  const pollTaskStatus = async (taskId: string, isModalOpen: boolean = true) => {
    try {
      const taskStatus = await documentAPI.getTaskStatus(taskId);

      // Update progress if modal is open
      if (isModalOpen) {
        setUploadProgress(taskStatus.progress);
        setUploadStatus(taskStatus.message);
      }

      if (taskStatus.status === 'completed') {
        // Stop polling
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }

        message.success(`File "${taskStatus.filename}" uploaded successfully! Generated ${taskStatus.result?.total_chunks || 0} document chunks`);

        // Remove from background tasks
        setBackgroundTasks(prev => {
          const newTasks = new Map(prev);
          newTasks.delete(taskId);
          return newTasks;
        });

        // Close modal and refresh if modal is open
        if (isModalOpen) {
          setTimeout(() => {
            setIsModalVisible(false);
            setSelectedFile(null);
            setFilename('');
            setUploading(false);
            setUploadProgress(0);
            setUploadStatus('');
            setCurrentTaskId(null);
          }, 1000);
        }

        // Always refresh documents list
        loadDocuments();
      } else if (taskStatus.status === 'failed') {
        // Stop polling
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }

        message.error(`File "${taskStatus.filename}" upload failed: ${taskStatus.error || 'Unknown error'}`);

        // Remove from background tasks
        setBackgroundTasks(prev => {
          const newTasks = new Map(prev);
          newTasks.delete(taskId);
          return newTasks;
        });

        if (isModalOpen) {
          setUploading(false);
          setUploadProgress(0);
          setUploadStatus('');
          setCurrentTaskId(null);
        }
      } else {
        // Update background task progress
        setBackgroundTasks(prev => {
          const newTasks = new Map(prev);
          newTasks.set(taskId, {
            filename: taskStatus.filename,
            progress: taskStatus.progress
          });
          return newTasks;
        });
      }
    } catch (error: any) {
      console.error('Error polling task status:', error);

      // Stop polling on error
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }

      message.error('Failed to check upload status');

      if (isModalOpen) {
        setUploading(false);
        setCurrentTaskId(null);
      }
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) {
      message.error('Please select a file to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadStatus('Uploading file...');

    try {
      const result = await documentAPI.uploadDocument(selectedFile);

      setCurrentTaskId(result.task_id);
      setUploadStatus('Processing document...');

      // Start polling task status
      pollIntervalRef.current = setInterval(() => {
        pollTaskStatus(result.task_id);
      }, 1000); // Poll every 1 second
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || 'File upload failed';
      message.error(errorMsg);
      setUploading(false);
      setUploadProgress(0);
      setUploadStatus('');
    }
  };

  // Background polling for all tasks
  const pollBackgroundTasks = async () => {
    for (const taskId of backgroundTasks.keys()) {
      await pollTaskStatus(taskId, false);
    }
  };

  // Start background polling
  const startBackgroundPolling = () => {
    if (!backgroundPollRef.current) {
      backgroundPollRef.current = setInterval(() => {
        pollBackgroundTasks();
      }, 2000); // Poll every 2 seconds
    }
  };

  // Stop background polling if no tasks
  useEffect(() => {
    if (backgroundTasks.size === 0 && backgroundPollRef.current) {
      clearInterval(backgroundPollRef.current);
      backgroundPollRef.current = null;
    } else if (backgroundTasks.size > 0 && !backgroundPollRef.current) {
      startBackgroundPolling();
    }
  }, [backgroundTasks]);

  const handleModalCancel = () => {
    // If uploading, move to background and continue monitoring
    if (uploading && currentTaskId) {
      // Add to background tasks
      setBackgroundTasks(prev => {
        const newTasks = new Map(prev);
        newTasks.set(currentTaskId, {
          filename: filename || selectedFile?.name || 'Unknown',
          progress: uploadProgress
        });
        return newTasks;
      });

      // Stop modal polling
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }

      message.info('Upload continues in background. You can continue working.');
    }

    // Reset modal state
    setIsModalVisible(false);
    setSelectedFile(null);
    setFilename('');
    setUploadProgress(0);
    setUploadStatus('');
    setUploading(false);
    setCurrentTaskId(null);
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
      if (backgroundPollRef.current) {
        clearInterval(backgroundPollRef.current);
      }
    };
  }, []);

  const columns = [
    {
      title: 'Action',
      key: 'action',
      width: 60,
      render: (_: any, record: Document) => (
        <Popconfirm
          title="Delete this document?"
          onConfirm={() => handleDelete(record.document_id)}
          okText="Yes"
          cancelText="No"
        >
          <Button type="link" danger icon={<DeleteOutlined />} size="small" />
        </Popconfirm>
      ),
    },
    {
      title: () => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>Filename</span>
          <Input
            placeholder="Filter..."
            value={filenameFilter}
            onChange={(e) => setFilenameFilter(e.target.value)}
            onClick={(e) => e.stopPropagation()}
            style={{ width: 120, fontSize: 12 }}
            size="small"
            allowClear
          />
        </div>
      ),
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
      render: (text: string) => (
        <span style={{ display: 'flex', alignItems: 'center' }}>
          <FileTextOutlined style={{ marginRight: 6, color: '#1890ff', fontSize: 13, flexShrink: 0 }} />
          <span style={{ fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{text}</span>
        </span>
      ),
    },
    {
      title: 'Size',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => <span style={{ fontSize: 12 }}>{formatFileSize(size)}</span>,
      width: 80,
      ellipsis: true,
    },
    {
      title: 'Chunks',
      dataIndex: 'total_chunks',
      key: 'total_chunks',
      render: (chunks: number) => <Tag color="blue" style={{ fontSize: 11, margin: 0 }}>{chunks}</Tag>,
      width: 70,
    },
    {
      title: () => (
        <Checkbox
          checked={isAllSelected}
          indeterminate={isIndeterminate}
          onChange={(e) => handleSelectAll(e.target.checked)}
        />
      ),
      key: 'select',
      width: 45,
      fixed: 'right' as const,
      render: (_: any, record: Document) => (
        <Checkbox
          checked={selectedDocIds.includes(record.document_id)}
          onChange={(e) => handleSelectChange(record.document_id, e.target.checked)}
        />
      ),
    },
  ];

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span>
            {`Document Library (${filteredDocuments.length}`}
            {filenameFilter && documents.length !== filteredDocuments.length && ` / ${documents.length}`}
            {`)` }
          </span>
          {backgroundTasks.size > 0 && (
            <Tooltip
              title={
                <div>
                  {Array.from(backgroundTasks.entries()).map(([taskId, task]) => (
                    <div key={taskId} style={{ marginBottom: '4px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold' }}>{task.filename}</div>
                      <Progress
                        percent={task.progress}
                        size="small"
                        status="active"
                        style={{ marginTop: '4px' }}
                      />
                    </div>
                  ))}
                </div>
              }
            >
              <Tag color="processing" style={{ cursor: 'pointer' }}>
                {backgroundTasks.size} uploading
              </Tag>
            </Tooltip>
          )}
        </div>
      }
      extra={
        <div style={{ display: 'flex', gap: '8px' }}>
          <Button
            icon={<UploadOutlined />}
            onClick={() => setIsModalVisible(true)}
          >
            Upload
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadDocuments}
            loading={loading}
          >
            Refresh
          </Button>
        </div>
      }
    >
      <Table
        columns={columns}
        dataSource={filteredDocuments}
        rowKey="document_id"
        loading={loading}
        size="small"
        pagination={{
          pageSize: 10,
          size: 'small',
          showTotal: (total) => {
            const selectedCount = selectedDocIds.length;
            if (selectedCount > 0) {
              return `Total ${total} documents (${selectedCount} selected for query)`;
            }
            return `Total ${total} documents (querying all)`;
          },
        }}
      />

      <Modal
        title="Upload PDF Document"
        open={isModalVisible}
        onCancel={handleModalCancel}
        footer={null}
        width={600}
        closable={true}
        maskClosable={!uploading}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Drag Box */}
          <Dragger
            name="file"
            accept=".pdf"
            multiple={false}
            beforeUpload={handleFileSelect}
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

          {/* Filename Input */}
          <Input
            placeholder="Filename"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            disabled={uploading}
            addonBefore="Filename:"
          />

          {/* Progress Indicator */}
          {uploading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Progress percent={uploadProgress} status={uploadProgress === 100 ? 'success' : 'active'} />
              <div style={{ textAlign: 'center', color: '#666', fontSize: '14px' }}>
                {uploadStatus}
              </div>
              <div style={{
                textAlign: 'center',
                color: '#666',
                fontSize: '12px',
                padding: '8px',
                background: '#f5f5f5',
                borderRadius: '4px'
              }}>
                💡 You can close this window and continue working. The upload will continue in the background.
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="primary"
            onClick={handleUploadSubmit}
            loading={uploading}
            disabled={!selectedFile || uploading}
            block
          >
            {uploading ? 'Processing...' : 'Submit'}
          </Button>
        </div>
      </Modal>
    </Card>
  );
};

export default DocumentList;
