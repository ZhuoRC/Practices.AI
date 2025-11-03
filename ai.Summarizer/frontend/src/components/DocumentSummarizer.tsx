import { useState } from 'react'
import {
  Card,
  Upload,
  InputNumber,
  Button,
  Typography,
  Space,
  Alert,
  message,
  Row,
  Col,
  Spin,
} from 'antd'
import {
  FileTextOutlined,
  ThunderboltOutlined,
  InboxOutlined,
  LoadingOutlined,
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import { summarizeDocument } from '../services/api'
import './Summarizer.css'

const { Dragger } = Upload
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

interface DocumentSummarizerProps {
  onSummaryGenerated: (result: SummaryResult) => void
  summaryLength: number
  onSummaryLengthChange: (length: number) => void
}

export function DocumentSummarizer({
  onSummaryGenerated,
  summaryLength,
  onSummaryLengthChange,
}: DocumentSummarizerProps) {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const handleSummarize = async () => {
    if (fileList.length === 0) {
      message.warning('Please select a document file first')
      return
    }

    setLoading(true)
    setError('')

    try {
      const file = fileList[0].originFileObj as File
      const data = await summarizeDocument(file, summaryLength)

      onSummaryGenerated(data)
      message.success('Document summarized successfully!')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to summarize document'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    maxCount: 1,
    fileList: fileList,
    beforeUpload: () => false,
    onChange: (info) => {
      setFileList(info.fileList.slice(-1))
      setError('')
    },
    onDrop: (e) => {
      console.log('Dropped files', e.dataTransfer.files)
    },
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card className="input-card">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Title level={4}>
              <FileTextOutlined /> Document Summarization
            </Title>
            <Text type="secondary">
              Upload a document file (PDF, TXT, DOCX, MD) to generate a summary.
            </Text>
          </div>

          <Dragger {...uploadProps} accept=".pdf,.txt,.docx,.doc,.md">
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint">
              Support for PDF, TXT, DOCX, DOC, and Markdown files
            </p>
          </Dragger>

          <Row gutter={16} align="middle">
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>Summary Length (characters):</Text>
                <InputNumber
                  min={100}
                  max={2000}
                  value={summaryLength}
                  onChange={(value) => onSummaryLengthChange(value || 500)}
                  style={{ width: '100%' }}
                />
              </Space>
            </Col>
            <Col span={12} style={{ textAlign: 'right' }}>
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={handleSummarize}
                loading={loading}
                disabled={fileList.length === 0}
                size="large"
              >
                Generate Summary
              </Button>
            </Col>
          </Row>
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
              <Title level={4}>Generating Summary...</Title>
              <Text type="secondary">
                Processing your document. This may take a few moments depending on the file size.
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

export default DocumentSummarizer
