#!/usr/bin/env python3
"""
词库统计脚本

输出每个词库文件的词条数量及总计。
"""

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSITIVE_WORDS_DIR = os.path.join(REPO_ROOT, "data", "sensitive_words")
STOPWORDS_DIR = os.path.join(REPO_ROOT, "data", "stopwords")


def discover_files():
    files = []
    for dirname, suffixes in (
        (SENSITIVE_WORDS_DIR, (".txt",)),
        (STOPWORDS_DIR, (".dic", ".txt")),
    ):
        if not os.path.isdir(dirname):
            continue
        for filename in sorted(os.listdir(dirname)):
            if filename.endswith(suffixes):
                files.append(os.path.join(dirname, filename))
    return files


def split_words(content):
    comma_count = content.count(",")
    line_count = len(content.splitlines())
    if comma_count >= max(1, line_count // 2):
        raw_words = content.split(",")
    else:
        raw_words = content.splitlines()
    return [w.strip() for w in raw_words if w.strip()]


def count_words(filepath):
    for enc in ("utf-8", "utf-16", "gbk"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        return -1, -1

    words = split_words(content)
    unique = set(words)
    return len(words), len(unique)


def main():
    total = 0
    total_unique = 0

    print(f"{'文件':<35} {'总数':>8} {'去重后':>8}")
    print("-" * 55)

    for filepath in discover_files():
        filename = os.path.relpath(filepath, REPO_ROOT)
        if not os.path.exists(filepath):
            print(f"{filename:<35} {'N/A':>8} {'N/A':>8}")
            continue

        count, unique = count_words(filepath)
        total += count
        total_unique += unique
        print(f"{filename:<35} {count:>8} {unique:>8}")

    print("-" * 55)
    print(f"{'合计':<35} {total:>8} {total_unique:>8}")


if __name__ == "__main__":
    main()
