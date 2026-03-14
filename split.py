from __future__ import annotations

from pathlib import Path

from novel2audiobook.pipeline import prepare_book, write_chapters

DEFAULT_INPUT_FILE = Path("Novels/《 》 .txt")
DEFAULT_OUTPUT_DIR = Path("Novels/《 》 ")


def split_and_save(input_file: str | Path, encoding: str, out_dir: str | Path) -> list[Path]:
    book = prepare_book(
        source=input_file,
        input_format="txt",
        encoding=encoding,
        normalize=False,
        splitter_name="chinese_novel",
        include_volumes=False,
    )
    return write_chapters(book, out_dir, encoding=encoding, start_index=1)


def split_chapters_and_volumes(input_file: str | Path, encoding: str, out_dir: str | Path) -> list[Path]:
    book = prepare_book(
        source=input_file,
        input_format="txt",
        encoding=encoding,
        normalize=False,
        splitter_name="chinese_novel",
        include_volumes=True,
    )
    return write_chapters(book, out_dir, encoding=encoding, start_index=0)


if __name__ == "__main__":
    files = split_and_save(DEFAULT_INPUT_FILE, "utf-8", DEFAULT_OUTPUT_DIR)
    print(f"已切分 {len(files)} 章到 {DEFAULT_OUTPUT_DIR}")
