# 进阶玩法与扩展

## 进阶玩法思路
- **ControlNet**：加入 `ControlNetLoader` + `ApplyControlNet`，可用草图/深度图约束构图
- **图生图**：以 `LoadImage` + `VAEEncode` 提供初始 latent，再由 `KSampler` 生成
- **局部重绘**：结合 `Mask` 节点与 `Inpaint` 模式，仅修改指定区域
- **批处理**：使用 `ForEach`、`BatchPromptSchedule` 等节点自动化多提示词

## 自定义节点与模型管理
1. 将第三方节点仓库克隆到 `ComfyUI/custom_nodes/<节点名>` 并 `pip install` 依赖
2. 新增模型或 LoRA 时放入对应目录，如 `models/checkpoints`、`models/lora`，重启后即可选择
3. 关注日志窗口，缺模型或算子会直接报路径；使用 `Manager` 插件可 GUI 安装
