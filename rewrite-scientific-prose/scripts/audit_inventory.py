#!/usr/bin/env python3
"""Report changed scientific tokens for human review; never certify fidelity or readability."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

MATH = re.compile(r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|(?<!\\)\$(?!\$)[^\n$]*(?<!\\)\$|\\\([\s\S]*?\\\)")
CITATION = re.compile(r"\[(?:\d+[^\]\n]*|@[^\]\n]+)\]")
NUMBER = re.compile(r"(?<![\w])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")

def inventory(text):
    return {"math": MATH.findall(text), "citations": CITATION.findall(text),
            "numbers": NUMBER.findall(text), "links": LINK.findall(text)}

def difference(before, after):
    left, right = Counter(before), Counter(after)
    return {"removed_or_relocated": list((left-right).elements()),
            "added_or_reexpressed": list((right-left).elements())}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("revised", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    before = inventory(args.source.read_text(encoding="utf-8"))
    after = inventory(args.revised.read_text(encoding="utf-8"))
    report = {
        "purpose": "Review prompts only. Token equality is not scientific or readability validation.",
        "source": str(args.source), "revised": str(args.revised),
        "changes": {key: difference(before[key], after[key]) for key in before},
        "limitations": [
            "Citation brackets, headings and prose numerals can overlap.",
            "Equivalent mathematical delimiters or notation produce differences.",
            "Verbal quantities, semantic scope and citation validity need human review.",
            "Relocation must be reconciled against the claim ledger."
        ]
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

if __name__ == "__main__":
    main()
