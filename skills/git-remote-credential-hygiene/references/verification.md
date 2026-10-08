# Verification per step

Stop the workflow on the first failed check. `...` means masked output.

| Step | Command | Expected |
|---|---|---|
| 1 inventory | `git remote -v` (mask `***`) | Every remote classified: clean HTTPS, embedded-credential, or SSH |
| 2 scan | `scripts/scan_remote_hygiene.py <repo>` | Exit 0 `CLEAN...`, or exit 1 with `file:line [label] ...` lines |
| 2b home file | check `~/.git-credentials` existence | Absent (ok), or scanned with masked findings only |
| 3 helper | `git config --get-all --show-origin credential.helper` | A helper plus its config origin (e.g. system `manager`) |
| 4 moved | re-run the step-2 scan | Exit 0; no `user:pass@` pattern in any URL line |
| 5 record | `git credential fill` with `protocol/host` input | A `username=...` line; password line never shown |
| 5 fetch | `git ls-remote <remote> HEAD` | A commit hash plus `HEAD` |
| 5 push | `git push --dry-run <remote> <branch>` | Exit code 0 (`Everything up-to-date` when clean) |
| 6 report | `git status --porcelain=v1 --branch` | No unintended modifications |

Failure rules: a missing helper, a failing `ls-remote`, or a nonzero
dry-run exit stops the workflow for a user decision. Never retry with a
guessed credential; ask the user.
