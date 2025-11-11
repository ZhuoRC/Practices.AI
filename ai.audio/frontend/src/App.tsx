import React, { useState, useEffect } from 'react';
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
  Slider,
  Tag,
  Tooltip,
  Badge,
  Tabs,
  List,
  Avatar
} from 'antd';
import {
  SoundOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  CloudOutlined,
  DesktopOutlined,
  RobotOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  HeartOutlined
} from '@ant-design/icons';
import { ttsApi } from './services/api';
import { TTSRequest, TTSResponse, ProviderInfo, VoiceInfo, HealthResponse } from './types/tts';
import AudioPlayer from './components/AudioPlayer';
import VoiceSelector from './components/VoiceSelector';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

function App() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TTSResponse | null>(null);
  const [providers, setProviders] = useState<string[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [providerInfo, setProviderInfo] = useState<Record<string, ProviderInfo>>({});
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [previewAudio, setPreviewAudio] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadProviders();
    loadHealth();
  }, []);

  // Load provider voices when provider changes
  useEffect(() => {
    if (selectedProvider) {
      loadVoices(selectedProvider);
      loadProviderInfo(selectedProvider);
    }
  }, [selectedProvider]);

  const loadProviders = async () => {
    try {
      const providerList = await ttsApi.getProviders();
      setProviders(providerList);
      if (providerList.length > 0) {
        setSelectedProvider(providerList[0]);
      }
    } catch (error: any) {
      message.error(`Failed to load providers: ${error.message}`);
    } finally {
      setLoadingProviders(false);
    }
  };

  const loadHealth = async () => {
    try {
      const healthData = await ttsApi.healthCheck();
      setHealth(healthData);
    } catch (error: any) {
      console.error('Health check failed:', error);
    }
  };

  const loadVoices = async (provider: string) => {
    try {
      setLoading(true);
      const response = await ttsApi.getProviderVoices(provider);
      setVoices(response.voices);
    } catch (error: any) {
      message.error(`Failed to load voices: ${error.message}`);
      setVoices([]);
    } finally {
      setLoading(false);
    }
  };

  const loadProviderInfo = async (provider: string) => {
    try {
      const info = await ttsApi.getProviderInfo(provider);
      setProviderInfo(prev => ({ ...prev, [provider]: info }));
    } catch (error: any) {
      console.error('Failed to load provider info:', error);
    }
  };

  const handleGenerateSpeech = async (values: any) => {
    setLoading(true);
    setResult(null);
    setPreviewAudio(null);

    try {
      const request: TTSRequest = {
        text: values.text,
        provider: selectedProvider,
        voice_id: values.voice_id,
        speed: values.speed || 1.0,
        pitch: values.pitch || 0.0,
        volume: values.volume || 1.0,
        output_format: values.output_format || 'mp3',
        sample_rate: values.sample_rate
      };

      const response = await ttsApi.generateSpeech(request);
      setResult(response);
      message.success('语音生成成功！');
    } catch (error: any) {
      console.error('Speech generation error:', error);
      message.error(error.message || '语音生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleVoicePreview = async (voiceId: string) => {
    try {
      const previewBlob = await ttsApi.getVoicePreview(selectedProvider, voiceId);
      const audioUrl = URL.createObjectURL(previewBlob);
      setPreviewAudio(audioUrl);
      
      // Auto-play preview
      const audio = new Audio(audioUrl);
      audio.play().catch(e => console.error('Auto-play failed:', e));
      
      // Clean up after 5 seconds
      setTimeout(() => {
        URL.revokeObjectURL(audioUrl);
        setPreviewAudio(null);
      }, 5000);
    } catch (error: any) {
      console.error('Voice preview failed:', error);
      // Don't show error for preview failure
    }
  };

  const getProviderIcon = (provider: string) => {
    const icons = {
      'azure': <CloudOutlined style={{ color: '#0078D4' }} />,
      'google': <CloudOutlined style={{ color: '#4285F4' }} />,
      'elevenlabs': <RobotOutlined style={{ color: '#FF6B35' }} />,
      'local': <DesktopOutlined style={{ color: '#52C41A' }} />
    };
    return icons[provider as keyof typeof icons] || <CloudOutlined />;
  };

  const getProviderName = (provider: string) => {
    const names = {
      'azure': 'Azure Cognitive Services',
      'google': 'Google Cloud TTS',
      'elevenlabs': 'ElevenLabs',
      'local': 'Local TTS'
    };
    return names[provider as keyof typeof names] || provider;
  };

  return (
    <Layout className="min-h-screen">
      <Header className="header">
        <div className="logo">
          <SoundOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        </div>
        <Title level={3} style={{ color: '#1a1a1a', margin: 0 }}>
          AI 语音合成器
        </Title>
        {health && (
          <div style={{ marginLeft: 'auto' }}>
            <Badge 
              count={health.available_providers.length} 
              style={{ backgroundColor: '#52c41a' }}
            >
              <Tag color="blue">服务正常</Tag>
            </Badge>
          </div>
        )}
      </Header>

      <Layout>
        <Sider width={300} theme="light" className="provider-sider">
          <div style={{ padding: '16px' }}>
            <Title level={5}>
              <Space>
                <CloudOutlined />
                TTS 提供商
              </Space>
            </Title>
            
            {loadingProviders ? (
              <Spin size="large" />
            ) : (
              <List
                dataSource={providers}
                renderItem={provider => (
                  <List.Item
                    className={`provider-item ${selectedProvider === provider ? 'selected' : ''}`}
                    onClick={() => setSelectedProvider(provider)}
                  >
                    <Space>
                      {getProviderIcon(provider)}
                      <div>
                        <div>{getProviderName(provider)}</div>
                        {providerInfo[provider] && (
                          <Tag
                            color={providerInfo[provider].is_configured ? 'green' : 'red'}
                          >
                            {providerInfo[provider].is_configured ? '已配置' : '未配置'}
                          </Tag>
                        )}
                      </div>
                    </Space>
                  </List.Item>
                )}
              />
            )}

            {selectedProvider && providerInfo[selectedProvider] && (
              <Card size="small" style={{ marginTop: '16px' }}>
                <Title level={5}>
                  <InfoCircleOutlined /> 提供商信息
                </Title>
                <Paragraph type="secondary">
                  {providerInfo[selectedProvider].description}
                </Paragraph>
                <div>
                  <strong>最大文本长度:</strong> {providerInfo[selectedProvider].max_text_length}
                </div>
                <div>
                  <strong>支持格式:</strong>
                  <Space wrap style={{ marginTop: '4px' }}>
                    {providerInfo[selectedProvider].supported_formats.map(format => (
                      <Tag key={format}>{format.toUpperCase()}</Tag>
                    ))}
                  </Space>
                </div>
              </Card>
            )}
          </div>
        </Sider>

        <Content style={{ padding: '24px' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <Row gutter={[24, 24]}>
              <Col xs={24} lg={12}>
                <Card title="语音合成设置" className="input-card">
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleGenerateSpeech}
                    initialValues={{
                      speed: 1.0,
                      pitch: 0.0,
                      volume: 1.0,
                      output_format: 'mp3'
                    }}
                  >
                    <Form.Item
                      name="text"
                      label="文本内容"
                      rules={[
                        { required: true, message: '请输入要合成的文本' },
                        { min: 1, message: '文本长度至少为1个字符' },
                        { max: 5000, message: '文本长度不能超过5000个字符' }
                      ]}
                    >
                      <TextArea
                        rows={6}
                        placeholder="请输入要转换为语音的文本内容..."
                        showCount
                        maxLength={5000}
                      />
                    </Form.Item>

                    <Form.Item
                      name="voice_id"
                      label="选择语音"
                      rules={[{ required: true, message: '请选择语音' }]}
                    >
                      <VoiceSelector
                        voices={voices}
                        loading={loading}
                        onPreview={handleVoicePreview}
                        selectedProvider={selectedProvider}
                      />
                    </Form.Item>

                    <Tabs defaultActiveKey="basic" size="small">
                      <TabPane tab="基础设置" key="basic">
                        <Form.Item name="output_format" label="音频格式">
                          <Select placeholder="选择音频格式">
                            <Option value="mp3">MP3</Option>
                            <Option value="wav">WAV</Option>
                            <Option value="ogg">OGG</Option>
                            <Option value="flac">FLAC</Option>
                          </Select>
                        </Form.Item>
                      </TabPane>
                      
                      <TabPane tab="高级设置" key="advanced">
                        <Form.Item label={`语速: ${form.getFieldValue('speed')?.toFixed(2) || '1.00'}`}>
                          <Form.Item name="speed" noStyle>
                            <Slider
                              min={0.25}
                              max={4.0}
                              step={0.1}
                              marks={{
                                0.25: '0.25x',
                                1.0: '1.0x',
                                2.0: '2.0x',
                                4.0: '4.0x'
                              }}
                            />
                          </Form.Item>
                        </Form.Item>

                        <Form.Item label={`音调: ${form.getFieldValue('pitch')?.toFixed(0) || '0'}Hz`}>
                          <Form.Item name="pitch" noStyle>
                            <Slider
                              min={-20}
                              max={20}
                              step={1}
                              marks={{
                                '-20': '-20Hz',
                                0: '0Hz',
                                20: '+20Hz'
                              }}
                            />
                          </Form.Item>
                        </Form.Item>

                        <Form.Item label={`音量: ${form.getFieldValue('volume')?.toFixed(2) || '1.00'}`}>
                          <Form.Item name="volume" noStyle>
                            <Slider
                              min={0.0}
                              max={2.0}
                              step={0.1}
                              marks={{
                                0.0: '静音',
                                1.0: '100%',
                                2.0: '200%'
                              }}
                            />
                          </Form.Item>
                        </Form.Item>
                      </TabPane>
                    </Tabs>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        size="large"
                        loading={loading}
                        block
                        icon={<SoundOutlined />}
                      >
                        {loading ? '生成中...' : '生成语音'}
                      </Button>
                    </Form.Item>
                  </Form>
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card title="生成结果" className="result-card">
                  {previewAudio && (
                    <Alert
                      message="语音预览播放中"
                      type="info"
                      showIcon
                      style={{ marginBottom: '16px' }}
                      closable
                      onClose={() => setPreviewAudio(null)}
                    />
                  )}

                  {loading && (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                      <Spin size="large" />
                      <div style={{ marginTop: '16px' }}>
                        <Paragraph>正在生成语音，请稍候...</Paragraph>
                      </div>
                    </div>
                  )}

                  {result && !loading && (
                    <div>
                      <Alert
                        message="语音生成完成"
                        type="success"
                        showIcon
                        style={{ marginBottom: '16px' }}
                      />

                      <div style={{ marginBottom: '16px' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Space>
                            <span>提供商: <strong>{getProviderName(result.provider_used)}</strong></span>
                            <Divider type="vertical" />
                            <span>时长: <strong>{result.duration.toFixed(2)}秒</strong></span>
                            <Divider type="vertical" />
                            <span>大小: <strong>{(result.file_size / 1024).toFixed(1)}KB</strong></span>
                          </Space>
                          <Space>
                            <span>格式: <strong>{result.format.toUpperCase()}</strong></span>
                            <Divider type="vertical" />
                            <span>采样率: <strong>{result.sample_rate}Hz</strong></span>
                          </Space>
                        </Space>
                      </div>

                      <AudioPlayer
                        audioUrl={ttsApi.getAudioDownloadUrl(result.audio_id)}
                        title="生成的语音"
                      />

                      <div style={{ marginTop: '16px' }}>
                        <Button
                          type="default"
                          icon={<DownloadOutlined />}
                          onClick={() => {
                            window.open(ttsApi.getAudioDownloadUrl(result.audio_id), '_blank');
                          }}
                        >
                          下载音频
                        </Button>
                      </div>
                    </div>
                  )}

                  {!result && !loading && (
                    <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                      <Paragraph>请在左侧输入文本和设置参数，然后点击"生成语音"</Paragraph>
                    </div>
                  )}
                </Card>
              </Col>
            </Row>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
