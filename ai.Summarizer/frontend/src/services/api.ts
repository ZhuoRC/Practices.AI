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

export default api
