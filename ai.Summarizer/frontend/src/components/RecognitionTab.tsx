import { useState } from 'react'
import {
  Card,
  Upload,
  Button,
  Typography,
  Space,
  Alert,
  message,
  Row,
  Col,
} from 'antd'
import {
  SoundOutlined,
  ThunderboltOutlined,
  InboxOutlined,
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import {
  transcribeAudio,
  isAudioVideoFile,
  type TaskResult
} from '../services/api'
import { ProgressIndicator } from './ProgressIndicator'
import { TranscriptionResult } from './TranscriptionResult'
import './Summarizer.css'

const { Dragger } = Upload
const { Title, Text } = Typography

export function RecognitionTab() {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [progressMessage, setProgressMessage] = useState<string>('')
  const [progressPercent, setProgressPercent] = useState<number>(0)
  const [transcriptionText, setTranscriptionText] = useState<string>('')
  const [isTranscribing, setIsTranscribing] = useState<boolean>(false)

  const handleTranscribe = async () => {
    if (fileList.length === 0) {
      message.warning('Please select an audio or video file first')
      return
    }

    setLoading(true)
    setError('')
    setProgressMessage('Uploading file and starting transcription...')
    setProgressPercent(5)
    setTranscriptionText('')

    try {
      const file = fileList[0].originFileObj as File

      // Validate file type
      if (!isAudioVideoFile(file.name)) {
        throw new Error('Please upload an audio or video file (MP3, WAV, M4A, MP4, AVI, MOV, MKV)')
      }

      setIsTranscribing(true)

      // Transcribe audio/video
      const data = await transcribeAudio(
        file,
        null, // auto-detect language
        (task: TaskResult) => {
          console.log('Progress update:', task)
          if (task.progress) {
            setProgressMessage(task.progress)
            console.log('Set progress message:', task.progress)
          }
          if (task.progress_percent !== undefined) {
            setProgressPercent(task.progress_percent)
            console.log('Set progress percent:', task.progress_percent)
          }
        }
      )

      // Set transcription text
      if (data.summary) {
        setTranscriptionText(data.summary)
        message.success('Transcription completed successfully!')
      } else {
        // If no transcription text, show warning
        setError('Transcription completed but no text was returned')
        message.warning('Transcription completed but no text was returned')
      }

    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to transcribe audio/video'
      setError(errorMsg)
      message.error(errorMsg)
      console.error('Transcription error:', err)
    } finally {
      setLoading(false)
      setIsTranscribing(false)
    }
  }

  const handleClearTranscription = () => {
    setTranscriptionText('')
    setFileList([])
    setError('')
    setProgressMessage('')
    setProgressPercent(0)
    message.info('Transcription cleared')
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
      setTranscriptionText('')
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
              <SoundOutlined /> Speech Recognition
            </Title>
            <Text type="secondary">
              Upload an audio or video file to transcribe speech to text.
            </Text>
          </div>

          <Dragger {...uploadProps} accept=".mp3,.wav,.m4a,.mp4,.avi,.mov,.mkv,.flac,.ogg,.aac,.wma,.wmv,.flv,.webm">
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint">
              Support for audio files (MP3, WAV, M4A, FLAC, OGG, AAC) and video files (MP4, AVI, MOV, MKV, WMV, FLV, WebM)
            </p>
          </Dragger>

          <Row gutter={16}>
            <Col span={24} style={{ textAlign: 'right' }}>
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={handleTranscribe}
                loading={loading}
                disabled={fileList.length === 0}
                size="large"
              >
                Start Transcription
              </Button>
            </Col>
          </Row>
        </Space>
      </Card>

      {/* Progress Indicator */}
      {loading && (
        <Card className="progress-card">
          <ProgressIndicator
            loading={loading}
            progressMessage={progressMessage || 'Starting transcription...'}
            progressPercent={progressPercent}
            isAsyncProcessing={true}
            title="Speech Recognition in Progress..."
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
        title="Speech Recognition Result"
        variant="document"
        onClear={handleClearTranscription}
        showSummarize={false}
      />
    </Space>
  )
}

export default RecognitionTab
