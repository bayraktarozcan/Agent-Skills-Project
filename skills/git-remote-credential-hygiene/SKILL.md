---
name: git-remote-credential-hygiene
description: Use this skill whenever git remotes, .git/config, or credential storage are involved. Check remote URLs for embedded user:password@ credentials and plaintext tokens, move a repository-config credential into the Windows, macOS, or Linux OS credential store, prove fetch and push authentication on GitHub and GitLab remotes without ever printing a secret, or plan rotation-first remediation after a plaintext credential exposure. Triggers on remote audits, credential moves, and auth verification requests.
---

# Git Remote Credential Hygiene

Audit git remote authentication without exposing a secret: inventory the
remotes, scan for plaintext credentials, confirm the OS credential
helper, move credentials into the manager (approval-gated), then prove
fetch and push work. Scanner skills (e.g. GitGuardian) find leaked
secrets in code; this skill owns the remote-URL-to-OS-manager move plus
the dual-remote authentication proof.

Default to the read-only steps and stop on the first failed check: a
half-verified auth claim is worse than no claim, because the user will
rely on it.

Open the reference that matches the step at hand:

| Open when... | Read |
|---|---|
| matching a token shape or masking a finding | `references/patterns.md` |
| checking helper setup or hitting an OS quirk | `references/platform-notes.md` |
| needing the exact command and expected output | `references/verification.md` |
| deciding what to do about a finding | `references/remediation.md` |
| checking what this skill guarantees and excludes | `SPEC.md` |

## Workflow

1. Inventory remotes with `git remote -v`. Mask secret parts as `***`
   before showing anything, then classify each URL as clean HTTPS,
   embedded-credential, or SSH. Account for every URL.
2. Scan with `scripts/scan_remote_hygiene.py <repo>` and check
   `~/.git-credentials` when present. Report findings as file + line
   with masked values only.
3. Confirm an OS credential helper is configured
   (`git config --get-all --show-origin credential.helper`). Stop when
   none is configured; unauthenticated guessing helps nobody.
4. Move credentials only with explicit user approval and only when step
   2 found plaintext. Rewrite remote URLs to tokenless HTTPS, then store
   the credential in the OS manager. Ask the user for the secret value;
   never invent one. Re-scan afterwards and expect a clean result.
5. Prove authentication without changing anything: confirm the manager
   returns a record (show the `username=` line only, never the
   password), then run fetch plus push dry-runs per remote.
6. Report changed URLs (masked), verification results, and rotation or
   expiry advice. Log actions without secret values.

## Rules

- Never print, write to disk, or commit a secret value, because any
  copy widens exposure permanently. Emit masked output only.
- Rotate or revoke a leaked or moved secret at its source before
  cleanup; cleanup alone leaves the old value valid, so it never
  replaces rotation.
- Request the smallest scope and shortest expiry that works, so a
  future leak costs as little as possible.
- Mark untested OS or tool combinations unsupported instead of guessing
  commands; a wrong command against credentials is a safety incident.
