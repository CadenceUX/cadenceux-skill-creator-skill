# CHANGELOG — cadenceux-skill-creator

## [2.1.0] — 2026-10-11

### Added

- **Validator: skill update self-check.** Warns when a published skill (one with a `VERSION`
  file) has no `raw/main/VERSION` self-check (or, for the orchestrator, its stack check).
- **Validator: preview version numbers.** Fails when a file names a Claris ADT version number;
  ADT is in Claris's preview programs. Tested against a planted line.
- Conventions: every published skill carries the self-check and defers to
  `fmp-dev-orchestrator`'s stack check; preview version numbers are never published; each
  FileMaker release updates `versions.json` in cadenceux-skills.
- Release checklist: `versions.json` and the preview-version check. New eval case:
  preview-versions.

### Verified

- Validator run on all nine CadenceUX skills: clean on both new checks.

## [2.0.0] — 2026-10-11

Rebuilt against Anthropic's skill authoring best practices
(platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) and aligned with
`claris-filemaker-pro` v2.1.0, the CadenceUX reference implementation. First public release on
GitHub (github.com/CadenceUX/cadenceux-skill-creator-skill).

### How this release was verified

- Every item of Anthropic's "Checklist for effective Skills" mapped to a section of SKILL.md,
  `references/validation-checklist.md` or `scripts/validate_skill.py`.
- `scripts/validate_skill.py` run against this skill (clean) and against every other CadenceUX
  skill updated in the same session.
- Five eval cases plus three near-misses in `evals/evals.json`.

### Changed

- **SKILL.md cut from 761 to under 250 lines.** Detail moved into five new reference files,
  each linked directly from SKILL.md: `frontmatter.md`, `testing-and-evals.md`,
  `packaging-and-release.md`, `execution-surfaces.md`, `validation-checklist.md`.
- **Frontmatter standard now matches `claris-filemaker-pro` v2.1.0:** `name` and `description`
  first, `>-` folded values, `license: CC-BY-4.0`, `metadata` with `author` and `version` only,
  three-part semantic versions. Replaces the v1.x `compatibility`-first order and the
  "Built and maintained" metadata row.
- **Description rewritten in the third person** with a "Use when" and a "Not for" clause.
- **Workflow is a copyable checklist** with a validation feedback loop.
- Reference files over 100 lines need a contents list at the top of the file (was: 300+ lines,
  with the list in SKILL.md).

### Added

- **Evals first:** write 3+ cases from observed failures and record a no-skill baseline before
  drafting; run on Haiku, Sonnet and Opus; save dated results.
- **`scripts/validate_skill.py`:** the mechanical checks, with a fix printed for each failure.
- Anthropic practices that were missing: references one level deep, reserved words in `name`,
  no XML tags, degrees of freedom, one default rather than a menu, consistent terminology,
  "Old patterns" for superseded methods, MCP tools by fully qualified name, script rules (handle
  errors, explain constants, list packages, run-versus-read).
