# Frontmatter, limits and the skill card

## Contents
- Hard limits
- The CadenceUX standard and why
- How Claude.ai renders the card
- Versions
- File count

## Hard limits

Validated on upload; a breach fails the install or silently truncates.

| Field | Rule |
|---|---|
| `name` | ≤ 64 characters; lowercase letters, numbers and hyphens only; no leading, trailing or doubled hyphens; no XML tags; must not contain "anthropic" or "claude" |
| `description` | Non-empty; ≤ 1,024 characters; no XML tags (avoid `<` and `>` entirely) |
| `compatibility` | Optional; ≤ 500 characters |
| Keys | Only `name`, `description`, `license`, `allowed-tools`, `compatibility`, `metadata` |
| SKILL.md | Exactly one per skill; nested SKILL.md files are rejected |

Count the description after every edit. One that looks fine in an editor fails at 1,025.

## The CadenceUX standard and why

```yaml
---
name: claris-filemaker-pro
description: >-
  FileMaker Pro reference for … Use whenever … Not for …
license: CC-BY-4.0
compatibility: >-
  Claude.ai, Claude Desktop, Cowork and Claude Code. ADT mode needs …
metadata:
  author: Darrin Southern, CadenceUX
  version: "2.1.0"
---
```

- **`name` and `description` first.** They are what every surface reads first.
- **`>-` (folded, strip) for long values.** Line breaks fold to spaces and the trailing newline
  is stripped. Never write a long value as one plain-scalar line: a colon followed by a space
  breaks the YAML and the raw frontmatter appears in the rendered body. Don't use `|` for
  `compatibility`; the kept newline renders badly.
- **`license: CC-BY-4.0`** on every CadenceUX skill.
- **`metadata` holds `author` and `version` only.** Every metadata key becomes a visible card
  row, so catalog or plugin version data belongs in the reference JSON's own `meta` block.
- **`compatibility` lists only surfaces the skill was designed and tested for**, plus any hard
  requirement ("ADT mode needs the Claris ADT plugin").

## How Claude.ai renders the card

- Each `metadata` key renders as a labelled row ("Version / 2.1.0", "Author / …").
- Metadata values are plain text; markdown links show as raw characters.
- The card is built from frontmatter. Never hand-write a "Version" or "Compatibility" block in
  the body; it duplicates the card and drifts.

## Versions

- Semantic versioning, three parts: `"2.1.0"`. Minor for content additions, patch for fixes,
  major for restructures.
- `metadata.version`, the root `VERSION` file, `.claude-plugin/plugin.json` `version` and the
  newest CHANGELOG heading must be byte-identical. The self-version check is a plain string
  compare, so `v2.1.0` versus `2.1.0` reports "update available" forever.

## File count

No official ceiling is published, but uploads have been reported to fail above roughly 200
files ("zip file contains more than 200 files"). Large catalogs consolidate into a few JSON
files grouped by category. `monkeybread-mbs-plugin`'s July 2026 rebuild hit 241 files with one
file per component and now bin-packs components into size-balanced `group-NN.json` files.
Check `unzip -l` on every release archive.
