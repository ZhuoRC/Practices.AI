import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Popconfirm, message, Tag } from 'antd';
import { DeleteOutlined, ReloadOutlined, FileTextOutlined } from '@ant-design/icons';
import { documentAPI, Document } from '../services/api';

interface DocumentListProps {
  refreshTrigger: number;
}

const DocumentList: React.FC<DocumentListProps> = ({ refreshTrigger }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const docs = await documentAPI.listDocuments();
      setDocuments(docs);
    } catch (error) {
      message.error('Failed to load document list');
      console.error('Load documents error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [refreshTrigger]);

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

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleString('en-US');
  };

  const columns = [
    {
      title: 'Filename',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string) => (
        <span>
          <FileTextOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          {text}
        </span>
      ),
    },
    {
      title: 'File Size',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => formatFileSize(size),
      width: 120,
    },
    {
      title: 'Chunks',
      dataIndex: 'total_chunks',
      key: 'total_chunks',
      render: (chunks: number) => <Tag color="blue">{chunks} chunks</Tag>,
      width: 120,
    },
    {
      title: 'Upload Time',
      dataIndex: 'modified_time',
      key: 'modified_time',
      render: (time: number) => formatDate(time),
      width: 180,
    },
    {
      title: 'Action',
      key: 'action',
      width: 100,
      render: (_: any, record: Document) => (
        <Popconfirm
          title="Are you sure you want to delete this document?"
          onConfirm={() => handleDelete(record.document_id)}
          okText="Yes"
          cancelText="No"
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <Card
      title={`Document Library (${documents.length})`}
      extra={
        <Button
          icon={<ReloadOutlined />}
          onClick={loadDocuments}
          loading={loading}
        >
          Refresh
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={documents}
        rowKey="document_id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total ${total} documents`,
        }}
      />
    </Card>
  );
};

export default DocumentList;
