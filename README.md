# Novel2Audiobook

把小说文本处理、章节切分、语音合成、音频转码拆成了可扩展模块。

## 结构

- `novel2audiobook/inputs`: 输入源接口与实现，当前内置 `txt`
- `novel2audiobook/processors`: 文本清洗与章节切分
- `novel2audiobook/tts`: TTS 引擎接口与实现，当前内置 `pyttsx3`、`melotts`、`qwen3tts`
- `novel2audiobook/audio`: 音频转码接口与实现，当前内置 `pydub`
- `novel2audiobook/pipeline.py`: 组合各模块的统一流程
- `app.py`: CLI 入口

## 常用命令

```bash
python3 app.py list
python3 app.py list-voices --engine pyttsx3 --chinese-only
python3 app.py list-voices --engine melotts --chinese-only
python3 app.py normalize "Novels/书名.txt" "Novels/书名_清洗后.txt"
python3 app.py split "Novels/书名.txt" "Novels/书名"
python3 app.py tts "Novels/书名" "Output/书名_audiobook" --engine pyttsx3 --voice-index 8 --rate 230
python3 app.py tts "Novels/书名" "Output/书名_melo" --engine melotts --language ZH --speaker ZH --device auto --speed 1.0
python3 app.py tts "Novels/书名" "Output/书名_qwen" --engine qwen3tts --task custom_voice --language Chinese --speaker Vivian
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

## MeloTTS

- 官方仓库: https://github.com/myshell-ai/MeloTTS
- 官方安装说明: https://github.com/myshell-ai/MeloTTS/blob/main/docs/install.md
- 适合场景: 本地神经网络 TTS，多语言，支持中文夹英文，官方说明 CPU 也可实时推理

按官方文档，在 Linux 或 macOS 上可以这样安装：

```bash
git clone https://github.com/myshell-ai/MeloTTS.git
cd MeloTTS
pip install -e .
python -m unidic download
```

如果 macOS 本地安装遇到兼容问题，官方也提供了 Docker 运行方式。接入本项目后，可直接使用：

```bash
python3 app.py list-voices --engine melotts
python3 app.py tts "Novels/test" "Output/test_melo" --engine melotts --language ZH --speaker ZH --device auto --speed 1.0
```

## Qwen3-TTS

- 官方仓库: https://github.com/QwenLM/Qwen3-TTS
- 官方模型页:
  - https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
  - https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
- 官方安装说明里推荐使用全新 Python 环境，并执行 `pip install qwen-tts`

本项目当前接入了三种模式：

- `custom_voice`: 使用官方预置 timbre，默认走较轻的 `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`
- `voice_design`: 用文本描述声音，默认走 `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`
- `voice_clone`: 用参考音频和参考文本克隆声音，默认走较轻的 `Qwen/Qwen3-TTS-12Hz-0.6B-Base`

本地运行前请先注意这些限制：

- 官方示例主要是 `cuda:0 + bfloat16 + flash_attention_2`，更适合 Linux/NVIDIA GPU
- 官方仓库没有给出 Apple Silicon / MPS 的明确运行说明；在 macOS 上更保守的预期应当是 CPU 可尝试、速度可能很慢
- 官方 Hugging Face 页面显示：
  - `0.6B-CustomVoice` 模型文件约 `2.5 GB`，另有约 `682 MB` 的 `speech_tokenizer`
  - `1.7B-CustomVoice` 模型文件约 `4.52 GB`，另有约 `682 MB` 的 `speech_tokenizer`
- 官方 README 写明 `vLLM` 目前仅支持离线推理，不是这里这种逐章本地文件输出的首选接法

安装示例：

```bash
python3.12 -m venv .venv-qwen3tts
source .venv-qwen3tts/bin/activate
pip install -U pip
pip install qwen-tts soundfile
```

如果你有 NVIDIA GPU，并想按官方推荐跑得更快，可以额外安装 `flash-attn`，并在命令里传 `--attn-implementation flash_attention_2`。

接入本项目后的基本用法：

```bash
python3 app.py tts "Novels/test" "Output/test_qwen" --engine qwen3tts --task custom_voice --language Chinese --speaker Vivian
python3 app.py tts "Novels/test" "Output/test_qwen_design" --engine qwen3tts --task voice_design --language Chinese --instruct "温柔、克制、偏成熟的女声"
python3 app.py tts "Novels/test" "Output/test_qwen_clone" --engine qwen3tts --task voice_clone --language Chinese --ref-audio "/abs/path/ref.wav" --ref-text "参考音频对应的文本"
```

如果你想把一整套 Qwen3-TTS 参数固定下来，不想每次都敲长命令，可以直接用仓库里的示例配置文件：

- 示例文件: `configs/qwen3tts.example.yaml`
- 依赖: 读取 YAML 配置需要 `PyYAML`

```bash
pip install PyYAML
python3 app.py tts "Novels/test" "Output/test_qwen" --tts-config "configs/qwen3tts.example.yaml"
```

命令行参数优先级高于配置文件，所以你可以在配置文件里固定模型和设备，再在单次命令里覆盖 `--speaker` 或 `--instruct`。

新增音频转码器：

1. 在 `novel2audiobook/audio/` 下实现 `AudioConverter`
2. 调用 `register_audio_converter("ffmpeg", YourConverter)`

## 依赖

- `pyttsx3` 用于本地语音合成
- `pydub` 用于音频格式转换
- `tqdm` 用于进度条

如果使用 `pydub` 转 mp3，系统还需要可用的 `ffmpeg`。
