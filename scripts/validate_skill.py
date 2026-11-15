#!/usr/bin/env python3
"""Validate a skill folder against Anthropic's skill rules and CadenceUX conventions.

Usage:
    python3 scripts/validate_skill.py /path/to/skill-folder
    python3 scripts/validate_skill.py --own /path/to/skill-folder
    python3 scripts/validate_skill.py --claude-code /path/to/skill-folder
    python3 scripts/validate_skill.py --archive /path/to/skill-name-vX.Y.Z.zip

--own is for a developer's own skill: it drops the CadenceUX-only checks (CC-BY-4.0 licence,
cadenceux marketplace wording) and warns if CadenceUX branding has leaked into the skill.

--claude-code is for a skill that ships only inside a Claude Code plugin: it also accepts
Claude Code's own frontmatter keys (when_to_use, disable-model-invocation, argument-hint, …),
which the Claude.ai upload rejects. --own and --claude-code can be combined.

Prints one line per check (PASS, WARN or FAIL, with the fix) and exits 1 if anything failed.
Needs only the Python standard library. If PyYAML is installed it is used to parse the
frontmatter; otherwise a small built-in parser handles the CadenceUX frontmatter shape.
"""
import json
import re
import sys
import zipfile
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
# Read by Claude Code only (code.claude.com/docs/en/skills); the Claude.ai upload rejects them.
CLAUDE_CODE_KEYS = {"when_to_use", "argument-hint", "arguments", "disable-model-invocation",
                    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
                    "background", "hooks", "paths", "shell"}
LISTING_MAX = 1536            # Claude Code cuts description + when_to_use here in the skill listing
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


def main(folder, own=False, claude_code=False):
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

    cc_keys = set(fm) & CLAUDE_CODE_KEYS
    extra = set(fm) - ALLOWED_KEYS - (CLAUDE_CODE_KEYS if claude_code else set())
    if extra:
        hint = ""
        if extra & CLAUDE_CODE_KEYS:
            hint = (" (Claude Code-only keys: if the skill ships only in a Claude Code plugin, "
                    "re-run with --claude-code; otherwise remove them)")
        report("FAIL", f"Frontmatter keys - remove: {', '.join(sorted(extra))}{hint}")
    else:
        report("PASS", "Frontmatter keys")
    if claude_code and cc_keys:
        report("WARN", f"Claude Code-only keys ({', '.join(sorted(cc_keys))}): ship through the plugin "
                       "marketplace only, never as a .skill or zip upload; say so in compatibility")
    if claude_code and not cc_keys:
        report("WARN", "--claude-code but no Claude Code-only keys: the plain mode is enough")

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
    listing = len(desc) + len(str(fm.get("when_to_use", "") or ""))
    if listing > LISTING_MAX:
        report("WARN", f"description + when_to_use is {listing} chars; Claude Code's skill listing "
                       f"cuts it at {LISTING_MAX}")

    comp = str(fm.get("compatibility", "") or "")
    if comp and len(comp) > COMPATIBILITY_MAX:
        report("FAIL", f"compatibility {len(comp)} chars > {COMPATIBILITY_MAX}")
    elif not comp:
        report("WARN", "no compatibility field (drives the Claude.ai card)")
    else:
        report("PASS", f"compatibility ({len(comp)} chars)")

    if own:
        if not fm.get("license"):
            report("WARN", "no license field: add the licence the developer chose (and a LICENSE file)")
    elif str(fm.get("license", "")) != "CC-BY-4.0":
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
        report("WARN", "no .claude-plugin/plugin.json (needed to install as a Claude Code plugin)"
               if own else "no .claude-plugin/plugin.json (needed for the cadenceux marketplace)")
    cl = root / "CHANGELOG.md"
    if cl.is_file() and version and version not in cl.read_text(encoding="utf-8")[:4000]:
        report("FAIL", f"CHANGELOG.md has no entry for {version} near the top")
    if not (root / "README.md").is_file():
        report("FAIL", "README.md missing")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    if vfile.is_file():
        if "raw/main/VERSION" in skill_text or "stack_check" in skill_text:
            report("PASS", "skill update self-check present")
        else:
            report("WARN", "no skill update self-check: fetch the repo's raw/main/VERSION once per session "
                           "(see references/packaging-and-release.md)")
    # Preview programs: never publish preview version numbers (e.g. Claris ADT builds).
    preview = re.compile(r"\b(ADT|Agentic Development Toolkit)\b[^\n|]{0,20}\bv?0\.\d+(?:\.\d+)?")
    hits = []
    for f in root.rglob("*"):
        if (f.is_file() and ".git" not in f.parts and f.suffix in (".md", ".json", ".py", ".txt")
                and f.name != "validate_skill.py" and f.stat().st_size < 2_000_000):
            for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if preview.search(line):
                    hits.append(f"{f.relative_to(root)}:{n}")
    if hits:
        report("FAIL", "preview version number published (ADT is in a preview program): " + ", ".join(hits[:5]))
    else:
        report("PASS", "no preview version numbers")
    if own:
        # A developer's own skill must not carry CadenceUX's name, attribution or prefixes.
        brand = re.compile(r"Darrin Southern|cadenceux\.com\.au|linkedin\.com/in/darrin-southern|Built and maintained by .*CadenceUX")
        leaks = []
        for f in [skill_md, root / "README.md", root / "LICENSE", root / ".claude-plugin" / "plugin.json"]:
            if f.is_file():
                for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if brand.search(line):
                        leaks.append(f"{f.relative_to(root)}:{n}")
        if leaks:
            report("WARN", "CadenceUX branding in a developer's own skill: " + ", ".join(leaks[:5]))
        if str(fm.get("name", "")).startswith(("cadenceux-", "claris-")):
            report("WARN", f"name '{fm.get('name')}' uses a CadenceUX prefix; use the developer's own (or none)")
        if not leaks and not str(fm.get("name", "")).startswith(("cadenceux-", "claris-")):
            report("PASS", "no CadenceUX branding")
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


