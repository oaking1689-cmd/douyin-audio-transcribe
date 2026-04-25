"""
抖音直播音频录制与转写脚本
使用 Virtual Audio Cable 录制系统音频 + Whisper 转写
支持录制到直播结束或每日22:00自动结束(北京时间)
"""
import subprocess
import os
import sys
import datetime
import time
import signal

FFMPEG_PATH = r"C:\Users\happy\.qclaw\tools\douyin-recorder\DouyinLiveRecorder_v4.0.7\ffmpeg\ffmpeg.exe"
OUTPUT_DIR = r"C:\Users\happy\.qclaw\workspace\douyin-live-transcription"

# 北京时区 (UTC+8)
BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))
DEFAULT_END_HOUR = 22  # 默认22:00结束

class RecordingSession:
    def __init__(self, duration_seconds: int = None, end_time: datetime.time = None):
        self.start_time = datetime.datetime.now(BEIJING_TZ)
        self.end_time = None
        self.output_file = None
        self.should_stop = False
        
        # 设置结束时间
        if end_time:
            end_dt = datetime.datetime.combine(self.start_time.date(), end_time, BEIJING_TZ)
            if end_dt <= self.start_time:
                end_dt += datetime.timedelta(days=1)
            self.end_time = end_dt
        elif duration_seconds:
            self.end_time = self.start_time + datetime.timedelta(seconds=duration_seconds)
        else:
            # 默认22:00结束
            default_end = datetime.time(DEFAULT_END_HOUR, 0, tzinfo=BEIJING_TZ)
            end_dt = datetime.datetime.combine(self.start_time.date(), default_end, BEIJING_TZ)
            if end_dt <= self.start_time:
                end_dt += datetime.timedelta(days=1)
            self.end_time = end_dt
    
    def check_should_stop(self) -> bool:
        """检查是否应该停止录制"""
        if self.should_stop:
            return True
        
        now = datetime.datetime.now(BEIJING_TZ)
        
        # 检查是否到达结束时间
        if now >= self.end_time:
            print(f"\n[{now.strftime('%H:%M:%S')}] 已到达结束时间 {self.end_time.strftime('%H:%M:%S')}，停止录制")
            return True
        
        return False
    
    def get_remaining_seconds(self) -> int:
        """获取剩余录制秒数"""
        now = datetime.datetime.now(BEIJING_TZ)
        remaining = (self.end_time - now).total_seconds()
        return max(1, int(remaining))  # 至少录制1秒


def get_current_beijing_time() -> datetime.datetime:
    """获取当前北京时间"""
    return datetime.datetime.now(BEIJING_TZ)


