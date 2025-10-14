#%%
import re
import os
import pyttsx3
from pathlib import Path

def split_sentences(text):
    # 按中文和英文标点分句，保留标点
    parts = re.split(r'([。！？!?])', text)
    sentences = []
    for i in range(0, len(parts), 2):
        s = parts[i].strip()
        if not s:
            continue
        p = parts[i+1] if i+1 < len(parts) else ''
        sentences.append((s + p).strip())
    return sentences

def tts_batch(text, out_dir="tts_out", voice=None, rate=180, volume=1.0):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    if voice is not None:
        engine.setProperty('voice', voice)   # 可枚举 voices 选择中文
    engine.setProperty('rate', rate)         # 语速
    engine.setProperty('volume', volume)     # 音量

    # sentences = split_sentences(text)
    sentences = [text, 'test']
    files = []
    for idx, sent in enumerate(sentences, 1):
        fname = Path(out_dir) / f"part_{idx:04d}.aiff"  # macOS 常见为 AIFF
        engine.save_to_file(sent, str(fname))
        files.append(str(fname))
    engine.runAndWait()
    return files

if __name__ == "__main__":
    long_text = "这是一个用于演示的长文本。它会被自动按句子切分，并批量合成为音频文件！请根据需要调整语速和音量。"
    files = tts_batch(long_text, out_dir="tts_cn_demo", rate=180)
    print("Generated segments:", files)
    # 之后可用 sox/ffmpeg 拼接与转码为 mp3，例如：
    # sox tts_cn_demo/part_*.aiff output.wav && ffmpeg -i output.wav output.mp3



# %%
