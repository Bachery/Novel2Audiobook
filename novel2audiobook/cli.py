from __future__ import annotations

import argparse
from pathlib import Path

from novel2audiobook.audio import available_audio_converters
from novel2audiobook.inputs import available_input_providers
from novel2audiobook.models import AudioConvertOptions, TTSOptions
from novel2audiobook.pipeline import convert_audio_directory, prepare_book, run_pipeline, synthesize_book, write_chapters
from novel2audiobook.processors import available_splitters
from novel2audiobook.processors.cleanup import normalize_text_file
from novel2audiobook.tts import available_tts_engines, create_tts_engine


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
    tts.add_argument("--engine", default="pyttsx3")
    tts.add_argument("--voice")
    tts.add_argument("--voice-index", type=int, default=8)
    tts.add_argument("--rate", type=int, default=230)
    tts.add_argument("--volume", type=float, default=1.0)
    tts.add_argument("--audio-format", default="aiff")

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
    run.add_argument("--engine", default="pyttsx3")
    run.add_argument("--voice")
    run.add_argument("--voice-index", type=int, default=8)
    run.add_argument("--rate", type=int, default=230)
    run.add_argument("--volume", type=float, default=1.0)
    run.add_argument("--audio-format", default="aiff")
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
            engine_name=args.engine,
            options=TTSOptions(
                voice=args.voice,
                voice_index=args.voice_index,
                rate=args.rate,
                volume=args.volume,
                audio_format=args.audio_format,
            ),
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
            tts_engine=args.engine,
            tts_options=TTSOptions(
                voice=args.voice,
                voice_index=args.voice_index,
                rate=args.rate,
                volume=args.volume,
                audio_format=args.audio_format,
            ),
            audio_converter=args.converter,
            convert_options=AudioConvertOptions(
                source_format=args.audio_format,
                target_format=args.target_format,
                bitrate=args.bitrate,
            ),
        )
        for stage, files in results.items():
            print(f"{stage}: {len(files)} files")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
