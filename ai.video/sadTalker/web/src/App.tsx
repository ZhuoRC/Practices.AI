import { useState, useRef, useCallback, useEffect } from 'react'
import './App.css'

interface TaskStatus {
  status: 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  result: string | null
  error: string | null
}

interface GenerateSettings {
  preprocess: string
  stillMode: boolean
  useEnhancer: boolean
  batchSize: number
  size: number
  poseStyle: number
  expressionScale: number
}

const API_BASE = '/api'

function App() {
  const [sourceImage, setSourceImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [drivenAudio, setDrivenAudio] = useState<File | null>(null)
  const [audioPreview, setAudioPreview] = useState<string>('')

  const [settings, setSettings] = useState<GenerateSettings>({
    preprocess: 'crop',
    stillMode: false,
    useEnhancer: false,
    batchSize: 2,
    size: 256,
    poseStyle: 0,
    expressionScale: 1.0
  })

  const [isLoading, setIsLoading] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null)
  const [error, setError] = useState<string>('')

  const imageInputRef = useRef<HTMLInputElement>(null)
  const audioInputRef = useRef<HTMLInputElement>(null)
  const pollIntervalRef = useRef<number | null>(null)

  // 处理图片选择
  const handleImageSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSourceImage(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target?.result as string)
      reader.readAsDataURL(file)
    }
  }, [])

  // 处理音频选择
  const handleAudioSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setDrivenAudio(file)
      setAudioPreview(URL.createObjectURL(file))
    }
  }, [])

  // 轮询任务状态
  const pollTaskStatus = useCallback(async (id: string) => {
    try {
      const response = await fetch(`${API_BASE}/task/${id}`)
      const data: TaskStatus = await response.json()
      setTaskStatus(data)

      if (data.status === 'completed' || data.status === 'failed') {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
        }
        setIsLoading(false)

        if (data.status === 'failed') {
          setError(data.error || '生成失败')
        }
      }
    } catch (err) {
      console.error('轮询失败:', err)
    }
  }, [])

  // 开始轮询
  const startPolling = useCallback((id: string) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
    }
    pollIntervalRef.current = window.setInterval(() => pollTaskStatus(id), 2000)
  }, [pollTaskStatus])

  // 提交生成任务
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!sourceImage || !drivenAudio) {
      setError('请上传图片和音频文件')
      return
    }

    setError('')
    setIsLoading(true)
    setTaskStatus(null)

    const formData = new FormData()
    formData.append('source_image', sourceImage)
    formData.append('driven_audio', drivenAudio)
    formData.append('preprocess', settings.preprocess)
    formData.append('still_mode', String(settings.stillMode))
    formData.append('use_enhancer', String(settings.useEnhancer))
    formData.append('batch_size', String(settings.batchSize))
    formData.append('size', String(settings.size))
    formData.append('pose_style', String(settings.poseStyle))
    formData.append('expression_scale', String(settings.expressionScale))

    try {
      const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '提交失败')
      }

      const data = await response.json()
      setTaskId(data.task_id)
      startPolling(data.task_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败')
      setIsLoading(false)
    }
  }

  // 重置表单
  const handleReset = () => {
    setSourceImage(null)
    setImagePreview('')
    setDrivenAudio(null)
    setAudioPreview('')
    setTaskId(null)
    setTaskStatus(null)
    setError('')
    setIsLoading(false)
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
  }

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>SadTalker</h1>
        <p className="subtitle">AI 驱动的说话视频生成器</p>
      </header>

      <main className="main">
        <form onSubmit={handleSubmit} className="form">
          {/* 文件上传区域 */}
          <div className="upload-row">
            {/* 图片上传 */}
            <div className="upload-group">
              <label>源图片</label>
              <div
                className={`upload-area ${imagePreview ? 'has-file' : ''}`}
                onClick={() => imageInputRef.current?.click()}
              >
                <input
                  ref={imageInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  hidden
                />
                {imagePreview ? (
                  <img src={imagePreview} alt="预览" className="preview-image" />
                ) : (
                  <div className="upload-placeholder">
                    <span className="upload-icon">+</span>
                    <span>点击上传图片</span>
                    <span className="hint">支持 JPG, PNG</span>
                  </div>
                )}
              </div>
            </div>

            {/* 音频上传 */}
            <div className="upload-group">
              <label>驱动音频</label>
              <div
                className={`upload-area ${drivenAudio ? 'has-file' : ''}`}
                onClick={() => audioInputRef.current?.click()}
              >
                <input
                  ref={audioInputRef}
                  type="file"
                  accept="audio/*"
                  onChange={handleAudioSelect}
                  hidden
                />
                {drivenAudio ? (
                  <div className="audio-info">
                    <span className="audio-icon">♪</span>
                    <span className="audio-name">{drivenAudio.name}</span>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <span className="upload-icon">+</span>
                    <span>点击上传音频</span>
                    <span className="hint">支持 WAV, MP3</span>
                  </div>
                )}
              </div>
              {audioPreview && (
                <audio src={audioPreview} controls className="audio-preview" />
              )}
            </div>
          </div>

          {/* 设置面板 */}
          <div className="settings-panel">
            <h3>生成设置</h3>
            <div className="settings-grid">
              <div className="setting-item">
                <label>预处理方式</label>
                <select
                  value={settings.preprocess}
                  onChange={e => setSettings({...settings, preprocess: e.target.value})}
                >
                  <option value="crop">crop - 裁剪人脸</option>
                  <option value="resize">resize - 调整大小</option>
                  <option value="full">full - 全身</option>
                  <option value="extcrop">extcrop - 扩展裁剪</option>
                  <option value="extfull">extfull - 扩展全身</option>
                </select>
              </div>

              <div className="setting-item">
                <label>分辨率</label>
                <select
                  value={settings.size}
                  onChange={e => setSettings({...settings, size: Number(e.target.value)})}
                >
                  <option value={256}>256 x 256</option>
                  <option value={512}>512 x 512</option>
                </select>
              </div>

              <div className="setting-item">
                <label>姿态风格 (0-45)</label>
                <input
                  type="number"
                  value={settings.poseStyle}
                  min={0}
                  max={45}
                  onChange={e => setSettings({...settings, poseStyle: Number(e.target.value)})}
                />
              </div>

              <div className="setting-item">
                <label>表情强度</label>
                <input
                  type="number"
                  value={settings.expressionScale}
                  min={0.1}
                  max={2.0}
                  step={0.1}
                  onChange={e => setSettings({...settings, expressionScale: Number(e.target.value)})}
                />
              </div>

              <div className="setting-item">
                <label>批处理大小</label>
                <input
                  type="number"
                  value={settings.batchSize}
                  min={1}
                  max={10}
                  onChange={e => setSettings({...settings, batchSize: Number(e.target.value)})}
                />
              </div>

              <div className="setting-item checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.stillMode}
                    onChange={e => setSettings({...settings, stillMode: e.target.checked})}
                  />
                  静止模式 (减少头部运动)
                </label>
              </div>

              <div className="setting-item checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.useEnhancer}
                    onChange={e => setSettings({...settings, useEnhancer: e.target.checked})}
                  />
                  使用 GFPGAN 增强
                </label>
              </div>
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={isLoading}>
            {isLoading ? (
              <>
                <span className="spinner"></span>
                处理中...
              </>
            ) : '生成视频'}
          </button>
        </form>

        {/* 错误提示 */}
        {error && (
          <div className="error-section">
            <h3>错误</h3>
            <p>{error}</p>
            <button onClick={handleReset} className="retry-btn">重试</button>
          </div>
        )}

        {/* 进度显示 */}
        {taskStatus && taskStatus.status === 'processing' && (
          <div className="progress-section">
            <h3>生成进度</h3>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${taskStatus.progress}%` }}
              />
            </div>
            <p className="progress-message">{taskStatus.message}</p>
          </div>
        )}

        {/* 结果展示 */}
        {taskStatus && taskStatus.status === 'completed' && taskId && (
          <div className="result-section">
            <h3>生成结果</h3>
            <video
              src={`${API_BASE}/download/${taskId}`}
              controls
              className="result-video"
            />
            <div className="result-actions">
              <a
                href={`${API_BASE}/download/${taskId}`}
                download={`sadtalker_${taskId}.mp4`}
                className="download-btn"
              >
                下载视频
              </a>
              <button onClick={handleReset} className="new-btn">
                生成新视频
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>
          基于 <a href="https://github.com/OpenTalker/SadTalker" target="_blank" rel="noreferrer">SadTalker</a> 构建
        </p>
      </footer>
    </div>
  )
}

export default App