- `.claude-plugin/plugin.json`, the `maintainer/` folder convention, retiring a skill (archive,
  don't delete), and the rule that FileMaker skills defer to the Claris Agentic Development
  Toolkit (ADT) rather than generating clipboard XML.

### Removed

- Model-tier names that aren't public, and references to the retired `agentic-gate` and
  `fmp-dev-full-script` skills as live examples (historical incident notes remain in this
  changelog).

## v1.13 — 2026-07-17 (updated 2026-07-17, pre-release)

Lessons from the session that built `agentic-gate` (CadenceUX's first published Claude Code
plugin) and its companion skill `cadenceux-plugin-creator` (v1.0, same day):

**Pre-release update (same day, unshipped — amended in place):** the dependency-naming
principle's worked example originally named a vendor plugin currently in private beta —
exactly the kind of leak a public repo can't carry. Example rephrased generically, and the
principle itself gained the embargo clause: unreleased/private-beta products are never named
in public-bound skills, even in incident citations; describe generically until they ship.

- **New writing principle + validation checklist item: name skill dependencies exactly, never
  generically.** Motivated by a confirmed same-day failure: `fmp-dev-full-script`'s generic
  "use a dedicated FileMaker script-XML reference skill" phrasing let a different vendor's
  bundled catalog match as the source in a session where both toolsets were loaded — a full
  generation run was built from the wrong reference and had to be redone. Exact names (plus
  naming known look-alikes as non-sources) remove the ambiguity; enforcement of the boundary
  itself is hook territory (`agentic-gate`).
- **Capturing intent gains question 7:** if any part of the ask needs a *guarantee* ("always
  block", "never allow") rather than advice, a skill can't promise it — route that part to
  `cadenceux-plugin-creator` (hooks, packaged as plugins) before building. Matching validation
  checklist item added.
- **Relationship to other skills: added `cadenceux-plugin-creator`** (two-way deferral: it owns
  the plugin container, this skill owns SKILL.md authoring including skills bundled inside
  plugins) **and declared the planned `cadenceux-hook-creator` split** — hook mechanics (event
  protocol, engine patterns, standalone install/testing) will move out of plugin-creator into
  a dedicated skill when the first standalone hook or second protocol-detail need arrives.
  Declared in both skills now per this skill's own declared-overlap convention.

## v1.12 — 2026-07-11 (updated 2026-07-12, pre-release)

Rolled in the new sibling skill `cadenceux-sonnet-craft` (v1.0) and `cadenceux-fable-mode`'s
v1.2 cross-reference release, both built 2026-07-11. Retires v1.11's inline duplication in
favour of pointing at the now-maintained source.

**2026-07-12 pre-release correction (Fable 5 review pass):** the Quick validation checklist
bullet for Sonnet-heavy-work discipline still named `cadenceux-fable-mode` as the layer to
apply — inconsistent with the rewritten *Before you start* section, which points to
`cadenceux-sonnet-craft` first. The bullet now matches. The same review verified the declared
five-rule shared core cited here matches both sibling skills' own Relationship sections
word-for-word.

- **"Before you start" Sonnet-discipline block rewritten.** `cadenceux-sonnet-craft` — the new
  domain-general Fable-tier craft layer, which names skill-building as an explicit covered
  domain — is now the maintained home of the five principles this section spelled out inline
  since v1.11 (victory condition, evidence over "should work", two-retry cap, diagnosis-vs-
  action, no scope creep). Points there first, with `cadenceux-fable-mode` demoted to "load
  this too if the skill being built is itself FileMaker-specific" rather than the default
  target. The condensed five-principle fallback stays for sessions where sonnet-craft isn't
  installed.
- **New two-signal model-check note in "Before you start"**, sourced from a confirmed failure
  mode in `cadenceux-fable-mode` v1.1's build session: the "You are powered by" system-prompt
  line goes stale after a mid-session `/model` switch, and the most recent `/model` stdout has
  to win over it. Previously this skill's own environment check only said "note the model" with
  no guidance on which signal to trust after a switch.
- **New writing principle: declare deliberate cross-skill overlap, don't let it happen
  silently.** Generalises the pattern `cadenceux-sonnet-craft` and `cadenceux-fable-mode`
  introduced for each other on 2026-07-11 (a five-rule declared shared core, each skill's own
  Relationship section naming the other, a maintenance-trigger rule) into a reusable authoring
  convention for any future domain-general/domain-specific skill pair. Added as the reference
  example in "CadenceUX skill conventions" and as a new Quick validation checklist item.
- **New "Relationship to other skills" section** (this skill didn't have one before): documents
  that this skill defers to, rather than duplicates, `cadenceux-sonnet-craft` and
  `cadenceux-fable-mode` — the inverse of a declared shared core, named explicitly so a future
  editor doesn't accidentally re-inline what's now owned elsewhere.
- Version self-check baseline updated to `"1.12"`.

No changes to platform limits, packaging rules, the testing loop, or verification-patterns.md.

## v1.11 — 2026-07-07

Cross-referenced `cadenceux-fable-mode` as a sub-instruction for heavy skill-building work done
on Sonnet.

- **New guidance in "Before you start"**: when Developer chooses to proceed on Sonnet for heavy
  work (a reference-catalog build, an accuracy audit) rather than switching model — a real
  choice, made building `beezwax-bbox-plugin` on 2026-07-07 — layer on `cadenceux-fable-mode`'s
  discipline. That skill's own trigger is scoped to FileMaker/fmp-dev work in this workspace, so
  it won't fire on its own for skill-building, but its underlying checklist (victory condition
  before planning, evidence over "should work" via three-tier Static/Functional/Negative
  verification, same-error retries capped at two, diagnosis kept separate from action, no
  unrequested scope creep) is a procedural fix for exactly Sonnet's characteristic failure mode
  and generalizes directly to a catalog build. Documented as five translated principles rather
  than a blanket "go read that skill" pointer, since `cadenceux-fable-mode`'s own examples are
  all FileMaker-HTTP-bridge-specific and don't map 1:1 without translation.
- **New validation-checklist bullet** verifying this discipline was actually applied (not just
  acknowledged) when heavy work ran on Sonnet.
- This is a mitigation for when Developer has already decided to proceed on Sonnet, not a
  substitute for the existing model-recommendation table — a factual error is still more likely
  to survive review on Sonnet than on Fable/Opus.

## v1.10 — 2026-07-05

Cross-skill examples made maintenance-free — cite events, not live state.

- **New writing principle: cite other skills by dated events and durable design facts, never
  by live state.** The file-count section described `monkeybread-mbs-plugin` as "7,370
  functions across 233 components" — true when written, false the day that skill's v1.3
  rebuild shipped (and nothing forces this file to be updated in step). Live counts,
  versions, and surface claims about other skills now point at the other skill's own source
  of truth (`VERSION`, `references/index.json` meta, CHANGELOG) instead of copying values.
- Applied throughout this skill's own text: the `monkeybread-mbs-plugin` file-count example
  now cites the durable event ("its v1.2 rebuild hit 241 files") without live counts; the
  `metadata.version` baseline no longer quotes `claris-filemaker-pro`'s current version; the
  compatibility and Chat-vs-Code sections describe reference-lookup skills as a category
  instead of asserting which named skills are chat-only (the MBS skill's own frontmatter
  already contradicted that list); README updated to match.
- No process changes — the creation loop, packaging, and validation checklist are unchanged
  beyond the new principle's checklist-adjacent guidance.

## v1.9 — 2026-07-05

The `.skill` double-click install path, documented and made a convention for every generated
skill.

- **New Release packaging subsection — "The `.skill` copy is the double-click install path".**
  The `.skill` file is the release zip with the extension renamed (renaming in Finder is
  equivalent to the packaging `cp`); the Claude desktop app registers `.skill` as its own
  document type, so double-clicking opens the install flow directly — the simplest install
  method. Platform status verified 2026-07-05: **macOS confirmed** (Claude.app's `Info.plist`
  declares the `skill` extension as a "Skill File" document type); **Windows unverified** (no
  public documentation confirms the association; word instructions as "macOS" until tested);
  **browser not applicable** (Customize → Skills zip upload remains the only path — the
  Anthropic Help Center documents only that method).
- **New convention for every skill this creator produces**: README.md installation sections
  lead with the double-click `.skill` method (with the macOS/Windows caveat) and keep the
  Customize → Skills zip upload as the documented fallback. Added to the CadenceUX skill
  conventions and the Quick validation checklist.
- This skill's own README updated to follow the new convention, and its stale version line
  (still reading v1.4) corrected to match the release.

## v1.8 — 2026-07-04

Restructure for progressive disclosure — no content changes beyond pointer text.

- **New `references/verification-patterns.md`** — the three staleness-check sections (External
  reference & version-checking with the documentation-freshness axis, and the generic Skill's
  own version self-check pattern) plus the Catalog accuracy section moved out of SKILL.md into
  one reference file with a contents list. SKILL.md v1.7 had grown to 764 lines, half again
  over the ~500-line target this skill itself prescribes; it's now ~620 with a compact pointer
  section ("Staleness checks & catalog accuracy") summarising when to read the reference file.
- This skill's **own operational self-check stays in SKILL.md** (it must run at session start
  without a reference-file hop); only the generic pattern for other skills moved.
- All cross-references updated to point at the reference file; README file list updated (the
  skill is no longer references-free).

## v1.7 — 2026-07-04 (updated same day, pre-release)

Lessons from the four-skill accuracy audit (claris-filemaker-pro, fmp-dev-gate,
fmp-dev-full-script, fmp-dev-orchestrator) folded into the skill creator's own logic.

### Added in same-day update

- **New opening section: Before you start — environment check.** Run first, every session:
  note the current model and surface, compare against guidance, flag mismatches to Developer
  before heavy work. Model guidance: most capable model available (Fable/Mythos tier, else
  Opus) for reference-catalog builds/audits and accuracy work where factual errors ship inside
  reference material; Sonnet is fine for routine drafting and packaging where the checklist is
  the guardrail. Surface guidance points to the chat-vs-Code subsection.
- **Shipped-status check added to Amending an unshipped version** — before choosing bump vs
  amend, fetch the repo's `VERSION` (and releases) and compare with the working copy, rather
  than assuming or relying on memory; a repo check can't see Claude.ai uploads, so upload state
  is still confirmed with Developer.
- **Adopted from Anthropic's official skill-creator** (`anthropics/skills` repo, reviewed
  2026-07-04; their skill carries no version number — frontmatter is name + description only):
  persistent test cases in `evals/evals.json`; with-skill vs baseline comparison runs when
  testing from Claude Code (plus a pointer to their bundled `run_eval.py`, `quick_validate.py`,
  `package_skill.py`, `improve_description.py` tooling); the automated `claude -p` description
  loop noted as available in Code; the per-domain `references/` organisation pattern; and the
  Principle of Lack of Surprise. Their eval-viewer/benchmarking pipeline was reviewed and not
  adopted — it assumes their bundled Python tooling and subagent grading, which doesn't fit
  this skill's manual chat workflow.
