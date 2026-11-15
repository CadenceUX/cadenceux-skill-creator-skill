# Testing and evals

## Contents
- Evaluation-driven development
- evals.json format
- Choosing the baseline
- Running evals (Claude Code)
- Running evals (Claude.ai chat)
- Grading
- The results file
- Reading the transcripts
- Description tuning: measure, don't guess
- Anthropic's skill-creator tools
- Observing real use

## Evaluation-driven development

Create evals before writing much of the skill:

1. **Find the gaps.** Run representative tasks with no skill loaded and note each concrete
   failure (wrong value, invented parameter, missed step).
2. **Write at least three cases** that test those gaps, plus near-misses that must not trigger
   the skill.
3. **Record the baseline** score.
4. **Write the minimum skill** that closes the gaps.
5. **Run, compare with the baseline, refine.**

A case that passes without the skill is not testing anything the skill adds. Subjective skills
(writing style, design) still get cases, but grade them by reading rather than forcing
pass/fail facts onto taste.

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
an optional dependency (for example `adt` versus `standalone`). Trigger testing uses a separate
file in Anthropic's format (see Description tuning).

## Choosing the baseline

The baseline answers "better than what?":

- **A new skill:** no skill at all.
- **An update to a released skill:** the released version. Snapshot it before editing, from the
  tag rather than the working folder:
  `git archive vX.Y.Z --prefix=skill-snapshot-X.Y.Z/ | tar -x -C <workspace>`.
  Almost any version beats no skill; only the release tells you whether this change helped.

Keep the snapshot for the whole round so every iteration compares against the same thing.

## Running evals (Claude Code)

Work in a scratch workspace outside the skill folder, one folder per round:
`<workspace>/iteration-N/<case-id>/{new,baseline}/`.

1. **Launch every run in the same turn**: the skill on Haiku, Sonnet and Opus, plus the
   baseline, with a fresh subagent per run so no context leaks between runs. Baselines launched
   later run under drifted conditions.
2. Tell each agent the skill path, to read SKILL.md and follow it, and to answer only the
   prompt. Haiku shows whether the skill gives enough guidance; Opus shows whether it
   over-explains.
3. **Record tokens and time as each run finishes.** The subagent's completion notice carries
   `total_tokens` and `duration_ms`, and nothing else keeps them, so write them down straight
   away (a `timing.json` per run, or the results table). A skill that passes at twice the
   tokens isn't free; the cost belongs in the comparison.
4. While runs are in flight, check the `must` and `must_not` lists still say what you'd grade.

## Running evals (Claude.ai chat)

No subagents. Read SKILL.md as a fresh instance would and work each case, then show the results
to the developer. A baseline isn't meaningful when the author is also the runner, and there are
no token or time figures to compare.

## Grading

- **Script what a script can check** (a field present, a value right, a file valid) and run it
  every round; read only what needs judgement. Scripts are faster and repeatable, and they
  don't drift between rounds.
- Grade each `must` and `must_not` with its evidence: the quote or line it rests on.
- **Flag cases that don't discriminate.** A case the baseline passes too, every time, tests
  nothing the skill adds: sharpen or replace it. A case that flips between runs is flaky: fix
  the prompt or the grading before trusting it.
- For a bigger change, or when the developer wants to read through outputs themselves,
  Anthropic's benchmark aggregator and review viewer do this well (see below).

## The results file

Save `evals/results-YYYY-MM-DD.md`:

```markdown
# Eval results — skill-name 1.1.0 — 2026-10-11

Baseline: released 1.0.0 (Sonnet). Fresh subagent per run.

| Case | Baseline | Haiku | Sonnet | Opus | Notes |
|---|---|---|---|---|---|
| short-id | ❌ | ✅ | ✅ | ✅ | baseline gave X |

Score: baseline 1/4, Haiku 4/4, Sonnet 4/4, Opus 4/4.
Tokens (mean per run): baseline 21k, Haiku 24k, Sonnet 23k, Opus 26k. Time: …
Changes made after this run: …
```

