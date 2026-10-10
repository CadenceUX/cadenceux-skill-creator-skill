#!/usr/bin/env python3
"""Validate a skill folder against Anthropic's skill rules and CadenceUX conventions.

Usage:
    python3 scripts/validate_skill.py /path/to/skill-folder

Prints one line per check (PASS, WARN or FAIL, with the fix) and exits 1 if anything failed.
Needs only the Python standard library. If PyYAML is installed it is used to parse the
frontmatter; otherwise a small built-in parser handles the CadenceUX frontmatter shape.
"""
import json
import re
import sys
from pathlib import Path

# Limits published in Anthropic's skill authoring docs.
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
BODY_LINES_MAX = 500          # "keep SKILL.md body under 500 lines"
TOC_THRESHOLD = 100           # reference files longer than this need a contents list
FILE_COUNT_SOFT_MAX = 200     # community-reported upload failure point
FILE_COUNT_WARN = 180         # warn with headroom before the soft max
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "compatibility", "metadata"}
RESERVED = ("anthropic", "claude")
XML_TAG = re.compile(r"<\s*/?\s*[A-Za-z][^>]*>")

results = []


def report(level, message):
    results.append(level)
    print(f"{level:4}  {message}")


def parse_frontmatter(text):
    """Return (frontmatter dict, body text). Raises ValueError if no frontmatter block."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with a '---' frontmatter block")
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        raise ValueError("frontmatter block is not closed with '---'")
    raw = parts[0][3:].lstrip("\n")
    body = parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
    try:
        import yaml  # optional dependency
        data = yaml.safe_load(raw) or {}
        return data, body
    except ImportError:
        return _mini_yaml(raw), body


def _mini_yaml(raw):
    """Parse top-level keys, folded/literal block scalars and one level of nesting."""
    data, lines, i = {}, raw.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).strip()
        if value in (">", ">-", "|", "|-"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            joiner = " " if value.startswith(">") else "\n"
            data[key] = joiner.join(b for b in block if b).strip()
            continue
        if value == "":
            nested = {}
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                n = re.match(r'^\s+"?([^":]+)"?:\s*(.*)$', lines[i])
                if n:
                    nested[n.group(1).strip()] = n.group(2).strip().strip('"')
                i += 1
            data[key] = nested
            continue
        data[key] = value.strip('"')
        i += 1
    return data


def main(folder):
    root = Path(folder).resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        print(f"FAIL  No SKILL.md in {root}")
        return 1

    nested = [p for p in root.rglob("SKILL.md") if p != skill_md and ".git" not in p.parts]
    report("FAIL" if nested else "PASS",
           f"Exactly one SKILL.md{'; remove nested: ' + ', '.join(map(str, nested)) if nested else ''}")

    try:
        fm, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    except ValueError as e:
        report("FAIL", str(e))
        return 1

    extra = set(fm) - ALLOWED_KEYS
    report("FAIL" if extra else "PASS",
           f"Frontmatter keys{' - remove: ' + ', '.join(sorted(extra)) if extra else ''}")

    name = str(fm.get("name", ""))
    problems = []
    if not name:
        problems.append("missing")
    if len(name) > NAME_MAX:
        problems.append(f"{len(name)} chars > {NAME_MAX}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or "x"):
        problems.append("use lowercase letters, numbers and single hyphens only")
    if any(r in name for r in RESERVED):
        problems.append("must not contain 'anthropic' or 'claude'")
    if name and name != root.name and not root.name.startswith(name):
        problems.append(f"folder '{root.name}' doesn't match name (fine for a '-skill' repo folder)")
    level = "FAIL" if any("folder" not in p for p in problems) else ("WARN" if problems else "PASS")
    report(level, f"name '{name}'" + (": " + "; ".join(problems) if problems else ""))

    desc = str(fm.get("description", "") or "")
    dprob = []
    if not desc.strip():
        dprob.append("empty")
    if len(desc) > DESCRIPTION_MAX:
        dprob.append(f"{len(desc)} chars > {DESCRIPTION_MAX}")
    if XML_TAG.search(desc) or "<" in desc or ">" in desc:
        dprob.append("contains angle brackets / XML tags")
    if re.match(r"^\s*(I |I'm |You |Use this|Create |Build |Make )", desc):
        dprob.append("write in the third person ('Creates…', not 'I…'/'You…'/imperative)")
    report("FAIL" if dprob else "PASS",
           f"description ({len(desc)} chars)" + (": " + "; ".join(dprob) if dprob else ""))
    if not re.search(r"\b(Use when|Use whenever|Use for|Use it when)\b", desc):
        report("WARN", "description has no 'Use when…' clause saying when to trigger")

    comp = str(fm.get("compatibility", "") or "")
    if comp and len(comp) > COMPATIBILITY_MAX:
        report("FAIL", f"compatibility {len(comp)} chars > {COMPATIBILITY_MAX}")
    elif not comp:
        report("WARN", "no compatibility field (drives the Claude.ai card)")
    else:
        report("PASS", f"compatibility ({len(comp)} chars)")

    if str(fm.get("license", "")) != "CC-BY-4.0":
        report("WARN", "license should be CC-BY-4.0 (CadenceUX standard)")
    meta = fm.get("metadata") or {}
    version = str(meta.get("version", "")) if isinstance(meta, dict) else ""
    extra_meta = set(meta) - {"author", "version"} if isinstance(meta, dict) else set()
    if not version:
        report("FAIL", "metadata.version missing")
    if extra_meta:
        report("WARN", f"metadata keys render as card rows; remove: {', '.join(sorted(extra_meta))}")
    if version.startswith("v"):
        report("FAIL", f"metadata.version '{version}' must not have a 'v' prefix")

    body_lines = len(body.splitlines())
    report("FAIL" if body_lines >= BODY_LINES_MAX else "PASS",
           f"SKILL.md body {body_lines} lines (limit {BODY_LINES_MAX})")

    refs_dir = root / "references"
    linked = set(re.findall(r"references/[A-Za-z0-9_./-]+", skill_md.read_text(encoding="utf-8")))
    if refs_dir.is_dir():
        for ref in sorted(refs_dir.rglob("*.md")):
            rel = ref.relative_to(root).as_posix()
            text = ref.read_text(encoding="utf-8")
            n = len(text.splitlines())
            if n > TOC_THRESHOLD and not re.search(r"^#{1,3}\s*Contents", "\n".join(text.splitlines()[:40]),
                                                   re.M | re.I):
                report("FAIL", f"{rel}: {n} lines with no '## Contents' near the top")
            if rel not in linked:
                report("WARN", f"{rel} is not linked from SKILL.md")
            chained = [m for m in re.findall(r"\]\((?:\.\./)?references/[^)]+\.md\)|\]\([a-z0-9_-]+\.md\)", text)]
            if chained:
                report("WARN", f"{rel} links on to other reference files ({len(chained)}); keep references one level deep")
    # Only real markdown links must resolve; prose may mention another skill's reference files.
    for link in re.findall(r"\]\((references/[^)#\s]+)", skill_md.read_text(encoding="utf-8")):
        if not (root / link).exists():
            report("FAIL", f"SKILL.md links to missing file {link}")

    for md in [skill_md] + (list(refs_dir.rglob("*.md")) if refs_dir.is_dir() else []):
        if re.search(r"\b(?:references|scripts|assets)\\[A-Za-z0-9_.-]+", md.read_text(encoding="utf-8")):
            report("FAIL", f"{md.relative_to(root)}: Windows-style backslash path; use forward slashes")

    vfile = root / "VERSION"
    if vfile.is_file():
        v = vfile.read_text(encoding="utf-8").strip()
        report("PASS" if v == version else "FAIL", f"VERSION '{v}' vs metadata.version '{version}'")
    else:
        report("WARN", "no VERSION file (required for skills published to GitHub)")
    pj = root / ".claude-plugin" / "plugin.json"
    if pj.is_file():
        try:
            pv = str(json.loads(pj.read_text(encoding="utf-8")).get("version", ""))
            report("PASS" if pv == version else "FAIL", f"plugin.json version '{pv}' vs '{version}'")
        except json.JSONDecodeError as e:
            report("FAIL", f"plugin.json is not valid JSON: {e}")
    else:
        report("WARN", "no .claude-plugin/plugin.json (needed for the cadenceux marketplace)")
    cl = root / "CHANGELOG.md"
    if cl.is_file() and version and version not in cl.read_text(encoding="utf-8")[:4000]:
        report("FAIL", f"CHANGELOG.md has no entry for {version} near the top")
    if not (root / "README.md").is_file():
        report("FAIL", "README.md missing")
    ev = root / "evals" / "evals.json"
    if ev.is_file():
        try:
            cases = json.loads(ev.read_text(encoding="utf-8")).get("cases", [])
            report("PASS" if len(cases) >= 3 else "FAIL", f"evals: {len(cases)} cases (need 3+)")
        except json.JSONDecodeError as e:
            report("FAIL", f"evals/evals.json is not valid JSON: {e}")
    else:
        report("FAIL", "evals/evals.json missing (write 3+ cases)")

    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts and p.name != ".DS_Store"]
    level = "FAIL" if len(files) >= FILE_COUNT_SOFT_MAX else ("WARN" if len(files) >= FILE_COUNT_WARN else "PASS")
    report(level, f"{len(files)} files (uploads reported to fail above ~{FILE_COUNT_SOFT_MAX})")

    fails, warns = results.count("FAIL"), results.count("WARN")
    print(f"\n{'CLEAN' if not fails else 'NOT CLEAN'}: {fails} fail, {warns} warn")
    return 1 if fails else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
