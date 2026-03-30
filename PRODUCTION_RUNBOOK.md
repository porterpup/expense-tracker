PRODUCTION SECRET RUNBOOK

1. Generate: create strong secrets via KMS or secure RNG (e.g. openssl rand -hex 32) or asymmetric keys; add metadata (owner, purpose, expiry).
2. Store: store only in an enterprise vault (HashiCorp Vault, AWS Secrets Manager, 1Password/Bitwarden) with KMS encryption, versioning, and access policies.
3. Deploy/update runtime envs: update staging first; then push to Vercel (Project → Settings → Environment Variables or vercel CLI) and GitHub Actions (Repo/Org Secrets). Use CI-only secrets where possible.
4. Distribute securely: share vault access or a secure password-manager item; never send plaintext via email/Slack. Use short-lived tokens for humans.
5. Verify with signed test: create a short-lived signed test token (HMAC/RSA), exercise the code path in staging, verify signature and logs before promoting.
6. Revoke & remove local copies: rotate keys, revoke old tokens in provider consoles, delete local files, clear shell/history, remove CI/cache copies.
7. Log & audit rotation: enable audit logging, record rotations and who approved them; keep logs immutable for 90+ days per policy.
8. Recommended cadence: rotate secrets every 90 days; rotate immediately on suspected compromise or leaked secret.
9. Emergency steps: revoke, rotate, redeploy envs, invalidate sessions, run signed tests, notify stakeholders.
10. Contact/notes: on-call/PagerDuty, security@company.example, maintain this file in repo; update when processes or providers change.