def record_audio(session: RecordingSession, output_file: str = None) -> str:
    """录制系统音频（通过 CABLE Output）"""
    if output_file is None:
        timestamp = get_current_beijing_time().strftime("%Y%m%d_%H%M%M")
        output_file = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.wav")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    session.output_file = output_file
    
    print(f"\n{'='*50}")
    print(f"🎙️  抖音直播录制开始")
    print(f"{'='*50}")
    print(f"开始时间: {get_current_beijing_time().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"计划结束: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"输出文件: {output_file}")
    print(f"{'='*50}\n")
    
    while not session.check_should_stop():
        remaining = session.get_remaining_seconds()
        
        # 分段录制，每段5分钟，避免文件过大
        segment_duration = min(300, remaining)
        
        segment_file = output_file.rsplit('.', 1)[0] + '_temp.wav'
        
        cmd = [
            FFMPEG_PATH,
            '-f', 'dshow',
            '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)',
            '-t', str(segment_duration),
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            segment_file,
            '-y'
        ]
        
        now = get_current_beijing_time()
        elapsed = (now - session.start_time).total_seconds()
        print(f"[{now.strftime('%H:%M:%S')}] 录制中... 已录制 {int(elapsed/60)}分{ int(elapsed%60)}秒，剩余约 {remaining//60}分{remaining%60}秒")
        
        try:
            subprocess.run(cmd, check=True, timeout=segment_duration + 10)
        except subprocess.TimeoutExpired:
            print("分段录制超时，继续下一段...")
        
        # 合并音频文件
        if os.path.exists(segment_file):
            merge_audio_files(output_file, segment_file)
            os.remove(segment_file)
    
    print(f"\n✅ 录制完成!")
    print(f"结束时间: {get_current_beijing_time().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    return output_file


def merge_audio_files(main_file: str, temp_file: str):
    """合并音频文件"""
    if not os.path.exists(main_file):
        os.rename(temp_file, main_file)
        return
    
    # 使用 FFmpeg 合并
    merged_file = main_file.rsplit('.', 1)[0] + '_merged.wav'
    
    cmd = [
        FFMPEG_PATH,
        '-i', 'concat:"' + main_file + '|' + temp_file + '"',
        '-acodec', 'pcm_s16le',
        merged_file,
        '-y'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        os.remove(main_file)
        os.rename(merged_file, main_file)
    except:
        # 如果合并失败，直接追加
        append_audio(main_file, temp_file)


def append_audio(dest_file: str, src_file: str):
    """追加音频到目标文件"""
    temp_file = dest_file.rsplit('.', 1)[0] + '_appended.wav'
    
    cmd = [
        FFMPEG_PATH,
        '-i', f'concat:{dest_file}|{src_file}',
        '-c', 'copy',
        temp_file,
        '-y'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        os.remove(dest_file)
        os.rename(temp_file, dest_file)
    except:
        # 简单追加
        with open(dest_file, 'ab') as fdest:
            with open(src_file, 'rb') as fsrc:
                fdest.write(fsrc.read())


def transcribe_audio(audio_file: str, model: str = 'base', output_file: str = None) -> str:
    """使用 Whisper 转写音频"""
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(OUTPUT_DIR, f"transcript_{base_name}.txt")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 设置 FFmpeg 路径
    os.environ['PATH'] = os.path.dirname(FFMPEG_PATH) + os.pathsep + os.environ.get('PATH', '')
    
    import whisper
    print(f"\n🎤 开始转写...")
    print(f"加载 Whisper 模型: {model}")
    whisper_model = whisper.load_model(model)
    
    print(f"转写文件: {audio_file}")
    result = whisper_model.transcribe(audio_file, language='zh')
    
    transcript = result['text']
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    print(f"\n✅ 转写完成!")
    print(f"转写长度: {len(transcript)} 字")
    print(f"保存到: {output_file}")
    
    return output_file


def check_audio_level(audio_file: str) -> dict:
    """检查音频电平"""
    cmd = [FFMPEG_PATH, '-i', audio_file, '-af', 'volumedetect', '-f', 'null', '-']
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    mean_vol = None
    max_vol = None
    
    for line in result.stderr.split('\n'):
        if 'mean_volume' in line:
            mean_vol = float(line.split(':')[1].strip().split()[0])
        if 'max_volume' in line:
            max_vol = float(line.split(':')[1].strip().split()[0])
    
    return {'mean_volume': mean_vol, 'max_volume': max_vol}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='抖音直播音频录制与转写')
    parser.add_argument('action', choices=['record', 'transcribe', 'both'], help='操作类型')
    parser.add_argument('--duration', type=int, help='录制时长（秒），默认录制到22:00或直播结束')
    parser.add_argument('--end-time', type=str, help='结束时间(HH:MM格式，北京时间)，默认22:00')
    parser.add_argument('--input', type=str, help='输入音频文件（用于转写）')
    parser.add_argument('--model', type=str, default='base', help='Whisper 模型')
    parser.add_argument('--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 解析结束时间
    end_time = None
    if args.end_time:
        try:
            hour, minute = map(int, args.end_time.split(':'))
            end_time = datetime.time(hour, minute, tzinfo=BEIJING_TZ)
        except:
            print(f"警告: 无效的结束时间格式 {args.end_time}，将使用默认22:00")
    
    if args.action == 'record':
        session = RecordingSession(duration_seconds=args.duration, end_time=end_time)
        audio_file = record_audio(session, args.output)
        levels = check_audio_level(audio_file)
        print(f"\n📊 音频电平: mean={levels['mean_volume']}dB, max={levels['max_volume']}dB")
    
    elif args.action == 'transcribe':
        if not args.input:
            print("错误: 转写需要指定 --input 音频文件")
            sys.exit(1)
        transcribe_audio(args.input, args.model, args.output)
    
    elif args.action == 'both':
        session = RecordingSession(duration_seconds=args.duration, end_time=end_time)
        audio_file = record_audio(session, args.output)
        levels = check_audio_level(audio_file)
        print(f"\n📊 音频电平: mean={levels['mean_volume']}dB, max={levels['max_volume']}dB}")
        
        if levels['mean_volume'] and levels['mean_volume'] < -50:
            print("⚠️ 警告: 音频电平过低，请检查 Virtual Audio Cable 配置")
        
        transcribe_audio(audio_file, args.model)
