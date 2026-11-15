# Frontmatter, limits and the skill card

## Contents
- Hard limits
- The CadenceUX standard and why
- How Claude.ai renders the card
- Claude Code–only skills
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

## Claude Code–only skills

The six keys above are the portable set: the Claude.ai upload, the Skills API and Anthropic's
packager accept nothing else. Claude Code reads more, and ignores keys it doesn't know. A skill
that ships only inside a Claude Code plugin, and is never uploaded as a `.skill` or zip, may use
them. The ones that matter most:

| Field | What it does |
|---|---|
| `when_to_use` | Extra trigger text, added to the description in the skill listing |
| `disable-model-invocation: true` | Only the user can start it (as a `/` command); Claude never loads it on its own |
| `user-invocable: false` | The reverse: Claude can load it, but it's hidden from the `/` menu |
| `argument-hint` | Shown in autocomplete, e.g. `"[environment]"` |
| `disallowed-tools` | Tools blocked while the skill runs (`allowed-tools` is portable) |
| `context: fork` (+ `agent`) | Runs the skill in a forked subagent instead of the main conversation |
| `paths` | Glob patterns that limit when the skill is offered |
| `model`, `effort` | Model and effort while the skill runs |

The body can also use `$ARGUMENTS` (or `$0`, `$1`, … for single arguments) to receive what the
user typed after the command, and `${CLAUDE_SKILL_DIR}` to reach the skill's own files from any
working directory. A line starting `` !`command` `` runs that command when the skill loads and
puts its output in place.

Rules for using them:

- **Decide the surface first.** One extra key makes the skill Claude Code–only: say so in
  `compatibility`, and ship it through the plugin marketplace only, never as a release
  `.skill` or zip.
- **Validate with `--claude-code`**: `scripts/validate_skill.py --claude-code <folder>` accepts
  these keys and still fails unknown ones (usually typos).
- **A plugin skill is namespaced**: `/plugin-name:skill-name`, not `/skill-name`.
- **`disable-model-invocation` is a setting, not a promise in prose**, so it's the right tool
  for "Claude must never run this by itself". Anything stronger (block a tool call, check an
  edit) is a hook: route it to `cadenceux-plugin-creator`.
- Claude Code cuts the description plus `when_to_use` at 1,536 characters in the listing. Keep
  the description itself under 1,024 regardless, so the limit is the same everywhere.

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
