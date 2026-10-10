# cadenceux-skill-creator-skill

A [Claude skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for
building, updating and reviewing Claude skills to
[Anthropic's skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
with the packaging and publishing conventions CadenceUX uses for its Claris FileMaker skills.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).

---

## What it does

- **Evals first.** Turns failures observed without a skill into `evals/evals.json` cases
  (`must` / `must_not`), records a no-skill baseline, then writes the minimum skill that passes.
- **Progressive disclosure.** SKILL.md under 500 lines, reference files one level deep, a
  contents list at the top of any reference over 100 lines.
- **A validator script.** `scripts/validate_skill.py` checks frontmatter limits (name, reserved
  words, description length, XML tags, allowed keys), body length, reference depth and contents
  lists, version agreement across `VERSION`, frontmatter and `plugin.json`, eval count and file
  count, and prints the fix for each failure.
- **Testing across models.** Runs each case on Haiku, Sonnet and Opus against the baseline, and
  tunes the description against should-trigger and near-miss prompts.
- **Staleness checks** for skills that catalog a vendor's plugin, API or product, and rules for
  keeping "all N" counts honest.
- **Publishing.** GitHub repo and tagged release, `.claude-plugin/plugin.json`, the `cadenceux`
  plugin marketplace, `.zip` and `.skill` archives, and how to retire a skill cleanly.

The reference example of a skill built this way is
[claris-filemaker-pro](https://github.com/CadenceUX/claris-filemaker-pro-skill).

## Install

**Claude Code (plugin):** this repository is its own one-plugin marketplace.

```bash
claude plugin marketplace add https://github.com/CadenceUX/cadenceux-skill-creator-skill.git
claude plugin install cadenceux-skill-creator@cadenceux-skill-creator
```

**claude.ai and Cowork:** Customize → Plugins → Add marketplace from GitHub →
`CadenceUX/cadenceux-skill-creator-skill`.

**Claude desktop app (macOS):** download the `.skill` file from the
[latest release](https://github.com/CadenceUX/cadenceux-skill-creator-skill/releases) and
double-click it.

**Claude.ai in a browser:** Customize → Skills → upload the release `.zip`.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The workflow, frontmatter standard, writing rules |
| `references/frontmatter.md` | Limits, the CadenceUX standard, card rendering, versions |
| `references/testing-and-evals.md` | Evaluation-driven development, evals.json, model runs |
| `references/packaging-and-release.md` | GitHub, plugin.json, marketplace, archives, retiring |
| `references/execution-surfaces.md` | What scripts can do in chat, Code and the API |
| `references/validation-checklist.md` | The full checklist (mechanical and judgement items) |
| `references/verification-patterns.md` | Staleness checks and catalog accuracy |
| `scripts/validate_skill.py` | Standard-library validator |
| `evals/evals.json` | Test cases for this skill |

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use it, fork it, adapt it. Attribute it.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
