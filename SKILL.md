---
name: cadenceux-skill-creator
description: >-
  Creates, updates and reviews Claude skills for CadenceUX and Claris FileMaker projects to
  Anthropic's skill authoring best practices. Covers the full loop: capture intent, write evals
  first, draft SKILL.md with progressive disclosure, test on Haiku, Sonnet and Opus against a
  no-skill baseline, iterate, then package for GitHub, the cadenceux plugin marketplace and
  Claude.ai. Includes staleness checks for skills that catalog a vendor's plugin, API or product.
  Use when building a new skill, updating or auditing an existing one, writing skill evals,
  fixing a skill that isn't triggering, or publishing a skill release, even when phrased
  casually ("make a skill for X", "update the Y skill", "my skill isn't triggering"). Not for
  hooks or anything that must be enforced rather than advised; that belongs in a plugin.
license: CC-BY-4.0
compatibility: >-
  Claude Code (recommended for builds, evals and packaging), Claude.ai, Claude Desktop and
  Cowork.
metadata:
  author: Darrin Southern, CadenceUX
  version: "2.1.2"
---

# CadenceUX Skill Creator

Builds and maintains Claude skills to Anthropic's authoring best practices, with CadenceUX's
packaging and publishing conventions on top. The reference example of a finished skill is
`claris-filemaker-pro` v2.1.0 (github.com/CadenceUX/claris-filemaker-pro-skill): match its
frontmatter, structure, evals and packaging.

## Workflow

Copy this checklist into the response and tick it off. Jump in at the step the work is at.

```
Skill progress:
- [ ] 1. Environment check (model and surface)
- [ ] 2. Capture intent
- [ ] 3. Write 3+ evals; run a no-skill baseline
- [ ] 4. Draft the skill: minimum content that passes the evals
- [ ] 5. Validate: run scripts/validate_skill.py, fix, re-run until clean
- [ ] 6. Run the evals on Haiku, Sonnet and Opus; compare with the baseline
- [ ] 7. Iterate until evals pass; tune the description
- [ ] 8. Package and publish
```

## 1. Environment check

Note the **model** and **surface** before any work, and say so in one sentence if the
environment is a poor fit ("this is a catalog audit; worth switching to Opus first"). Don't
block light work waiting for a better environment.

**Read the model from two signals.** The "You are powered by …" system-prompt line is fixed at
session start; a later `/model` output (`Set model to …`) overrides it. Re-read both each time
rather than recalling an earlier turn.

| Task | Model |
|---|---|
| Reference-catalog builds and audits, accuracy reviews, multi-skill consistency passes | The most capable available (Opus or better). A July 2026 audit at that tier found 58 missing steps and 8 phantom entries that had survived earlier passes. |
| Wording, description tuning, README/CHANGELOG, packaging | Sonnet is fine; the validator and checklist are the guardrails. |

If heavy work proceeds on Sonnet anyway, load `cadenceux-sonnet-craft` if it's installed (and
`cadenceux-fable-mode` too when the skill being built touches live FileMaker state). If neither
is installed, apply the core discipline directly: define the victory condition first, evidence
over "should be accurate", cap same-error retries at two, keep diagnosis separate from action,
no unrequested scope.

**Surface.** Build, validate, run evals and package from Claude Code (code execution, subagents,
the real filesystem). Check the rendered skill card and real triggering in Claude.ai after
upload. Details: [references/execution-surfaces.md](references/execution-surfaces.md).

## 2. Capture intent

If the conversation already holds the workflow ("turn this into a skill"), extract the answers
from it first: tools used, steps, corrections, input and output formats. Then ask only for the
gaps:

1. What should the skill enable Claude to do, and when should it trigger (phrases, file types,
   contexts)?
2. What does good output look like?
3. Does it need bundled scripts or reference files?
4. Does it catalog something external that changes (a plugin, an API, a product)? Then it needs
   a staleness check from the start: [references/verification-patterns.md](references/verification-patterns.md).
5. Will it be published to GitHub or the marketplace? Then it needs `VERSION`, the
   self-version check and `.claude-plugin/plugin.json` from the start.
6. Does any part need a **guarantee** ("always block X", "never allow Y")? A skill is advice
   and bends under context pressure. Enforcement is a hook packaged in a plugin; route that part
   to `cadenceux-plugin-creator` and say so plainly.

## 3. Evals first

Write the evals before the skill, so it solves observed gaps rather than imagined ones:

