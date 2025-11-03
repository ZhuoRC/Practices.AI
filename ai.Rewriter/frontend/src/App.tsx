import React, { useState } from 'react';
import {
  Layout,
  Typography,
  Card,
  Form,
  Input,
  Button,
  Select,
  Space,
  message,
  Spin,
  Divider,
  Row,
  Col,
  Alert,
  Radio,
  Tag,
  Tooltip
} from 'antd';
import { EditOutlined, ThunderboltOutlined, DesktopOutlined, CloudOutlined, LaptopOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { rewriteText } from './services/api';
import './App.css';

const { Header, Content } = Layout;
const { Title, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

interface RewriteRequest {
  source_text: string;
  requirements: string;
  mode: string;
  segment_size?: number;
}

interface RewriteResponse {
  rewritten_text: string;
  mode_used: string;
  segments_processed: number;
  token_usage?: TokenUsage;
}

function App() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RewriteResponse | null>(null);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    setResult(null);

    try {
      const request: RewriteRequest = {
        source_text: values.sourceText,
        requirements: values.requirements,
        mode: values.mode,
        segment_size: values.segmentSize || 500
      };

      const response = await rewriteText(request);
      setResult(response);
      message.success('文本改写完成！');
    } catch (error: any) {
      console.error('Rewrite error:', error);
      message.error(error.message || '改写失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout className="min-h-screen">
      <Header className="header">
        <div className="logo">
          <EditOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        </div>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          AI 文本改写器
        </Title>
      </Header>

      <Content style={{ padding: '24px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={12}>
              <Card title="输入设置" className="input-card">
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleSubmit}
                  initialValues={{
                    mode: 'cloud',
                    segmentSize: 500
                  }}
                >
                  <Form.Item
                    name="sourceText"
                    label="原文"
                    rules={[
                      { required: true, message: '请输入要改写的文本' },
                      { min: 10, message: '文本长度至少为10个字符' }
                    ]}
                  >
                    <TextArea
                      rows={8}
                      placeholder="请输入需要改写的原始文本..."
                      showCount
                      maxLength={10000}
                    />
                  </Form.Item>

                  <Form.Item
                    name="requirements"
                    label="改写要求"
                    rules={[
                      { required: true, message: '请输入改写要求' },
                      { min: 5, message: '改写要求至少为5个字符' }
                    ]}
                  >
                    <TextArea
                      rows={3}
                      placeholder="请输入改写要求，例如：使文本更简洁、改变语气、增加细节等..."
                      showCount
                      maxLength={500}
                    />
                  </Form.Item>

                  <Form.Item
                    name="mode"
                    label={
                      <Space>
                        <span>改写模式</span>
                        <Tag color="blue" icon={<CloudOutlined />}>可切换</Tag>
                        <Tooltip title="云端模式使用通义千问API，速度快；本地模式需要安装Ollama">
                          <QuestionCircleOutlined style={{ color: '#888', cursor: 'help' }} />
                        </Tooltip>
                      </Space>
                    }
                    extra={
                      <Space direction="vertical" size={0} style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                        <div>💡 云端模式：快速、高质量，需要 API Key</div>
                        <div>🖥️ 本地模式：离线可用，需要安装 Ollama 服务</div>
                      </Space>
                    }
                  >
                    <Radio.Group buttonStyle="solid" style={{ display: 'flex', width: '100%' }}>
                      <Radio.Button value="cloud" style={{ flex: 1 }}>
                        <Space size="small">
                          <ThunderboltOutlined style={{ color: '#1890ff' }} />
                          <span>云端模式</span>
                        </Space>
                      </Radio.Button>
                      <Radio.Button value="local" style={{ flex: 1 }}>
                        <Space size="small">
                          <LaptopOutlined style={{ color: '#52c41a' }} />
                          <span>本地模式</span>
                        </Space>
                      </Radio.Button>
                    </Radio.Group>
                  </Form.Item>

                  <Form.Item name="segmentSize" label="分段大小 (字符)">
                    <Select placeholder="选择分段大小">
                      <Option value={300}>300 字符</Option>
                      <Option value={500}>500 字符</Option>
                      <Option value={800}>800 字符</Option>
                      <Option value={1000}>1000 字符</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      size="large"
                      loading={loading}
                      block
                      icon={<EditOutlined />}
                    >
                      {loading ? '改写中...' : '开始改写'}
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="改写结果" className="result-card">
                {loading && (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: '16px' }}>
                      <Paragraph>正在改写文本，请稍候...</Paragraph>
                    </div>
                  </div>
                )}

                {result && !loading && (
                  <div>
                    <Alert
                      message="改写完成"
                      type="success"
                      showIcon
                      style={{ marginBottom: '16px' }}
                    />

                    <div style={{ marginBottom: '16px' }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Space>
                          <span>使用模式: <strong>{result.mode_used === 'cloud' ? '云端' : '本地'}</strong></span>
                          <Divider type="vertical" />
                          <span>处理段数: <strong>{result.segments_processed}</strong></span>
                        </Space>
                        {result.token_usage && result.token_usage.total_tokens > 0 && (
                          <Space wrap>
                            <span>Token 使用: </span>
                            <span style={{ color: '#1890ff' }}>
                              输入 <strong>{result.token_usage.input_tokens.toLocaleString()}</strong>
                            </span>
                            <Divider type="vertical" />
                            <span style={{ color: '#52c41a' }}>
                              输出 <strong>{result.token_usage.output_tokens.toLocaleString()}</strong>
                            </span>
                            <Divider type="vertical" />
                            <span style={{ color: '#faad14' }}>
                              总计 <strong>{result.token_usage.total_tokens.toLocaleString()}</strong>
                            </span>
                          </Space>
                        )}
                      </Space>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                      <Title level={5}>改写结果:</Title>
                      <div className="result-text">
                        {result.rewritten_text}
                      </div>
                    </div>

                    <Button
                      type="default"
                      onClick={() => {
                        navigator.clipboard.writeText(result.rewritten_text);
                        message.success('已复制到剪贴板');
                      }}
                    >
                      复制结果
                    </Button>
                  </div>
                )}

                {!result && !loading && (
                  <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                    <Paragraph>请在左侧输入文本和改写要求，然后点击"开始改写"</Paragraph>
                  </div>
                )}
              </Card>
            </Col>
          </Row>
        </div>
      </Content>
    </Layout>
  );
}

export default App;
