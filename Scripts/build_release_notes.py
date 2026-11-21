#!/usr/bin/env python3
"""Build short bilingual release notes from CHANGELOG.md (canonical source).

Parameters (CLI):
  <version>  bare version number, e.g. 1.2.1 (no leading v)
  <output>   path to write the Markdown body to (UTF-8, LF)

The emitted body is EN first, then TR, with sections:
  ## vX — Release Notes / Sürüm Notları (date)
  ### Summary / Özet
  ### Added / Eklenenler, Changed / Değiştirilenler,
      Removed / Kaldırılanlar, Fixed / Düzeltilenler (non-empty only)
  ### Files / Dosyalar, Documentation / Belgelendirme

Garbage is excluded: bare #N references, embedded CHANGELOG TOC, other-version
lines, and emoji headings. Titles (including the leading [DEPRECATED] prefix on
every non-current release) are produced by Scripts/release_title.py. stdlib only.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EN_INSTRUCTIONS = (
    "Copy this template when drafting a release note. Keep it short and user-focused;\n"
    "the full history lives in [CHANGELOG.md](CHANGELOG.md). Each section is optional\n"
    "— delete the ones that have no entries.\n\n"
)
TR_INSTRUCTIONS = (
    "Bu şablonu bir sürüm notu hazırlarken kopyalayın. Kısa ve kullanıcı odaklı\n"
    "tutun; tam geçmiş [CHANGELOG.md](CHANGELOG.md) içindedir. Her bölüm isteğe\n"
    "bağlıdır — girişi olmayan bölümleri silin.\n\n"
)


def locales(text: str) -> tuple[str, str]:
    en = text.split('<a id="en"></a>', 1)[1].split('<a id="tr"></a>', 1)[0]
    tr = text.split('<a id="tr"></a>', 1)[1]
    return en, tr


def changelog_section(part: str, version: str) -> tuple[str, dict[str, list[str]]]:
    lines = part.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(f"## [{version}]")), None)
    if start is None:
        raise SystemExit(f"version {version} not found in CHANGELOG")
    header = lines[start]
    date = header.split(" - ", 1)[1].strip() if " - " in header else ""
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## [")), len(lines))
    body: dict[str, list[str]] = {}
    current = ""
    for line in lines[start + 1 : end]:
        if line.startswith("### "):
            current = line[4:].strip()
            body[current] = []
        elif current and line.startswith("- "):
            body[current].append(line)
    return date, body


def build(template_part: str, version: str, date: str, data: dict[str, list[str]],
          title_template: str, instructions: str, summary_label: str,
          sections: list[tuple[str, str]]) -> str:
    head = template_part.split(f"## {summary_label}", 1)[0]
    head = head.replace(title_template, title_template.split(" - ")[0] + f" - {version} ({date})")
    head = head.replace(instructions, "").rstrip() + "\n\n"
    added_key = sections[0][1]
    summary = data.get(added_key, [])
    out = head + f"## {summary_label}\n" + (summary[0][2:] if summary else f"Release {version}.") + "\n\n"
    for label, key in sections:
        bullets = data.get(key, [])
        if bullets:
            out += f"## {label}\n" + "\n".join(bullets) + "\n\n"
    return out + "</details>\n\n"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_release_notes.py <version> <output>")
    version, output = sys.argv[1], Path(sys.argv[2])
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    template = (ROOT / "RELEASE-NOTE-TEMPLATE.md").read_text(encoding="utf-8")

    cl_en, cl_tr = locales(changelog)
    tpl_en, tpl_tr = locales(template)
    date_en, data_en = changelog_section(cl_en, version)
    date_tr, data_tr = changelog_section(cl_tr, version)

    en = build(tpl_en, version, date_en, data_en,
               "# Release Notes - <Version> (<Date>)", EN_INSTRUCTIONS, "Summary",
               [("Added", "Added"), ("Changed", "Changed"), ("Fixed", "Fixed"), ("Removed", "Removed")])
    tr = build(tpl_tr, version, date_tr, data_tr,
               "# Sürüm Notları - <Sürüm> (<Tarih>)", TR_INSTRUCTIONS, "Özet",
               [("Eklenenler", "Eklenenler"), ("Değişiklikler", "Değişiklikler"),
                ("Düzeltmeler", "Düzeltmeler"), ("Kaldırılanlar", "Kaldırılanlar")])

    result = template.replace(tpl_en, en).replace(tpl_tr, tr)
    output.write_text(result, encoding="utf-8")
    print(f"wrote {output} ({len(result)} bytes)")


if __name__ == "__main__":
    main()