1. Run 3+ representative prompts **without** the skill and note what goes wrong.
2. Turn those failures into cases in `evals/evals.json` with `must` and `must_not` facts.
3. Add near-miss prompts that should **not** trigger the skill.
4. Record the baseline score.

Format, grading and running across models: [references/testing-and-evals.md](references/testing-and-evals.md).

## 4. Draft the skill

### Frontmatter (CadenceUX standard)

```yaml
---
name: kebab-case-name
description: >-
  Third person. What it does, then "Use when …" with concrete triggers and key terms,
  then "Not for …" for the nearest out-of-scope neighbours.
license: CC-BY-4.0
compatibility: >-
  The surfaces it's designed and tested for, plus any hard requirement.
metadata:
  author: Darrin Southern, CadenceUX
  version: "1.0.0"
---
```

Hard limits (checked by `scripts/validate_skill.py`): `name` ≤ 64 characters, lowercase letters,
numbers and hyphens only, no "anthropic" or "claude"; `description` non-empty, ≤ 1,024
characters, no XML tags; `compatibility` ≤ 500 characters; only the keys `name`, `description`,
`license`, `allowed-tools`, `compatibility`, `metadata`. Rationale, card rendering and
versioning rules: [references/frontmatter.md](references/frontmatter.md).

### Description

The description is all Claude sees when choosing among 100+ skills. Write it in the **third
person** ("Creates …", never "I can …" or "You can …"), say **what** and **when**, include the
terms users actually type, and close with a "Not for" clause naming the nearest neighbours.
Leave out counts and versions; they go stale and the description can't warn anyone.

### Structure and progressive disclosure

```
skill-name/
├── SKILL.md              overview and navigation; body under 500 lines
├── VERSION               bare version string, same as metadata.version
├── CHANGELOG.md
├── README.md
├── references/           loaded on demand, one level deep from SKILL.md
├── scripts/              run by Claude as part of the skill
├── maintainer/           build and verification tools; not part of the skill's job
├── evals/evals.json      plus dated results files
└── .claude-plugin/plugin.json
```

- Keep the SKILL.md body under 500 lines. Split by domain or task into `references/` and link
  each file **directly from SKILL.md**; never chain references (a link inside a reference file
  may only be partially read).
- Any reference file over 100 lines starts with a `## Contents` list.
- Name files for their content (`error-codes.md`, not `doc2.md`); forward slashes in every path.
- Large catalogs: consolidate into a few JSON files, never one file per category. Uploads fail
  above roughly 200 files.

### Writing the body

- **Concise.** Claude is already capable; add only what it doesn't know. Cut every sentence
  that doesn't change behaviour.
- **Degrees of freedom match fragility.** Open tasks get guidance and heuristics; fragile
  sequences get exact commands ("run exactly this; add no flags").
- **One default, with an escape hatch**, not a menu of equal options.
- **Workflows** for multi-step tasks, with a copyable checklist; **feedback loops** for quality
  (validate → fix → repeat; proceed only when clean).
- **Concrete examples**: input/output pairs where style matters.
- **Consistent terminology**: one term per concept, used throughout.
- **No time-sensitive instructions** ("before August, use …"). Put superseded methods in an
  "Old patterns" section.
- **MCP tools by fully qualified name** (`ServerName:tool_name`).
- **Cite other skills by dated events and durable facts, never live state.** "Its July rebuild
  hit 241 files" stays true; "covers 7,370 functions" goes stale. Point at the other skill's
  own `VERSION`, catalog meta block or CHANGELOG for current numbers.
- **Name dependencies exactly** (`claris-filemaker-pro`, not "a FileMaker reference skill"),
  and name known look-alikes as non-sources. Generic phrasing gets substituted when a similar
  toolset shares the session.
- **Never name an unreleased or private-beta product** in a skill headed for a public repo;
  describe it generically until it ships.
- **No surprises**: nothing in the skill that someone reading only the description wouldn't
  expect.
- **Declare deliberate overlaps** between skills in a "Relationship to other skills" section in
  both, naming the maintained home of the shared rules and a maintenance trigger.

### Scripts

- Scripts handle their own errors with specific messages; they don't hand failures back to
  Claude to improvise.
