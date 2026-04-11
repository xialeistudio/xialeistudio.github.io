---
title: "Echoic：用 AI 练英语发音，音素级实时评分"
date: 2026-04-10T10:00:00+08:00
slug: echoic-ai-pronunciation-practice
categories:
- 开源项目
tags:
- AI
- 英语学习
- 发音练习
- FastAPI
- React
- WhisperX
featured: true
---

最近开源了一个项目 [Echoic](https://github.com/xialeistudio/echoic)——一个 AI 驱动的英语发音练习工具。核心功能：导入任意音频，逐句跟读，即时获得音素级评分。

<!--more-->

## 为什么做这个

市面上的发音练习工具要么是封闭的 APP（无法导入自己的素材），要么评分是个黑盒（只告诉你"很好"或"需要改进"，不告诉你哪个音发错了）。

我想要的是：
1. **用自己喜欢的内容练习**——导入任意音频，不被平台内容库限制
2. **看到音素级别的反馈**——不是"这句话说得不好"，而是"第3个单词的第2个音素发音偏差"
3. **离线可用**——模型跑在本地，不依赖云端服务

## 技术实现

整体流程分四步：**ASR 识别 → 强制对齐 → 发音评分 → AI 分析（可选）**。

### 语音识别：WhisperX

使用 [WhisperX](https://github.com/m-bain/whisperX) 对用户录音进行 ASR，输出带时间戳的词级识别结果。WhisperX 基于 faster-whisper（CTranslate2 后端），在 CPU 上推理速度也还可以接受。

模型大小可配，`base` 适合日常使用，`large-v2` 精度更高但更慢。

### 强制对齐：wav2vec2

ASR 给出的是词级时间戳，要做到**音素级对齐**需要第二步：用 wav2vec2 做强制对齐（forced alignment），将音频的每一帧映射到具体的音素。

这一步决定了"哪个音素在哪个时间点被发出"，是后续评分的基础。

### 发音评分

评分模型同样基于 wav2vec2 + phonemizer：

1. 对参考文本提取预期音素序列（phonemizer → IPA）
2. 对用户录音提取实际音素序列（wav2vec2）
3. 用 Levenshtein 编辑距离对齐两个序列，逐音素比较

最终输出三个维度：

| 维度 | 含义 |
|---|---|
| 准确度（Accuracy） | 发出的音素与目标音素的吻合程度 |
| 流利度（Fluency） | 停顿和节奏是否自然 |
| 完整度（Completeness） | 有没有漏发或多发音素 |

三者加权合并为总分，权重通过环境变量可配。

### AI 分析（可选）

接入 OpenAI API，对每个句子提供翻译和语法解析。这个功能是可选的，不配置 API Key 时自动跳过，核心发音练习功能完全不依赖 LLM。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React 18、Vite、Tailwind CSS、shadcn/ui、WaveSurfer.js |
| 后端 | FastAPI、SQLAlchemy、Alembic |
| ASR | WhisperX（faster-whisper + CTranslate2） |
| 对齐 | wav2vec2 |
| 评分 | wav2vec2 + phonemizer |
| 数据库 | PostgreSQL 16 |

## 主要功能

- **音频导入**：上传本地文件或从 URL 导入
- **逐句练习**：支持调速播放，逐句跟读录音
- **音素展示**：每个单词显示 IPA 国际音标
- **实时评分**：准确度、流利度、完整度三维评分
- **练习历史**：记录每次练习结果，可回顾进步曲线
- **练习热力图**：365 天活跃度可视化，和 GitHub 贡献图一样
- **句子收藏**：标记重点句子，专项强化

## 快速上手

依赖：Python 3.11+、Node.js 20+、pnpm、PostgreSQL 16、ffmpeg、espeak-ng。

```bash
# macOS
brew install ffmpeg espeak-ng postgresql@16

# 克隆仓库
git clone https://github.com/xialeistudio/echoic.git
cd echoic

# 启动数据库（Docker）
make db

# 后端
cd backend
uv sync
cp .env.example .env   # 按需修改
uv run alembic upgrade head
cd .. && make run

# 前端（另开终端）
make dev-frontend
```

访问 `http://localhost:5173` 即可使用。

生产环境先 `make build` 构建前端，产物会输出到 `backend/static`，之后 `make run` 统一由 `http://localhost:8000` 提供服务。

## 一些设计决策

**为什么不用云端 ASR？**

云端 ASR（如 Whisper API）有网络延迟，且每次练习都要上传录音，隐私性差。本地跑虽然第一次加载模型慢，但之后每次评分延迟在秒级以内，体验更好。

**为什么选 WhisperX 而不是原版 Whisper？**

WhisperX 的强制对齐能力是关键——原版 Whisper 只给词级时间戳，做不到音素级对比。另外 WhisperX 的 CTranslate2 后端比原版 Whisper 快 4-8 倍。

**评分为什么用 Levenshtein 而不是直接比较？**

用户在练习时难免有漏音、加音的情况，直接索引比较会错位。Levenshtein 对齐能正确处理插入/删除，给出更准确的音素级匹配。

## 未来计划

- [ ] 支持 CUDA 加速（目前默认 CPU，速度受限）
- [ ] 跟读进度追踪（整本书/整部剧的完成度）
- [ ] 音素弱项分析（统计哪些音素反复出错）
- [ ] 移动端适配

## 开源地址

GitHub：[xialeistudio/echoic](https://github.com/xialeistudio/echoic)，MIT 协议，欢迎 Star 和 PR。
