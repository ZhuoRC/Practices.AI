# 界面速览与基础工作流

## 界面速览
- **Queue**：查看执行进度与历史结果
- **Node Graph**：拖拽节点、连接端口、设置参数，是核心工作台
- **右侧属性面板**：展示当前节点参数与提示词编辑框
- **Viewer**：显示实时输出，支持查看中间图、保存或拷贝

## 节点菜单分类
- **utils**：图像尺寸调整、噪声生成、数据格式转换等辅助工具
- **sampling**：各类采样器与调度节点，控制步数、CFG、温度等扩散过程参数
- **loaders**：模型、权重、提示词列表等加载节点，负责从磁盘或 API 读取资源
  - `Load Checkpoint`：加载基础 Stable Diffusion 模型 (SD1.5/SDXL 等)
  - `Load VAE`：单独加载 VAE 权重以修正颜色或压缩效果
  - `Load LoRA` / `Load LoRA Model`：导入 LoRA 并与当前模型组合
  - `Load ControlNet Model` / `(diff)`：加载 ControlNet 权重或差分模型
  - `Load Style Model`：加载风格转移或风格 LoRA
  - `Load CLIP Vision`：载入 CLIP 视觉编码器，用于图生图/特征提取
  - `unCLIPCheckpointLoader`：加载含有 unCLIP 分支的模型
  - `GLIGENLoader`：载入支持 GLIGEN 文本框约束的模型
  - `LoraLoaderModelOnly`：仅替换 LoRA 权重，不改变基础模型
  - `HypernetworkLoader`：加载 Hypernetwork 对模型进行特征强化
  - `Load Upscale Model`：导入超分模型 (如 ESRGAN)
  - `Save LoRA Weights`：将当前训练/微调的 LoRA 权重写入文件
  - `Load Image Dataset from Folder`：批量读取图像数据集
  - `Load Image and Text Dataset from Folder`：同时读取图像与配套文本标签
  - `AudioEncoderLoader`：加载音频编码器，为语音或音频驱动工作流准备
  - `video_models`：子菜单，提供视频扩散或帧插值模型加载
- **conditioning**：正/负向提示词、风格嵌入、CLIP 处理等条件控制
- **latent**：在 latent 空间内创建、修改或合并噪声图的节点
- **image**：对可视域图片进行裁剪、滤镜、上采样、合成等操作
- **mask**：生成或处理遮罩，常用于局部重绘和 ControlNet
- **_for_testing**：实验性或调试节点，可能随版本变化，生产环境慎用
- **advanced**：模块化组合、图像分析、数学表达式等高级功能
- **model_patches**：对模型权重做临时修补或注入 LoRA、LyCORIS 的节点
- **training**：训练相关工具，如数据预处理或导出训练集元数据
- **audio**：音频输入输出与分析节点，用于语音驱动或跨模态实验
- **sd**：Stable Diffusion 核心管线节点集合，如 KSampler、VAE 等
- **3d**：深度图、法线图、相机矩阵等 3D 数据处理节点
- **camera**：虚拟相机、视角设定相关节点，与 3D/控制节点配合
- **context**：在流程间传递变量或上下文的节点，便于复用
- **api node**：用于构建可被 ComfyUI API 调用的自定义工作流接口
- **api**：直接调用外部 REST/WebSocket 服务或与前端交互的节点

## VAE 是什么？
VAE（Variational Autoencoder，变分自编码器）是 Stable Diffusion 管线中负责“像素 ↔ 潜空间”转换的模块。模型在潜空间里运行扩散过程，最终需要通过 VAE 解码成可见图像；若要做图生图或局部重绘，也会先把像素编码成 latent。

- VAE 的不同会影响成图的颜色、对比度与细节保留度；部分模型会配套推荐的 VAE。
- 默认情况下 Checkpoint 中已包含 VAE，但也可以通过 `Load VAE` 节点替换，以修正泛白、偏色等问题。
- 扩散生成的输出在 `VAE Decode` 节点必须使用匹配的 VAE 权重，避免出现噪点或模糊。

## KSampler 是什么？
KSampler 是 Stable Diffusion 中负责迭代采样的节点，决定 latent 噪声如何逐步还原成图像。它通常连接模型输出、噪声输入与条件信号，是调节质量与风格的核心工具。

### 关键输入端口
- **model**：接入 `Checkpoint Loader` 等节点输出的模型权重。
- **positive / negative**：接入提示词条件节点（通常来自 `CLIP Text Encode`），分别提供正向与反向/负向提示。
- **latent_image**：初始 latent 图像，来自 `Empty Latent Image`、`VAE Encode` 等节点。

### 常用参数说明
- **seed**：生成起始噪声的随机种子；固定 seed 可复现图像，设置为 `-1` 或启用随机选项可提升多样性。
- **control after generate**：决定完成一次采样后如何处理 seed，常见选项有 `keep`（保持不变）、`randomize`（生成后随机下次 seed）、`increment`（逐次递增），便于批量生成时自动变化。
- **steps**：采样步数，步数越高画面细节越丰富但耗时越长；常在 20~50 步之间权衡质量与速度。
- **cfg**：Classifier-Free Guidance Scale，数值越高越严格遵循提示词但可能牺牲自然度，一般在 5~12 之间调节。
- **sampler_name**：选择扩散求解器（如 `euler`, `dpm++ 2m`, `heun` 等），不同算法在锐度、速度与噪点控制上各有风格。
- **scheduler**：控制噪声调度曲线（`normal`, `karras`, `exponential` 等），与采样器搭配影响过渡平滑度与收敛速度。
- **denoise**：决定从多少噪声开始去噪，范围 0~1；图生图时降低值（如 0.5）可保留原图结构，1.0 则完全重绘。

