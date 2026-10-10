# Validation checklist

Run `scripts/validate_skill.py` first; it covers the mechanical items marked (auto). Then work
through the judgement items.

## Contents
- Frontmatter
- Structure
- Content
- Scripts
- Testing
- Publishing
- Catalog and vendor skills

## Frontmatter
- [ ] (auto) `name` ≤ 64 chars, `[a-z0-9-]`, no "anthropic" or "claude", no XML tags
- [ ] (auto) `description` non-empty, ≤ 1,024 chars, no XML tags
- [ ] (auto) Only allowed keys; `compatibility` ≤ 500 chars
- [ ] (auto) `license: CC-BY-4.0`; `metadata` has `author` and `version` only
- [ ] Description is third person, says what and when, uses the words users type, ends with a
      "Not for" clause, and carries no counts or versions
- [ ] `compatibility` claims only surfaces the skill was designed and tested for

## Structure
- [ ] (auto) SKILL.md body under 500 lines; exactly one SKILL.md
- [ ] (auto) Every reference file over 100 lines starts with `## Contents`
- [ ] (auto) Reference files are linked from SKILL.md and don't link on to further references
- [ ] (auto) No backslashes in paths
- [ ] Files named for their content; organised by domain or task

## Content
- [ ] Nothing Claude already knows; every section changes behaviour
- [ ] Freedom matches fragility; one default per choice
- [ ] Multi-step tasks have a copyable checklist; quality-critical steps have a feedback loop
- [ ] Concrete examples where output style matters
- [ ] One term per concept throughout
- [ ] No time-sensitive instructions; superseded methods in "Old patterns"
- [ ] MCP tools named `ServerName:tool_name`
- [ ] Other skills cited by dated events and durable facts, not live counts
- [ ] Dependencies named exactly, with known look-alikes named as non-sources
- [ ] No unreleased or private-beta product named in a public skill
- [ ] Anything that must be guaranteed was routed to a plugin hook, not promised here
- [ ] Deliberate overlaps declared in both skills' "Relationship to other skills"
- [ ] `## Licence` ends with the attribution line; Australian English; "CadenceUX" one word

## Scripts
- [ ] Errors handled in the script with specific messages
- [ ] Every constant explained
- [ ] Required packages listed with install commands
- [ ] Run-versus-read intent stated for each script
- [ ] Wording matches the execution surfaces (see execution-surfaces.md)
- [ ] Build and verification tools in `maintainer/`, not `scripts/`

## Testing
- [ ] At least three eval cases plus near-misses in `evals/evals.json`
- [ ] Baseline recorded; the skill beats it
- [ ] Run on Haiku, Sonnet and Opus; results file saved
- [ ] Description tuned against should-trigger and near-miss prompts

## Publishing
- [ ] (auto) `VERSION`, `metadata.version`, `plugin.json` version identical
- [ ] (auto) Under ~200 files
- [ ] CHANGELOG entry says what changed and how it was verified
- [ ] README: what it does, install (marketplace, `.skill`, zip), attribution line
- [ ] Shipped status checked before choosing bump or amend
- [ ] Marketplace, website, llms.txt and orchestrator updated if the skill set changed

## Catalog and vendor skills
- [ ] A version snapshot and a staleness check whose signal was proven to move
- [ ] Every "all N" count re-derived from the vendor's source this release
- [ ] No catalog entry links to a generic index page (the phantom-entry signature)
- [ ] Every syntax example checked against the catalog or live docs
- [ ] A router routes only to skills that exist
