import React from 'react'
import { Progress, Alert, Space, Typography, Spin } from 'antd'
import {
  FileTextOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography

interface ProgressIndicatorProps {
  loading: boolean
  progressMessage: string
  progressPercent: number
  isAsyncProcessing?: boolean
  title?: string
  showSteps?: boolean
  currentStep?: number
  totalSteps?: number
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  loading,
  progressMessage,
  progressPercent,
  isAsyncProcessing = false,
  title = "Processing...",
  showSteps = true,
  currentStep = 2,
  totalSteps = 4
}) => {
  if (!loading) return null

  // Define processing steps for different types
  const getSteps = () => {
    if (isAsyncProcessing) {
      return [
        {
          title: 'Prepare',
          description: 'Preparing audio file for transcription...',
          status: 'finish',
        },
        {
          title: 'Transcribe',
          description: 'Converting speech to text using Whisper...',
          status: 'process',
        },
        {
          title: 'Summarize',
          description: 'Generating AI summary from transcription...',
          status: 'wait',
        },
        {
          title: 'Complete',
          description: 'Finalizing results...',
          status: 'wait',
        },
      ]
    } else {
      return [
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
      ]
    }
  }

  const getProgressColor = () => {
    if (progressPercent >= 80) return '#52c41a'
    if (progressPercent >= 60) return '#fa8c16'
    return '#1890ff'
  }

  const getStatusIcon = () => {
    if (progressPercent >= 90) return <CheckCircleOutlined />
    if (progressPercent >= 50) return <ThunderboltOutlined />
    return <ClockCircleOutlined />
  }

  return (
    <div className="progress-indicator">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Spin size="large" />
          <Title level={4} style={{ marginTop: '16px', marginBottom: '8px' }}>
            {title}
          </Title>
          <Paragraph style={{ color: '#8c8c8c', fontSize: '16px' }}>
            {isAsyncProcessing
              ? 'Audio/video transcription may take several minutes...'
              : 'This may take a few minutes depending on document size...'}
          </Paragraph>
        </div>

        {/* Progress Message */}
        {progressMessage && (
          <Alert
            message="Current Status"
            description={
              <Space>
                {getStatusIcon()}
                <Text strong>{progressMessage}</Text>
              </Space>
            }
            type="info"
            showIcon={false}
            style={{ marginTop: '16px' }}
          />
        )}

        {/* Progress Bar */}
        <div>
          <Progress
            percent={progressPercent || 0}
            status="active"
            strokeColor={{
              '0%': '#108ee9',
              '100%': getProgressColor(),
            }}
            format={(percent) => `${percent}%`}
            trailColor="#f0f0f0"
          />
        </div>

        {/* Processing Steps */}
        {showSteps && (
          <div className="processing-steps">
            {getSteps().map((step, index) => (
              <div
                key={index}
                className={`step-item ${index === currentStep ? 'active' : ''} ${
                  index < currentStep ? 'completed' : ''
                }`}
                style={{
                  padding: '8px 0',
                  opacity: index <= currentStep ? 1 : 0.5,
                  transition: 'all 0.3s ease'
                }}
              >
                <Space>
                  {index < currentStep && <CheckCircleOutlined style={{ color: '#52c41a' }} />}
                  {index === currentStep && <ThunderboltOutlined style={{ color: '#1890ff' }} />}
                  {index > currentStep && <ClockCircleOutlined style={{ color: '#8c8c8c' }} />}
                  <div>
                    <Text strong={index <= currentStep}>
                      Step {index + 1}: {step.title}
                    </Text>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                      {step.description}
                    </div>
                  </div>
                </Space>
              </div>
            ))}
          </div>
        )}

        {/* Performance Tips */}
        <Alert
          message={isAsyncProcessing ? "Audio/Video Processing" : "Performance Tip"}
          description={
            isAsyncProcessing
              ? "The audio/video file is being transcribed using OpenAI Whisper on your GPU. After transcription, the text will be summarized using the Map-Reduce architecture."
              : "Larger documents are automatically split into optimal chunk sizes to balance speed and quality. Each chunk is processed sequentially for best accuracy."
          }
          type="info"
          showIcon
        />
      </Space>
    </div>
  )
}