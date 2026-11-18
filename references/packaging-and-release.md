# Packaging and publishing

## Contents
- Release checklist
- GitHub repository
- plugin.json and the cadenceux marketplace
- Release archives (.zip and .skill)
- Amending an unshipped version
- Retiring a skill

## Release checklist

```
Release progress:
- [ ] scripts/validate_skill.py reports clean
- [ ] Evals re-run on this version; results file saved
- [ ] metadata.version, VERSION, plugin.json version and CHANGELOG heading identical
- [ ] CHANGELOG entry: what changed and how it was verified
- [ ] README current: what it does, install, attribution
- [ ] Shipped status checked (bump vs amend)
- [ ] Pushed to GitHub, tagged vX.Y.Z, GitHub release created
- [ ] Marketplace entry current (cadenceux-skills), and `versions.json` there updated
- [ ] No preview version numbers anywhere (validator check; release notes too)
- [ ] .zip and .skill built from the release tag, `validate_skill.py --archive` clean, attached
      to the GitHub release and saved to the confirmed folder
- [ ] Developer told what's live and what still needs a manual upload
```

## GitHub repository

- One repo per skill: `CadenceUX/<skill-name>-skill`, folder root = skill root.
- Add a description, the homepage (the cadenceux.com.au page or post), and topics
  (`claude-skill`, `claude`, `anthropic`, plus domain topics such as `filemaker`, `claris`).
- Tag every release `vX.Y.Z` and create a GitHub release whose notes summarise the CHANGELOG
  entry. Attach the `.zip` and `.skill` archives.
- Don't commit `.DS_Store`; add a `.gitignore`.
- Add a `.gitattributes` that marks `.claude-plugin/`, `evals/`, `maintainer/` (if present),
  `.gitignore` and `.gitattributes` as `export-ignore`. GitHub's **Code → Download ZIP** and a
  release's **Source code (zip)** honour it; without it those archives carry `plugin.json` and
  the Claude desktop app sends them to the plugin installer instead of installing the skill.
  A git clone (the marketplace route) still gets every file.

## plugin.json and the cadenceux marketplace

Every skill repo carries `.claude-plugin/plugin.json` so it installs as a plugin:

```json
{
  "name": "skill-name",
  "displayName": "Human Name",
  "version": "1.0.0",
  "description": "One or two sentences.",
  "author": { "name": "Darrin Southern", "url": "https://cadenceux.com.au" },
  "homepage": "https://github.com/CadenceUX/skill-name-skill",
  "repository": "https://github.com/CadenceUX/skill-name-skill",
  "license": "CC-BY-4.0",
  "keywords": ["filemaker", "claris"],
  "skills": ["./"]
}
```

The marketplace lives at github.com/CadenceUX/cadenceux-skills
(`.claude-plugin/marketplace.json`). Each entry points at a skill repo by HTTPS URL. When a
skill is added, renamed or retired, update the marketplace entry, its README, and every page
that lists the skills (cadenceux.com.au Skills page, llms.txt, the routing table in `cadenceux-dx`).

Install line users run:

```bash
claude plugin marketplace add https://github.com/CadenceUX/cadenceux-skills.git
claude plugin install <skill-name>@cadenceux
```

## Release archives (.zip and .skill)

Every release also ships as an archive of the skill folder plus an identical `.skill` copy.
Build it from a clean checkout of the release tag, never from a working folder: a working copy
can be missing files. On 2026-10-12, nine releases had shipped without `VERSION`,
`CHANGELOG.md` and `README.md` because they were zipped from stripped local copies.

Build with `build_release.sh` from the `cadenceux-github` skill: the one archive builder for
CadenceUX and developer skills alike, so the two release paths can't drift apart. It reads
the files **as committed at the tag** with `git archive`, so nothing uncommitted can leak in or
go missing, and `.gitattributes` export-ignore leaves out `.claude-plugin/` (the Claude app's
skill upload rejects an archive that carries a plugin manifest; the marketplace reads it from
the repo), `evals/`, `maintainer/` and the git files. It refuses to build when the four version
numbers disagree, the folder name doesn't match `name`, or a manifest would be inside.

1. Tag and push the release first.
2. Run the builder from the repo, by its path in the installed `cadenceux-github` skill, or
   download it once (`curl -fsSLO https://github.com/CadenceUX/cadenceux-github-skill/raw/main/scripts/build_release.sh`):
   `bash build_release.sh X.Y.Z /path/to/repo`
   It writes `dist/skill-name-vX.Y.Z.zip`, an identical `.skill`, and unversioned copies of
   both (`dist/` holds only `*.zip` and `*.skill`, which the repo's `.gitignore` already
   ignores). Say why `.claude-plugin/` is left out when you report the build.
3. `python3 scripts/validate_skill.py --archive dist/skill-name-vX.Y.Z.zip` and continue only
   when it reports clean: `SKILL.md`, `VERSION`, `CHANGELOG.md` and `README.md` present,
   versions matching, no `.claude-plugin/`, the `.skill` copy identical.
4. Attach all four to the GitHub release (`gh release create vX.Y.Z --verify-tag … <files>`, or
   `gh release upload vX.Y.Z <files> --clobber`). The README links to
   `releases/latest/download/skill-name.skill` and `.zip`, which only resolve to the newest
   release if every release carries the unversioned names.

Until 2026-11-18 this checklist zipped a fresh clone instead, which kept `evals/` in the
archive; releases from before then carry it. Either is valid to upload.

The `.skill` file is the same zip renamed. The Claude desktop app registers the extension on
macOS, so double-clicking it starts the install; Windows is unverified, so word it as "macOS".
In a browser, the route is Customize → Skills → upload the zip.

Save archives to the developer's release folder. Ask where it is, or check where the
previous release's archives were saved; never assume a path. Flag older archives of the same
skill sitting there; they're what gets uploaded by mistake.

**Repackaging a shipped release.** If a release's archive is wrong but the tagged repo is
right (a file missing from the zip, an extra file in it), rebuild the archive from that tag,
check it with `--archive` and replace the release's attachments with `--clobber` (the
unversioned copies too, if it's the latest release). Keep the
version: the skill's files haven't changed. Note the date in the release notes, and rebuild any
bundle or download page that carries the old archive.

## Amending an unshipped version

Fix a version in place (no bump) only if it hasn't shipped anywhere. Check rather than assume:
compare the repo's `raw/main/VERSION` and latest release tag with the working copy. If the repo
is behind, also confirm with the developer that it hasn't been uploaded to Claude.ai, since no
repo state can show that. Then keep the version, mark the CHANGELOG heading
"(updated YYYY-MM-DD, pre-release)", and rebuild the archives with the same stem. Once shipped,
every correction is a patch bump.

## Retiring a skill

1. Add a "Retired" notice at the top of the README: why, and what replaces it.
2. Commit, push, then archive the repo (`gh repo archive CadenceUX/<repo> --yes`). Archiving is
   reversible; deleting isn't, so archive by default.
3. Remove it from the marketplace, the website, llms.txt, routing tables and bundles.
4. Grep every other skill for its name and fix stale references.
