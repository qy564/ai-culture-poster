# AI 工程说明文档

**项目：** AI 创作大赛参赛作品  
**作品一：** 《文明代码：从甲骨到AI》  
**作品二：** 《和融世界 · 文脉生根》  
**版本：** v1.0  
**日期：** 2026年7月1日

---

## 一、技术路线总览

```
┌─────────────────────────────────────────────────────────┐
│                   技术架构总览                          │
├──────────┬──────────────────────────────────────────────┤
│ 阶段     │ 工具/技术                                   │
├──────────┼──────────────────────────────────────────────┤
│ 构思     │ ChatGPT / Claude（概念发散、视觉方案策划）   │
│ 提示词   │ 中英双语精细 Prompt Engineering              │
│ 基础生成 │ ComfyUI (SDXL / Flux) / DALL-E 3 API         │
│ 迭代调优 │ 种子遍历 + CFG 调参 + 局部重绘               │
│ 后处理   │ 4x 超分辨率放大 + 色调统一 + 细节增强        │
│ 输出     │ 8K 纵向竖构图概念海报（1216×1664→4864×6656） │
└──────────┴──────────────────────────────────────────────┘
```

---

## 二、模型选择与依据

| 模型 | 用途 | 选型理由 |
|------|------|----------|
| **SDXL 1.0** | 基础构图生成 | 高分辨率原生支持(1024+)，构图稳定性好，文化符号理解能力强 |
| **Flux.1-dev** | 细节质感增强 | 光影表现力极佳，特别适合 "电影级灯光" 要求的场景 |
| **4x-UltraSharp** | 超分辨率放大 | 保留原始细节的同时将分辨率提升至印刷级 |
| **DALL-E 3 (备选)** | API 管线验证 | 复杂语义理解能力强，适合长提示词测试 |

选择 SDXL + Flux 组合的原因：SDXL 擅长整体构图与空间关系，Flux 擅长材质表现与光影氛围，二者互补可达成 "远观构图震撼、近看细节丰富" 的视觉效果。

---

## 三、提示词工程策略

### 3.1 分层提示词结构

每一幅作品的提示词均采用 **三层金字塔结构**：

```
层级1：主体框架（画面核心构图与主体）
  ↓
层级2：细节填充（材质、纹理、文化元素）
  ↓
层级3：品质控制（风格限定词、技术参数）
```

### 3.2 提示词示例（作品一）

**中文正向提示词（精简版）：**
```
纵向构图，巨大的文明之树贯穿天地，
树根由甲骨文、金文、篆书竹简组成，散发金色光芒，
向上转化为二进制代码0和1，再转化为数据流与神经网络，
树干融合水墨肌理、青铜器纹样、祥云与电路纹理，
隐约可见长城轮廓，树冠由AI神经节点和发光网络组成，
顶部悬浮发光地球，多国语言'你好'藏于树冠中，
金色与深蓝主色调，东方美学与未来科技融合，
超精细细节，史诗级视觉冲击，电影级灯光，8K
```

**英文正向提示词（完整版）：**
```
Masterpiece concept poster, vertical composition,
a gigantic tree of civilization spanning heaven and earth.
Roots composed of oracle bone script, bronze inscriptions,
seal script, bamboo slips, radiating ancient golden light.
Characters gradually evolve into binary code 0 and 1,
then transform into luminous data flow and neural networks.
Trunk fuses ink wash texture, bronze vessel patterns,
auspicious cloud motifs with futuristic circuit textures,
forming the Great Wall silhouette from a distance.
Crown consists of AI neural nodes, digital light points,
and glowing neural networks extending globally.
Floating luminous Earth at the top connecting continents.
Multilingual 'Hello' (Hello, Bonjour, Hola, こんにちは, مرحباً)
hidden within the crown.
Gold and deep blue color palette.
Eastern aesthetics meets futuristic technology.
Hyper-detailed, epic visual impact, cinematic lighting,
ultra high quality, 8K resolution.
```

### 3.3 负向提示词设计

| 类别 | 关键词 |
|------|--------|
| 构图问题 | 杂乱无章、构图倾斜、元素堆砌、不协调 |
| 画质问题 | 低分辨率、模糊不清、变形扭曲、过度曝光 |
| 文化问题 | 西方中心视角、文化符号滥用、不尊重传统 |
| 审美问题 | 低俗审美、色彩失衡、廉价感 |

---

## 四、ComfyUI 工作流说明

工作流文件：`workflow_comfyui.json`

### 4.1 节点拓扑

```
CheckpointLoader → CLIPTextEncode(正/负)
                 → EmptyLatentImage(1216×1664)
                 → KSampler(seed=42, steps=30, cfg=7.5)
                 → VAEDecode → ImageUpscaleWithModel(4x)
                 → SaveImage
```

### 4.2 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 分辨率 | 1216×1664 | 纵向竖构图，约 3:4 海报比例 |
| Steps | 30 | 平衡生成质量与速度 |
| CFG | 7.5 | 概念类作品推荐值 |
| Sampler | Euler | 稳定性好，细节丰富 |
| Scheduler | Normal | 默认调度器 |
| Denoise | 1.0 | 文生图模式 |
| Upscale | 4x-UltraSharp | 输出 4864×6656（8K 级） |

### 4.3 迭代策略

1. **种子遍历**：以 seed=42 为基准，±10 范围内遍历最佳构图
2. **局部重绘**：对不满意的局部区域（如树冠密度）进行 Inpaint 优化
3. **色调统一**：放大后使用色调 LUT 确保整体色彩一致性

---

## 五、Python 工程脚本

脚本文件：`generate_poster.py`

### 5.1 功能模块

| 模块 | 函数 | 职责 |
|------|------|------|
| 配置管理 | `load_config()` | 加载 API 密钥、模型参数、输出路径 |
| Prompt 模板 | `build_prompt()` | 组装分层提示词（中/英双语） |
| API 调用 | `call_generation_api()` | 调用图像生成 API 并获取结果 |
| 后处理 | `upscale_image()` | 超分辨率放大 |
| 管线 | `run_pipeline()` | 串联完整生成流程 |

### 5.2 使用方式

```bash
# 安装依赖
pip install openai pillow requests

# 生成作品一（文明代码）
python generate_poster.py --artwork 1 --output ./output

# 生成作品二（和融世界）
python generate_poster.py --artwork 2 --output ./output

# 指定 API Key
python generate_poster.py --artwork 1 --api-key sk-xxx
```

### 5.3 扩展性设计

- 通过配置文件 `config.json` 支持多模型切换
- `PromptTemplate` 类支持自由扩展新的作品模板
- 预留局部重绘接口 `inpaint_region()` 便于后续优化

---

## 六、Prompt 版本管理

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2026-07-01 | 初始版本，双作品完整提示词 |

---

## 七、交付文件清单

```
AI工程文件/
├── README.md                      ← 本说明文件
├── generate_poster.py             ← Python 生成脚本
├── workflow_comfyui.json          ← ComfyUI 工作流文件
├── prompts/
│   ├── prompt_文明代码.txt          ← 作品一提示词
│   ├── prompt_和融世界.txt          ← 作品二提示词
│   └── negative_prompts.txt        ← 通用负向提示词
├── config/
│   └── config.json                 ← API 配置模板
└── output/                         ← 生成结果目录
```

---

## 八、版权与规范声明

- 本工程所有提示词与工作流均为原创设计
- 使用的基础模型遵守各模型的开源许可协议
- 生成过程中的种子参数已记录，确保可复现性
- 提交内容不包含第三方侵权元素

---

*工程文件编制人：Kun*  
*日期：2026年7月1日*
