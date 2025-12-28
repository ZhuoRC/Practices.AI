# 阶段5：Web界面和API分析和实现计划

## 1. 需求分析

### 核心目标
- 提供用户友好的Web界面操作整个视频生成流程
- 实现RESTful API支持程序化调用
- 提供实时进度监控和状态反馈
- 支持项目管理和历史记录
- 实现用户配置和预设管理

### 功能特性
- 项目创建和配置
- 脚本上传和编辑
- 音频和视频参数配置
- 实时处理进度显示
- 结果预览和下载
- 批处理管理
- 系统监控和日志

## 2. 技术架构设计

### 2.1 后端API架构

#### FastAPI主应用
```python
# web_interface/backend/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from api.routes import projects, scripts, audio, video, merge, system
from core.config import Settings
from core.database import Database
from core.scheduler import TaskScheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    app.state.settings = Settings()
    app.state.db = Database(app.state.settings.database_url)
    await app.state.db.initialize()
    
    app.state.scheduler = TaskScheduler()
    await app.state.scheduler.start()
    
    yield
    
    # 关闭时清理
    await app.state.scheduler.stop()
    await app.state.db.close()

# 创建FastAPI应用
app = FastAPI(
    title="AI视频生成器",
    description="基于AI的自动化视频生成系统",
    version="1.0.0",
    lifespan=lifespan
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="../outputs"), name="outputs")

# API路由
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["脚本处理"])
app.include_router(audio.router, prefix="/api/audio", tags=["音频生成"])
app.include_router(video.router, prefix="/api/video", tags=["视频生成"])
app.include_router(merge.router, prefix="/api/merge", tags=["视频合并"])
app.include_router(system.router, prefix="/api/system", tags=["系统管理"])

@app.get("/")
async def root():
    """根路径"""
    return {"message": "AI视频生成器 API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

#### 项目管理API
```python
# web_interface/backend/api/routes/projects.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_database
from models.project import Project, ProjectCreate, ProjectUpdate
from services.project_service import ProjectService

router = APIRouter()

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    script_content: str
    config: Optional[dict] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    config: dict
    progress: float

