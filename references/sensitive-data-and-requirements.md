# Sensitive data and requirements

## Contents
- Why this matters
- What never goes in a skill
- Where the real values go instead
- Placeholders for examples and evals
- Declaring requirements
- What the validator checks
- Your own client list
- Allowing a reviewed line
- Old repositories and history

## Why this matters

A skill travels. Every Claude.ai upload sends the whole folder, a `.skill` file is a zip anyone
can open, a GitHub repo keeps every past commit, and the evals ship inside the release archive.
Anything written into any file of a skill should be safe to hand to a stranger. That holds for
private skills too: they get shared, forked and pasted into support threads.

## What never goes in a skill

In any file: SKILL.md, references, scripts, evals, results files, README, CHANGELOG.

- **Secrets.** Passwords, API keys, tokens, private keys, service-account key files, `.env`
  files, certificates, passwords inside URLs.
- **Client data.** Client names, server hostnames and URLs, IP addresses, admin consoles,
  ports, account and user names on any server, database and file names (`.fmp12`), records,
  screenshots of records, Save-as-XML and DDR exports.
- **Accounts anywhere.** Email addresses, service-account emails, cloud project IDs, analytics
  and Search Console property IDs, tag IDs, marketplace or store account IDs, including the
  developer's own.
- **Personal paths.** `/Users/<name>/…`, `/home/<name>/…`, `C:\Users\<name>\…`: they name a
  person and break on every other machine.
- **Unreleased products** and preview build numbers (already a validator failure).

Public facts are fine: a vendor's documentation URL, a public API's base URL
(the documented base URL of a vendor's API), the skill author's public attribution line.

## Where the real values go instead

The skill describes **where to find** a value, never the value:

| Kind of value | Lives in | The skill says |
|---|---|---|
| Secrets, keys | A file outside the skill folder, `chmod 600`, or the OS keychain | "the key file named by `GOOGLE_APPLICATION_CREDENTIALS`" |
| Client servers, accounts | A local config file per client, outside the skill | "the host in `~/.config/example-skill/<client>.json`" |
| The developer's own IDs and setup | Claude's memory for the project, or a local config | "your GA4 property ID (ask, or read it from the config)" |
| Paths | `~/…` relative to home, or `${CLAUDE_SKILL_DIR}` for the skill's own files | `~/.config/example-skill/` |

Each of these is then declared in the skill's Requirements section, so a new user knows to
create it.

## Placeholders for examples and evals

Eval prompts and examples need realistic shapes, not real values. Use reserved names that can't
belong to anyone:

- Domains: `example.com`, `example.org`, `example.net`, or any name under `.example`, `.test`
  or `.invalid` (`fms1.client.example`).
- IP addresses: the documentation ranges `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`.
- People and companies: invented (`Sam Lee`, `Acme Logistics`), with no real domain attached.
- Emails: `name@example.com`.
- IDs: obviously fake (`properties/123456789`, `G-XXXXXXXXXX`).

A failure observed on a real client's file becomes an eval only after it's rewritten with
placeholders.

## Declaring requirements

Any skill that needs more than a chat gets a `## Requirements` section in SKILL.md, near the
top, listing everything it reaches outside its own folder:

```markdown
## Requirements

| Kind | Name | Used for | Surfaces |
|---|---|---|---|
| Connector (MCP) | `Wix` | Drafting blog posts | Claude.ai, Claude Code |
| API | Google Analytics Data API, service-account key in `GOOGLE_APPLICATION_CREDENTIALS` | Traffic reports | Claude Code |
| Path | `~/.config/example-skill/` | Key and settings, created by the user | Claude Code |
| CLI | `gh` | Opening pull requests | Claude Code |
| Account | Viewer on the GA4 account | Reading reports | any |
```

- **Kinds**: Connector (MCP server, by its server name), API (with how it authenticates), CLI,
  Path, Environment variable, Account or permission.
- Say what each is for and where it works. A Claude.ai chat has no local paths or CLIs; say so
  rather than leave the skill to fail.
- `compatibility` stays the one-line summary ("Claude Code; needs the Wix connector and a GA4
  service account").
- Name connectors exactly, as `ServerName:tool_name` in the body, so the requirement and the
  calls match.

## What the validator checks

`scripts/validate_skill.py` scans every text file in the skill (and every file in an archive
with `--archive`):

- **Fails** on secrets: private-key blocks, `"private_key"` fields, Google API keys, GitHub,
  Anthropic, OpenAI, Slack and AWS key formats, passwords inside URLs, and files that are keys
  or client data by type (`.env`, `.pem`, `.p12`, `.pfx`, `.key`, `id_rsa`, `.fmp12`).
- **Warns**, with file and line, on: email addresses, service-account emails, IP addresses in
  private ranges or in URLs, server-style hostnames (`fms.`, `filemaker.`, `admin.`, `vpn.`,
  `.local`, `.internal`, explicit ports, `fmnet://` addresses), analytics, tag and Search
  Console IDs, named `.fmp12` files, personal home paths, and Save-as-XML or DDR exports.
  Reserved placeholders (above) are never flagged.
- **Fails** on any term from the developer's own client list (below).
- **Inventories** every path, MCP connector, API host, environment variable and CLI the skill
  mentions, and warns on each one missing from `## Requirements`.

## Your own client list

Patterns catch things with a recognisable shape: hostnames, IP addresses, emails, IDs. They
can't know that "Acme", `fmsadmin` or `acmelogistics` is a client. Keep a private list of
client names, domains, server names and account names, one per line (`#` comments), at
`~/.config/cadenceux-skill-creator/sensitive-terms.txt`, or point
`CADENCEUX_SENSITIVE_TERMS` at another file. The validator fails on any match in any file of
any skill. The list lives outside every skill and is never committed; add a client when the
work starts, not after a release.

## Allowing a reviewed line

When a warning is a deliberate public fact (a vendor's documented support address, a public
IP in a protocol explanation), add `sensitive-ok` in a comment on that line after review. It
silences warnings on that line only. Where a comment can't go (JSON evals), list the exact
reviewed value in `sensitive-allow.txt` at the skill root, with a `#` note saying why it's
fictional or public. Neither silences a failure: a secret or a listed client term has no
reviewed form.

## Old repositories and history

Removing a value from the current files doesn't remove it from git history or from releases
already downloaded. If a secret was ever committed: rotate it first (the old value is burnt),
then clean the history. `cadenceux-github` carries the procedure ("Fixing a committed secret").
For client hostnames and accounts, tell the developer: their client may need to know.
