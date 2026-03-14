# Novel2Audiobook

把小说文本处理、章节切分、语音合成、音频转码拆成了可扩展模块。

## 结构

- `novel2audiobook/inputs`: 输入源接口与实现，当前内置 `txt`
- `novel2audiobook/processors`: 文本清洗与章节切分
- `novel2audiobook/tts`: TTS 引擎接口与实现，当前内置 `pyttsx3`
- `novel2audiobook/audio`: 音频转码接口与实现，当前内置 `pydub`
- `novel2audiobook/pipeline.py`: 组合各模块的统一流程
- `app.py`: CLI 入口

## 常用命令

```bash
python3 app.py list
python3 app.py list-voices --engine pyttsx3 --chinese-only
python3 app.py normalize "Novels/书名.txt" "Novels/书名_清洗后.txt"
python3 app.py split "Novels/书名.txt" "Novels/书名"
python3 app.py tts "Novels/书名" "Output/书名_audiobook" --engine pyttsx3 --voice-index 8 --rate 230
python3 app.py convert "Output/书名_audiobook" "Output/书名_audiobook_mp3"
python3 app.py run "Novels/书名.txt" --chapters-dir "Novels/书名" --audio-dir "Output/书名_audiobook" --converted-dir "Output/书名_audiobook_mp3" --voice-index 8
```

## 扩展方式

新增输入格式：

1. 在 `novel2audiobook/inputs/` 下实现 `BookInput`
2. 调用 `register_input_provider("epub", YourInputProvider)`

新增 TTS 引擎：

1. 在 `novel2audiobook/tts/` 下实现 `TTSEngine`
2. 调用 `register_tts_engine("edge_tts", YourTTSEngine)`

当前 `pyttsx3` 的默认中文语音索引是 `8`。可以通过 CLI 的 `--voice-index`，或代码里的 `TTSOptions(voice_index=...)` / `n2ab.py` 里的 `DEFAULT_VOICE_INDEX` 修改。

新增音频转码器：

1. 在 `novel2audiobook/audio/` 下实现 `AudioConverter`
2. 调用 `register_audio_converter("ffmpeg", YourConverter)`

## 依赖

- `pyttsx3` 用于本地语音合成
- `pydub` 用于音频格式转换
- `tqdm` 用于进度条

如果使用 `pydub` 转 mp3，系统还需要可用的 `ffmpeg`。
