# SPEC -- git-remote-credential-hygiene

Version: 1.0.0 (2026-10-09). Status: active.

## Contract

This skill guarantees:

- Remote authentication is audited end to end (inventory, scan, helper
  check, auth proof) without emitting a secret value anywhere.
- Every workflow step has a verification command with an expected
  output; the run stops on the first failed check.
- The only mutating step (credential move) requires explicit user
  approval, and remediation is rotation-first.
- Untested OS or tool combinations are reported as unsupported, never
  guessed.

## Non-goals

History rewriting, secrets-manager backends (Vault, cloud KMS), CI OIDC
setup, SSH key lifecycle, breach forensics, and operating secret
scanners (covered by scanner skills such as GitGuardian).

## Layout

`SKILL.md` routes; `references/` holds per-step detail;
`scripts/scan_remote_hygiene.py` is the read-only scanner (exit 0
clean, 1 findings, 2 error); `evals/evals.json` holds the trigger and
behavior cases.

## Change log

- 1.0.0 (2026-10-09): initial contract; reworked to the Agent Skills
  shape (router SKILL.md, trigger-rich description, evals.json).
