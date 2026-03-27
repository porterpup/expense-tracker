# FlyRely Development Workflow (March 22, 2026)

## Single Source of Truth: GitHub
- Repo: https://github.com/porterpup/flyrely-api
- All code changes flow through GitHub
- Railway auto-deploys on push to master

## My Working Copy (OpenClaw Server)
- Location: `/var/lib/openclaw/.openclaw/workspace-flyrely/flyrely-api-working/`
- Synced with GitHub master
- I execute changes here, then push
- Sean doesn't need to touch this

## Execution Model
When Sean says "do X":
1. Pull latest from GitHub
2. Make changes locally (on OpenClaw)
3. Commit with clear message
4. Push to master
5. Tell Sean it's done
6. Verify with curl tests

## Deliverables
- Strategy docs, reports, analysis → `/Users/seanbutton/Documents/AgentOutput/`
- Code → GitHub only (no separate copies)

## Version Control
- GitHub master = authoritative source
- My local copy = working branch
- Sean's Mac = optional (pulls when needed or uses deployed version)

No more parallel copies. No more sync issues.
