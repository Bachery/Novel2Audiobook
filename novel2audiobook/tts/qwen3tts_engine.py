from __future__ import annotations

from pathlib import Path

from novel2audiobook.models import TTSOptions, VoiceInfo
from novel2audiobook.tts.base import TTSEngine
from novel2audiobook.utils import ensure_directory

DEFAULT_QWEN3_TASK = "custom_voice"
DEFAULT_QWEN3_LANGUAGE = "Chinese"
DEFAULT_QWEN3_CUSTOM_SPEAKER = "Vivian"
DEFAULT_QWEN3_MODELS = {
    "custom_voice": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    "voice_design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "voice_clone": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
}
TASK_ALIASES = {
    "custom": "custom_voice",
    "custom_voice": "custom_voice",
    "voice_design": "voice_design",
    "design": "voice_design",
    "voice_clone": "voice_clone",
    "clone": "voice_clone",
}


def normalize_qwen_task(task: str | None) -> str:
    if not task:
        return DEFAULT_QWEN3_TASK
    normalized = task.strip().lower().replace("-", "_")
    try:
        return TASK_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported Qwen3-TTS task: {task}. "
            f"Available: {', '.join(sorted(DEFAULT_QWEN3_MODELS))}"
        ) from exc


def resolve_qwen_model_id(options: TTSOptions) -> str:
    if options.model_id:
        return options.model_id
    return DEFAULT_QWEN3_MODELS[normalize_qwen_task(options.task)]


class Qwen3TTSEngine(TTSEngine):
    def __init__(self) -> None:
        self._model_cache: dict[tuple[str, str, str, str | None], object] = {}

    def default_audio_format(self) -> str:
        return "wav"

    @staticmethod
    def _resolve_device_map(device: str | None) -> str:
        if device and device != "auto":
            return device
        try:
            import torch
        except ImportError:
            return "cpu"
        if torch.cuda.is_available():
            return "cuda:0"
        return "cpu"

    @staticmethod
    def _resolve_dtype(dtype: str | None, device_map: str) -> object:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError("缺少 torch，无法加载 Qwen3-TTS") from exc

        if dtype:
            normalized = dtype.strip().lower()
            mapping = {
                "float32": torch.float32,
                "fp32": torch.float32,
                "float16": torch.float16,
                "fp16": torch.float16,
                "bfloat16": torch.bfloat16,
                "bf16": torch.bfloat16,
            }
            try:
                return mapping[normalized]
            except KeyError as exc:
                raise ValueError(f"Unsupported Qwen3-TTS dtype: {dtype}") from exc

        if device_map.startswith("cuda"):
            if hasattr(torch.cuda, "is_bf16_supported") and torch.cuda.is_bf16_supported():
                return torch.bfloat16
            return torch.float16
        if device_map.startswith("mps"):
            return torch.float16
        return torch.float32

    def _load_model(self, options: TTSOptions) -> object:
        model_id = resolve_qwen_model_id(options)
        device_map = self._resolve_device_map(options.device)
        dtype = self._resolve_dtype(options.dtype, device_map)
        attn_implementation = options.attn_implementation
        cache_key = (model_id, device_map, str(dtype), attn_implementation)
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        try:
            from qwen_tts import Qwen3TTSModel
        except ImportError as exc:
            raise RuntimeError(
                "缺少 qwen-tts。请先按 README 中的 Qwen3-TTS 安装说明安装。"
            ) from exc

        model_kwargs: dict[str, object] = {
            "device_map": device_map,
            "dtype": dtype,
        }
        if attn_implementation:
            model_kwargs["attn_implementation"] = attn_implementation
        model = Qwen3TTSModel.from_pretrained(model_id, **model_kwargs)
        self._model_cache[cache_key] = model
        return model

    @staticmethod
    def _extract_first_wave(result: tuple[object, int]) -> tuple[object, int]:
        wavs, sample_rate = result
        if isinstance(wavs, list):
            if not wavs:
                raise RuntimeError("Qwen3-TTS 未返回音频数据")
            first = wavs[0]
            if isinstance(first, (int, float)):
                return wavs, sample_rate
            return first, sample_rate
        return wavs, sample_rate

    @staticmethod
    def _write_audio(output_path: Path, wav: object, sample_rate: int) -> None:
        try:
            import soundfile as sf
        except ImportError as exc:
            raise RuntimeError("缺少 soundfile，无法写出 Qwen3-TTS 生成的音频") from exc
        sf.write(str(output_path), wav, sample_rate)

    def synthesize_text(self, text: str, output_path: Path, options: TTSOptions) -> Path:
        task = normalize_qwen_task(options.task)
        language = options.language or DEFAULT_QWEN3_LANGUAGE
        ensure_directory(output_path.parent)
        model = self._load_model(options)

        if task == "custom_voice":
            speaker = options.speaker or options.voice or DEFAULT_QWEN3_CUSTOM_SPEAKER
            wav, sample_rate = self._extract_first_wave(
                model.generate_custom_voice(
                    text=text,
                    language=language,
                    speaker=speaker,
                    instruct=options.instruct,
                )
            )
        elif task == "voice_design":
            if not options.instruct:
                raise ValueError("Qwen3-TTS voice_design 模式需要 instruct")
            wav, sample_rate = self._extract_first_wave(
                model.generate_voice_design(
                    text=text,
                    language=language,
                    instruct=options.instruct,
                )
            )
        else:
            if not options.ref_audio or not options.ref_text:
                raise ValueError("Qwen3-TTS voice_clone 模式需要 ref_audio 和 ref_text")
            if options.voice_clone_x_vector_only_mode:
                prompt = model.create_voice_clone_prompt(
                    ref_audio=options.ref_audio,
                    ref_text=options.ref_text,
                    x_vector_only_mode=True,
                )
                wav, sample_rate = self._extract_first_wave(
                    model.generate_voice_clone(
                        text=text,
                        language=language,
                        voice_clone_prompt=prompt,
                    )
                )
            else:
                wav, sample_rate = self._extract_first_wave(
                    model.generate_voice_clone(
                        text=text,
                        language=language,
                        ref_audio=options.ref_audio,
                        ref_text=options.ref_text,
                    )
                )

        self._write_audio(output_path, wav, sample_rate)
        return output_path

    def list_voices(self) -> list[VoiceInfo]:
        options = TTSOptions(task="custom_voice", model_id=DEFAULT_QWEN3_MODELS["custom_voice"], device="cpu")
        model = self._load_model(options)
        speakers = list(model.get_supported_speakers())
        languages = tuple(model.get_supported_languages())
        default_speaker = DEFAULT_QWEN3_CUSTOM_SPEAKER if DEFAULT_QWEN3_CUSTOM_SPEAKER in speakers else speakers[0]
        return [
            VoiceInfo(
                id=speaker,
                name=f"Qwen3-TTS {speaker}",
                languages=languages,
                is_default=speaker == default_speaker,
            )
            for speaker in speakers
        ]
