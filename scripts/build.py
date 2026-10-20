#!/usr/bin/env python3
"""Validate daily JSON files, rebuild data/index.json, and render each day to Markdown.

Usage: python3 scripts/build.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")

CATEGORIES = {
    "world": ["國際政治與地緣", "全球經濟與市場", "貿易、關稅與供應鏈", "台灣與亞太", "ESG／氣候與歐盟法規"],
    "markets": ["美股", "台股", "產業與個股"],
    "ai": ["模型與產品", "晶片與算力", "產業與投資", "政策與監管", "研究與安全"],
}


def validate(day: dict, name: str) -> list[str]:
    errors = []
    for key in ("date", "title", "sections", "observation", "sources"):
        if key not in day:
            errors.append(f"{name}: missing '{key}'")
    if day.get("date") and f"{day['date']}.json" != name:
        errors.append(f"{name}: date field '{day['date']}' does not match filename")
    for section in day.get("sections", []):
        allowed = CATEGORIES.get(section.get("id"))
        if allowed is None:
            errors.append(f"{name}: unknown section id '{section.get('id')}'")
            continue
        for i, item in enumerate(section.get("items", [])):
            where = f"{name}: {section['id']}[{i}]"
            for key in ("title", "category", "summary", "why", "sources"):
                if not item.get(key):
                    errors.append(f"{where}: missing '{key}'")
            if item.get("category") and item["category"] not in allowed:
                errors.append(f"{where}: category '{item['category']}' not in {allowed}")
            for g in item.get("glossary", []):
                if not g.get("term") or not g.get("def"):
                    errors.append(f"{where}: glossary entry needs 'term' and 'def': {g!r}")
            for src in item.get("sources", []):
                if not str(src.get("url", "")).startswith("http"):
                    errors.append(f"{where}: bad source url {src!r}")
        if section["id"] == "markets" and not section.get("outlook"):
            errors.append(f"{name}: markets section missing 'outlook'")
    return errors


def to_markdown(day: dict) -> str:
    out = [f"# {day['title']}", ""]
    for section in day["sections"]:
        out += [f"## {section['name']}", ""]
        for n, item in enumerate(section["items"], 1):
            out += [
                f"### {n}. {item['title']}",
                f"`{item['category']}`",
                "",
                item["summary"],
                "",
                f"**為什麼重要：** {item['why']}",
                "",
            ]
            if item.get("glossary"):
                out += ["> 📖 名詞小辭典"] + [f"> - **{g['term']}**：{g['def']}" for g in item["glossary"]] + [""]
        if section.get("outlook"):
            mood = f"（{section['mood']}）" if section.get("mood") else ""
            out += [f"### 美股・台股綜合判斷{mood}", "", section["outlook"], ""]
    out += ["## 綜合觀察", "", day["observation"], "", "Sources:", ""]
    out += [f"- [{s['title']}]({s['url']})" for s in day["sources"]]
    return "\n".join(out) + "\n"


def main() -> int:
    files = sorted((p for p in DATA.iterdir() if DATE_RE.match(p.name)), reverse=True)
    errors, entries = [], []
    for path in files:
        day = json.loads(path.read_text(encoding="utf-8"))
        errs = validate(day, path.name)
        errors += errs
        if errs:
            continue
        path.with_suffix(".md").write_text(to_markdown(day), encoding="utf-8")
        entries.append({
            "date": day["date"],
            "title": day["title"],
            "items": [
                {"section": s["id"], "category": it["category"], "title": it["title"], "anchor": f"{s['id']}-{i + 1}"}
                for s in day["sections"]
                for i, it in enumerate(s["items"])
            ],
        })
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    index = {"categories": CATEGORIES, "days": entries}
    (DATA / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(entries)} day(s) indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
