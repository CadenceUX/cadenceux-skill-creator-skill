# Verification patterns — staleness checks & catalog accuracy

Extracted from SKILL.md v1.8 to keep the main file lean. Read this file whenever a skill
catalogs an external vendor/plugin/API, is published to GitHub, or is having its coverage
claims audited.

## Contents

1. **External reference & version-checking** — vendor/plugin release drift (passive and active
   patterns, required pieces) plus the documentation-freshness axis
2. **Skill's own version self-check** — watching the skill's own GitHub repo for newer releases
3. **Catalog accuracy** — the seven rules for coverage claims: count from the source, never
   from the previous version

---

## External reference & version-checking (required for plugin/vendor skills)

Any skill whose content is a **snapshot of something external that keeps shipping updates** —
a FileMaker plugin's function catalog, a vendor API, a product's changelog — goes stale the
moment the vendor releases something new. Build the staleness check in at creation time, not
as a retrofit. `claris-filemaker-pro` and `goya-be-plugin` both needed a follow-up release to
add this after the fact; don't repeat that for new skills.

This covers two genuinely different kinds of drift — design for both, they're not the same check:

- **Plugin/vendor release drift** — has the *plugin itself* shipped a newer version than this
  catalog was built against? Covered by the patterns below.
- **Documentation freshness** — has a *specific doc page* been edited since the catalog captured
  it, independent of whether the plugin's release version changed at all? See *Documentation
  freshness check* further down — this is a separate, third axis alongside this section and
  *Skill's own version self-check* below.

### Decide which check pattern fits

There are two patterns already proven in production, pick based on what the vendor exposes:

| Pattern | Use when | Example |
|---|---|---|
| **Passive (per-fetch)** | Individual doc pages carry their own version marker | `claris-filemaker-pro` — every Claris help page has an "Originated in version" section in the page body, compared on every live fetch |
| **Active (on-demand)** | The vendor has a releases page / changelog / API but individual pages don't self-report a version | `goya-be-plugin` — GitHub Releases API checked only when asked, or before a catalog rebuild |

Most plugin vendors (GitHub-hosted, or with a simple "latest release" page) fit the active
pattern. Use the passive pattern only when per-page version metadata is actually there —
don't fetch a whole release history just to answer one function lookup.

**Validate that the chosen signal actually moves before documenting it.** A field that looks
like a version marker may track something else entirely. Confirmed 2026-07-04:
`claris-filemaker-pro` originally compared each Claris page's YAML frontmatter `version:` field
against its stored FM version — but that frontmatter tracks the *documentation build*, not the
FileMaker release (pages for FM-26-originated features still returned `version: 22 / 2025`), so
the documented check could never fire. The reliable signal was the page body's "Originated in
version" section. The design-time test that catches this: fetch a page for a feature you *know*
shipped in the newest release and confirm the signal reflects that release. If it doesn't, the
signal is wrong no matter how plausible it looks.

### Required pieces

1. **A frontmatter/metadata field recording the snapshot version**, e.g. `plugin_version_at_build`,
   `last_known_fm_version`, or similar — name it for what it's actually tracking. Put the same
   value in the reference file's own `meta` block if there is one, so the catalog is
   self-describing even if SKILL.md frontmatter is stripped on install.
2. **A documented check procedure** in the SKILL.md body — the exact URL/API call, how to find
   the *release page* (not a beta/pre-release tag — filter those out explicitly, vendors are
   inconsistent about flagging them correctly), and how to compare against the stored version.
3. **A standard advisory message**, not a blocker:
   > ⚠️ **Skill version drift detected** — the latest [vendor] release is [X], but this skill's
   > catalog was built against [Y]. New or changed functions since then won't be reflected here.
   > Consider [rebuild instruction] before relying on anything not already in this catalog.
4. **A trigger condition for running the check** — don't run it on every single lookup if it
   requires a network call per use; run it when the user asks if the skill is current, asks
   about something that seems missing, mentions "latest"/"newest", or before recommending a
   catalog rebuild.
5. **Still answer from the local catalog regardless** — drift is advisory. A newer plugin
   version existing doesn't make the local data wrong, just possibly incomplete.

### Where to point the active-pattern check

Identify the vendor's actual *release* page during intent capture, not the marketing/download
page — for GitHub-hosted plugins that's the Releases API
(`https://api.github.com/repos/{owner}/{repo}/releases`), for others it may be a changelog page
or RSS feed. Confirm with Developer or by inspection which one the vendor actually keeps current;
download pages often lag the real changelog.

### Documentation freshness check (a third, separate axis)

A function's doc page can be edited — clarified, corrected, expanded — without the plugin's
release version changing at all. That's invisible to both the plugin-release check above and the
skill's-own-version self-check; it needs its own signal, found per-vendor since there's no
universal one:

| Signal available | Use when | Example |
|---|---|---|
| Per-page version marker | Vendor's doc page states which version introduced/last-touched it | `claris-filemaker-pro` — "Originated in version" body section (passive pattern above); `monkeybread-mbs-plugin` — page text has a "Created [date], last changed [date]" line |
| Git commit history for the doc file | Docs live in a GitHub repo with no embedded version/date marker on the page itself | `goya-be-plugin` — `GET /repos/{owner}/{repo}/commits?path={doc-file-path}&per_page=1`, read `commit.author.date` |