- Three new checklist items: environment check ran, shipped status checked not assumed,
  evals.json saved with baseline comparison where Code is available.

- **New section: Catalog accuracy — count from the source, never from the previous version.**
  claris-filemaker-pro shipped multiple releases claiming "all 165 script steps" while missing
  58 real steps and carrying 8 phantom entries. Seven rules added: re-derive every coverage
  claim per release; enumerate by page metadata (topic_type) rather than title heuristics —
  heuristics missed 8 of the 58 gaps, the exhaustive sweep of all 1,104 sitemap pages proved
  the corrected catalog exact; grep for phantom entries (doc_url pointing at a generic index
  page); cross-check independent third-party catalogs as lead-finders but verify every lead
  against vendor docs (the third party had its own misfiled entries); sweep the whole skill
  ecosystem for a corrected fact; verify concrete syntax examples in pattern skills against the
  reference catalog (fmp-dev-gate's AI example used three invented parameters); and routing
  tables may only route to skills that actually exist.
- **New section: Amending an unshipped version (no bump)** — fix-in-place rules for versions
  that haven't shipped: annotate the CHANGELOG entry "(updated YYYY-MM-DD, pre-release)",
  rebuild same-stem archives (delete before zip — zip appends into existing archives), and flag
  stale older archives in the release folder.
- **Staleness-check pattern corrected and hardened.** The passive-pattern example wrongly cited
  Claris page frontmatter `version:` — verified 2026-07-04 that field tracks the documentation
  build, not the FileMaker release (FM-26 pages still say version 22/2025), so a check built on
  it can never fire. Example corrected to the "Originated in version" body section, plus a new
  rule: validate that the chosen drift signal actually moves, by fetching a page for a feature
  known to be in the newest release before documenting the procedure.
- **New subsection: Which surface to run this skill creator itself from.** Mechanical/verifiable
  work (catalog sweeps, char counts, ecosystem greps, packaging) belongs in Claude Code;
  UI-observable checks (rendered frontmatter card, real trigger behaviour, `/mnt/skills/user/`
  installed copies, `present_files` delivery) are chat-only. Default: build and verify from
  Code, do final card/trigger checks in Claude.ai after upload.
- **Six new validation-checklist items** covering the drift-signal live test, coverage-claim
  re-derivation, phantom doc_url check, syntax-example verification, and router-target
  existence.

## v1.6 — 2026-06-30

Documented confirmed card-rendering behaviour based on live testing of `goya-be-plugin` v1.2.

- **Card rendering is fully documented** — every `metadata` key renders as its own labeled row;
  quoted YAML keys with spaces (e.g. `"Built and maintained"`) produce clean labels; metadata
  values are plain text only (markdown links render as raw characters, not clickable links);
  `compatibility` must be a plain scalar, not a `|` block literal (block literals collapse to
  one line and add a trailing newline that causes rendering issues); extra metadata keys produce
  ugly underscore-labeled rows and should be avoided.
- **Standard CadenceUX card pattern** documented: `compatibility` (platform only) + `"Built and maintained": "Darrin Southern from CadenceUX"` + `version` — produces three clean, correctly labeled rows.
- **Frontmatter template** updated to show the `"Built and maintained"` metadata key.
- **Validation checklist** updated: `compatibility` plain-scalar requirement explicit; new items
  for `"Built and maintained"` metadata key presence and the no-extra-metadata-keys rule.
- This skill's own frontmatter updated to v1.6 with the `"Built and maintained"` key applied.

## v1.5 — 2026-06-30

- **Standard attribution line added** — every skill produced by this creator must now include
  `Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).`
  at the end of the SKILL.md `## Licence` section and in README.md after the opening
  description. Added to the *CadenceUX skill conventions* section and the *Quick validation
  checklist* (two new items: SKILL.md licence attribution present, README.md attribution present).
- **"CadenceUX" is one word** — convention and checklist now explicitly prohibit "Cadence UX"
  (with space). Fixed the one instance of "Cadence UX" that existed in this skill's README.md.
- This skill's own SKILL.md and README.md updated to include the attribution line.

## v1.4 — 2026-06-25

- **File count limit section now cites `monkeybread-mbs-plugin` by name** as the worked example —
  it has the highest function count of any of Developer's reference skills (7,370 functions,
  233 components) and is what actually hit the ~200-file ceiling in practice (241 files on a
  naive one-file-per-component build, fixed by bin-packing into 20 group files). Previously the
  section only described the pattern generically; now it points to the real precedent.
