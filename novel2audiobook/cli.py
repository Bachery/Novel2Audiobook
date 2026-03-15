from __future__ import annotations

import argparse
from pathlib import Path

from novel2audiobook.config import extract_tts_config, load_config_mapping, resolve_config_paths
from novel2audiobook.audio import available_audio_converters
from novel2audiobook.inputs import available_input_providers
from novel2audiobook.models import AudioConvertOptions, TTSOptions
from novel2audiobook.pipeline import convert_audio_directory, prepare_book, run_pipeline, synthesize_book, write_chapters
from novel2audiobook.processors import available_splitters
from novel2audiobook.processors.cleanup import normalize_text_file
from novel2audiobook.tts import available_tts_engines, create_tts_engine


def load_tts_config(args: argparse.Namespace) -> dict[str, object]:
    config_path = getattr(args, "tts_config", None)
    if not config_path:
        return {}
    data, path = load_config_mapping(config_path)
    tts_config = extract_tts_config(data)
    return resolve_config_paths(tts_config, path)


def pick_tts_arg(args: argparse.Namespace, config: dict[str, object], key: str, fallback: object = None) -> object:
    value = getattr(args, key, None)
    if value is not None:
        return value
    return config.get(key, fallback)


def resolve_tts_engine_name(args: argparse.Namespace, config: dict[str, object] | None = None) -> str:
    merged = config or {}
    engine_name = pick_tts_arg(args, merged, "engine", "pyttsx3")
    if not isinstance(engine_name, str):
        raise ValueError("TTS engine name must be a string")
    return engine_name


