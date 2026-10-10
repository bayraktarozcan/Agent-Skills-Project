# Detection patterns

Each finding is reported as `file:line [label] masked-line`. The full
secret value is never emitted. Masking rule: at most the first 4
characters plus `***` plus the total length, and only in transient
terminal output -- never written to a file, log, or commit. Prefer
reporting host/username metadata with the value fully replaced by `***`.

| Label | Pattern (regex) | Meaning |
|---|---|---|
| `gitlab-token` | `glpat-[A-Za-z0-9_-]+` | GitLab personal/project/group token |
| `github-token` | `ghp_[A-Za-z0-9]+` | GitHub classic personal access token |
| `github-oauth` | `gho_[A-Za-z0-9]+` | GitHub OAuth access token |
| `github-fine-grained` | `github_pat_[A-Za-z0-9_]+` | GitHub fine-grained token |
| `access-token-marker` | `x-access-token` (case-insensitive) | OAuth-style URL username marker |
| `embedded-credentials` | `://[^/\s@]+:[^/\s@]+@` | `user:password@` inside a URL |

Masking shapes (no real values):

- URL line `https://user:pass@host/...` renders as `https://***@host/...`.
- A token renders at most as `glpa*** (len=26)`; default to full `***`.

False-positive notes:

- `x-access-token` as a username with the real secret in the manager is
  fine; it is only a finding when paired with an embedded secret.
- SSH URLs (`git@host:...`) carry no embedded password; classify them,
  do not flag them.
