from __future__ import annotations

from pathlib import Path

from novel2audiobook.processors.cleanup import (
    chinese_to_arabic,
    compare_title,
    extract_chinese_numbers,
    normalize_text_file,
)

DEFAULT_INPUT_FILE = Path("Novels/《 》.txt")
DEFAULT_OUTPUT_FILE = Path("Novels/《 》.txt")


def process_file(input_file: str | Path, output_file: str | Path) -> Path:
    return normalize_text_file(input_file, output_file, encoding="utf-8")


if __name__ == "__main__":
    output_file = process_file(DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_FILE)
    print(f"处理完成！结果已保存到 {output_file}")
