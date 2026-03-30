
---

## Tools Available to Bruce

### exec — Terminal / Bash
You have full shell access via the `exec` tool running as the `openclaw` user on the Mac.
- Working directory: `/var/lib/openclaw/`
- Shell: bash
- Use for: running scripts, installing packages, file operations, calling CLIs

**Wrappers (always use these, not raw binaries):**
| Alias | What it does |
|-------|-------------|
| `git-oc` | git with OpenClaw identity (HOME=/var/lib/openclaw) |
| `gh-oc` | GitHub CLI with OpenClaw credentials |
| `vercel-oc` | Vercel CLI with OpenClaw token |
| `python3-oc` | Python with OpenClaw PYTHONPATH |

### git — Version Control
Use `git-oc` for all git operations. Credentials are stored in `/var/lib/openclaw/.git-credentials`.
Git identity: `OpenClaw Bot <openclaw@sean-hq.local>`

### GitHub CLI (gh-oc)
Use `gh-oc` for GitHub operations: issues, PRs, CI runs, releases.
- Auth: token stored in `/var/lib/openclaw/.config/gh/hosts.yml`
- GitHub user: porterpup
- Do NOT use `gh` directly — always use `gh-oc` to stay in OpenClaw's HOME

### Vercel CLI (vercel-oc)
Use `vercel-oc` for deployments, env vars, and project management.
- Token: set via VERCEL_TOKEN env in wrapper
- Do NOT use `vercel` directly — always use `vercel-oc`

### Deployment Workflow
When asked to deploy:
1. Pull latest: `git-oc -C <repo> pull origin main`
2. Make changes, commit: `git-oc -C <repo> commit -am "message"` 
3. Push: `git-oc -C <repo> push origin main`
4. Vercel auto-deploys on push OR manually: `vercel-oc --cwd <dir> --prod`
5. Verify with curl: `curl -s https://<deployment-url>/health`

### Red Lines (exec)
- Never run `rm -rf /` or destructive system commands
- Never expose token values in logs or output to Sean
- Never commit secrets to git repos
- Always confirm before deleting data that cannot be recovered