- Explain every constant (why 30 seconds, why 3 retries).
- List required packages and how to install them; never assume they're present.
- Say whether Claude should **run** a script or **read** it as reference.
- Tools the maintainer runs to build or verify the skill live in `maintainer/`, not `scripts/`.
- Wording depends on where the skill runs (plain chat can't execute anything):
  [references/execution-surfaces.md](references/execution-surfaces.md).

## 5. Validate

Run the validator from this skill's folder against the skill being built:

```bash
python3 scripts/validate_skill.py /path/to/skill-folder
```

It checks the frontmatter limits, body length, reference depth and contents lists, VERSION and
plugin.json agreement, and file count, and prints each failure with the fix. Fix, re-run, and
continue only when it reports clean. Then work through the judgement items in
[references/validation-checklist.md](references/validation-checklist.md).

## 6–7. Test and iterate

Run every eval case on Haiku, Sonnet and Opus, plus the no-skill baseline, with a fresh
subagent per run (Claude Code). A skill that doesn't beat its baseline isn't earning its
context. Generalise each failure into a fix to the skill, not a patch for that one prompt, and
re-run. Then tune the description against 8–10 should-trigger and 8–10 near-miss prompts. Save
results as `evals/results-YYYY-MM-DD.md`. In Claude.ai chat there are no subagents: run the
cases yourself and skip the baseline. Full procedure:
[references/testing-and-evals.md](references/testing-and-evals.md).

## 8. Package and publish

GitHub repo, `VERSION`, tagged release, `plugin.json`, the `cadenceux` marketplace entry,
release `.zip` and `.skill` archives, and the rule for amending an unshipped version:
[references/packaging-and-release.md](references/packaging-and-release.md).

Build the release archives from a clean checkout of the tag, never a working folder, and run
`python3 scripts/validate_skill.py --archive <file>.zip` on each before attaching it: it fails
an archive missing `VERSION`, `CHANGELOG.md` or `README.md`, or carrying `.claude-plugin/`
(leave the manifest out and say why: the Claude app's skill upload rejects an archive with a
plugin manifest; the marketplace reads it from the repo).

Releases are export-only from here. This skill can produce the files and push to GitHub; it
can't install anything into Claude.ai. Say so rather than reporting a skill as "installed".

## Staleness checks and catalog accuracy

Skills that snapshot an external product need a drift signal that's been proven to move, a
documentation-freshness note, and counts re-derived from the vendor's source every release.
Read [references/verification-patterns.md](references/verification-patterns.md) before working
on any catalog or vendor skill.

## This skill's own version check

On the first skill-building request of a session, once:

1. Fetch `https://github.com/CadenceUX/cadenceux-skill-creator-skill/raw/main/VERSION`.
2. If it's newer than `metadata.version` above, open the first response with:
   > ⚠️ **Skill update available.** This is v[installed]; v[latest] is at
   > https://github.com/CadenceUX/cadenceux-skill-creator-skill/releases
3. If the fetch fails, skip silently. Don't repeat the notice in the same session.

## CadenceUX conventions

- `cadenceux-` prefix for brand and workflow skills; `claris-` for FileMaker reference skills.
- Australian English in everything user-facing. "CadenceUX" is one word.
- The SKILL.md `## Licence` section and the README both end with:
  `Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).`
- README install section: the `cadenceux` marketplace first, then the double-click `.skill`
  file (macOS), then the Customize → Skills zip upload.
- FileMaker skills assume the Claris Agentic Development Toolkit (ADT) may be installed: where
  ADT can read or change the file directly, defer to it rather than generating clipboard XML
  or copy-paste snippets.
- Every published skill carries a skill update self-check (the repo's `raw/main/VERSION`, once
  per session) that defers to `fmp-dev-orchestrator`'s stack check when that's installed.
- Preview programs: never publish preview version numbers (Claris ADT builds, preview FileMaker
  Pro builds) in skill files, changelogs, evals or release notes. Report them to the user from
  their own install only. The validator fails on an ADT version number.
- On every FileMaker skill release, update `versions.json` in `CadenceUX/cadenceux-skills`
  (the skill's new version; `tested_with` for public products only).

## Relationship to other skills

- **claris-filemaker-pro** — the reference implementation of these practices.
- **cadenceux-sonnet-craft** / **cadenceux-fable-mode** — how rigorously a session works; this
  skill owns what a good skill looks like. It defers to them and keeps no copy of their rules.
- **cadenceux-plugin-creator** — owns the plugin container: hooks, install verbs, marketplace
  mechanics. It defers here for any SKILL.md a plugin bundles; this skill routes enforcement
  asks there.

## Licence

This skill is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
