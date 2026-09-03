from __future__ import annotations

import re
from pathlib import Path

EXTRA_RE = re.compile(r"^番外(?:[零一二三四五六七八九十百千0-9].*|[\s:：\(\)（）【】].*|$)")
AFTERWORD_RE = re.compile(r"^完本感言(?:[\s:：\(\)（）【】].*|$)")
CHAPTER_RE = re.compile(r"^第[零一二三四五六七八九十百千万两0-9]+章(?:$|\s|[^章])")


def extract_chinese_numbers(text: str) -> list[str]:
    return re.findall(r"[零一二三四五六七八九十百千]+", text)


def chinese_to_arabic(chinese_num: str) -> str:
    chinese_digits = {
        "零": 0,
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }
    chinese_units = {"十": 10, "百": 100, "千": 1000}

    num = 0
    unit = 1
    for index in range(len(chinese_num) - 1, -1, -1):
        char = chinese_num[index]
        if char in chinese_units:
            unit = chinese_units[char]
            if index == 0 or chinese_num[index - 1] not in chinese_digits:
                num += unit
            continue
        if char in chinese_digits:
            num += chinese_digits[char] * unit
            unit = 1
    return str(num)


def compare_title(str1: str, str2: str, diff: int = 1) -> str | bool:
    if str1 == str2:
        return str1
    if len(str1) < len(str2):
        str1, str2 = str2, str1
    if len(str1) - len(str2) > diff:
        return False
    index1 = 0
    index2 = 0
    diff_found = False
    while index1 < len(str1) and index2 < len(str2):
        if str1[index1] != str2[index2]:
            if diff_found:
                return False
            diff_found = True
            index1 += 1
            continue
        index1 += 1
        index2 += 1
    return str1


def is_chapter_heading(line: str) -> bool:
    return bool(CHAPTER_RE.match(line)) or bool(EXTRA_RE.match(line)) or bool(AFTERWORD_RE.match(line))


def normalize_text(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.replace("(", "（").replace(")", "）").strip()
        if not line or line.count("=") >= 10:
            continue
        if is_chapter_heading(line):
            if lines:
                lines.append("")
            lines.append(line)
            continue
        lines.append(f"\t{line}")
    if not lines:
        return ""
    return "\n".join(lines).rstrip() + "\n"


def normalize_text_file(input_file: str | Path, output_file: str | Path, encoding: str = "utf-8") -> Path:
    input_path = Path(input_file)
    output_path = Path(output_file)
    normalized = normalize_text(input_path.read_text(encoding=encoding, errors="ignore"))
    output_path.write_text(normalized, encoding=encoding, errors="ignore")
    return output_path
