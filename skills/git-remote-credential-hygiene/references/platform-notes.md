# Platform notes

Only claim what was tested. Everything else stays unsupported until
verified on that OS.

| OS | Credential helper | Status |
|---|---|---|
| Windows | `manager` (Git Credential Manager, system config) | Verified: configured and returning records |
| macOS | `osxkeychain` | Unsupported (untested here) |
| Linux | `libsecret` (needs libsecret plus dbus) | Unsupported (untested here) |

Known pitfalls and workarounds:

- PowerShell 5.1 pipes can corrupt `git credential approve` stdin
  ("missing protocol field"). Workaround: write the input to an ASCII
  temp file, feed it with `cmd /c "git credential approve < file"`,
  then delete the temp file immediately.
- `git credential fill` prints the secret. Filter output to the
  `username=` line only; never display or store the password line.
- A remote may define several push URLs (mirror setups). `git remote
  -v` shows each; test every push URL with a dry run.
- A hosting provider may rename a repo path. Pushing still works
  through the redirect, but update the remote URL and re-verify with
  `git ls-remote <remote> HEAD`.
- `git push --dry-run` writes to stderr with exit code 0 on success; in
  PowerShell check `$LASTEXITCODE`, not `$?`, after native commands.
