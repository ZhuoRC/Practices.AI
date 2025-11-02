import { useState } from 'react'
import {
  Card,
  Upload,
  Input,
  InputNumber,
  Button,
  Typography,
  Space,
  Alert,
  message,
  Row,
  Col,
} from 'antd'
import {
  FileTextOutlined,
  CloudUploadOutlined,
  ThunderboltOutlined,
  ApiOutlined,
} from '@ant-design/icons'
import type { UploadFile } from 'antd'
import {
  summarizeDocumentEnhanced,
  transcribeAudio,
  isAudioVideoFile,
  type TaskResult
} from '../services/api'
import { ProgressIndicator } from './ProgressIndicator'
import { TranscriptionResult } from './TranscriptionResult'
import './Summarizer.css'

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
  const [progressMessage, setProgressMessage] = useState<string>('')
  const [progressPercent, setProgressPercent] = useState<number>(0)
  const [isAsyncProcessing, setIsAsyncProcessing] = useState<boolean>(false)
  const [transcriptionText, setTranscriptionText] = useState<string>('')
  const [isTranscribing, setIsTranscribing] = useState<boolean>(false)

  const handleDocumentUpload = async () => {
    if (fileList.length === 0) {
      message.warning('Please select a file first')
      return
    }

    setLoading(true)
    setError('')
    setProgressMessage('')
    setProgressPercent(0)
    setTranscriptionText('') // Clear previous transcription

    try {
      const file = fileList[0].originFileObj as File

      // Check if it's an audio/video file
      const isAsync = isAudioVideoFile(file.name)
      setIsAsyncProcessing(isAsync)

      if (isAsync) {
        message.info('Audio/video file detected. Processing may take several minutes...')
      }

      // Use enhanced API with progress callback
      const data = await summarizeDocumentEnhanced(
        file,
        summaryLength,
        (task: TaskResult) => {
          // Update progress message and percentage
          if (task.progress) {
            setProgressMessage(task.progress)
          }
          if (task.progress_percent !== undefined) {
            setProgressPercent(task.progress_percent)
          }
        }
      )

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

  const handleTranscription = async () => {
    if (fileList.length === 0) {
      message.warning('Please select an audio/video file first')
      return
    }

    const file = fileList[0].originFileObj as File

    // Check if it's an audio/video file
    if (!isAudioVideoFile(file.name)) {
      message.error('Please select an audio or video file (MP3, WAV, M4A, MP4, AVI, MOV, MKV)')
      return
    }

    setIsTranscribing(true)
    setError('')
    setTranscriptionText('')
    setProgressMessage('')
    setProgressPercent(0)

    try {
      message.info('Starting transcription. This may take a few minutes...')

      // Transcribe audio
      const transcription = await transcribeAudio(
        file,
        (task: TaskResult) => {
          // Update progress message and percentage
          if (task.progress) {
            setProgressMessage(task.progress)
          }
          if (task.progress_percent !== undefined) {
            setProgressPercent(task.progress_percent)
          }
        }
      )

      setTranscriptionText(transcription)
      message.success('Transcription completed successfully!')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to transcribe audio'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setIsTranscribing(false)
      setProgressMessage('')
      setProgressPercent(0)
    }
  }

  const handleFileChange = (info: any) => {
    let newFileList = [...info.fileList]
    newFileList = newFileList.slice(-1)
    setFileList(newFileList)
    setError('')
    setTranscriptionText('') // Clear transcription when file changes
  }

  const handleClearTranscription = () => {
    setTranscriptionText('')
    message.info('Transcription cleared')
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Alert
        message="Supported Formats"
        description="Documents: PDF, DOCX, TXT, Markdown | Audio: MP3, WAV, M4A | Video: MP4, AVI, MOV, MKV"
        type="info"
        showIcon
      />

      <Upload.Dragger
        fileList={fileList}
        onChange={handleFileChange}
        beforeUpload={() => false}
        accept=".pdf,.docx,.txt,.md,.mp3,.wav,.m4a,.mp4,.avi,.mov,.mkv"
        maxCount={1}
      >
        <p className="ant-upload-drag-icon">
          <CloudUploadOutlined />
        </p>
        <p className="ant-upload-text">
          Click or drag file to this area to upload
        </p>
        <p className="ant-upload-hint">
          Support for documents (PDF, DOCX, TXT, MD), audio (MP3, WAV, M4A), and video (MP4, AVI, MOV, MKV)
        </p>
      </Upload.Dragger>

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

      <Row gutter={16}>
        <Col span={12}>
          <Button
            type="primary"
            size="large"
            block
            onClick={handleDocumentUpload}
            loading={loading}
            disabled={fileList.length === 0 || isTranscribing}
            icon={<ThunderboltOutlined />}
          >
            Generate Summary
          </Button>
        </Col>
        <Col span={12}>
          <Button
            type="default"
            size="large"
            block
            onClick={handleTranscription}
            loading={isTranscribing}
            disabled={fileList.length === 0 || loading || !isAudioVideoFile(fileList[0]?.name || '')}
            icon={<ApiOutlined />}
            style={{ borderColor: '#1890ff', color: '#1890ff' }}
          >
            Speech Recognition
          </Button>
        </Col>
      </Row>

      {/* Progress Indicator for Document Processing */}
      {loading && (
        <Card className="result-card" title="Processing...">
          <ProgressIndicator
            loading={loading}
            progressMessage={progressMessage}
            progressPercent={progressPercent}
            isAsyncProcessing={isAsyncProcessing}
            title={isAsyncProcessing ? "Audio/Video Processing..." : "Document Processing..."}
            showSteps={true}
            currentStep={isAsyncProcessing ? 2 : 2}
          />
        </Card>
      )}

      {/* Progress Indicator for Transcription */}
      {isTranscribing && (
        <Card className="result-card" title="Speech Recognition...">
          <ProgressIndicator
            loading={isTranscribing}
            progressMessage={progressMessage}
            progressPercent={progressPercent}
            isAsyncProcessing={true}
            title="Transcribing audio to text using Whisper..."
            showSteps={true}
            currentStep={1}
          />
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="result-card">
          <Alert message="Error" description={error} type="error" showIcon />
        </Card>
      )}

      {/* Transcription Result */}
      <TranscriptionResult
        transcription={transcriptionText}
        loading={isTranscribing}
        title="Document Transcription Result"
        variant="document"
        onClear={handleClearTranscription}
      />
    </Space>
  )
}

export default DocumentSummarizer