- **New "Skill's own version self-check" section** — a `VERSION` file at the skill folder root
  plus a session-start fetch/compare against the GitHub repo's `VERSION`, for any skill published
  to its own repo (`claris-filemaker-pro` already does this; this codifies the pattern for future
  skills instead of leaving each one to reinvent it). This is distinct from the existing
  *External reference & version-checking* section, which watches a third-party vendor's plugin —
  this one watches the skill's own release history. Added to *Capturing intent* (new question 6),
  the skill-folder anatomy diagram, the release-zip contents diagram, the packaging steps (bump
  `VERSION` alongside `metadata.version` and CHANGELOG), and the validation checklist.

## v1.3 — 2026-06-25

Prompted by the `monkeybread-mbs-plugin` v1.2 fix release: the zip got saved straight to `/tmp`
without asking, and only a `.zip` was produced until Developer asked for a `.skill` copy separately.
Both are now standard, not on-request.

- **Corrected the meaning of "install" — it was never actually happening.** The earlier
  "export-and-install" step assumed editing the working folder under
  `local-agent-mode-sessions/.../skills/<skill-name>/` satisfied "install," but Developer
  clarified install means the skill shows as updated on Claude's Customize → Plugins/Skills page
  — a different, app-internal location this skill creator has no write access to (confirmed by
  searching for a separate on-disk skills directory and finding none). Every release is now
  correctly described as **export-only**: this skill creator produces the `.zip`/`.skill` files
  and edits the working copy, but the actual Customize → Plugins update is always a manual step
  for Developer. Removed the false "export-and-install" choice from release packaging and the
  validation checklist.
