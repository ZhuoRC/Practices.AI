# 更新日志 (Changelog)

所有重要的项目变更都会记录在此文件中。

本项目遵循[语义化版本控制](https://semver.org/)规范。

## [1.0.1] - 2025-11-03

### 修复 (Fixed)
- **[关键] 修复请求挂起无响应问题** (main.py:74-79)
  - **问题描述**: Middleware 中调用 `await request.body()` 读取请求体用于日志记录，但读取后未缓存，导致 FastAPI 端点函数无法再次解析请求体，所有 `/rewrite` 请求因此挂起
  - **症状**:
    - 请求能到达 middleware（有日志记录）
    - 但永远不会到达 `/rewrite` 端点处理函数
    - 请求最终超时，无任何响应
  - **解决方案**: 实现请求体缓存机制
    ```python
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive
    ```
  - **测试验证**: 测试脚本 (`test_api_detailed.py`) 直接调用 API 成功，确认 Qwen API 配置正确
  - **影响范围**: 所有使用 POST /rewrite 端点的请求

### 新增 (Added)
- **启动脚本**: 新增 `start_clean.bat` 清理启动脚本
  - 完整的服务停止和清理流程
  - 环境验证和依赖检查
  - 详细的启动日志和状态信息
  - 适合首次运行和故障排除

### 改进 (Changed)
- **文档更新**: 大幅改进 README.md
  - 新增详细的故障排除部分，包含 6 个常见问题
  - 完善启动说明，提供 3 种启动选项（快速/清理/跨平台）
  - 添加更新日志和技术支持部分
  - 增加日志文件位置和调试指南

- **启动选项**: 更新启动文档
  - `start.bat`: 快速启动，日常使用
  - `start_clean.bat`: 清理启动，故障排除
  - `start.py`: 跨平台启动，服务监控

### 技术细节
**受影响文件**:
- `backend/main.py`: 修复 middleware 请求体处理逻辑
- `README.md`: 更新文档和故障排除指南
- `CHANGELOG.md`: 新增变更日志
- `start_clean.bat`: 新增清理启动脚本

**测试**:
- ✅ 直接 API 测试成功（test_api_detailed.py）
- ✅ 从前端发送请求验证修复有效

---

## [1.0.0] - 2025-11-02

### 新增 (Added)
- 🎉 **初始版本发布**
- ✅ **双模式 AI 支持**
  - 云端模式: 阿里云通义千问 (Qwen) API
  - 本地模式: Ollama + Mistral 7B Instruct
- ✅ **智能分段改写**
  - 按句子边界智能分段
  - 上下文连贯性保持
  - 自动结果拼接
- ✅ **现代化 Web 界面**
  - React 18 + TypeScript
  - Ant Design UI 组件库
  - 响应式设计
- ✅ **完整的后端 API**
  - FastAPI 框架
  - OpenAPI 文档 (Swagger/ReDoc)
  - 详细的日志记录
- ✅ **便捷的启动脚本**
  - Windows 批处理脚本 (start.bat)
  - Python 跨平台脚本 (start.py)
  - 自动依赖安装
  - 服务健康检查

### 功能特点
- 支持大文本分段处理
- 可自定义分段大小 (300/500/800/1000 字符)
- 实时处理状态反馈
- 结果一键复制
- 完整的错误处理和日志

---

## 版本规范

### 版本号格式
- **主版本号 (Major)**: 不兼容的 API 变更
- **次版本号 (Minor)**: 向后兼容的功能性新增
- **修订号 (Patch)**: 向后兼容的问题修正

### 变更类型
- **Added**: 新增功能
- **Changed**: 功能变更
- **Deprecated**: 即将废弃的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug 修复
- **Security**: 安全相关

---

[1.0.1]: https://github.com/yourusername/ai.Rewriter/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/yourusername/ai.Rewriter/releases/tag/v1.0.0
