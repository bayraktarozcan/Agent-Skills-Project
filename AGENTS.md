# AGENTS.md / Agent Working Contract

Agent working contract for this repository. Truth over completeness: content here
only states what is verified by the live project. Nothing is fabricated.

## Project
- Host: GitLab. Project: bayraktarozcan/AgentSynapse. Default branch: `main`.
- This is a personal, single-owner, direct-push repository. No MR/PR gate is in
  use (branch protection = Maintainers push, force-push disabled).

## CI status (active: default-branch pipeline only)
- `.gitlab-ci.yml` is ACTIVE but limited to the default branch:
  `workflow: rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]`.
  - Jobs: `skills-syntax` (py_compile + `--version`/`--list`), `skills-profile-coverage`
    (`--check --profile temel` and `--profile tam`), and `pages` (docs -> GitLab Pages).
  - CI runs on pushes to `main`. It is NOT a quality gate for MRs/PRs (none are used).
  - No test-suite exists, so there is still no real coverage badge source. Do NOT
    register or keep badges that fake a pipeline/coverage source; they would lie.
  - Only badges with a live-verified real SVG (HTTP 200, `image/svg+xml`) are kept.
- Current verified badges: `Latest Release` (https://gitlab.com/bayraktarozcan/AgentSynapse/-/badges/release.svg) and `MIT License`
  (https://img.shields.io/gitlab/license/bayraktarozcan%2FAgentSynapse.svg), both probed HTTP 200 real SVG.
  Note: the native license path https://gitlab.com/bayraktarozcan/AgentSynapse/-/badges/license.svg is NOT registered
  and currently returns 403; the registered license badge is the shields.io URL above.
- The README's static shields.io badges (skills/repos/categories/license) are static
  text badges over verified facts (571+ skills, 35 repos, 10 categories, MIT).

## Badge policy (apply when touching badges)
1. Register a badge only after probing its image URL returns HTTP 200 with
   content-type `image/svg+xml` (real SVG, not an error page).
2. Remove badges whose data source is gone (old/broken). Do not replace them
   with a static badge that lies (e.g., a fake pipeline/coverage/unknown license).
3. Verify the final badge list by live-probing every image URL before closing.

## Conventions
- Keep all added files and scripts ASCII-safe; avoid inline PowerShell fragments
  that mix quote terminators (write scripts to temp and run with
  `powershell.exe -File`); repository tooling is Windows PowerShell + GitLab `glab`.
- Commit message style: conventional commits (e.g., `docs:`), single clean commit
  per logical change, direct push to `main` on both remotes (origin + gitlab).

## License
- Repo ships `LICENSE` = MIT (https://gitlab.com/bayraktarozcan/AgentSynapse/-/blob/main/LICENSE). The license badge reflects real
  GitLab license data served by shields.io (verified HTTP 200 SVG).

## Local / Yerel Yansıma
- This file is the single source of truth for agents. The Turkish translation lives
  in `AGENTS-TR.md`, which is a local human-review mirror only: it is git-ignored
  and MUST NOT be committed, staged, or pushed.
- Rule: whenever this file changes, `AGENTS-TR.md` must be refreshed in the same
  session so that the two `sync-sha` values match.
- `sync-sha` = SHA1 (UTF-8, no BOM) of this file's content with its own
  `<!-- mirror-sync: ... -->` line removed. The value is written on the last line of
  `AGENTS.md` and in the header of `AGENTS-TR.md`; if they differ, the mirror drifted
  and must be regenerated before any commit.
<!-- mirror-sync: sync-sha=d858fbfd13941f2ec01d058689a3b870f77df09f -->
