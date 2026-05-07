#!/usr/bin/env python3
"""
模型输入敏感检测示例。

用法:
  python3 scripts/check_text.py
"""

import argparse
import json
import os
import unicodedata

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSITIVE_WORDS_DIR = os.path.join(REPO_ROOT, "data", "sensitive_words")

REASON_RULES = (
    (("色情",), "输入内容涉及色情信息。"),
    (("广告", "推广"), "输入内容涉及广告推广信息。"),
    (("政治", "反动", "gfw", "新思想", "民生", "贪腐"), "输入内容涉及政治或社会敏感信息。"),
    (("涉枪", "涉爆", "暴恐"), "输入内容涉及枪支、爆炸物或暴恐相关信息。"),
    (("网址", "非法网址"), "输入内容涉及违规或可疑网址信息。"),
    (("covid", "疫情"), "输入内容涉及疫情相关敏感信息。"),
)


def normalize_text(text):
    """统一全半角和大小写，降低简单绕过的影响。"""
    return unicodedata.normalize("NFKC", text).lower()


def split_words(content):
    """兼容每行一词和逗号分隔两种词库格式。"""
    comma_count = content.count(",")
    line_count = len(content.splitlines())
    if comma_count >= max(1, line_count // 2):
        raw_words = content.split(",")
    else:
        raw_words = content.splitlines()

    return [word.strip() for word in raw_words if word.strip()]


def load_sensitive_words(data_dir):
    entries = []
    seen = set()

    for filename in sorted(os.listdir(data_dir)):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(data_dir, filename)
        if not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            words = split_words(f.read())

        category = os.path.splitext(filename)[0]
        for word in words:
            normalized_word = normalize_text(word)
            key = (category, normalized_word)
            if key in seen:
                continue
            seen.add(key)
            entries.append({
                "category": category,
                "source": filename,
                "word": word,
                "normalized_word": normalized_word,
            })

    return entries


def build_reason(category):
    normalized_category = normalize_text(category)
    for keywords, reason in REASON_RULES:
        if any(keyword in normalized_category for keyword in keywords):
            return reason
    return "输入内容涉及敏感信息。"


def check_text(text, entries, max_reasons):
    normalized_text = normalize_text(text)
    reasons = []

    for entry in entries:
        if entry["normalized_word"] in normalized_text:
            reasons.append({
                "category": entry["category"],
                "source": entry["source"],
                "word": entry["word"],
                "reason": build_reason(entry["category"]),
            })
            if len(reasons) >= max_reasons:
                break

    return {
        "ok": not reasons,
        "reasons": reasons,
    }


def print_result(result):
    print("True" if result["ok"] else "False")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def run_interactive(entries, max_reasons):
    print("请输入待检测文本，可输入多行。")
    print("输入 /check 提交检测，输入 /clear 清空当前内容，输入 exit 或 quit 退出。")
    buffer = []
    while True:
        try:
            line = input("> ")
        except EOFError:
            if buffer:
                result = check_text("\n".join(buffer), entries, max_reasons)
                print_result(result)
            print()
            break

        command = line.strip().lower()
        if command in {"exit", "quit"}:
            break
        if command == "/clear":
            buffer = []
            print("已清空当前输入。")
            continue
        if command == "/check":
            if not buffer:
                print("当前没有待检测内容。")
                continue
            result = check_text("\n".join(buffer), entries, max_reasons)
            print_result(result)
            buffer = []
            continue

        buffer.append(line)


def main():
    parser = argparse.ArgumentParser(description="检测模型输入是否命中敏感词。")
    parser.add_argument(
        "--max-reasons",
        type=int,
        default=20,
        help="最多输出多少条归因，默认 20。",
    )
    args = parser.parse_args()

    entries = load_sensitive_words(SENSITIVE_WORDS_DIR)
    run_interactive(entries, max(1, args.max_reasons))


if __name__ == "__main__":
    main()
