# Checkpoint 断点续传功能

## 功能说明

为了避免长文档处理中途中断导致重复消耗token，系统实现了checkpoint（检查点）机制，支持断点续传。

## 工作原理

### 1. 自动检测
- 系统根据文档内容生成唯一的task_id（基于MD5哈希）
- 开始处理前，自动检查是否存在该文档的checkpoint
- 如果存在，从上次中断的地方继续

### 2. 增量保存
- 每处理完一个chunk，立即保存checkpoint
- Checkpoint包含：
  - 已完成的chunk摘要
  - 已使用的token统计
  - 处理进度
  - 元数据（文件名、长度等）

### 3. 自动清理
- 处理成功完成后，自动删除checkpoint
- 避免checkpoint文件堆积

## 使用场景

### 场景1：网络中断
```
处理94个chunks的文档时，在第50个chunk时网络断开
→ 重新上传同一文档
→ 系统检测到checkpoint，从第51个chunk继续
→ 节省了50个chunks的token消耗
```

### 场景2：程序崩溃
```
处理过程中backend崩溃
→ 重启backend
→ 重新上传文档
→ 从checkpoint恢复，继续处理
```

### 场景3：手动中断
```
处理太慢，手动取消
→ 稍后重新上传
→ 从上次位置继续
```

## 控制台输出

### 首次处理
```
Chunking document...
Created 94 chunks
🆕 Starting fresh summarization (task_id: a1b2c3d4e5f6_20250101_120000)
Map phase: Summarizing chunks...
  Summarizing chunk 1/94...
  Chunk 1 summarized (150 chars) - Tokens: 2100
  💾 Checkpoint saved: 1/94 chunks completed
  ...
```

### 断点续传
```
Chunking document...
Created 94 chunks
✓ Found checkpoint: 50/94 chunks already completed
⏭ Resuming from chunk 51
💰 Saved tokens so far: 105000 tokens
Map phase: Summarizing chunks...
  Summarizing chunk 51/94...
  ...
```

### 完成后
```
Reduce phase: Generating final summary...
Final summary generated (5000 chars)
🗑 Checkpoint cleaned up: a1b2c3d4e5f6_20250101_120000
```

## Checkpoint文件位置

```
backend/data/checkpoints/
├── a1b2c3d4e5f6_20250101_120000.json
├── b2c3d4e5f6a7_20250101_130000.json
└── ...
```

## Checkpoint文件格式

```json
{
  "task_id": "a1b2c3d4e5f6_20250101_120000",
  "timestamp": "2025-01-01T12:00:00",
  "progress": {
    "completed_chunks": 50,
    "total_chunks": 94,
    "percentage": 53.19
  },
  "chunk_summaries": ["...", "..."],
  "chunk_details": [{...}, {...}],
  "total_tokens": {
    "prompt_tokens": 89000,
    "completion_tokens": 16000,
    "total_tokens": 105000
  },
  "metadata": {
    "filename": "large_document.pdf",
    "original_length": 250000,
    "summary_length": 5000
  }
}
```

## 管理Checkpoint

### 查看所有checkpoint
```python
from app.services.checkpoint import get_checkpoint_manager

mgr = get_checkpoint_manager()
checkpoints = mgr.list_checkpoints()
print(f"Found {len(checkpoints)} checkpoints")
```

### 手动清理旧checkpoint
```python
# 清理7天前的checkpoint
mgr = get_checkpoint_manager()
cleaned = mgr.cleanup_old_checkpoints(days=7)
print(f"Cleaned {cleaned} old checkpoints")
```

### 手动删除checkpoint
```python
mgr = get_checkpoint_manager()
mgr.delete_checkpoint(task_id="a1b2c3d4e5f6_20250101_120000")
```

## 注意事项

### ✅ 支持的场景
- 文档摘要（`summarize_document`）
- 相同文档内容的重复处理
- 不同summary_length设置（会创建新checkpoint）

### ❌ 不支持的场景
- 网页摘要（`summarize_webpage`）- 暂未实现
- 文档内容发生变化（会被视为新文档）

### 安全性
- Checkpoint文件仅保存摘要和统计，不保存原始文档内容
- 使用MD5哈希确保相同文档的checkpoint可复用
- 自动清理机制防止文件堆积

## Token节省示例

### 大文档处理（94 chunks）

| 场景 | 完成进度 | Token消耗 | 节省 |
|------|---------|-----------|------|
| 从头开始 | 0% → 100% | ~210,000 | - |
| 中断恢复（50%） | 50% → 100% | ~105,000 | **50%** |
| 中断恢复（90%） | 90% → 100% | ~21,000 | **90%** |

**成本节省**：
- 如果token价格是 ¥0.001/1K tokens
- 从50%恢复可节省：105,000 tokens = **¥0.105**
- 对于企业用户，大量文档处理可节省**数千元**

## 最佳实践

1. **长文档优先**：对于超过50 chunks的文档，checkpoint价值最大
2. **网络不稳定时**：在网络环境不好时处理大文档，checkpoint是保障
3. **定期清理**：建议每周清理一次旧checkpoint（已自动完成）
4. **监控进度**：关注console输出的checkpoint保存信息

## 未来改进

- [ ] 支持网页摘要的checkpoint
- [ ] 前端显示checkpoint恢复状态
- [ ] 支持多任务并发处理
- [ ] Checkpoint压缩存储
- [ ] 自定义checkpoint保存间隔（如每10个chunks保存一次）
