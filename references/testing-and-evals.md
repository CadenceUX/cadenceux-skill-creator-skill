# Testing and evals

## Contents
- Evaluation-driven development
- evals.json format
- Running evals (Claude Code)
- Running evals (Claude.ai chat)
- Grading and the results file
- Description tuning
- Observing real use

## Evaluation-driven development

Create evals before writing much of the skill:

1. **Find the gaps.** Run representative tasks with no skill loaded and note each concrete
   failure (wrong value, invented parameter, missed step).
2. **Write at least three cases** that test those gaps, plus near-misses that must not trigger
   the skill.
3. **Record the baseline** score without the skill.
4. **Write the minimum skill** that closes the gaps.
5. **Run, compare with the baseline, refine.**

A case that passes without the skill is not testing anything the skill adds.

## evals.json format

The CadenceUX format (as used in `claris-filemaker-pro`):

```json
{
  "skill": "skill-name",
  "version": "1.0.0",
  "notes": "Grade each answer against must / must_not.",
  "cases": [
    {
      "id": "short-id",
      "mode": "any",
      "prompt": "The user's request, exactly as typed.",
      "must": ["Fact or behaviour a correct answer must contain"],
      "must_not": ["An error earlier versions or the baseline made"]
    }
  ],
  "near_misses": [
    {
      "id": "short-id",
      "prompt": "An adjacent request that should NOT use this skill.",
      "expect": "not triggered"
    }
  ]
}
```

`must_not` entries come from real failures. Use `mode` when the skill behaves differently with
an optional dependency (for example `adt` versus `standalone`).

## Running evals (Claude Code)

For every case, run a fresh subagent per configuration so no context leaks between runs:

- **Baseline:** no skill, same prompt.
- **Haiku, Sonnet, Opus:** skill loaded (pass the skill's path and tell the agent to read
  SKILL.md and follow it).

Ask each agent to answer only the prompt. Grade the answers yourself against `must` and
`must_not`. Haiku shows whether the skill gives enough guidance; Opus shows whether it
over-explains. Anthropic's skill-creator tooling (`github.com/anthropics/skills`,
`skills/skill-creator/`) includes runnable eval and description-tuning scripts worth using here.

## Running evals (Claude.ai chat)

No subagents. Read SKILL.md as a fresh instance would and work each case, then show the results
to the developer. A baseline isn't meaningful when the author is also the runner.

## Grading and the results file

Save `evals/results-YYYY-MM-DD.md`:

```markdown
# Eval results — skill-name 1.0.0 — 2026-10-11

| Case | Baseline | Haiku | Sonnet | Opus | Notes |
|---|---|---|---|---|---|
| short-id | ❌ | ✅ | ✅ | ✅ | baseline gave X |

Score: baseline 1/4, Haiku 4/4, Sonnet 4/4, Opus 4/4.
Changes made after this run: …
```

Generalise each failure into a fix to the skill, then re-run the affected cases on all three
models.

## Description tuning

1. Write 8–10 prompts that should trigger the skill and 8–10 near-misses that shouldn't.
2. For each, ask: given only the name and description among many skills, would Claude pick this
   one?
3. Rewrite to fix misses: add the terms users actually type, sharpen the "Not for" clause.
4. Re-count characters (≤ 1,024) and re-check for XML tags.

In Claude Code, Anthropic's `improve_description.py` automates this loop.

## Observing real use

Watch how Claude navigates the skill in real work: files read in an unexpected order (structure
unclear), references never opened (badly signposted or unnecessary), one reference read every
time (belongs in SKILL.md). Feed those observations back as eval cases.
