# Bruce — Local Environment Notes

## Shell Environment
- User: openclaw
- Home: /var/lib/openclaw
- Shell: bash (via exec tool)
- Wrappers: git-oc, gh-oc, vercel-oc, python3-oc (all in /var/lib/openclaw/bin/)

## GitHub
- Username: porterpup
- Auth: token in /var/lib/openclaw/.config/gh/hosts.yml
- CLI: gh-oc (wrapper sets HOME=/var/lib/openclaw)

### Repos (primary)
| Repo | Local clone | Vercel project |
|------|-------------|----------------|
| porterpup/expense-tracker | /var/lib/openclaw/.openclaw/workspace-bruce/expense-tracker/ | webapp + ingestion_service |
| porterpup/flyrely-api | /var/lib/openclaw/flyrely-api/ | (Railway — managed by FlyRely agent) |

## Vercel
- CLI: vercel-oc (wrapper sets VERCEL_TOKEN from env)
- Token: /var/lib/openclaw/.vercel-token (sourced by wrapper)
- Team/org: personal (porterpup)

### Vercel Projects
| Project | Dir | URL |
|---------|-----|-----|
| expense-tracker webapp | webapp/ | https://expense-tracker.vercel.app (or aliased) |
| ingestion-service | ingestion_service/ | https://ingestionservice.vercel.app |

## Git Identity
- Name: OpenClaw Bot
- Email: openclaw@sean-hq.local
- Credential store: /var/lib/openclaw/.git-credentials

## Python
- Binary: python3-oc (sets PYTHONPATH=/var/lib/openclaw/lib/python)
- Or system python3 for simple scripts

## Node / npm
- node: /usr/local/bin/node (v24)
- npm: /usr/local/bin/npm
- npx: /usr/local/bin/npx

## Useful Paths
- OpenClaw workspace: /var/lib/openclaw/.openclaw/workspace-bruce/
- OpenClaw config: /var/lib/openclaw/.openclaw/openclaw.json
- Logs: /var/lib/openclaw/.openclaw/logs/
- Agent outputs (sync'd to Sean's Mac): /Users/seanbutton/Documents/AgentOutput/
