#!/usr/bin/env python3
"""
词库数据验证脚本

检查项：
  - 文件编码（UTF-8）
  - 空行检测
  - 重复词条检测
  - 词条统计
"""

import os
import sys

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


def check_encoding(filepath):
    """检查文件是否为有效的 UTF-8 编码"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False


def split_words(content):
    comma_count = content.count(",")
    line_count = len(content.splitlines())
    if comma_count >= max(1, line_count // 2):
        raw_words = content.split(",")
    else:
        raw_words = content.splitlines()
    return [w.strip() for w in raw_words]


def load_words(filepath):
    """加载词条列表"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return split_words(content)


def find_duplicates(words):
    """查找重复词条"""
    seen = {}
    duplicates = []
    for i, w in enumerate(words):
        if not w:
            continue
        if w in seen:
            duplicates.append((w, seen[w], i))
        else:
            seen[w] = i
    return duplicates


def find_empty_entries(words):
    """查找空词条"""
    return [i for i, w in enumerate(words) if not w.strip()]


def main():
    errors = 0
    warnings = 0
    total_words = 0

    print("=" * 60)
    print("  sensitive-stop-words 数据验证")
    print("=" * 60)
    print()

    for filepath in discover_files():
        filename = os.path.relpath(filepath, REPO_ROOT)

        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename} — 文件不存在")
            continue

        print(f"  检查 {filename}")

        if not check_encoding(filepath):
            print(f"    [ERROR] 文件编码不是有效的 UTF-8")
            errors += 1
            continue

        words = load_words(filepath)
        non_empty = [w for w in words if w]
        total_words += len(non_empty)

        # 重复检测
        duplicates = find_duplicates(words)
        if duplicates:
            print(f"    [WARN]  发现 {len(duplicates)} 个重复词条:")
            for word, first, second in duplicates[:5]:
                print(f"            '{word}' (行 {first + 1} 与 {second + 1})")
            if len(duplicates) > 5:
                print(f"            ... 还有 {len(duplicates) - 5} 个")
            warnings += len(duplicates)

        # 空条目检测
        empty = find_empty_entries(words)
        if empty:
            print(f"    [WARN]  发现 {len(empty)} 个空条目")
            warnings += len(empty)

        print(f"    [OK]    {len(non_empty)} 条有效词条")
        print()

    print("=" * 60)
    print(f"  总计: {total_words} 条词条")
    print(f"  错误: {errors}")
    print(f"  警告: {warnings}")
    print("=" * 60)

    if errors > 0:
        print("\n验证失败！请修复以上错误。")
        sys.exit(1)

    print("\n验证通过。")
    sys.exit(0)


if __name__ == "__main__":
    main()
