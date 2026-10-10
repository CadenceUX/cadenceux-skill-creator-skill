# Execution surfaces: what a skill's scripts can actually do

A SKILL.md reads the same everywhere, but whether Claude can run a bundled script depends on
where the skill is loaded. Decide the intended surfaces during intent capture, before writing
`scripts/`.

| Surface | Can Claude run scripts? | Consequence |
|---|---|---|
| Claude.ai chat, code execution off | No | Claude can only read the script. The skill must say the developer runs it locally, never "run `x.py`". |
| Claude.ai chat, code execution on | Yes, in an ephemeral sandbox | Scripts run, but without the user's files or the skill's install path unless uploaded into the session. Packages install from PyPI and npm. |
| Claude Code, Agent SDK | Yes, on the real filesystem | Scripts run directly via Bash. This is where builds, catalog sweeps and evals belong. |
| Claude API with code execution | Yes, in a server sandbox | No network access and no runtime package installs: bundle or avoid dependencies. |

## Wording by surface

- **Chat-only skills** (typical for reference lookups): scripts are maintainer tools. Put them
  in `maintainer/` and say "run this locally to rebuild the catalog".
- **Code-first skills** (live system access, such as FileMaker via ADT): write instructions as
  commands Claude runs.
- **Either**: write it conditionally: "If code execution is available, run
  `scripts/check.py` and read its output; otherwise give the developer the command and ask for
  the result."

`compatibility` signals the intended surface to a human but isn't enforced, so the body still
handles the other cases.

## Which surface to run this skill creator from

- **Claude Code** for anything mechanical or verifiable: validation, character counts,
  ecosystem greps, catalog sweeps, evals with subagents, packaging, git and GitHub.
- **Claude.ai** for what only the product UI shows: the rendered card, real triggering on that
  surface, and the installed copy under `/mnt/skills/user/`.
