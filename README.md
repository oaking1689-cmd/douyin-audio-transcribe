# Douyin Audio Transcribe Skill

抖音直播音频录制 + Whisper 转写工具。

## 功能

- 通过系统音频录制直播音频（Virtual Audio Cable）
- 使用 OpenAI Whisper 本地转写为文字
- 支持多模型选择（tiny/base/small/medium/large）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Virtual Audio Cable

下载 [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) 并安装。

### 3. 运行转写

```bash
python scripts/transcribe.py --input audio.wav --model medium
```

## 目录结构

```
├── ffmpeg/                  # 音视频处理工具
├── scripts/
│   └── transcribe.py        # 转写脚本
├── SKILL.md
└── requirements.txt
```

## 注意事项

- 需要安装 VB-Audio Virtual Cable
- Whisper ```large``` 模型需要 ~10GB 显存，建议使用 ```medium``` 或 ```small``
- 转写为本地运行，零 Token 消耗