**Don't claim precision you don't have.** None of these catalogs store a per-function "last
checked" timestamp, so there's no exact stored baseline to diff a fetched date against. Treat
whatever signal you find as **informational context to surface to the user** ("this page was
last edited on [date]" / "this function was last documented in version [X]") rather than a firm
drift flag like the plugin-release check above. Only do this on-demand — when the user asks if
something's current, or local catalog details seem to disagree with observed behaviour — never as
a background check on every routine lookup.

---

## Skill's own version self-check (required when a skill is published to GitHub)

This is a different check from *External reference & version-checking* above in this file — that one watches
a third-party vendor's plugin/API for drift. This one watches the **skill's own GitHub repo** for
a newer release than what's currently installed, so Developer finds out a skill update exists
without having to remember to check. `claris-filemaker-pro` already does this; bring any new
skill that gets a GitHub repo up to the same pattern, don't leave it Claude.ai-only.

### Required pieces

1. **A `VERSION` file at the skill folder root** — a bare version string and nothing else (e.g.
   `1.9`), no markdown, no key. This is what the self-check fetches and compares against; keep it
   in lock-step with `metadata.version` and the latest CHANGELOG.md entry on every release.
2. **A documented self-check procedure** in the SKILL.md body:
   1. At the start of each session, on the first on-topic question, fetch
      `https://github.com/{owner}/{repo}/raw/main/VERSION` (substitute the skill's actual repo).
   2. Parse the returned string as the latest available version.
   3. Compare with this skill's installed version (the value baked into this SKILL.md at release
      time — keep it current).
   4. If latest > installed, prepend this notice to the first response:
      > ⚠️ **Skill update available**
      > This skill is v[installed]. v[latest] is available at
      > https://github.com/{owner}/{repo}/releases
      > Update your local skill files to get the latest coverage.
   5. Don't repeat the notice again in the same session.
   6. If the fetch fails or returns an unexpected value, skip silently — never surface the error
      or block the user's actual question.

Only add this section to a skill once it actually has a GitHub repo to check — don't fetch a URL
that doesn't exist yet for a skill that's only ever been distributed as a `.zip`/`.skill` file.

---

## Catalog accuracy — count from the source, never from the previous version

Hard-won 2026-07-04: `claris-filemaker-pro` shipped multiple releases claiming "all 165 script
steps" while actually missing **58 real steps** and carrying **8 phantom entries** (step names
that don't exist in FileMaker, or misnamed real steps). The error survived several review passes
because each release inherited the count from the one before instead of re-deriving it. Rules
that would have caught it years earlier:

1. **Never inherit a coverage claim.** Any "all N functions/steps" statement gets re-derived
   from the vendor's authoritative source at every rebuild — not carried forward, not adjusted
   by "we added 3 so now it's N+3".
2. **Enumerate by page metadata, not title heuristics.** The definitive method when the vendor
   has a machine-readable sitemap (Claris publishes `llms-full.txt`): fetch every page and
   classify by its own metadata (Claris pages carry `topic_type: script-step-reference` /
   `function-reference`). A title-prefix heuristic ("steps start with Set/Go to/Open…") missed
   8 of the 58 gaps (AVPlayer Play, Dial Phone, Execute SQL…); the exhaustive metadata sweep of
   all 1,104 pages found every one and proved the corrected catalog exact (215 ↔ 215, zero
   drift either way). With code execution this sweep is a couple of minutes of parallel fetches.
3. **Grep for phantom entries.** A catalog entry whose `doc_url` points at a generic index or
   reference page instead of a per-item page is a red flag that the item was guessed, not
   sourced. All 8 phantoms in the claris catalog shared this signature.
4. **Cross-check against an independent catalog when one exists** (a community repo, another
   vendor mirror). Differences in *either* direction are leads — but verify every lead against
   the vendor's own docs before acting, because third-party catalogs have their own parser
   errors (the one checked that day misfiled three script steps as functions and listed a
   conceptual page as a step). Never copy from the third party; use it only to find where to
   look.
5. **Sweep the whole ecosystem for the stale fact.** When a count or claim is corrected in one
   skill, grep every other skill in the family for the old value — `fmp-dev-orchestrator` and
   `fmp-dev-full-script` (since retired) both quoted the wrong step count (and full-script quoted a *different*
   wrong count, "225+", that matched no source at all).
6. **Concrete syntax examples in pattern skills are catalog claims too.** A boilerplate/rules
   skill that shows worked examples (like `fmp-dev-gate`'s AI script pattern) must have every
   example verified against the reference catalog or live docs — that example used three
   invented parameters on real script steps and survived review because it *looked* plausible.
   Validate examples the same way as catalog entries: check each named option against the
   authoritative syntax.
7. **Routing tables only route to skills that exist.** A directory/orchestrator skill must be
   checked against the actually-installed skill set — `fmp-dev-orchestrator` routed seven topics
   to a `claris-help` skill that had never been built. When a topic has no dedicated skill, say
   so and point at the live docs instead of inventing a skill name. Re-check the table whenever
   a skill is added or retired.