def build_tts_options(args: argparse.Namespace, config: dict[str, object] | None = None) -> TTSOptions:
    merged = config or {}
    engine_name = resolve_tts_engine_name(args, merged)
    engine = create_tts_engine(engine_name)
    return TTSOptions(
        voice=pick_tts_arg(args, merged, "voice"),
        voice_index=pick_tts_arg(args, merged, "voice_index"),
        speaker=pick_tts_arg(args, merged, "speaker"),
        language=pick_tts_arg(args, merged, "language"),
        device=pick_tts_arg(args, merged, "device"),
        speed=pick_tts_arg(args, merged, "speed"),
        task=pick_tts_arg(args, merged, "task"),
        model_id=pick_tts_arg(args, merged, "model_id"),
        instruct=pick_tts_arg(args, merged, "instruct"),
        ref_audio=pick_tts_arg(args, merged, "ref_audio"),
        ref_text=pick_tts_arg(args, merged, "ref_text"),
        dtype=pick_tts_arg(args, merged, "dtype"),
        attn_implementation=pick_tts_arg(args, merged, "attn_implementation"),
        voice_clone_x_vector_only_mode=bool(
            pick_tts_arg(args, merged, "voice_clone_x_vector_only_mode", False)
        ),
        rate=pick_tts_arg(args, merged, "rate", 230),
        volume=pick_tts_arg(args, merged, "volume", 1.0),
        audio_format=pick_tts_arg(args, merged, "audio_format", engine.default_audio_format()),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="novel2audiobook",
        description="小说转有声书工具，支持模块化输入、章节拆分、TTS 与音频转码。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="查看当前已注册的输入、切分器、TTS 引擎和转码器")

    list_voices = subparsers.add_parser("list-voices", help="列出指定 TTS 引擎的可用语音")
    list_voices.add_argument("--engine", default="pyttsx3")
    list_voices.add_argument("--chinese-only", action="store_true")

    normalize = subparsers.add_parser("normalize", help="清洗单个 txt 文本")
    normalize.add_argument("input")
    normalize.add_argument("output")
    normalize.add_argument("--encoding", default="utf-8")

    split = subparsers.add_parser("split", help="读取单本小说并切分为章节 txt")
    split.add_argument("source")
    split.add_argument("output_dir")
    split.add_argument("--input-format", default="auto")
    split.add_argument("--encoding", default="utf-8")
    split.add_argument("--splitter", default="chinese_novel")
    split.add_argument("--include-volumes", action="store_true")
    split.add_argument("--skip-normalize", action="store_true")
    split.add_argument("--start-index", type=int, default=1)

    tts = subparsers.add_parser("tts", help="把章节 txt 或整本 txt 转成音频")
    tts.add_argument("source")
    tts.add_argument("output_dir")
    tts.add_argument("--input-format", default="auto")
    tts.add_argument("--encoding", default="utf-8")
    tts.add_argument("--splitter", default="chinese_novel")
    tts.add_argument("--include-volumes", action="store_true")
    tts.add_argument("--skip-normalize", action="store_true")
    tts.add_argument("--tts-config")
    tts.add_argument("--engine")
    tts.add_argument("--voice")
    tts.add_argument("--speaker")
    tts.add_argument("--language")
    tts.add_argument("--device")
    tts.add_argument("--task")
    tts.add_argument("--model-id")
    tts.add_argument("--instruct")
    tts.add_argument("--ref-audio")
    tts.add_argument("--ref-text")
    tts.add_argument("--dtype")
    tts.add_argument("--attn-implementation")
    tts.add_argument("--voice-clone-x-vector-only-mode", action="store_true", default=None)
    tts.add_argument("--speed", type=float)
    tts.add_argument("--voice-index", type=int)
    tts.add_argument("--rate", type=int)
    tts.add_argument("--volume", type=float)
    tts.add_argument("--audio-format")

    convert = subparsers.add_parser("convert", help="批量转换音频格式")
    convert.add_argument("input_dir")
    convert.add_argument("output_dir")
    convert.add_argument("--converter", default="pydub")
    convert.add_argument("--source-ext", default=".aiff")
    convert.add_argument("--target-format", default="mp3")
    convert.add_argument("--bitrate")

    run = subparsers.add_parser("run", help="串联执行切分、TTS 和转码")
    run.add_argument("source")
    run.add_argument("--chapters-dir")
    run.add_argument("--audio-dir")
    run.add_argument("--converted-dir")
    run.add_argument("--input-format", default="auto")
    run.add_argument("--encoding", default="utf-8")
    run.add_argument("--splitter", default="chinese_novel")
    run.add_argument("--include-volumes", action="store_true")
    run.add_argument("--skip-normalize", action="store_true")
    run.add_argument("--tts-config")
    run.add_argument("--engine")
    run.add_argument("--voice")
    run.add_argument("--speaker")
    run.add_argument("--language")
    run.add_argument("--device")
    run.add_argument("--task")
    run.add_argument("--model-id")
    run.add_argument("--instruct")
    run.add_argument("--ref-audio")
    run.add_argument("--ref-text")
    run.add_argument("--dtype")
    run.add_argument("--attn-implementation")
    run.add_argument("--voice-clone-x-vector-only-mode", action="store_true", default=None)
    run.add_argument("--speed", type=float)
    run.add_argument("--voice-index", type=int)
    run.add_argument("--rate", type=int)
    run.add_argument("--volume", type=float)
    run.add_argument("--audio-format")
    run.add_argument("--converter", default="pydub")
    run.add_argument("--target-format", default="mp3")
    run.add_argument("--bitrate")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        print("input providers:", ", ".join(available_input_providers()))
        print("splitters:", ", ".join(available_splitters()))
        print("tts engines:", ", ".join(available_tts_engines()))
        print("audio converters:", ", ".join(available_audio_converters()))
        return 0

    if args.command == "list-voices":
        engine = create_tts_engine(args.engine)
        print("candidate_index\tvoice_id\tname\tlanguages\tdefault")
        for voice in engine.list_voices():
            if args.chinese_only and voice.candidate_index is None:
                if not any(
                    language.upper().startswith("ZH") or language.upper().startswith("CHINESE")
                    for language in voice.languages
                ):
                    continue
            languages = ", ".join(voice.languages) or "-"
            candidate = "-" if voice.candidate_index is None else str(voice.candidate_index)
            default_marker = "default" if voice.is_default else ""
            print(f"{candidate}\t{voice.id}\t{voice.name}\t{languages}\t{default_marker}")
        return 0

    if args.command == "normalize":
        path = normalize_text_file(args.input, args.output, encoding=args.encoding)
        print(path)
        return 0

    if args.command == "split":
        book = prepare_book(
            source=args.source,
            input_format=args.input_format,
            encoding=args.encoding,
            normalize=not args.skip_normalize,
            splitter_name=args.splitter,
            include_volumes=args.include_volumes,
        )
        files = write_chapters(book, args.output_dir, encoding=args.encoding, start_index=args.start_index)
        print(f"wrote {len(files)} chapters to {Path(args.output_dir)}")
        return 0

    if args.command == "tts":
        tts_config = load_tts_config(args)
        tts_engine = resolve_tts_engine_name(args, tts_config)
        tts_options = build_tts_options(args, tts_config)
        book = prepare_book(
            source=args.source,
            input_format=args.input_format,
            encoding=args.encoding,
            normalize=not args.skip_normalize,
            splitter_name=args.splitter,
            include_volumes=args.include_volumes,
        )
        files = synthesize_book(
            book,
            args.output_dir,
            engine_name=tts_engine,
            options=tts_options,
        )
        print(f"generated {len(files)} audio files in {Path(args.output_dir)}")
        return 0

    if args.command == "convert":
        files = convert_audio_directory(
            args.input_dir,
            args.output_dir,
            converter_name=args.converter,
            source_ext=args.source_ext,
            options=AudioConvertOptions(
                source_format=args.source_ext.lstrip("."),
                target_format=args.target_format,
                bitrate=args.bitrate,
            ),
        )
        print(f"converted {len(files)} files to {Path(args.output_dir)}")
        return 0

    if args.command == "run":
        tts_config = load_tts_config(args)
        tts_engine = resolve_tts_engine_name(args, tts_config)
        tts_options = build_tts_options(args, tts_config)
        results = run_pipeline(
            source=args.source,
            chapters_dir=args.chapters_dir,
            audio_dir=args.audio_dir,
            converted_dir=args.converted_dir,
            input_format=args.input_format,
            encoding=args.encoding,
            splitter_name=args.splitter,
            include_volumes=args.include_volumes,
            normalize=not args.skip_normalize,
            tts_engine=tts_engine,
            tts_options=tts_options,
            audio_converter=args.converter,
            convert_options=AudioConvertOptions(
                source_format=tts_options.audio_format,
                target_format=args.target_format,
                bitrate=args.bitrate,
            ),
        )
        for stage, files in results.items():
            print(f"{stage}: {len(files)} files")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
