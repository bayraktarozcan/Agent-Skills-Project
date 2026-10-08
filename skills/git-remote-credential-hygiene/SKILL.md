---
name: git-remote-credential-hygiene
description: Use when checking whether git remote URLs hide embedded passwords or tokens, when moving a plaintext credential from repository config into the operating-system credential store, when fetch or push authentication must be proven on GitHub and GitLab remotes without ever printing a secret, or when a review asks for a rotation-first remediation plan after a credential was exposed in text.
---

# Git Remote Credential Hygiene

Goal: prove that git remote authentication is stored safely -- no
plaintext secret in repo config -- and that fetch plus push work on every
remote, without ever printing a secret value.

Complements secret-scanner skills (e.g. GitGuardian): those find leaked
secrets in code; this owns the remote-URL-to-OS-manager move plus
dual-remote authentication proof.

## When to use

- Remote URLs may contain embedded `user:password@` credentials.
- A token or password is suspected in `.git/config` or
  `~/.git-credentials`.
- Fetch or push authentication must be proven on GitHub and GitLab
  remotes.
- A review asks for a rotation-first plan after a plaintext exposure.

## Workflow (default read-only; stop on first failure)

1. **Inventory.** List remotes; classify each URL as clean HTTPS (no
   embedded credential), embedded-credential, or SSH.
   Verify: every URL accounted for, secret parts masked as `***`.
2. **Scan.** Run `scripts/scan_remote_hygiene.py <repo>`; see
   `references/patterns.md`.
   Verify: findings as file + line with masked values only.
3. **Helper.** Confirm an OS credential helper is configured; see
   `references/platform-notes.md`.
   Verify: helper name plus config origin shown; stop if none.
4. **Move (APPROVAL GATE).** Only with explicit user approval and only
   if step 2 found plaintext: rewrite remote URLs to tokenless HTTPS,
   then store the credential in the OS manager. The user supplies the
   secret; the agent never invents one.
   Verify: config re-scan is clean; see `references/remediation.md`.
5. **Verify auth.** Confirm the manager returns a record (username
   only), then test fetch and push without changing anything.
   Verify: expected outputs in `references/verification.md`.
6. **Report.** Changed URLs (masked), verification results, rotation or
   expiry advice. Log actions without secret values.

## Rules

- Never print, write to disk, or commit a secret value. Masked output.
- Steps 1-3 and 5 change nothing. Step 4 needs explicit approval.
- Rotation-first: a leaked or moved secret is rotated or revoked at the
  source before cleanup; cleanup never replaces rotation.
- Least privilege and short expiry for every requested scope.
- Do not claim support for an untested OS or tool; mark unsupported.
