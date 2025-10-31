import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Popconfirm, message, Tag, Checkbox } from 'antd';
import { DeleteOutlined, ReloadOutlined, FileTextOutlined } from '@ant-design/icons';
import { documentAPI, Document } from '../services/api';

interface DocumentListProps {
  refreshTrigger: number;
  selectedDocIds: string[];
  onSelectionChange: (docIds: string[]) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  refreshTrigger,
  selectedDocIds,
  onSelectionChange
}) => {
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

  const handleSelectChange = (docId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedDocIds, docId]);
    } else {
      onSelectionChange(selectedDocIds.filter(id => id !== docId));
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(documents.map(doc => doc.document_id));
    } else {
      onSelectionChange([]);
    }
  };

  const isAllSelected = documents.length > 0 && selectedDocIds.length === documents.length;
  const isIndeterminate = selectedDocIds.length > 0 && selectedDocIds.length < documents.length;

  const columns = [
    {
      title: 'Action',
      key: 'action',
      width: 70,
      render: (_: any, record: Document) => (
        <Popconfirm
          title="Are you sure you want to delete this document?"
          onConfirm={() => handleDelete(record.document_id)}
          okText="Yes"
          cancelText="No"
        >
          <Button type="link" danger icon={<DeleteOutlined />} size="small" />
        </Popconfirm>
      ),
    },
    {
      title: 'Filename',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string) => (
        <span>
          <FileTextOutlined style={{ marginRight: 6, color: '#1890ff', fontSize: 13 }} />
          <span style={{ fontSize: 13 }}>{text}</span>
        </span>
      ),
    },
    {
      title: 'File Size',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => <span style={{ fontSize: 13 }}>{formatFileSize(size)}</span>,
      width: 90,
    },
    {
      title: 'Chunks',
      dataIndex: 'total_chunks',
      key: 'total_chunks',
      render: (chunks: number) => <Tag color="blue" style={{ fontSize: 11, margin: 0 }}>{chunks}</Tag>,
      width: 70,
    },
    {
      title: 'Upload Time',
      dataIndex: 'upload_time',
      key: 'upload_time',
      render: (time: string) => <span style={{ fontSize: 13 }}>{time}</span>,
      width: 110,
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
      width: 50,
      fixed: 'right',
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
    </Card>
  );
};

export default DocumentList;
