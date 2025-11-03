import { useState } from 'react'
import {
  Card,
  Input,
  InputNumber,
  Button,
  Typography,
  Space,
  Alert,
  message,
  Spin,
} from 'antd'
import {
  GlobalOutlined,
  ThunderboltOutlined,
  LoadingOutlined,
} from '@ant-design/icons'
import {
  summarizeWebpage,
} from '../services/api'

const { Title, Text } = Typography

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

interface WebpageSummarizerProps {
  onSummaryGenerated: (result: SummaryResult) => void
  summaryLength: number
  onSummaryLengthChange: (length: number) => void
}

export function WebpageSummarizer({
  onSummaryGenerated,
  summaryLength,
  onSummaryLengthChange,
}: WebpageSummarizerProps) {
  const [url, setUrl] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const handleWebpageSummarize = async () => {
    if (!url.trim()) {
      message.warning('Please enter a URL')
      return
    }

    setLoading(true)
    setError('')

    try {
      const data = await summarizeWebpage(url, summaryLength)
      onSummaryGenerated(data)
      message.success('Webpage summarized successfully!')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to summarize webpage'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value)
    setError('')
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card className="input-card">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Title level={4}>
              <GlobalOutlined /> Webpage Summarization
            </Title>
            <Text type="secondary">
              Enter a webpage URL to extract and summarize its content.
            </Text>
          </div>

          <Input
            size="large"
            placeholder="https://example.com/article"
            value={url}
            onChange={handleUrlChange}
            prefix={<GlobalOutlined />}
            onPressEnter={handleWebpageSummarize}
          />

          <div>
            <Text>Summary Length (characters):</Text>
            <InputNumber
              min={100}
              max={2000}
              value={summaryLength}
              onChange={(value) => onSummaryLengthChange(value || 500)}
              style={{ width: '100%', marginTop: '8px' }}
            />
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
      </Card>

      {/* Loading Indicator */}
      {loading && (
        <Card className="result-card">
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <Spin
              indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
              size="large"
            />
            <div style={{ marginTop: '20px' }}>
              <Title level={4}>Processing Webpage...</Title>
              <Text type="secondary">
                Extracting and summarizing content from the webpage. This may take a few moments.
              </Text>
            </div>
          </div>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="result-card">
          <Alert message="Error" description={error} type="error" showIcon />
        </Card>
      )}
    </Space>
  )
}

export default WebpageSummarizer