Generalise each failure into a fix to the skill, not a patch for that one prompt, then re-run
the affected cases on all three models.

## Reading the transcripts

Read how each run reached its answer, not only the answer:

- **Repeated work.** If several runs each wrote the same helper (a parser, a converter), bundle
  one tested script in `scripts/` and tell the skill to run it. Every later use stops
  reinventing it, and the answers get more consistent.
- **Wasted effort.** A section that sends every run down an unproductive path costs tokens:
  cut it and re-run to see whether anything breaks.
- **Unused material.** A reference no run opened is badly signposted or unnecessary.

## Description tuning: measure, don't guess

Reading a description and judging whether Claude would pick it is a guess. In Claude Code,
measure it:

1. **Write the trigger set**: about 20 realistic queries in `evals/trigger-evals.json`, in
   Anthropic's format `[{"query": "…", "should_trigger": true}, …]`. Half should trigger:
   different phrasings, cases that never name the skill, cases where it competes with a
   neighbour and should win. Half are near-misses that share keywords but need something else.
   Make them concrete (file names, versions, a bit of backstory, casual typing). One-step asks
   such as "read this file" make poor tests: Claude answers those without any skill.
2. **Agree the set with the developer.** Bad queries produce a bad description.
3. **Run Anthropic's `run_loop.py`** (below) with the model powering the session. It runs each
   query three times through `claude -p`, holds 40% of the set back, rewrites the description
   from the failures for up to five rounds, and returns `best_description` chosen on the
   held-back score, so the result isn't tuned to the prompts it's scored on.
4. **Apply and re-check**: ≤ 1,024 characters, no angle brackets, still third person with a
   "Not for" clause, then `scripts/validate_skill.py`. Show the developer before and after,
   with the scores.

In Claude.ai chat there's no `claude -p`: judge each query against the description instead, and
say the result is unmeasured.

**Before blaming the wording in Claude Code, check the listing.** Claude Code cuts each
description (with any `when_to_use`) at 1,536 characters and keeps the whole skill listing to
about 1% of the context window. When too many skills are installed, it drops the descriptions
of the least-used skills first and shows only their names. A skill whose description isn't
being shown won't trigger however it's worded: remove unused skills or raise the
`skillListingBudgetFraction` setting.

## Anthropic's skill-creator tools

Anthropic's `skill-creator` plugin (`skill-creator@claude-plugins-official`, source
`github.com/anthropics/skills`, `skills/skill-creator/`) carries tested tools for the measured
parts of this loop. Use them where they are rather than copying them into a skill: copies fall
behind.

Install it once in Claude Code: `claude plugin install skill-creator@claude-plugins-official`.
Find its folder with `find ~/.claude/plugins -path '*skill-creator/scripts/run_loop.py'` and
run the scripts from the `skills/skill-creator/` folder above `scripts/` (they import
`scripts.*`). They need Python 3.10+ and the `claude` CLI on the path.

```bash
# Measured description tuning: 5 rounds, 3 runs per query, 40% held back
python3 -m scripts.run_loop --eval-set /path/to/evals/trigger-evals.json \
  --skill-path /path/to/skill --model <session-model-id> --max-iterations 5 --verbose

# One measurement of the current description, no rewriting
python3 -m scripts.run_eval --eval-set /path/to/evals/trigger-evals.json --skill-path /path/to/skill
```

The trigger runs put temporary command files in the nearest `.claude/commands/` folder above
the working directory, so start them from a scratch folder, not inside a client's repository.

For a larger benchmark, `scripts/aggregate_benchmark.py` turns per-run grading and timing into
pass rates with mean and spread, and `eval-viewer/generate_review.py` opens a page where the
developer reads each output and leaves feedback. Both expect Anthropic's workspace and
`grading.json` layout, described in its `references/schemas.md`. This skill's `evals.json` and
results file stay the CadenceUX record either way.

## Observing real use

Watch how Claude navigates the skill in real work: files read in an unexpected order (structure
unclear), references never opened (badly signposted or unnecessary), one reference read every
time (belongs in SKILL.md). Feed those observations back as eval cases.
