import React, { useState } from 'react';
import { Layout, Typography, Row, Col, Divider } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger document list refresh
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', height: '64px' }}>
          <BookOutlined style={{ fontSize: 24, color: '#1890ff', marginRight: 12 }} />
          <Title level={3} style={{ margin: 0 }}>
            RAG Intelligent Q&A System
          </Title>
        </div>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        <Row gutter={[16, 16]} style={{ height: '100%' }}>
          {/* Left Column: Upload and Document List */}
          <Col xs={24} lg={10}>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            <DocumentList refreshTrigger={refreshTrigger} />
          </Col>

          {/* Right Column: Chat Interface */}
          <Col xs={24} lg={14}>
            <div style={{ height: 'calc(100vh - 112px)' }}>
              <ChatInterface />
            </div>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default App;
