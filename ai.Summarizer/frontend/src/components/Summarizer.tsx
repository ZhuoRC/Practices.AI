import { useState, useEffect } from 'react'
import {
  Layout,
  Card,
  Tabs,
  Upload,
  Input,
  InputNumber,
  Button,
  Typography,
  Space,
  Alert,
  Spin,
  Statistic,
  Row,
  Col,
  message,
  Tag,
  Progress,
  Steps,
} from 'antd'
import {
  FileTextOutlined,
  GlobalOutlined,
  CloudUploadOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  SplitCellsOutlined,
  CheckCircleOutlined,
  ApiOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import type { UploadFile } from 'antd'
import { summarizeDocument, summarizeWebpage, checkHealth, downloadSummary } from '../services/api'
import './Summarizer.css'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { TabPane } = Tabs

interface SummaryResult {
  summary: string
  chunk_count: number
  processing_time: number
  source_type: string
  source_name?: string
}

function Summarizer() {
  const [activeTab, setActiveTab] = useState<string>('document')
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [url, setUrl] = useState<string>('')
  const [summaryLength, setSummaryLength] = useState<number>(500)
  const [loading, setLoading] = useState<boolean>(false)
  const [result, setResult] = useState<SummaryResult | null>(null)
  const [error, setError] = useState<string>('')
  const [healthStatus, setHealthStatus] = useState<{
    status: string
    llm_provider: string
    model: string
  } | null>(null)

  useEffect(() => {
    checkHealthStatus()
  }, [])

  const checkHealthStatus = async () => {
    try {
      const health = await checkHealth()
      setHealthStatus(health)
    } catch (err) {
      console.error('Health check failed:', err)
    }
  }

  const handleDocumentUpload = async () => {
    if (fileList.length === 0) {
      message.warning('Please select a file first')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const file = fileList[0].originFileObj as File
      const data = await summarizeDocument(file, summaryLength)
      setResult(data)
      message.success('Summary generated successfully!')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to generate summary'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleWebpageSummarize = async () => {
    if (!url.trim()) {
      message.warning('Please enter a URL')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await summarizeWebpage(url, summaryLength)
      setResult(data)
      message.success('Summary generated successfully!')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to generate summary'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (info: any) => {
    let newFileList = [...info.fileList]
    newFileList = newFileList.slice(-1)
    setFileList(newFileList)
    setResult(null)
    setError('')
  }

  return (
    <Layout className="summarizer-layout">
      <Header className="summarizer-header">
        <div className="header-content">
          <Space align="center">
            <ThunderboltOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
            <Title level={2} style={{ margin: 0, color: 'white' }}>
              AI Document Summarizer
            </Title>
          </Space>
          {healthStatus && (
            <Space>
              <Tag color="success" icon={<CheckCircleOutlined />}>
                {healthStatus.status.toUpperCase()}
              </Tag>
              <Tag color="blue">{healthStatus.llm_provider.toUpperCase()}</Tag>
              <Tag color="purple">{healthStatus.model}</Tag>
            </Space>
          )}
        </div>
      </Header>

      <Content className="summarizer-content">
        <div className="content-wrapper">
          <Card className="main-card">
            <Tabs activeKey={activeTab} onChange={setActiveTab} size="large">
              <TabPane
                tab={
                  <span>
                    <FileTextOutlined />
                    Document Upload
                  </span>
                }
                key="document"
              >
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <Alert
                    message="Supported Formats"
                    description="PDF, DOCX, TXT, Markdown files are supported"
                    type="info"
                    showIcon
                  />

                  <Upload.Dragger
                    fileList={fileList}
                    onChange={handleFileChange}
                    beforeUpload={() => false}
                    accept=".pdf,.docx,.txt,.md"
                    maxCount={1}
                  >
                    <p className="ant-upload-drag-icon">
                      <CloudUploadOutlined />
                    </p>
                    <p className="ant-upload-text">
                      Click or drag file to this area to upload
                    </p>
                    <p className="ant-upload-hint">
                      Support for PDF, DOCX, TXT, and Markdown files
                    </p>
                  </Upload.Dragger>

                  <div>
                    <Text strong>Summary Length (characters):</Text>
                    <InputNumber
                      min={100}
                      max={8000}
                      step={100}
                      value={summaryLength}
                      onChange={(value) => setSummaryLength(value || 500)}
                      style={{ width: '100%', marginTop: '8px' }}
                      size="large"
                    />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      Recommended: 500 for quick, 1000-2000 for detailed, 5000-8000 for comprehensive (max: 8000)
                    </Text>
                  </div>

                  <Button
                    type="primary"
                    size="large"
                    block
                    onClick={handleDocumentUpload}
                    loading={loading}
                    disabled={fileList.length === 0}
                    icon={<ThunderboltOutlined />}
                  >
                    Generate Summary
                  </Button>
                </Space>
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <GlobalOutlined />
                    Webpage URL
                  </span>
                }
                key="webpage"
              >
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <Alert
                    message="Web Content Extraction"
                    description="Enter a URL to extract and summarize webpage content"
                    type="info"
                    showIcon
                  />

                  <Input
                    size="large"
                    placeholder="https://example.com/article"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    prefix={<GlobalOutlined />}
                    onPressEnter={handleWebpageSummarize}
                  />

                  <div>
                    <Text strong>Summary Length (characters):</Text>
                    <InputNumber
                      min={100}
                      max={8000}
                      step={100}
                      value={summaryLength}
                      onChange={(value) => setSummaryLength(value || 500)}
                      style={{ width: '100%', marginTop: '8px' }}
                      size="large"
                    />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      Recommended: 500 for quick, 1000-2000 for detailed, 5000-8000 for comprehensive (max: 8000)
                    </Text>
                  </div>

                  <Button
                    type="primary"
                    size="large"
                    block
                    onClick={handleWebpageSummarize}
                    loading={loading}
                    disabled={!url.trim()}
                    icon={<ThunderboltOutlined />}
                  >
                    Generate Summary
                  </Button>
                </Space>
              </TabPane>
            </Tabs>
          </Card>

          {loading && (
            <Card className="result-card" title="Processing...">
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div style={{ textAlign: 'center' }}>
                  <Spin size="large" />
                  <Paragraph style={{ marginTop: '20px', color: '#8c8c8c', fontSize: '16px' }}>
                    Processing document using Map-Reduce architecture...
                  </Paragraph>
                </div>

                <Steps
                  current={1}
                  items={[
                    {
                      title: 'Load',
                      description: 'Extract text from source',
                      status: 'finish',
                    },
                    {
                      title: 'Chunk',
                      description: 'Split into manageable pieces',
                      status: 'finish',
                    },
                    {
                      title: 'Map',
                      description: 'Summarizing each chunk...',
                      status: 'process',
                    },
                    {
                      title: 'Reduce',
                      description: 'Generate final summary',
                      status: 'wait',
                    },
                  ]}
                />

                <div>
                  <Paragraph style={{ marginBottom: '8px', color: '#8c8c8c' }}>
                    This may take a few minutes depending on document size...
                  </Paragraph>
                  <Progress
                    percent={50}
                    status="active"
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                  />
                </div>

                <Alert
                  message="Performance Tip"
                  description="Larger documents are automatically split into optimal chunk sizes (2000-3000 characters) to balance speed and quality. Each chunk is processed sequentially for best accuracy."
                  type="info"
                  showIcon
                />
              </Space>
            </Card>
          )}

          {error && (
            <Card className="result-card">
              <Alert message="Error" description={error} type="error" showIcon />
            </Card>
          )}

          {result && !loading && (
            <Card className="result-card" title="Summary Result">
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="Processing Time"
                      value={result.processing_time}
                      suffix="s"
                      prefix={<ClockCircleOutlined />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="Chunks Processed"
                      value={result.chunk_count}
                      prefix={<SplitCellsOutlined />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="Source Type"
                      value={result.source_type}
                      prefix={<FileTextOutlined />}
                    />
                  </Col>
                </Row>

                {result.token_usage && (
                  <Row gutter={16}>
                    <Col span={8}>
                      <Statistic
                        title="Total Tokens"
                        value={result.token_usage.total_tokens}
                        prefix={<ApiOutlined />}
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="Prompt Tokens"
                        value={result.token_usage.prompt_tokens}
                        prefix={<ApiOutlined />}
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="Completion Tokens"
                        value={result.token_usage.completion_tokens}
                        prefix={<ApiOutlined />}
                        valueStyle={{ color: '#fa8c16' }}
                      />
                    </Col>
                  </Row>
                )}

                {result.source_name && (
                  <Alert
                    message="Source"
                    description={result.source_name}
                    type="info"
                    showIcon
                  />
                )}

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <Title level={4} style={{ margin: 0 }}>Summary</Title>
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={() => {
                        const filename = `summary_${result.source_type}_${Date.now()}.md`
                        downloadSummary(result, filename)
                        message.success('Summary downloaded successfully!')
                      }}
                    >
                      Download Summary
                    </Button>
                  </div>
                  <TextArea
                    value={result.summary}
                    autoSize={{ minRows: 8, maxRows: 20 }}
                    readOnly
                    style={{
                      fontSize: '15px',
                      lineHeight: '1.6',
                      backgroundColor: '#ffffff',
                      color: '#000000',
                      border: '1px solid #d0d7de',
                    }}
                  />
                </div>
              </Space>
            </Card>
          )}

          <Card className="info-card" style={{ marginTop: '24px' }}>
            <Title level={4}>How It Works</Title>
            <Row gutter={[16, 16]}>
              <Col span={6}>
                <div className="step-card">
                  <Text strong>1. Load</Text>
                  <Paragraph style={{ fontSize: '12px', marginTop: '8px' }}>
                    Extract text from documents or webpages
                  </Paragraph>
                </div>
              </Col>
              <Col span={6}>
                <div className="step-card">
                  <Text strong>2. Chunk</Text>
                  <Paragraph style={{ fontSize: '12px', marginTop: '8px' }}>
                    Split text into 800-1200 character chunks
                  </Paragraph>
                </div>
              </Col>
              <Col span={6}>
                <div className="step-card">
                  <Text strong>3. Map</Text>
                  <Paragraph style={{ fontSize: '12px', marginTop: '8px' }}>
                    Generate summary for each chunk independently
                  </Paragraph>
                </div>
              </Col>
              <Col span={6}>
                <div className="step-card">
                  <Text strong>4. Reduce</Text>
                  <Paragraph style={{ fontSize: '12px', marginTop: '8px' }}>
                    Combine summaries into final result
                  </Paragraph>
                </div>
              </Col>
            </Row>
          </Card>
        </div>
      </Content>
    </Layout>
  )
}

export default Summarizer