- **Frontmatter key order is now `compatibility`, `metadata`, `name`, `description`** —
  compatibility before version (which lives inside `metadata`), in addition to metadata staying
  before name/description. Updated the frontmatter template, validation checklist, and this
  skill's own frontmatter to match.
- **`compatibility` now lists all three surfaces this skill actually runs in**:
  `Claude.ai, Claude Chat, Claude Code` — it had only said `Claude.ai`, which understated where
  this skill creator is genuinely used (it's been driven from Claude Code throughout this
  session). Also dropped the stale "Optimised for Claude.ai (no subagents or CLI)" line from the
  description, which directly contradicted the new compatibility claim. Added a checklist item
  warning against listing a surface a skill hasn't actually been designed/tested for — this isn't
  a default to apply to every skill, most of Developer's reference-lookup skills are genuinely
  Claude.ai-chat-only and should keep a single value.
- **Fixed broken Compatibility/Version rendering at the root, not with a workaround.** An earlier
  fix in this same v1.3 cycle hand-wrote a "Compatibility / Version" text block into the SKILL.md
  body to mimic the platform's display — but the real cause was that this skill's frontmatter was
  missing the top-level `compatibility` field (so Claude.ai's auto-rendered card never showed) and
  used a single long single-line `description:` scalar, which is fragile: an embedded colon can
  break YAML parsing and dump the raw, unparsed frontmatter as visible body text — exactly what
  Developer saw. Fixed by adding `compatibility: Claude.ai` to frontmatter, converting `description`
  to a `|` block-literal, and removing the now-redundant hand-written body block entirely — the
  platform renders the card automatically from frontmatter when both fields are present and valid.
  Updated the skill-creator's own instructions, frontmatter template, Platform limits table, and
  validation checklist so future skills get this right from the start instead of needing this same
  fix later.
- **`metadata` now comes first in frontmatter**, before `name` and `description`. Updated the
  frontmatter template example to match.
- **Release packaging now always asks Developer where to save** both files before writing anywhere
  persistent — no more silent default to a temp directory, and no assuming a previously-used
  folder is still the right one without confirming.
- **Every release now produces a `.skill`-extension copy alongside the `.zip`** (identical bytes,
  same stem) automatically — not just when explicitly requested.
- **New "Chat vs Code execution context" section**: documents the four surfaces a skill can run
  on (Claude.ai chat with code execution off, Claude.ai chat with it on, Claude Code/SDK, API
  with the code-execution tool) and what each means for whether a bundled `scripts/` file is
  something Claude can actually run versus documentation for a human to run elsewhere. Adds
  guidance on writing SKILL.md wording conditionally when a skill might land in either context.
- **Quick validation checklist** gained three items: `.skill` copy present, save destination
  confirmed with Developer, and `scripts/` wording matches the intended execution surface.
- **All `.zip`-only wording now also covers the `.skill` copy** — section headings, the release
  packaging intro, and the version-naming/checklist lines were updated so every mention of the
  release archive accounts for both extensions rather than just the `.zip`.
- **Save-destination step now checks for an existing local skills-release folder first** (e.g. a
  `Skill Masters` folder already on the Desktop, or wherever a prior release in this session was
  saved) and offers it as the first option — instead of asking blind every time or assuming one
  environment's folder is the standing default everywhere this skill creator runs.
- **New step 0 in release packaging**: asks Developer up front whether a build should be
  export-only (zip/.skill for manual install elsewhere) or export-and-install (also apply the
  update to whatever the active local skill installation is) — decided before packaging starts
  rather than assumed after the fact.
- **New required "Compatibility / Version" body block** — every SKILL.md must now open with a
  plain `Compatibility` / `Version` block right after the H1 title, mirroring how Claude.ai
  surfaces this metadata for an installed skill, kept in sync with `metadata.version` and the
  CHANGELOG. Added to this skill's own SKILL.md and to the validation checklist.

## v1.2 — 2026-06-25

Added the zip file-count limit to Platform limits, prompted by building
`monkeybread-mbs-plugin` (a 233-component, per-component-JSON reference catalog) and
finding its release zip landed at 241 files.

- **New "File count limit" subsection** under Platform limits: a community-reported
  (not Anthropic-documented) ~200-file ceiling on skill zip uploads — checked the
  official Agent Skills docs and the Claude Help Center "Creating custom Skills"
  article directly; neither states a file-count or zip-size number, so this is flagged
  as a practical/observed limit rather than a confirmed hard one, distinct from the
  documented `name`/`description`/`compatibility` limits in the main table.
- Explains *why* `goya-be-plugin` and `claris-filemaker-pro` consolidate their entire
  catalog into one or two JSON files: it's not just tidiness, it avoids this ceiling.
  Recommends grouped/consolidated reference files over one-file-per-category for any
  large catalog skill going forward.
- **Quick validation checklist** gained an `unzip -l | tail -1` file-count check before
  release.

## v1.1 — 2026-06-23

Codified the version-drift / staleness-check pattern as a required step for any new skill that
catalogs an external plugin, vendor product, or API — instead of letting each skill reinvent it
after the fact.

- **New "External reference & version-checking" section**: documents the two proven patterns
  already in production (`claris-filemaker-pro`'s passive per-fetch frontmatter check,
  `goya-be-plugin`'s active on-demand GitHub Releases API check), when to use each, the required
  metadata field, the standard advisory message format, and the rule that drift is advisory —
  never a blocker on answering from the local catalog.
- **Capturing intent** now asks whether the skill catalogs something external that can change
  underneath it, so the staleness check is designed in at v1.0 rather than bolted on in a later
  release (both `claris-filemaker-pro` and `goya-be-plugin` needed a follow-up version to add
  this retroactively).
- **Quick validation checklist** gained an item gating release on the version-check being present
  for any plugin/vendor/API skill.
- Added this CHANGELOG.md and README.md — the skill's own packaging rules require both on every
  release, and this skill had shipped without them.

## v1.0 — 2026-06-23

Initial release.

- Full skill-creation loop: capture intent, write SKILL.md, test, iterate, optimise description
- Platform limits table (name/description/compatibility length, frontmatter keys, one SKILL.md)
- Release packaging rules: always ship a complete zip, never a partial diff
- CadenceUX skill conventions (`cadenceux-` vs `claris-` prefixes)
