import { useState } from 'react'
import {
  Card,
  Button,
  Typography,
  Space,
  Alert,
  Input,
  message,
  Tag,
  Statistic,
  Row,
  Col,
} from 'antd'
import {
  DownloadOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  SoundOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import type { TaskResult } from '../services/api'

const { Title, Text } = Typography
const { TextArea } = Input

export interface TranscriptionData {
  text: string
  language?: string
  duration?: number
  provider?: string
  model?: string
  processing_time?: number
  word_count?: number
}

interface TranscriptionResultProps {
  transcription: string | TranscriptionData
  loading?: boolean
  title?: string
  showDownload?: boolean
  onDownload?: (text: string, filename: string) => void
  onClear?: () => void
  extraActions?: React.ReactNode
  variant?: 'document' | 'webpage'
  className?: string
}

export function TranscriptionResult({
  transcription,
  loading = false,
  title = 'Transcription Result',
  showDownload = true,
  onDownload,
  onClear,
  extraActions,
  variant = 'document',
  className = '',
}: TranscriptionResultProps) {
  const [downloadLoading, setDownloadLoading] = useState(false)

  // Parse transcription data
  let transcriptionData: TranscriptionData

  if (typeof transcription === 'string') {
    transcriptionData = {
      text: transcription,
      word_count: transcription.split(/\s+/).filter(word => word.length > 0).length,
    }
  } else {
    transcriptionData = transcription
  }

  const handleDownload = async () => {
    if (!transcriptionData.text) return

    setDownloadLoading(true)
    try {
      const filename = `${variant}_transcription_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.txt`

      if (onDownload) {
        onDownload(transcriptionData.text, filename)
      } else {
        // Default download implementation
        const blob = new Blob([transcriptionData.text], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }

      message.success('Transcription downloaded successfully!')
    } catch (error) {
      message.error('Failed to download transcription')
    } finally {
      setDownloadLoading(false)
    }
  }

  const getVariantColor = () => {
    return variant === 'webpage' ? '#52c41a' : '#1890ff'
  }

  const getVariantIcon = () => {
    return variant === 'webpage' ? <FileTextOutlined /> : <SoundOutlined />
  }

  if (!transcriptionData.text && !loading) {
    return null
  }

  return (
    <Card
      className={`transcription-result-card ${className}`}
      title={
        <Space>
          {getVariantIcon()}
          <span>{title}</span>
          {transcriptionData.provider && (
            <Tag color={getVariantColor()}>
              {transcriptionData.provider.toUpperCase()}
            </Tag>
          )}
        </Space>
      }
      extra={
        <Space>
          {showDownload && transcriptionData.text && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
              loading={downloadLoading}
              size="small"
            >
              Download
            </Button>
          )}
          {onClear && (
            <Button
              onClick={onClear}
              size="small"
            >
              Clear
            </Button>
          )}
          {extraActions}
        </Space>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Summary Statistics */}
        <Alert
          message={
            <Space>
              <CheckCircleOutlined />
              <span>Transcription Complete</span>
              {transcriptionData.language && (
                <Tag color="blue">{transcriptionData.language.toUpperCase()}</Tag>
              )}
            </Space>
          }
          description={
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text>
                {transcriptionData.word_count || transcriptionData.text.split(/\s+/).filter(word => word.length > 0).length} words transcribed
              </Text>
              {transcriptionData.duration && (
                <Text>
                  Duration: {Math.round(transcriptionData.duration)}s
                </Text>
              )}
              {transcriptionData.model && (
                <Text>
                  Model: {transcriptionData.model}
                </Text>
              )}
            </Space>
          }
          type="success"
          showIcon
        />

        {/* Detailed Statistics */}
        {(transcriptionData.duration || transcriptionData.processing_time || transcriptionData.model) && (
          <Row gutter={16}>
            {transcriptionData.processing_time && (
              <Col span={8}>
                <Statistic
                  title="Processing Time"
                  value={transcriptionData.processing_time}
                  suffix="s"
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: getVariantColor() }}
                />
              </Col>
            )}
            {transcriptionData.duration && (
              <Col span={8}>
                <Statistic
                  title="Audio Duration"
                  value={Math.round(transcriptionData.duration)}
                  suffix="s"
                  prefix={<SoundOutlined />}
                  valueStyle={{ color: getVariantColor() }}
                />
              </Col>
            )}
            <Col span={8}>
              <Statistic
                title="Words"
                value={transcriptionData.word_count || transcriptionData.text.split(/\s+/).filter(word => word.length > 0).length}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: getVariantColor() }}
              />
            </Col>
          </Row>
        )}

        {/* Transcription Text */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <Title level={4} style={{ margin: 0 }}>
              Transcribed Text
            </Title>
            <Space>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {transcriptionData.text.length} characters
              </Text>
            </Space>
          </div>
          <TextArea
            value={transcriptionData.text}
            readOnly
            autoSize={{ minRows: 8, maxRows: 25 }}
            style={{
              fontSize: '14px',
              lineHeight: '1.8',
              whiteSpace: 'pre-wrap',
              backgroundColor: '#fafafa',
              borderColor: getVariantColor(),
            }}
          />
        </div>
      </Space>
    </Card>
  )
}

export default TranscriptionResult