@router.post("/", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreateRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """创建新项目"""
    try:
        project_service = ProjectService(db)
        
        # 创建项目
        project = await project_service.create_project(
            name=request.name,
            description=request.description,
            script_content=request.script_content,
            config=request.config or {}
        )
        
        # 启动后台处理任务
        background_tasks.add_task(
            process_project_pipeline,
            project.id
        )
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
            config=project.config,
            progress=0.0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db = Depends(get_database)
):
    """获取项目列表"""
    project_service = ProjectService(db)
    projects = await project_service.list_projects(
        skip=skip, 
        limit=limit, 
        status=status
    )
    
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
            config=p.config,
            progress=p.progress
        )
        for p in projects
    ]

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db = Depends(get_database)
):
    """获取项目详情"""
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        config=project.config,
        progress=project.progress
    )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    db = Depends(get_database)
):
    """更新项目"""
    project_service = ProjectService(db)
    project = await project_service.update_project(project_id, request)
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        config=project.config,
        progress=project.progress
    )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db = Depends(get_database)
):
    """删除项目"""
    project_service = ProjectService(db)
    success = await project_service.delete_project(project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return {"message": "项目已删除"}

@router.get("/{project_id}/progress")
async def get_project_progress(
    project_id: str,
    db = Depends(get_database)
):
    """获取项目处理进度"""
    project_service = ProjectService(db)
    progress = await project_service.get_project_progress(project_id)
    
    if progress is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return {
        "project_id": project_id,
        "progress": progress.progress,
        "current_stage": progress.current_stage,
        "estimated_time_remaining": progress.estimated_time_remaining,
        "details": progress.details
    }
```

#### 脚本处理API
```python
# web_interface/backend/api/routes/scripts.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional

from services.script_service import ScriptService
from models.script import ScriptProcessRequest, ScriptResponse

router = APIRouter()

@router.post("/upload")
async def upload_script(file: UploadFile = File(...)):
    """上传脚本文件"""
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="只支持.txt文件")
    
    try:
        script_service = ScriptService()
        
        # 保存上传的文件
        content = await file.read()
        script_text = content.decode('utf-8')
        
        # 处理脚本
        processed_script = await script_service.process_script(script_text)
        
        return ScriptResponse(
            script_id=processed_script.id,
            segments=len(processed_script.segments),
            total_duration=processed_script.metadata.total_duration,
            language=processed_script.metadata.language
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本处理失败: {str(e)}")

@router.post("/process")
async def process_script(request: ScriptProcessRequest):
    """处理脚本内容"""
    try:
        script_service = ScriptService()
        processed_script = await script_service.process_script(
            text=request.text,
            style=request.style,
            config=request.config
        )
        
        return {
            "script_id": processed_script.id,
            "metadata": processed_script.metadata,
            "segments": [
                {
                    "id": seg.id,
                    "index": seg.index,
                    "title": seg.title,
                    "estimated_duration": seg.estimated_duration,
                    "keywords": [{"word": kw.word, "importance": kw.importance} for kw in seg.keywords]
                }
                for seg in processed_script.segments
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本处理失败: {str(e)}")

@router.get("/presets")
async def get_script_presets():
    """获取脚本处理预设"""
    return {
        "styles": [
            {"id": "conversational", "name": "对话风格", "description": "自然口语化"},
            {"id": "educational", "name": "教育风格", "description": "专业易懂"},
            {"id": "storytelling", "name": "故事风格", "description": "生动有趣"}
        ],
        "segment_configs": {
            "short": {"target_duration": 30, "max_duration": 45},
            "medium": {"target_duration": 45, "max_duration": 60},
            "long": {"target_duration": 60, "max_duration": 90}
        }
    }
```

### 2.2 WebSocket实时通信

#### 进度推送服务
```python
# web_interface/backend/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """连接WebSocket"""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        
        self.active_connections[project_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """断开WebSocket连接"""
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                self.active_connections[project_id].remove(websocket)
            
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_text(message)
    
    async def broadcast_to_project(self, message: dict, project_id: str):
        """向项目广播消息"""
        if project_id in self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False, default=str)
            
            # 创建发送任务列表
            tasks = []
            for connection in self.active_connections[project_id]:
                task = asyncio.create_task(
                    self._safe_send(connection, message_str)
                )
                tasks.append(task)
            
            # 并发发送
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_send(self, websocket: WebSocket, message: str):
        """安全发送消息"""
        try:
            await websocket.send_text(message)
        except Exception:
            # 连接已断开，忽略
            pass

manager = ConnectionManager()

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket端点"""
    await manager.connect(websocket, project_id)
    
    try:
        # 发送初始状态
        await manager.send_personal_message(
            json.dumps({"type": "connected", "project_id": project_id}),
            websocket
        )
        
        # 保持连接并处理客户端消息
        while True:
            data = await websocket.receive_text()
            
            # 处理客户端消息
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        websocket
                    )
                
            except json.JSONDecodeError:
                continue
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)

# 进度广播函数
async def broadcast_progress(project_id: str, stage: str, progress: float, details: dict = None):
    """广播进度更新"""
    message = {
        "type": "progress_update",
        "project_id": project_id,
        "stage": stage,
        "progress": progress,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    await manager.broadcast_to_project(message, project_id)

async def broadcast_stage_complete(project_id: str, stage: str, result: dict = None):
    """广播阶段完成"""
    message = {
        "type": "stage_complete",
        "project_id": project_id,
        "stage": stage,
        "result": result or {},
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast_to_project(message, project_id)

async def broadcast_error(project_id: str, error: str, stage: str = None):
    """广播错误信息"""
    message = {
        "type": "error",
        "project_id": project_id,
        "error": error,
        "stage": stage,
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast_to_project(message, project_id)
```

### 2.3 前端React应用

#### 主应用组件
```typescript
// web_interface/frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, theme } from 'antd';
import ProjectList from './components/ProjectList';
import ProjectDetail from './components/ProjectDetail';
import ScriptEditor from './components/ScriptEditor';
import VideoPreview from './components/VideoPreview';
import SystemMonitor from './components/SystemMonitor';
import { WebSocketProvider } from './contexts/WebSocketContext';

const { Header, Content, Sider } = Layout;

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  return (
    <Router>
      <WebSocketProvider>
        <Layout style={{ minHeight: '100vh' }}>
          <Sider 
            collapsible 
            collapsed={collapsed} 
            onCollapse={setCollapsed}
            theme={darkMode ? 'dark' : 'light'}
          >
            <div className="logo" />
            <NavigationMenu />
          </Sider>
          
          <Layout>
            <Header style={{ 
              padding: 0, 
              background: colorBgContainer 
            }}>
              <TopBar 
                darkMode={darkMode} 
                onToggleDarkMode={() => setDarkMode(!darkMode)}
              />
            </Header>
            
            <Content style={{ 
              margin: '24px 16px',
              padding: 24,
              background: colorBgContainer,
              borderRadius: 8
            }}>
              <Routes>
                <Route path="/" element={<ProjectList />} />
                <Route path="/projects/:id" element={<ProjectDetail />} />
                <Route path="/script/:id" element={<ScriptEditor />} />
                <Route path="/preview/:id" element={<VideoPreview />} />
                <Route path="/monitor" element={<SystemMonitor />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </WebSocketProvider>
    </Router>
  );
};

export default App;
```

#### 项目列表组件
```typescript
// web_interface/frontend/src/components/ProjectList.tsx
import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Tag, 
  Progress, 
  Modal, 
  message,
  Input,
  Select,
  Card,
  Statistic
} from 'antd';
import { 
  PlusOutlined, 
  EyeOutlined, 
  DeleteOutlined,
  PlayCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ProjectAPI, Project } from '../services/api';
import { CreateProjectModal } from './CreateProjectModal';
import { useWebSocket } from '../contexts/WebSocketContext';

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();
  const { subscribeToProject } = useWebSocket();

  // 加载项目列表
  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await ProjectAPI.getProjects({
        status: statusFilter || undefined,
        search: searchText || undefined
      });
      setProjects(data);
    } catch (error) {
      message.error('加载项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, [statusFilter, searchText]);

  // 订阅WebSocket更新
  useEffect(() => {
    projects.forEach(project => {
      if (project.status === 'processing') {
        const unsubscribe = subscribeToProject(project.id, (data) => {
          if (data.type === 'progress_update') {
            setProjects(prev => 
              prev.map(p => 
                p.id === project.id 
                  ? { ...p, progress: data.progress }
                  : p
              )
            );
          }
        });
        
        return unsubscribe;
      }
    });
  }, [projects, subscribeToProject]);

  const handleDelete = async (projectId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个项目吗？此操作不可撤销。',
      onOk: async () => {
        try {
          await ProjectAPI.deleteProject(projectId);
          message.success('项目已删除');
          loadProjects();
        } catch (error) {
          message.error('删除项目失败');
        }
      }
    });
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'pending': 'default',
      'processing': 'processing',
      'completed': 'success',
      'failed': 'error'
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts = {
      'pending': '等待中',
      'processing': '处理中',
      'completed': '已完成',
      'failed': '失败'
    };
    return texts[status] || status;
  };

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Project) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/projects/${record.id}`)}
        >
          {text}
        </Button>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      )
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number, record: Project) => (
        record.status === 'processing' ? (
          <Progress percent={Math.round(progress * 100)} size="small" />
        ) : (
          <span>-</span>
        )
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record: Project) => (
        <Space>
          <Button 
            icon={<EyeOutlined />} 
            onClick={() => navigate(`/projects/${record.id}`)}
          >
            查看
          </Button>
          {record.status === 'completed' && (
            <Button 
              icon={<PlayCircleOutlined />}
              onClick={() => navigate(`/preview/${record.id}`)}
            >
              预览
            </Button>
          )}
          <Button 
            icon={<DeleteOutlined />} 
            danger 
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Input.Search
              placeholder="搜索项目名称"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 200 }}
            />
            <Select
              placeholder="状态筛选"
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 120 }}
              allowClear
            >
              <Select.Option value="pending">等待中</Select.Option>
              <Select.Option value="processing">处理中</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
              <Select.Option value="failed">失败</Select.Option>
            </Select>
          </Space>
          
          <Space>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={loadProjects}
            >
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建项目
            </Button>
          </Space>
        </div>
      </Card>

      <Table
        columns={columns}
        dataSource={projects}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 个项目`
        }}
      />

      <CreateProjectModal
        visible={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onSuccess={() => {
          setCreateModalVisible(false);
          loadProjects();
        }}
      />
    </div>
  );
};

export default ProjectList;
```

#### 脚本编辑器组件
```typescript
// web_interface/frontend/src/components/ScriptEditor.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  Space, 
  Input, 
  Select, 
  Slider,
  Divider,
  Tag,
  message,
  Spin
} from 'antd';
import { 
  SaveOutlined, 
  EyeOutlined, 
  UploadOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { ScriptAPI, Project } from '../services/api';

const { TextArea } = Input;
const { Option } = Select;

interface ScriptSegment {
  id: string;
  index: number;
  title: string;
  content: string;
  estimated_duration: number;
  keywords: Array<{ word: string; importance: number }>;
}

const ScriptEditor: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [scriptContent, setScriptContent] = useState('');
  const [segments, setSegments] = useState<ScriptSegment[]>([]);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [style, setStyle] = useState('conversational');
  const [segmentDuration, setSegmentDuration] = useState(45);

  useEffect(() => {
    if (id) {
      loadProject(id);
    }
  }, [id]);

  const loadProject = async (projectId: string) => {
    setLoading(true);
    try {
      const data = await ProjectAPI.getProject(projectId);
      setProject(data);
      setScriptContent(data.script_content || '');
      
      if (data.segments) {
        setSegments(data.segments);
      }
    } catch (error) {
      message.error('加载项目失败');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessScript = async () => {
    if (!scriptContent.trim()) {
      message.warning('请输入脚本内容');
      return;
    }

    setProcessing(true);
    try {
      const result = await ScriptAPI.processScript({
        text: scriptContent,
        style: style,
        config: {
          target_duration: segmentDuration,
          max_duration: segmentDuration + 15
        }
      });

      setSegments(result.segments.map((seg: any, index: number) => ({
        id: seg.id,
        index: seg.index,
        title: seg.title,
        content: seg.rewritten_text,
        estimated_duration: seg.estimated_duration,
        keywords: seg.keywords
      })));

      message.success('脚本处理完成');
    } catch (error) {
      message.error('脚本处理失败');
    } finally {
      setProcessing(false);
    }
  };

  const handleSave = async () => {
    if (!project) return;

    try {
      await ProjectAPI.updateProject(project.id, {
        script_content: scriptContent,
        segments: segments
      });
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setScriptContent(content);
      };
      reader.readAsText(file, 'utf-8');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Button 
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
          >
            返回
          </Button>
          <Button 
            icon={<UploadOutlined />}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            上传文件
          </Button>
          <input
            id="file-input"
            type="file"
            accept=".txt"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
          <Button 
            type="primary" 
            icon={<SaveOutlined />}
            onClick={handleSave}
          >
            保存
          </Button>
        </Space>

        <div style={{ marginBottom: 16 }}>
          <Space>
            <span>处理风格：</span>
            <Select value={style} onChange={setStyle} style={{ width: 120 }}>
              <Option value="conversational">对话风格</Option>
              <Option value="educational">教育风格</Option>
              <Option value="storytelling">故事风格</Option>
            </Select>
            
            <span>段落时长：</span>
            <Slider
              min={20}
              max={90}
              value={segmentDuration}
              onChange={setSegmentDuration}
              style={{ width: 150 }}
              marks={{
                30: '30秒',
                45: '45秒',
                60: '60秒',
                90: '90秒'
              }}
            />
          </Space>
        </div>

        <Button 
          type="primary" 
          loading={processing}
          onClick={handleProcessScript}
        >
          处理脚本
        </Button>
      </Card>

      <div style={{ display: 'flex', gap: 16 }}>
        <Card title="脚本内容" style={{ flex: 1 }}>
          <TextArea
            value={scriptContent}
            onChange={(e) => setScriptContent(e.target.value)}
            placeholder="请输入或粘贴脚本内容..."
            rows={20}
            style={{ fontSize: '14px' }}
          />
        </Card>

        <Card title="分段预览" style={{ flex: 1 }}>
          {segments.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: '#999', 
              padding: '50px 0' 
            }}>
              点击"处理脚本"按钮来预览分段效果
            </div>
          ) : (
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              {segments.map((segment, index) => (
                <Card 
                  key={segment.id}
                  size="small"
                  style={{ marginBottom: 8 }}
                >
                  <div style={{ marginBottom: 8 }}>
                    <strong>段落 {index + 1}: {segment.title}</strong>
                    <Tag color="blue" style={{ marginLeft: 8 }}>
                      {segment.estimated_duration.toFixed(1)}秒
                    </Tag>
                  </div>
                  
                  <div style={{ marginBottom: 8, fontSize: '13px' }}>
                    {segment.content}
                  </div>
                  
                  {segment.keywords.length > 0 && (
                    <div>
                      <span style={{ fontSize: '12px', color: '#666' }}>关键词：</span>
                      {segment.keywords.map((kw, kwIndex) => (
                        <Tag 
                          key={kwIndex}
                          color={kw.importance > 0.8 ? 'gold' : 'blue'}
                          style={{ fontSize: '11px', margin: '2px' }}
                        >
                          {kw.word} ({(kw.importance * 100).toFixed(0)}%)
                        </Tag>
                      ))}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default ScriptEditor;
```

### 2.4 状态管理

#### WebSocket Context
```typescript
// web_interface/frontend/src/contexts/WebSocketContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';

interface WebSocketMessage {
  type: string;
  project_id?: string;
  data?: any;
  timestamp?: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  subscribeToProject: (projectId: string, callback: (data: any) => void) => () => void;
  sendMessage: (message: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [subscriptions, setSubscriptions] = useState<Map<string, Set<(data: any) => void>>>(new Map());

  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setSocket(null);
      
      // 尝试重连
      setTimeout(() => {
        console.log('Attempting to reconnect...');
        const reconnectWs = new WebSocket(wsUrl);
        setSocket(reconnectWs);
      }, 3000);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        if (message.project_id && subscriptions.has(message.project_id)) {
          const callbacks = subscriptions.get(message.project_id);
          callbacks?.forEach(callback => callback(message));
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  const subscribeToProject = (projectId: string, callback: (data: any) => void) => {
    const newSubscriptions = new Map(subscriptions);
    
    if (!newSubscriptions.has(projectId)) {
      newSubscriptions.set(projectId, new Set());
    }
    
    newSubscriptions.get(projectId)?.add(callback);
    setSubscriptions(newSubscriptions);

    // 发送订阅消息
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'subscribe',
        project_id: projectId
      }));
    }

    // 返回取消订阅函数
    return () => {
      const currentSubscriptions = new Map(subscriptions);
      const projectCallbacks = currentSubscriptions.get(projectId);
      
      if (projectCallbacks) {
        projectCallbacks.delete(callback);
        
        if (projectCallbacks.size === 0) {
          currentSubscriptions.delete(projectId);
        }
        
        setSubscriptions(currentSubscriptions);
      }
    };
  };

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  return (
    <WebSocketContext.Provider value={{
      isConnected,
      subscribeToProject,
      sendMessage
    }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};
```

### 2.5 系统监控界面

#### 监控仪表板
```typescript
// web_interface/frontend/src/components/SystemMonitor.tsx
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Progress, 
  Table,
  Tag,
  Alert,
  Space
} from 'antd';
import { 
  DesktopOutlined, 
  DatabaseOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { SystemAPI } from '../services/api';

interface SystemStatus {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_projects: number;
  queued_jobs: number;
  completed_today: number;
  failed_today: number;
}

interface JobInfo {
  id: string;
  type: string;
  status: string;
  progress: number;
  created_at: string;
  estimated_completion: string;
}

const SystemMonitor: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    cpu_usage: 0,
    memory_usage: 0,
    disk_usage: 0,
    active_projects: 0,
    queued_jobs: 0,
    completed_today: 0,
    failed_today: 0
  });
  
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    const loadSystemStatus = async () => {
      try {
        const [statusData, jobsData] = await Promise.all([
          SystemAPI.getSystemStatus(),
          SystemAPI.getActiveJobs()
        ]);
        
        setSystemStatus(statusData);
        setJobs(jobsData);
        setLastUpdate(new Date());
      } catch (error) {
        console.error('Failed to load system status:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSystemStatus();
    
    // 每5秒更新一次
    const interval = setInterval(loadSystemStatus, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (value: number) => {
    if (value < 50) return '#52c41a';
    if (value < 80) return '#faad14';
    return '#f5222d';
  };

  const getJobStatusColor = (status: string) => {
    const colors = {
      'running': 'processing',
      'completed': 'success',
      'failed': 'error',
      'queued': 'default'
    };
    return colors[status] || 'default';
  };

  const jobColumns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      render: (id: string) => <code>{id.substring(0, 8)}</code>
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getJobStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number, record: JobInfo) => (
        record.status === 'running' ? (
          <Progress percent={Math.round(progress * 100)} size="small" />
        ) : (
          <span>-</span>
        )
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleTimeString()
    },
    {
      title: '预计完成',
      dataIndex: 'estimated_completion',
      key: 'estimated_completion',
      render: (date: string) => date ? new Date(date).toLocaleTimeString() : '-'
    }
  ];

  return (
    <div>
      <Alert
        message={`系统状态更新时间: ${lastUpdate.toLocaleString()}`}
        type="info"
        style={{ marginBottom: 16 }}
      />

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="CPU使用率"
              value={systemStatus.cpu_usage}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(systemStatus.cpu_usage) }}
              prefix={<DesktopOutlined />}
            />
            <Progress 
              percent={systemStatus.cpu_usage} 
              showInfo={false}
              strokeColor={getStatusColor(systemStatus.cpu_usage)}
            />
          </Card>
        </Col>
        
        <Col span={6}>
          <Card>
            <Statistic
              title="内存使用率"
              value={systemStatus.memory_usage}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(systemStatus.memory_usage) }}
              prefix={<DatabaseOutlined />}
            />
            <Progress 
              percent={systemStatus.memory_usage} 
              showInfo={false}
              strokeColor={getStatusColor(systemStatus.memory_usage)}
            />
          </Card>
        </Col>
        
        <Col span={6}>
          <Card>
            <Statistic
              title="磁盘使用率"
              value={systemStatus.disk_usage}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(systemStatus.disk_usage) }}
              prefix={<DatabaseOutlined />}
            />
            <Progress 
              percent={systemStatus.disk_usage} 
              showInfo={false}
              strokeColor={getStatusColor(systemStatus.disk_usage)}
            />
          </Card>
        </Col>
        
        <Col span={6}>
          <Card>
            <Statistic
              title="活动项目"
              value={systemStatus.active_projects}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="排队任务"
              value={systemStatus.queued_jobs}
              valueStyle={{ color: '#faad14' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        
        <Col span={8}>
          <Card>
            <Statistic
              title="今日完成"
              value={systemStatus.completed_today}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        
        <Col span={8}>
          <Card>
            <Statistic
              title="今日失败"
              value={systemStatus.failed_today}
              valueStyle={{ color: '#f5222d' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="活动任务" loading={loading}>
        <Table
          columns={jobColumns}
          dataSource={jobs}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: false
          }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default SystemMonitor;
```

## 3. 数据库设计

### 3.1 数据模型
```python
# web_interface/backend/models/database.py
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    script_content = Column(Text)
    status = Column(String(50), default="pending")
    progress = Column(Float, default=0.0)
    config = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)

class ScriptSegment(Base):
    __tablename__ = "script_segments"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    index = Column(Integer, nullable=False)
    title = Column(String(255))
    original_text = Column(Text)
    rewritten_text = Column(Text)
    estimated_duration = Column(Float)
    keywords = Column(JSON)
    emotion = Column(String(50))
    created_at = Column(DateTime, default=func.now())

class AudioSegment(Base):
    __tablename__ = "audio_segments"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    segment_id = Column(String, nullable=False)
    file_path = Column(String(500))
    duration = Column(Float)
    voice_used = Column(String(100))
    provider_used = Column(String(50))
    file_size = Column(Integer)
    quality_score = Column(Float)
    created_at = Column(DateTime, default=func.now())

class VideoSegment(Base):
    __tablename__ = "video_segments"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    segment_id = Column(String, nullable=False)
    file_path = Column(String(500))
    duration = Column(Float)
    resolution = Column(JSON)
    fps = Column(Integer)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=func.now())

class MergeJob(Base):
    __tablename__ = "merge_jobs"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    status = Column(String(50), default="pending")
    output_path = Column(String(500))
    config = Column(JSON)
    progress = Column(Float, default=0.0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(String, primary_key=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100))
    project_id = Column(String)
    extra_data = Column(JSON)
    created_at = Column(DateTime, default=func.now())
```

## 4. 部署配置

### 4.1 Docker配置
```dockerfile
# Dockerfile.backend
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建输出目录
RUN mkdir -p /app/outputs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine as builder

WORKDIR /app

# 复制package文件
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4.2 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./web_interface/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/video_generator
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./outputs:/app/outputs
      - ./temp:/app/temp
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./web_interface/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=video_generator
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 5. 配置管理

### 5.1 后端配置
```python
# web_interface/backend/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "AI视频生成器"
    debug: bool = False
    version: str = "1.0.0"
    
    # 数据库配置
    database_url: str = "sqlite:///./video_generator.db"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # 文件存储配置
    uploads_dir: str = "./uploads"
    outputs_dir: str = "./outputs"
    temp_dir: str = "./temp"
    
    # AI服务配置
    openai_api_key: str = ""
    azure_speech_key: str = ""
    elevenlabs_api_key: str = ""
    
    # FFmpeg配置
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    
    # 任务队列配置
    max_concurrent_jobs: int = 2
    job_timeout_minutes: int = 30
    
    # 安全配置
    secret_key: str = "your-secret-key"
    allowed_hosts: list = ["localhost", "127.0.0.1"]
    
    class Config:
        env_file = ".env"
        env_prefix = "VIDEO_GEN_"
```

### 5.2 前端配置
```typescript
// web_interface/frontend/src/config/index.ts
export interface Config {
  apiUrl: string;
  wsUrl: string;
  maxFileSize: number;
  supportedFormats: string[];
  defaultSettings: {
    video: {
      resolution: string;
      fps: number;
      quality: string;
    };
    audio: {
      provider: string;
      voice: string;
      speed: number;
    };
  };
}

const config: Config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  maxFileSize: 50 * 1024 * 1024, // 50MB
  supportedFormats: ['.txt'],
  defaultSettings: {
    video: {
      resolution: '1920x1080',
      fps: 30,
      quality: 'high'
    },
    audio: {
      provider: 'azure',
      voice: 'zh-CN-XiaoxiaoNeural',
      speed: 1.0
    }
  }
};

export default config;
```

这个Web界面和API系统将提供完整的用户交互界面，支持实时监控、项目管理和系统控制，使整个视频生成流程变得用户友好且易于管理。
