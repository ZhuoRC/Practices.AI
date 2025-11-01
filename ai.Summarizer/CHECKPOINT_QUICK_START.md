# Checkpoint 断点续传 - 快速开始

## 🎯 核心功能

**自动断点续传** - 处理大文档时如果中途中断，重新上传后会自动从中断点继续，避免重复消耗token。

## 📊 效果演示

### 场景：处理94个chunks的大文档

#### 第一次上传（中途中断）
```
Loading document: large_document.pdf
Document loaded: 250000 characters
Chunking document...
Created 94 chunks
🆕 Starting fresh summarization (task_id: a1b2c3d4_20250101_120000)
Map phase: Summarizing chunks...
  Summarizing chunk 1/94...
  Chunk 1 summarized (150 chars) - Tokens: 2100
  💾 Checkpoint saved: 1/94 chunks completed
  ...
  Summarizing chunk 50/94...
  Chunk 50 summarized (145 chars) - Tokens: 2050
  💾 Checkpoint saved: 50/94 chunks completed
[中断 - 网络断开/手动停止/程序崩溃]
```

#### 重新上传同一文档
```
Loading document: large_document.pdf
Document loaded: 250000 characters
Chunking document...
Created 94 chunks
  ✓ Found checkpoint: 50/94 chunks already completed
  ⏭ Resuming from chunk 51
  💰 Saved tokens so far: 105000 tokens
Map phase: Summarizing chunks...
  Summarizing chunk 51/94...  ← 从这里继续，前50个chunks不重复处理
  Chunk 51 summarized (148 chars) - Tokens: 2080
  💾 Checkpoint saved: 51/94 chunks completed
  ...
  Summarizing chunk 94/94...
  Chunk 94 summarized (101 chars) - Tokens: 646
  💾 Checkpoint saved: 94/94 chunks completed
Reduce phase: Generating final summary...
Final summary generated (5000 chars)
🗑 Checkpoint cleaned up: a1b2c3d4_20250101_120000
```

## 💰 Token节省

| 进度 | 总Token消耗 | 断点续传Token | 节省比例 |
|-----|-----------|-------------|----------|
| 0% → 100% | 210,000 | - | - |
| 50% → 100% | 105,000 | 105,000 | **50%** ⬇️ |
| 90% → 100% | 21,000 | 189,000 | **90%** ⬇️ |

**成本节省示例**（按¥0.001/1K tokens计算）：
- 50%进度恢复：节省 **¥0.105**
- 90%进度恢复：节省 **¥0.189**
- 批量处理100个大文档，每个平均恢复50%：节省 **¥10.5**

## 🚀 使用方法

### 完全自动，无需额外操作！

1. **正常上传文档**
   - 系统自动创建checkpoint
   - 每处理一个chunk自动保存进度

2. **如果中途中断**
   - 不需要任何特殊操作
   - 直接重新上传**同一文档**

3. **系统自动识别**
   - 根据文档内容自动匹配checkpoint
   - 从上次中断位置继续
   - 完成后自动清理checkpoint

## ⚠️ 重要说明

### ✅ 什么情况会恢复checkpoint

- **相同文档内容**：文档二进制内容完全相同
- **任何中断原因**：网络断开、程序崩溃、手动停止
- **合理时间内**：checkpoint默认保留7天

### ❌ 什么情况不会恢复

- **文档内容改变**：哪怕文件名相同，内容不同会被视为新文档
- **不同文档类型**：document和webpage分别管理
- **Checkpoint过期**：超过7天的checkpoint会被自动清理

## 📁 Checkpoint文件

**存储位置**: `backend/data/checkpoints/`

每个checkpoint文件包含：
- ✅ 已完成的chunk摘要
- ✅ Token使用统计
- ✅ 处理进度信息
- ❌ 不包含原始文档内容（安全）

## 🔍 监控进度

### 控制台输出标识

| 图标 | 含义 |
|-----|------|
| 🆕 | 新任务，从头开始 |
| ✓ | 发现checkpoint |
| ⏭ | 从checkpoint恢复 |
| 💰 | 已保存的token数 |
| 💾 | Checkpoint已保存 |
| 🗑 | Checkpoint已清理 |

### 示例输出解读

```
✓ Found checkpoint: 50/94 chunks already completed
  ↑                 ↑    ↑
  找到checkpoint    已完成  总数量

⏭ Resuming from chunk 51
                      ↑
                    从这里继续

💰 Saved tokens so far: 105000 tokens
                       ↑
                     已节省的token数
```

## 🛠 高级功能

### 查看所有checkpoint

```bash
cd backend
python -c "
from app.services.checkpoint import get_checkpoint_manager
mgr = get_checkpoint_manager()
checkpoints = mgr.list_checkpoints()
for cp in checkpoints:
    print(f'Task: {cp[\"task_id\"]}')
    print(f'Progress: {cp[\"progress\"][\"completed_chunks\"]}/{cp[\"progress\"][\"total_chunks\"]}')
    print(f'Time: {cp[\"timestamp\"]}')
    print('---')
"
```

### 手动清理旧checkpoint

```bash
cd backend
python -c "
from app.services.checkpoint import get_checkpoint_manager
mgr = get_checkpoint_manager()
cleaned = mgr.cleanup_old_checkpoints(days=7)
print(f'Cleaned {cleaned} checkpoint(s)')
"
```

## ❓ 常见问题

### Q: 我怎么知道是否使用了checkpoint？
A: 查看控制台输出，如果看到 "✓ Found checkpoint" 就是从checkpoint恢复的。

### Q: Checkpoint会永久保存吗？
A: 不会，成功完成后自动删除，未完成的7天后自动清理。

### Q: 修改summary_length会复用checkpoint吗？
A: 不会，不同的summary_length会创建新的checkpoint。

### Q: Checkpoint文件占用多少空间？
A: 每个checkpoint约100KB-2MB，取决于chunk数量。

### Q: 可以手动删除checkpoint吗？
A: 可以，直接删除 `data/checkpoints/` 下的JSON文件，或使用上面的清理脚本。

### Q: 网页摘要支持checkpoint吗？
A: 暂不支持，只有文档摘要（PDF/DOCX/TXT）支持。

## 📝 最佳实践

1. **长文档优先使用**
   - 超过50 chunks的文档最值得使用
   - 小文档（<10 chunks）checkpoint意义不大

2. **网络不稳定环境**
   - 在网络环境差的情况下处理大文档
   - Checkpoint是最好的保障

3. **批量处理**
   - 处理大量相似文档时
   - 即使个别失败也不会浪费所有进度

4. **定期清理（自动完成）**
   - 系统会自动清理7天前的checkpoint
   - 无需手动干预

## 🎓 技术细节

详细技术文档请查看：`backend/app/services/CHECKPOINT_README.md`

---

**享受无压力的大文档处理体验！** 🎉
