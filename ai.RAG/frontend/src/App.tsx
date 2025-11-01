import React, { useState } from 'react';
import { Layout, Typography, Row, Col, Button } from 'antd';
import { BookOutlined, ApiOutlined } from '@ant-design/icons';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import { API_BASE_URL } from './services/api';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const swaggerUrl = `${API_BASE_URL}/docs`;

  const handleDocSelectionChange = (docIds: string[]) => {
    setSelectedDocIds(docIds);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <BookOutlined style={{ fontSize: 24, color: '#1890ff', marginRight: 12 }} />
            <Title level={3} style={{ margin: 0 }}>
              RAG Intelligent Q&A System
            </Title>
          </div>
          <Button
            type="primary"
            icon={<ApiOutlined />}
            href={swaggerUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            API Documentation
          </Button>
        </div>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        <Row gutter={[16, 16]} style={{ height: '100%' }}>
          {/* Left Column: Document List */}
          <Col xs={24} lg={10}>
            <DocumentList
              selectedDocIds={selectedDocIds}
              onSelectionChange={handleDocSelectionChange}
            />
          </Col>

          {/* Right Column: Chat Interface */}
          <Col xs={24} lg={14}>
            <div style={{ height: 'calc(100vh - 112px)' }}>
              <ChatInterface selectedDocIds={selectedDocIds} />
            </div>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default App;
