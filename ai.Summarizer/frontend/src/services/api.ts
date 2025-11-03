import axios from 'axios'

const API_BASE_URL = 'http://localhost:8002'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface TokenUsage {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface SummaryResponse {
  summary: string
  chunk_count: number
  processing_time: number
  source_type: string
  source_name?: string
  token_usage: TokenUsage
  summary_id?: string
}

export interface SummaryMetadata {
  id: string
  timestamp: string
  source_type: string
  source_name: string
  num_chunks: number
  processing_time: number
  model: string
  provider: string
  token_usage: TokenUsage
  original_length: number
}

export interface HealthResponse {
  status: string
  llm_provider: string
  model: string
}

interface BackendResponse {
  success: boolean
  message: string
  data: {
    final_summary: string
    num_chunks: number
    processing_time: number
    filename?: string
    url?: string
    original_length: number
    token_usage: TokenUsage
    summary_id?: string
  }
}

export const summarizeDocument = async (file: File, summaryLength: number = 500): Promise<SummaryResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('summary_length', summaryLength.toString())

  const response = await api.post<BackendResponse>(
    '/api/summarize/document',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  // Transform backend response to frontend format
  return {
    summary: response.data.data.final_summary,
    chunk_count: response.data.data.num_chunks,
    processing_time: response.data.data.processing_time,
    source_type: 'document',
    source_name: response.data.data.filename,
    token_usage: response.data.data.token_usage,
    summary_id: response.data.data.summary_id,
  }
}

export const summarizeWebpage = async (url: string, summaryLength: number = 500): Promise<SummaryResponse> => {
  const response = await api.post<BackendResponse>('/api/summarize/webpage', {
    url,
    summary_length: summaryLength,
  })

  // Transform backend response to frontend format
  return {
    summary: response.data.data.final_summary,
    chunk_count: response.data.data.num_chunks,
    processing_time: response.data.data.processing_time,
    source_type: 'webpage',
    source_name: response.data.data.url,
    token_usage: response.data.data.token_usage,
    summary_id: response.data.data.summary_id,
  }
}

export const summarizeText = async (text: string, filename: string = 'text_input', summaryLength: number = 500): Promise<SummaryResponse> => {
  const response = await api.post<BackendResponse>('/api/summarize/text', {
    text,
    filename,
    summary_length: summaryLength,
  })

  // Transform backend response to frontend format
  return {
    summary: response.data.data.final_summary,
    chunk_count: response.data.data.num_chunks,
    processing_time: response.data.data.processing_time,
    source_type: 'text',
    source_name: response.data.data.filename,
    token_usage: response.data.data.token_usage,
    summary_id: response.data.data.summary_id,
  }
}

interface BackendHealthResponse {
  status: string
  llm_provider: string
  llm_model: string
}

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<BackendHealthResponse>('/api/summarize/health')

  // Transform backend response to frontend format
  return {
    status: response.data.status,
    llm_provider: response.data.llm_provider,
    model: response.data.llm_model,
  }
}

