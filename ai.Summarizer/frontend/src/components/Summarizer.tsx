import { useState, useEffect } from 'react'
import {
  Layout,
  Card,
  Tabs,
  Typography,
  Space,
  Statistic,
  Row,
  Col,
  message,
  Tag,
  Button,
  Input,
  Alert,
} from 'antd'
import {
  FileTextOutlined,
  GlobalOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  SplitCellsOutlined,
  CheckCircleOutlined,
  DownloadOutlined,
  SoundOutlined,
  ApiOutlined,
  FileAddOutlined,
} from '@ant-design/icons'
import {
  checkHealth,
  downloadSummary,
} from '../services/api'
import { DocumentSummarizer } from './DocumentSummarizer'
import { WebpageSummarizer } from './WebpageSummarizer'
import { RecognitionTab } from './RecognitionTab'
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
  token_usage?: {
    total_tokens: number
    prompt_tokens: number
    completion_tokens: number
  }
}

function Summarizer() {
  const [activeTab, setActiveTab] = useState<string>('summary')
  const [summarySubTab, setSummarySubTab] = useState<string>('document')
  const [summaryLength, setSummaryLength] = useState<number>(500)
  const [result, setResult] = useState<SummaryResult | null>(null)
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

  const handleSummaryGenerated = (summaryResult: SummaryResult) => {
    setResult(summaryResult)
  }

  const handleClearResult = () => {
    setResult(null)
    message.info('Summary cleared')
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
              {/* Summary Tab */}
              <TabPane
                tab={
                  <span>
                    <ThunderboltOutlined />
                    Summary
                  </span>
                }
                key="summary"
              >
                <Tabs activeKey={summarySubTab} onChange={setSummarySubTab} type="card">
                  <TabPane
                    tab={
                      <span>
                        <FileTextOutlined />
                        Document
                      </span>
                    }
                    key="document"
                  >
                    <DocumentSummarizer
                      onSummaryGenerated={handleSummaryGenerated}
                      summaryLength={summaryLength}
                      onSummaryLengthChange={setSummaryLength}
                    />
                  </TabPane>

                  <TabPane
                    tab={
                      <span>
                        <GlobalOutlined />
                        Webpage
                      </span>
                    }
                    key="webpage"
                  >
                    <WebpageSummarizer
                      onSummaryGenerated={handleSummaryGenerated}
                      summaryLength={summaryLength}
                      onSummaryLengthChange={setSummaryLength}
                    />
                  </TabPane>
                </Tabs>
              </TabPane>

              {/* Recognition Tab */}
              <TabPane
                tab={
                  <span>
                    <SoundOutlined />
                    Recognition
                  </span>
                }
                key="recognition"
              >
                <RecognitionTab />
              </TabPane>
            </Tabs>
          </Card>

          {/* Summary Result */}
          {result && (
            <Card
              className="result-card"
              title="Summary Result"
              extra={
                <Button
                  type="default"
                  onClick={handleClearResult}
                  size="small"
                >
                  Clear
                </Button>
              }
            >
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