def check_archive(path):
    """Check a release archive (.zip or .skill) built for upload and for the GitHub release."""
    arc = Path(path).expanduser().resolve()
    if not arc.is_file():
        print(f"FAIL  No archive at {arc}")
        return 1
    try:
        z = zipfile.ZipFile(arc)
    except zipfile.BadZipFile:
        print(f"FAIL  {arc.name} is not a zip archive")
        return 1
    names = [n for n in z.namelist() if not n.endswith("/")]
    tops = {n.split("/", 1)[0] for n in z.namelist()}
    if len(tops) != 1 or any("/" not in n for n in names):
        report("FAIL", f"archive must hold exactly one top-level folder (found {sorted(tops)}); "
                       "zip the skill folder itself, not its contents")
        return finish()
    top = tops.pop()
    report("PASS", f"one top-level folder: {top}/")
    inside = {n.split("/", 1)[1] for n in names}

    # The files a published skill must carry. A working folder can be missing them (on
    # 2026-10-12 nine releases shipped without VERSION, CHANGELOG.md and README.md because
    # they were zipped from stripped local copies), so build from the release tag.
    for required in ("SKILL.md", "VERSION", "CHANGELOG.md", "README.md"):
        report("PASS" if required in inside else "FAIL",
               f"{required} {'present' if required in inside else 'missing: rebuild from a clean checkout of the release tag'}")

    for bad, why in ((".claude-plugin/", "the Claude app's skill upload rejects a plugin manifest"),
                     (".git/", "repository internals"),
                     (".gitignore", "repository file, not part of the skill")):
        hit = [n for n in inside if n == bad or n.startswith(bad)]
        report("FAIL" if hit else "PASS", f"{bad} {'included: exclude it (' + why + ')' if hit else 'not included'}")
    ds = [n for n in inside if n.endswith(".DS_Store")]
    report("WARN" if ds else "PASS", f".DS_Store {'included (' + str(len(ds)) + '): exclude it' if ds else 'not included'}")
    mt = [n for n in inside if n.startswith("maintainer/")]
    report("WARN" if mt else "PASS",
           f"maintainer/ {'included: build tools are not part of the skill; exclude it' if mt else 'not included'}")

    version = None
    if "SKILL.md" in inside:
        try:
            fm, _ = parse_frontmatter(z.read(f"{top}/SKILL.md").decode("utf-8"))
            version = str((fm.get("metadata") or {}).get("version", "")).strip() or None
            if fm.get("name") and fm.get("name") != top:
                report("WARN", f"folder '{top}' differs from name '{fm.get('name')}'")
            cc = set(fm) & CLAUDE_CODE_KEYS
            if cc:
                report("FAIL", f"SKILL.md uses Claude Code-only keys ({', '.join(sorted(cc))}): the Claude app's "
                               "upload rejects them; ship this skill through the plugin marketplace only")
        except (ValueError, UnicodeDecodeError) as e:
            report("FAIL", f"SKILL.md frontmatter unreadable: {e}")
    if version and "VERSION" in inside:
        v = z.read(f"{top}/VERSION").decode("utf-8").strip()
        report("PASS" if v == version else "FAIL", f"VERSION '{v}' vs metadata.version '{version}'")
    if version and "CHANGELOG.md" in inside:
        head = z.read(f"{top}/CHANGELOG.md").decode("utf-8", "replace")[:3000]
        report("PASS" if version in head else "FAIL", f"CHANGELOG.md {'has' if version in head else 'has no'} entry for {version} near the top")
    if version:
        stem_ok = arc.stem.endswith(f"-v{version}")
        report("PASS" if stem_ok else "WARN", f"archive name {'matches' if stem_ok else 'does not end with'} -v{version}")

    level = "FAIL" if len(names) >= FILE_COUNT_SOFT_MAX else ("WARN" if len(names) >= FILE_COUNT_WARN else "PASS")
    report(level, f"{len(names)} files (uploads reported to fail above ~{FILE_COUNT_SOFT_MAX})")

    twin = arc.with_suffix(".skill" if arc.suffix == ".zip" else ".zip")
    if twin.is_file():
        same = twin.read_bytes() == arc.read_bytes()
        report("PASS" if same else "FAIL", f"{twin.name} {'is identical' if same else 'differs: copy the zip again'}")
    else:
        report("WARN", f"no {twin.name} beside it (the release ships both)")
    return finish()


def finish():
    fails, warns = results.count("FAIL"), results.count("WARN")
    print(f"\n{'CLEAN' if not fails else 'NOT CLEAN'}: {fails} fail, {warns} warn")
    return 1 if fails else 0


if __name__ == "__main__":
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    known = {"--archive", "--own", "--claude-code"}
    if len(paths) != 1 or set(flags) - known or ("--archive" in flags and len(flags) > 1):
        print(__doc__)
        sys.exit(2)
    if "--archive" in flags:
        sys.exit(check_archive(paths[0]))
    sys.exit(main(paths[0], own="--own" in flags, claude_code="--claude-code" in flags))
