# Video Subtitle Remover - Web UI

这是一个为视频字幕去除器开发的现代化Web用户界面，基于React + TypeScript + Tailwind CSS构建。

## 功能特性

### 🎬 视频处理
- 支持多种视频格式（MP4, AVI, FLV, WMV, MOV, MKV）
- 实时视频预览
- 字幕区域手动选择
- 处理进度实时监控

### 🛠️ 算法支持
- **STTN**: 高质量的视频修复算法
- **LAMA**: 快速的图像修复算法
- **ProPainter**: 高级视频修复算法

### 🎯 字幕检测
- 自动字幕检测
- 手动字幕区域选择
- 可视化字幕区域预览
- 拖拽调整字幕区域

### ⚙️ 参数配置
- 算法参数精细调整
- 通用参数配置
- 预设配置支持
- 实时参数验证

### 🎨 用户体验
- 深色/浅色主题切换
- 响应式设计
- 实时状态反馈
- 直观的进度显示

## 快速开始

### 环境要求

- Node.js 16+
- Python 3.8+
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+）

### 安装和运行

#### 1. 创建虚拟环境并安装依赖

如果还没有创建虚拟环境，请先创建：

```bash
# 创建Python虚拟环境
python -m venv videoEnv

# 激活虚拟环境
videoEnv\Scripts\activate

# 安装Python依赖
pip install -r backend/requirements.txt
```

#### 2. 启动后端服务

```bash
# 方式1: 使用启动脚本（推荐）
start-backend.bat

# 方式2: 手动启动
# 先激活虚拟环境
videoEnv\Scripts\activate
# 切换到backend目录并启动
cd backend
python api.py
```

后端服务将在 `http://localhost:8001` 启动
  +++++++ REPLACE

#### 2. 启动前端开发服务器

```bash
# 方式1: 使用启动脚本
start-dev.bat

# 方式2: 手动启动
cd frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:3000` 启动
  +++++++ REPLACE

### 访问应用

打开浏览器访问 `http://localhost:3000` 即可使用Web UI。
  +++++++ REPLACE

## 使用指南

### 1. 上传视频文件

1. 点击"选择文件"按钮或拖拽文件到上传区域
2. 支持批量上传多个文件
3. 文件将自动上传到后端进行处理

### 2. 配置处理参数

#### 选择算法
- **STTN**: 推荐用于高质量视频修复
- **LAMA**: 适用于快速处理
- **ProPainter**: 最佳的视频修复效果

#### 字幕检测模式
- **自动**: 自动检测字幕位置
- **手动**: 手动指定字幕区域

#### 手动字幕选择
1. 在视频预览区域拖拽鼠标选择字幕区域
2. 绿色框显示当前选择的字幕区域
3. 可以调整框的大小和位置

### 3. 开始处理

1. 选择要处理的视频文件
2. 配置处理参数
3. 点击"开始处理"按钮
4. 在处理队列中监控进度

### 4. 下载结果

处理完成后：
1. 在结果管理区域查看处理后的视频
2. 点击下载按钮获取处理结果
3. 可以预览处理效果

## 技术架构

### 前端技术栈
- **React 18**: 用户界面框架
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 实用优先的CSS框架
- **Vite**: 快速的构建工具
- **React Router**: 单页应用路由

### 后端技术栈
- **FastAPI**: 现代的Python Web框架
- **Python**: 主要编程语言
- **OpenCV**: 计算机视觉库
- **PyTorch**: 深度学习框架

### 通信协议
- **RESTful API**: 文件上传和处理请求
- **HTTP轮询**: 任务状态更新
- **CORS**: 跨域资源共享

## 项目结构

```
ai.video/video-subtitle-remover/
├── frontend/                 # 前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── services/      # API服务
│   │   ├── types/         # TypeScript类型定义
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # 后端API
│   ├── api.py             # FastAPI应用
│   ├── main.py            # 字幕去除核心逻辑
│   └── requirements.txt    # Python依赖
├── start-dev.bat          # 前端启动脚本
├── start-backend.bat       # 后端启动脚本
└── README.md             # 项目说明
```

## API文档

### 主要端点

- `POST /upload` - 上传视频文件
- `POST /process` - 开始处理视频
- `GET /tasks/{task_id}` - 获取任务状态
- `GET /tasks` - 获取所有任务
- `GET /download/{task_id}` - 下载处理结果
- `DELETE /tasks/{task_id}` - 删除任务

详细API文档可访问 `http://localhost:8001/docs`
  +++++++ REPLACE

## 开发指南

### 添加新算法

1. 在后端实现新的算法逻辑
2. 更新API接口支持新算法
3. 在前端添加对应的参数配置组件
4. 更新类型定义

### 自定义主题

修改 `tailwind.config.js` 中的主题配置：

```javascript
theme: {
  extend: {
    colors: {
      'primary': '#your-color',
      // 其他颜色定义
    }
  }
}
```

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本是否满足要求
   - 确保所有依赖已正确安装
   - 检查端口8000是否被占用

2. **前端连接失败**
   - 确保后端服务正在运行
   - 检查CORS配置
   - 验证API地址设置

3. **文件上传失败**
   - 检查文件格式是否支持
   - 确保文件大小不超过限制
   - 检查网络连接

4. **处理任务失败**
   - 检查视频文件是否损坏
   - 确保算法参数配置正确
   - 查看后端日志获取详细错误信息

### 日志查看

- **后端日志**: 控制台输出
- **前端日志**: 浏览器开发者工具控制台
- **网络请求**: 浏览器网络面板

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

本项目基于MIT许可证开源。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持三种算法
- 完整的Web UI
- 实时处理进度
- 主题切换功能