// Download summary as file
export const downloadSummary = (summary: SummaryResponse, filename: string) => {
  const content = `# ${summary.source_name || 'Summary'}

## Metadata
- Source Type: ${summary.source_type}
- Chunks Processed: ${summary.chunk_count}
- Processing Time: ${summary.processing_time}s
- Total Tokens: ${summary.token_usage.total_tokens}
- Prompt Tokens: ${summary.token_usage.prompt_tokens}
- Completion Tokens: ${summary.token_usage.completion_tokens}

## Summary

${summary.summary}
`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Get summary history
export const getSummaryHistory = async (
  limit: number = 20,
  offset: number = 0,
  sourceType?: string
): Promise<SummaryMetadata[]> => {
  const params: any = { limit, offset }
  if (sourceType) params.source_type = sourceType

  const response = await api.get('/api/summarize/history', { params })
  return response.data.summaries
}

// Get specific summary by ID
export const getSummaryById = async (summaryId: string) => {
  const response = await api.get(`/api/summarize/history/${summaryId}`)
  return response.data.data
}

// Delete summary
export const deleteSummary = async (summaryId: string) => {
  const response = await api.delete(`/api/summarize/history/${summaryId}`)
  return response.data
}

// Get statistics
export const getStatistics = async () => {
  const response = await api.get('/api/summarize/statistics')
  return response.data.statistics
}

// Helper: Check if file is audio/video
export const isAudioVideoFile = (filename: string): boolean => {
  const audioVideoExt = ['.mp3', '.wav', '.m4a', '.mp4', '.avi', '.mov', '.mkv']
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return audioVideoExt.includes(ext)
}

// Submit document for async processing
export interface AsyncTaskResponse {
  success: boolean
  task_id: string
  message: string
  poll_endpoint: string
}

export const submitDocumentAsync = async (file: File, summaryLength: number = 500): Promise<AsyncTaskResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('summary_length', summaryLength.toString())

  const response = await api.post<AsyncTaskResponse>(
    '/api/summarize/document/async',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  return response.data
}

// Task status and result
export interface TaskResult {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
  filename: string
  file_size: number
  progress?: string
  progress_percent?: number  // Progress percentage (0-100)
  error?: string
  summary?: string
  chunk_count?: number
  total_tokens?: number
  processing_time?: number
  transcription_duration?: number
  transcription_text_length?: number
}

export interface TaskStatusResponse {
  success: boolean
  task: TaskResult
}

// Poll task status
export const pollTaskStatus = async (taskId: string): Promise<TaskResult> => {
  const response = await api.get<TaskStatusResponse>(`/api/summarize/task/${taskId}`)
  return response.data.task
}

// Poll until completion with retry logic
export const pollUntilComplete = async (
  taskId: string,
  onProgress?: (task: TaskResult) => void,
  pollInterval: number = 2000,
  maxAttempts: number = 300 // 10 minutes max at 2s intervals
): Promise<TaskResult> => {
  let attempts = 0

  while (attempts < maxAttempts) {
    const task = await pollTaskStatus(taskId)

    // Notify progress callback
    if (onProgress) {
      onProgress(task)
    }

    // Check if completed or failed
    if (task.status === 'completed') {
      return task
    }

    if (task.status === 'failed') {
      throw new Error(task.error || 'Task failed')
    }

    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, pollInterval))
    attempts++
  }

  throw new Error('Polling timeout: Task did not complete in time')
}

// Enhanced summarize document that auto-detects audio/video and uses async processing
export const summarizeDocumentEnhanced = async (
  file: File,
  summaryLength: number = 500,
  onProgress?: (task: TaskResult) => void
): Promise<SummaryResponse> => {
  // Check if it's an audio/video file
  if (isAudioVideoFile(file.name)) {
    // Use async endpoint for audio/video
    const asyncResponse = await submitDocumentAsync(file, summaryLength)

    // Poll until completion
    const taskResult = await pollUntilComplete(asyncResponse.task_id, onProgress)

    // Transform to SummaryResponse
    return {
      summary: taskResult.summary || '',
      chunk_count: taskResult.chunk_count || 0,
      processing_time: taskResult.processing_time || 0,
      source_type: 'audio/video',
      source_name: taskResult.filename,
      token_usage: {
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: taskResult.total_tokens || 0,
      },
    }
  } else {
    // Use synchronous endpoint for regular documents
    return await summarizeDocument(file, summaryLength)
  }
}

// Submit audio/video for transcription only (no summarization)
export const submitTranscriptionAsync = async (file: File): Promise<AsyncTaskResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<AsyncTaskResponse>(
    '/api/summarize/transcribe/async',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  return response.data
}

// Transcribe audio/video to text (full transcription, no summary)
export const transcribeAudio = async (
  file: File,
  language: string | null = null,
  onProgress?: (task: TaskResult) => void
): Promise<TaskResult> => {
  // Submit for transcription
  const asyncResponse = await submitTranscriptionAsync(file)

  // Poll until completion with more frequent updates for transcription
  const taskResult = await pollUntilComplete(
    asyncResponse.task_id,
    onProgress,
    1000, // Poll every 1 second for transcription (more frequent)
    1800 // 30 minutes max for long audio files
  )

  // Return full task result
  return taskResult
}

export default api
