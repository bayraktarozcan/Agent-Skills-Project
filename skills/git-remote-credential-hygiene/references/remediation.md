# Remediation doctrine (rotation-first)

Priority order. Cleanup never replaces rotation.

1. **Rotate or revoke at the source.** For a leaked or relocated
   secret, create the replacement (minimum scope, short expiry) and
   revoke the old value first: API keys around 90 days, critical or
   broad scopes around 30 days. Record the revoke path for every secret.
2. **Confirm exposure.** Note where the plaintext lived (file + line,
   commit range if already pushed). If it reached a remote, treat it as
   compromised even after cleanup.
3. **Clean.** Remove the secret from config files and rewrite remote
   URLs to tokenless HTTPS. Never commit a file that once held the
   value without verifying the history is clean.
4. **Move.** Store the current secret in the OS credential manager
   (approval-gated; the user supplies the value, the agent never
   invents one). Follow `platform-notes.md` workarounds.
5. **Verify.** Re-scan (expect exit 0), confirm the manager record
   (username only), and test fetch plus push dry-run per remote.
6. **Report.** Changed URLs (masked), verification results, and the
   rotation or expiry recommendation. Log actions without secret
   values.

Scope guidance: request the smallest scope that works and the shortest
expiry the provider allows. Prefer short-lived or federated credentials
(OIDC) over static tokens where the platform supports them.
