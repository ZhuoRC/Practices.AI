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
} from 'antd'
import {
  GlobalOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import {
  summarizeWebpage,
} from '../services/api'
import { ProgressIndicator } from './ProgressIndicator'
import { TranscriptionResult } from './TranscriptionResult'

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
  const [progressMessage, setProgressMessage] = useState<string>('')
  const [progressPercent, setProgressPercent] = useState<number>(0)
  const [isAsyncProcessing, setIsAsyncProcessing] = useState<boolean>(false)
  const [transcriptionText, setTranscriptionText] = useState<string>('')
  const [isTranscribing, setIsTranscribing] = useState<boolean>(false)

  const handleWebpageSummarize = async () => {
    if (!url.trim()) {
      message.warning('Please enter a URL')
      return
    }

    setLoading(true)
    setError('')
    setProgressMessage('')
    setProgressPercent(0)
    setTranscriptionText('') // Clear previous transcription

    try {
      const data = await summarizeWebpage(url, summaryLength)
      onSummaryGenerated(data)
      message.success('Summary generated successfully!')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to generate summary'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setLoading(false)
      setProgressMessage('')
      setProgressPercent(0)
      setIsAsyncProcessing(false)
    }
  }

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value)
    setError('')
    setTranscriptionText('') // Clear transcription when URL changes
  }

  // Note: Webpage transcription would require additional implementation
  // For now, this is a placeholder for future enhancement
  const handleWebpageTranscription = async () => {
    if (!url.trim()) {
      message.warning('Please enter a URL first')
      return
    }

    // This would be implemented in the future
    // For example, extracting audio from webpage and transcribing it
    message.info('Webpage audio transcription feature coming soon!')
  }

  const handleClearTranscription = () => {
    setTranscriptionText('')
    message.info('Transcription cleared')
  }

  return (
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
        onChange={handleUrlChange}
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
          onChange={(value) => onSummaryLengthChange(value || 500)}
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

      {/* Progress Indicator */}
      {loading && (
        <Card className="result-card" title="Processing...">
          <ProgressIndicator
            loading={loading}
            progressMessage={progressMessage}
            progressPercent={progressPercent}
            isAsyncProcessing={isAsyncProcessing}
            title="Extracting and processing webpage content..."
            showSteps={true}
            currentStep={2}
          />
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="result-card">
          <Alert message="Error" description={error} type="error" showIcon />
        </Card>
      )}

      {/* Placeholder for Webpage Transcription - Future Enhancement */}
      {/*
      <Card className="result-card" title="Audio Extraction Options">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Alert
            message="Feature Coming Soon"
            description="Extract and transcribe audio content from webpages (podcasts, videos, etc.)"
            type="info"
            showIcon
          />

          <Button
            type="default"
            size="large"
            block
            onClick={handleWebpageTranscription}
            loading={isTranscribing}
            disabled={!url.trim() || loading}
            icon={<ApiOutlined />}
            style={{ borderColor: '#52c41a', color: '#52c41a' }}
          >
            Extract & Transcribe Audio
          </Button>
        </Space>
      </Card>
      */}

      {/* Transcription Result (for future webpage audio transcription) */}
      <TranscriptionResult
        transcription={transcriptionText}
        loading={isTranscribing}
        title="Webpage Audio Transcription"
        variant="webpage"
        onClear={handleClearTranscription}
      />
    </Space>
  )
}

export default WebpageSummarizer