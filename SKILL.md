---
name: douyin-audio-transcribe
description: 抖音直播音频录制与转写工具。通过浏览器播放直播 + Virtual Audio Cable 录制系统音频 + Whisper 本地转写，实现直播内容的音频录制和文字转写。默认录制到直播结束或每日22:00(北京时间)自动结束。关键词：音频录制、转写、Whisper、逐字稿、直播转文字、抖音。
---

# 抖音直播音频录制与转写

通过浏览器 + Virtual Audio Cable + Whisper 实现直播音频录制和转写。

## 前置条件

### 1. Virtual Audio Cable

已安装 VB-Audio Virtual Cable，系统中有以下设备：
- **CABLE Input** - 输出设备（浏览器播放用）
- **CABLE Output** - 录制设备

### 2. Whisper

已安装 OpenAI Whisper：

```powershell
pip install openai-whisper
```

### 3. FFmpeg

内置路径：
```
C:\Users\happy\.qclaw\tools\douyin-recorder\DouyinLiveRecorder_v4.0.7\ffmpeg\
```

## 录制规则

| 条件 | 说明 |
|------|------|
| **默认结束时间** | 每日 22:00 (北京时间) |
| **可自定义结束时间** | 通过 --end-time 参数指定 |
| **录制时长** | 从开始录制到结束时间 |
| **自动分段** | 每5分钟自动保存一段，避免文件过大 |

## 使用流程

### Step 1: 配置音频输出

1. 右键任务栏音量 → 声音设置
2. 输出设备选择 **CABLE Input (VB-Audio)**

### Step 2: 打开直播间

使用浏览器打开抖音直播间，确保声音正常播放。

### Step 3: 运行录制

**默认录制到 22:00：**
```powershell
python "C:\Users\happy\.qclaw\skills\douyin-audio-transcribe\scripts\transcribe.py" record
```

**录制到指定时间：**
```powershell
python "C:\Users\happy\.qclaw\skills\douyin-audio-transcribe\scripts\transcribe.py" record --end-time "20:00"
```

**录制指定时长（秒）：**
```powershell
python "C:\Users\happy\.qclaw\skills\douyin-audio-transcribe\scripts\transcribe.py" record --duration 3600
```

### Step 4: 转写音频

```powershell
python "C:\Users\happy\.qclaw\skills\douyin-audio-transcribe\scripts\transcribe.py" transcribe --input "音频文件.wav"
```

**录制+转写一键完成：**
```powershell
python "C:\Users\happy\.qclaw\skills\douyin-audio-transcribe\scripts\transcribe.py" both
```

## 输出位置

默认保存在：
```
C:\Users\happy\.qclaw\workspace\douyin-live-transcription\
```

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `action` | 操作类型：`record`(录制) / `transcribe`(转写) / `both`(录制+转写) | `record` |
| `--duration` | 录制时长（秒），默认录制到22:00 | `--duration 3600` |
| `--end-time` | 结束时间(HH:MM，北京时间)，默认22:00 | `--end-time "20:00"` |
| `--input` | 输入音频文件（转写用） | `--input "recording.wav"` |
| `--output` | 输出文件路径 | `--output "my_recording.wav"` |
| `--model` | Whisper模型，默认base | `--model small` |

## 音频电平检查

录制完成后自动检查，正常值：mean_volume 约 -20dB ~ -30dB

## Whisper 模型选择

| 模型 | 显存 | 速度 | 准确度 |
|------|------|------|--------|
| tiny | ~1GB | 最快 | 一般 |
| base | ~1GB | 快 | 较好 |
| small | ~2GB | 中等 | 好 |
| medium | ~5GB | 慢 | 很好 |
| large | ~10GB | 最慢 | 最好 |

推荐：`base` 模型，平衡速度和准确度。

## 注意事项

- 需要先安装 Virtual Audio Cable 并配置音频输出
- 浏览器需要播放直播音频（不能静音）
- 录制过程中请勿关闭终端
- 建议使用 `both` 命令一次性完成录制和转写