### 采样器 vs. 调度器
- **采样器（Sampler）**：解决“如何迭代”的问题，决定每一步如何利用模型输出更新 latent（例如 Euler、DPM++、LCM）。不同采样器在精度、速度、噪声控制方面表现各异。
- **调度器（Scheduler）**：解决“每一步用多少噪声”的问题，即在整个采样过程中如何安排 σ/噪声幅度（例如 normal、karras、exponential）。调度器不改变采样算法本身，但会影响每一步的噪声强度，对细节层次和稳定性有显著影响。
- **搭配关系**：采样器负责步骤逻辑，调度器提供每个步骤的噪声曲线。常见做法是在同一采样器下尝试不同调度器（如 DPM++ 结合 karras）寻找最佳细节与速度平衡。

### 常见采样器速览
- **Euler / euler_a / euler_cfg_pp**：经典采样器，速度快、细节均衡；`_a` 为祖先版本，随机性更高；`cfg_pp` 变体对高 CFG 更稳定。
- **Heun / heunpp2**：基于改进欧拉法，保留更多高频细节，适合写实风格。
- **LMS**：线性多步求解器，生成较平滑的过渡，适合插画、低噪点需求。
- **DPM 系列**：`dpm_2`, `dpm_fast`, `dpm_adaptive` 等传统 DPM 求解器，在较高步数时保持稳定。
- **DPM++ 系列**：`dpmpp_2m`, `dpmpp_2s`, `dpmpp_sde` 及 `_heun`, `_sde_gpu`, `_cfg_pp` 变体。低步数下细节表现佳，`sde` 变体提供更柔和的噪声演化。
- **DPM++ 3M / multistep**：更高阶多步方法，在 30+ 步时可获得非常细腻的细节，代价是略慢。
- **IPNDM / IPNDM_v**：基于改进噪声预测的求解器，兼顾速度与细节，常用于 SDXL。
- **LCM**：Latent Consistency Model，用于快速采样（<10 步），适合实时或低延迟需求。
- **RES Multistep**：`res_multistep` 及其 `_cfg_pp`、`_ancestral` 变体，对复杂场景保持稳定色彩。
- **Gradient Estimation**：实验性求解器，通过梯度估计提升长提示词的可控度。
- **DDIM / DDPM**：原始扩散解法，画面较柔和；低步数下易产生模糊。
- **UniPC / UniPC_bh2**：统一预测校正方法，兼顾速度与稳定性，在高分辨率时表现优异。
- **SA Solver / SA Solver Pece**：用于减少高 CFG 时的噪点，适合风格化作品。
- **Seeds_2 / Seeds_3**：一次迭代多种噪声方案，增加探索性；配合随机 seed 使用。

> 带有 `_cfg_pp` 的选项会在高 CFG 下动态调整，引导值较大的情况下更不易崩坏；`_ancestral` / `_sde` 则会引入额外噪声增强随机性。

### 常见调度器选项
- **normal**：标准线性调度，步进均匀，适合大多数采样器的默认组合。
- **karras**：Karras sigma 调度，在早期保持更多噪声、后期快速收敛，常与 DPM++ 搭配提升细节。
- **exponential**：指数衰减，前期降噪迅速，适合想加快初期成型的场景。
- **linear_quadratic**：前半程线性、后半程二次曲线过渡，兼顾稳定与细节。
- **sgm_uniform**：SGM（Score-based Generative Model）均匀调度，针对 SDE 类型采样器优化，噪声变化平稳。
- **ddim_uniform**：DDIM 原版调度，适合同名采样器，画面过渡柔和。
- **beta**：依据 β 调度策略，渐进式降低噪声，常在写实风格中获得较干净的细节。
- **simple**：极简调度，直接线性插值；适合测试或配合快速采样器（如 LCM）。
- **kl_optimal**：依据 KL 最优理论自动分配噪声，对高 CFG 或复杂构图有更好的稳定性。

## 第一个工作流：文生图 (Text-to-Image)
1. 添加 `CheckpointLoaderSimple` 选择基础模型
2. 添加 `Positive Prompt` 与 `Negative Prompt` 节点，填入提示词
3. 通过 `KSampler` 设置采样器、步数、CFG Scale、Seed 等
4. 选择 `Empty Latent Image` 设定分辨率，再连接到 `KSampler` 的 `latent_image`
5. 将 `KSampler` 输出连到 `VAEDecode`，最后接 `SaveImage` 或 `PreviewImage` 查看结果
6. 点击 `Queue Prompt` 执行，观察右上角日志是否报错

> 小技巧：为节点命名 (右键 → Rename) 便于复用；使用 `Ctrl+E` 打包为 `workflow.json` 方便分享。
