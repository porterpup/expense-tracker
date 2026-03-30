---
name: vercel
description: "Vercel deployments via vercel-oc CLI: deploy projects, manage env vars, check deployment status, roll back. Use when: (1) deploying frontend or backend to Vercel, (2) setting/listing Vercel env vars, (3) checking deployment logs or status, (4) aliasing domains. NOT for: managing DNS outside Vercel, billing, or team/org admin."
metadata:
  {
    "openclaw":
      {
        "emoji": "▲",
        "requires": { "bins": ["vercel-oc"] },
      },
  }
---

# Vercel Skill

Use `vercel-oc` (the OpenClaw-wrapped Vercel CLI) for all Vercel operations.
Always use `vercel-oc`, never `vercel` directly (the wrapper injects the auth token).

## When to Use

✅ **USE this skill when:**
- Deploying a project to Vercel production or preview
- Checking deployment status or logs
- Adding/updating environment variables on Vercel
- Listing projects or deployments
- Rolling back to a previous deployment
- Aliasing a deployment to a custom domain

❌ **DON'T use this skill when:**
- Local dev (`npm run dev` is fine without Vercel)
- Managing DNS at an external registrar
- GitHub Actions CI (handle separately)

## Setup

Auth is pre-configured via the `vercel-oc` wrapper — no additional login needed.

```bash
vercel-oc whoami        # Verify auth is working
vercel-oc ls            # List all projects
```

## Common Commands

### Deploy to Production
```bash
# Deploy from project root
vercel-oc --cwd /path/to/project --prod

# Deploy webapp
vercel-oc --cwd /var/lib/openclaw/.openclaw/workspace-bruce/expense-tracker/webapp --prod

# Deploy ingestion_service
vercel-oc --cwd /var/lib/openclaw/.openclaw/workspace-bruce/expense-tracker/ingestion_service --prod
```

### Check Deployment Status
```bash
vercel-oc ls <project-name>             # List recent deployments
vercel-oc inspect <deployment-url>      # Inspect a specific deployment
```

### Manage Environment Variables
```bash
vercel-oc env ls <project-name>                              # List env vars
vercel-oc env add <NAME> production --value "<value>" --yes  # Add/update
vercel-oc env rm <NAME> production --yes                     # Remove
```

### Rollback
```bash
vercel-oc rollback <project-name>       # Roll back to previous deployment
```

### Logs
```bash
vercel-oc logs <deployment-url>         # Tail deployment logs
```

## Projects Reference

| Project name | Local path | Production URL |
|---|---|---|
| expense-tracker (webapp) | expense-tracker/webapp/ | https://expense-tracker.vercel.app |
| ingestionservice (backend) | expense-tracker/ingestion_service/ | https://ingestionservice.vercel.app |

## Tips
- Always run `--prod` for production; omit for preview deployments
- After `git push`, Vercel auto-deploys if GitHub integration is enabled — manual `vercel-oc --prod` is only needed for direct deploys
- Use `vercel-oc env add` to rotate secrets without touching code
- Verify deployments with `curl -s https://<url>/health | python3 -m json.tool`
