# FlyRely Hosting & Infrastructure Analysis

**Prepared for:** Production launch (Month 2–3)
**Date:** March 15, 2026
**Scope:** Full-stack hosting recommendation for web app + API + ML model + databases

---

## Part 1: Current State (Phase 1)

### What's Running Now
- **Backend API:** Railway (hospitible-solace project)
  - Python/FastAPI (main.py)
  - Prediction model (flight_delay_model_v2_weather.joblib)
  - CSV logging to predictions.csv
  - Endpoint: https://web-production-ea1e9.up.railway.app
  
- **Frontend:** TanStack Start (React, full-stack)
  - Location: `/var/lib/openclaw/.openclaw/workspace-flyrely/fr-chief/flyrely-app/`
  
- **Database:** Not specified (likely in-memory or local SQLite for MVP)

- **External APIs:**
  - OpenSky Network (flight data)
  - Tomorrow.io (weather)
  - BTS (historical delays)

### Costs (Phase 1)
- **Railway:** ~$5–10/month (hobby plan + usage)
- **External APIs:** Free tiers (OpenSky, Tomorrow.io 500 calls/day)
- **Total:** <$20/month

---

## Part 2: Production Architecture (Phase 2–3)

### What You'll Need to Run

**Tier 1: Frontend (Web + Mobile)**
- React web app (TanStack Start)
- iOS app (React Native or Swift)
- Android app (React Native or Kotlin)
- CDN for static assets + images

**Tier 2: Backend API**
- FastAPI (Python) or Node.js
- User authentication + JWT tokens
- Flight search/save/management
- Notification service (push, email, SMS)
- Subscription/billing logic
- Rate limiting + caching

**Tier 3: ML / Prediction Service**
- Flight delay prediction model (joblib or ONNX)
- Real-time inference (1–2 second latency requirement)
- Model versioning + A/B testing
- Scheduled retraining (weekly/monthly)

**Tier 4: Databases**
- PostgreSQL (primary: users, flights, predictions, subscriptions)
- Redis (cache layer + rate limiting)
- S3 (model artifacts, logs, backups)

**Tier 5: External Integrations**
- Stripe (subscriptions + payments)
- SendGrid/Mailgun (email)
- Firebase Cloud Messaging (push notifications)
- Twilio (SMS)
- Google Calendar API (sync)

**Tier 6: Ops & Monitoring**
- Error tracking (Sentry)
- Logging (DataDog or CloudWatch)
- APM (Application Performance Monitoring)
- Uptime monitoring
- Database backups

---

## Part 3: Hosting Options (Comparison)

### Option A: Full AWS (Recommended for Scale)

**Architecture:**
```
Frontend:        CloudFront + S3 (CDN + static assets)
Web App:         ECS Fargate (containerized FastAPI)
Database:        RDS PostgreSQL (managed)
Cache:           ElastiCache Redis
ML Service:      SageMaker or custom EC2
Storage:         S3 (models, logs, backups)
Secrets:         AWS Secrets Manager
CDN:             CloudFront
Monitoring:      CloudWatch + X-Ray
```

**Pros:**
- ✅ Infinite scalability (handles 10K+ users)
- ✅ Mature, production-grade
- ✅ Built-in monitoring + auto-scaling
- ✅ Global CDN (CloudFront)
- ✅ Excellent support for real-time APIs

**Cons:**
- ❌ Higher cost ($500–2K/month at scale)
- ❌ Steep learning curve
- ❌ More infrastructure to manage (even with managed services)
- ❌ Overkill for MVP (first 3 months)

**Estimated Costs (Month 3):**
- ECS Fargate: $50–100/month
- RDS PostgreSQL: $50–100/month (small instance)
- ElastiCache: $30–50/month
- CloudFront: $10–20/month
- S3: <$5/month
- SageMaker endpoint: $50–150/month (always-on)
- Monitoring + misc: $30–50/month
- **Total: $220–475/month**

---

### Option B: Vercel + Railway (Current Stack)

**Architecture:**
```
Frontend:        Vercel (TanStack Start)
Backend API:     Railway (FastAPI/Python)
Database:        Railway PostgreSQL add-on (or Supabase)
Cache:           Redis (Railway add-on)
ML Service:      Railway dedicated VM
Storage:         S3 (for models) or Railway volumes
```

**Pros:**
- ✅ Zero-friction deployment (git push → live)
- ✅ Already using TanStack on Vercel
- ✅ Cheap for early stage ($100–300/month)
- ✅ Simple scaling (just resize Railway plans)
- ✅ Great DX (minimal ops)

**Cons:**
- ❌ Less flexible than AWS (vendor lock-in to Railway)
- ❌ Railway has limits on concurrent requests
- ❌ Cold starts possible (Python on Railway)
- ❌ Not recommended for >100K predictions/day
- ❌ ML model serving is resource-heavy on Railway

**Estimated Costs (Month 3):**
- Vercel (TanStack Start): $20/month (hobby + bandwidth)
- Railway API servers: $100–150/month (2–3 dynos)
- Railway PostgreSQL: $30–50/month
- Railway Redis: $20–30/month
- ML model inference: $50–100/month (GPU or CPU-intensive)
- External APIs: $0–50/month (paid tiers)
- **Total: $220–380/month**

---

### Option C: Hybrid (Vercel + AWS Lambda)

**Architecture:**
```
Frontend:        Vercel
API:             AWS Lambda + API Gateway (serverless)
Database:        AWS RDS or managed Postgres
ML Service:      AWS Lambda (serverless) or SageMaker
Cache:           ElastiCache or DynamoDB
```

**Pros:**
- ✅ Pay-per-use (cheap for low volume, scales up)
- ✅ AWS infrastructure without always-on cost
- ✅ Good for bursty traffic patterns
- ✅ Less operational overhead

**Cons:**
- ❌ Cold start latency (Lambda spins up, ~1–5 sec)
- ❌ Complex for real-time predictions (1–2 sec latency requirement)
- ❌ More infrastructure to manage than Railway
- ❌ Harder to debug + monitor

**Estimated Costs (Month 3):**
- Vercel: $20/month
- Lambda: $20–50/month (pay-per-invocation)
- API Gateway: $5–15/month
- RDS: $50–100/month
- SageMaker: $50–150/month
- **Total: $145–335/month**

---

### Option D: Heroku (Simplicity Over Scale)

**Architecture:**
```
Frontend:        Heroku (buildpack for TanStack)
API:             Heroku Dyno (Python)
Database:        Heroku PostgreSQL
ML Service:      Heroku Worker Dyno
```

**Pros:**
- ✅ Dead simple (git push → live)
- ✅ Great DX (minimal setup)
- ✅ Good for MVP phase

**Cons:**
- ❌ Expensive (~$50–100/dyno/month)
- ❌ Heroku is sunsetting (Sept 2025 already happened)
- ❌ Limited scalability
- ❌ **Not recommended** (Heroku pricing > Railway + better features)

**Cost:** $200–400/month (not worth it)

---

## Part 4: RECOMMENDATION: Hybrid Approach (Months 1–6)

### Phase 1–2 (Now – Month 3): Railway Only
**Why:** Cheap, simple, proven to work with Phase 1 model.

**Architecture:**
```
Frontend:  Vercel (TanStack Start)
Backend:   Railway (FastAPI)
Database:  Railway PostgreSQL add-on
Cache:     Railway Redis add-on
ML Model:  Railway (same backend container)
```

**Cost:** $150–250/month

**Capacity:** Handles 1K–5K daily active users, 100–500 predictions/day

**Do this now:**
1. ✅ Migrate database to Railway PostgreSQL (from SQLite/in-memory)
2. ✅ Add Redis cache for rate limiting
3. ✅ Set up backups (Railway supports this)
4. ✅ Deploy to production (verify health checks pass)

---

### Phase 3 (Month 4–6): Migrate to AWS (When You Need Scale)

**Why migrate when?**
- DAU exceeds 1K (churn + new signups)
- Predictions exceed 500/day
- Railway request limits hit
- Response times degrade

**Target architecture at scale:**
```
Frontend:    Vercel + CloudFront
API:         ECS Fargate (auto-scaling)
Database:    RDS PostgreSQL (managed replication)
Cache:       ElastiCache Redis
ML Service:  EC2 spot instance or SageMaker endpoint
Monitoring:  CloudWatch + Sentry
```

**Why AWS over others?**
- ✅ Handles real-time predictions (1–2 sec latency)
- ✅ Auto-scaling for traffic spikes
- ✅ Global infrastructure (multi-region)
- ✅ Industry standard for startups

**Migration timeline (1–2 weeks):**
1. Set up VPC + subnets
2. Migrate RDS database (minimal downtime)
3. Deploy API to ECS Fargate
4. Configure auto-scaling
5. Point DNS to new endpoints
6. Monitor for 48h, roll back if needed

---

## Part 5: Detailed Railway Setup (Month 1–3)

### Step 1: Upgrade Database
**Current:** Likely SQLite or in-memory
**Target:** Railway PostgreSQL addon

```bash
# In Railway dashboard:
1. Click "New" → "Database" → "PostgreSQL"
2. Wait for creation (~2 min)
3. Copy DATABASE_URL from Railway env variables
4. Update .env in your project
5. Run migrations:
   alembic upgrade head
6. Test connection
```

**Cost:** $30/month (small instance)

### Step 2: Add Redis Cache
**For rate limiting + sessions**

```bash
# In Railway dashboard:
1. Click "New" → "Database" → "Redis"
2. Copy REDIS_URL
3. Update .env
4. Test connection with redis-cli
```

**Cost:** $20/month

### Step 3: Deploy API to Railway

**Update `main.py` to use PostgreSQL:**
```python
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
# Railway provides postgres://... format
engine = create_engine(DATABASE_URL)
```

**Deploy:**
```bash
git add -A
git commit -m "feat: add PostgreSQL support"
git push origin master
# Railway auto-deploys on push
```

### Step 4: Monitor & Backup

**In Railway dashboard:**
- Set up automated backups (daily)
- Configure monitoring (logs, errors)
- Set up alerts (disk space, CPU, memory)

---

## Part 6: Cost Breakdown (Month 1–12)

### Months 1–3 (Launch): Railway + Vercel

| Service | Cost | Notes |
|---------|------|-------|
| Vercel | $20 | TanStack Start hobby |
| Railway API | $100–150 | FastAPI + Python |
| Railway DB | $30 | PostgreSQL small |
| Railway Redis | $20 | Cache |
| External APIs | $0 | Free tiers |
| Stripe | Variable | 2.9% + $0.30 per transaction |
| SendGrid | $20 | 5K emails/month |
| Firebase | $0 | Free tier for push |
| Monitoring | $0 | Railway built-in |
| **Total** | **$190–240** | |

### Months 4–6 (Growth): Start AWS Migration

| Service | Cost | Notes |
|---------|------|-------|
| Vercel | $30 | Higher bandwidth |
| AWS ECS | $100–150 | Fargate (2 vCPU) |
| AWS RDS | $80–120 | PostgreSQL small |
| AWS ElastiCache | $40–60 | Redis |
| AWS S3 | $5–10 | Models + logs |
| AWS CloudWatch | $20–30 | Monitoring |
| Stripe | Variable | |
| SendGrid | $50 | 20K emails/month |
| Twilio | $20 | SMS support |
| Firebase | $10 | Push (paid tier) |
| Sentry | $30 | Error tracking |
| **Total** | **$385–500** | |

### Months 7–12 (Scale): Full AWS

| Service | Cost | Notes |
|---------|------|-------|
| AWS (all above) | $400–600 | Auto-scaling + multi-region |
| DataDog | $50–100 | Advanced monitoring |
| PagerDuty | $30 | On-call alerts |
| **Total** | **$510–780** | |

---

## Part 7: Implementation Checklist

### Immediate (This week)

- [ ] Upgrade Railway database to PostgreSQL
- [ ] Add Redis cache layer
- [ ] Test API health endpoint
- [ ] Set up automated backups
- [ ] Verify Stripe integration
- [ ] Add monitoring/logging

### Month 1

- [ ] Deploy landing page (Vercel)
- [ ] Set up email notifications (SendGrid)
- [ ] Add push notifications (Firebase)
- [ ] Performance testing (1K DAU sim)
- [ ] Security audit (OWASP top 10)

### Month 2–3

- [ ] Monitor real-time traffic
- [ ] Optimize database queries
- [ ] Scale if needed (add Railway resources)
- [ ] Plan AWS migration (Month 4)
- [ ] Set up budget alerts

### Month 4

- [ ] Migrate to AWS (1-week sprint)
- [ ] Update DNS + CDN
- [ ] Monitor for 48h
- [ ] Decommission Railway (or keep as backup)

---

## Part 8: Specific Recommendations for Your Stack

### For TanStack Start (Frontend)
- **Host on:** Vercel (native support)
- **CDN:** Vercel's global edge network (included)
- **Database:** No local DB needed (API handles everything)
- **Cost:** $20–50/month

### For FastAPI (Backend)
- **Month 1–3:** Railway (existing setup)
  - Simple, proven, cheap
  - Auto-deploys on git push
  - Handles prediction model
  
- **Month 4+:** AWS ECS Fargate
  - Containerize FastAPI
  - Use auto-scaling groups
  - Estimated: $100–150/month

### For ML Model (flight_delay_model_v2_weather.joblib)
- **Option 1 (Simpler):** Keep in API container
  - Load joblib on startup
  - Inference in FastAPI endpoint
  - Works for <100 predictions/sec
  
- **Option 2 (More scalable):** Separate ML service
  - AWS SageMaker endpoint
  - Separate from API
  - Auto-scaling
  - Cost: $50–150/month

**Recommendation:** Start with Option 1 (Month 1–3), migrate to Option 2 if latency becomes issue.

### For Database
- **Month 1–3:** Railway PostgreSQL
  - Managed backups
  - Built-in monitoring
  - Easy scaling
  
- **Month 4+:** AWS RDS
  - More control
  - Multi-region replicas
  - Better for large datasets

---

## Part 9: Monitoring & Observability Setup

### Essential Metrics (Day 1)

**Application:**
- Request latency (API response time)
- Error rate (4xx, 5xx responses)
- Prediction latency (model inference time)
- Database query time

**Infrastructure:**
- CPU usage
- Memory usage
- Disk space
- Network I/O

**Business:**
- Signups per day
- Trial conversions
- Predictions made
- Errors per user

### Tools Setup

**Option 1 (Minimal):**
- Railway built-in logs
- Google Analytics (frontend)
- Stripe dashboard (revenue)
- Cost: $0

**Option 2 (Recommended):**
- DataDog (unified monitoring)
- Sentry (error tracking)
- Google Analytics
- Stripe
- Cost: $50–100/month

**Option 3 (Enterprise):**
- DataDog
- Sentry
- PagerDuty
- Custom dashboards
- Cost: $100–150/month

---

## Summary & Action Items

### Recommended Path (Months 1–6)

```
Month 1–3: Railway + Vercel
├─ Cost: $200/month
├─ Capacity: 5K DAU
├─ Action: Setup PostgreSQL, Redis, backups
└─ Trigger to scale: When DAU > 1K or predictions > 500/day

Month 4–6: Migrate to AWS
├─ Cost: $400/month
├─ Capacity: 50K DAU
├─ Action: ECS Fargate, RDS, CloudFront
└─ Trigger to further scale: When DAU > 10K

Month 7+: AWS Production
├─ Cost: $500–800/month (depends on traffic)
├─ Capacity: 100K+ DAU
└─ Action: Multi-region, auto-scaling, advanced monitoring
```

### Do This Week

1. **Migrate to Railway PostgreSQL** (30 min)
   - Add Postgres addon
   - Update .env
   - Run migrations
   - Test

2. **Add Redis cache** (30 min)
   - Add Redis addon
   - Update rate limiting logic
   - Test

3. **Set up monitoring** (1 hour)
   - Railway logs
   - Health checks
   - Alerts

4. **Plan AWS migration** (1 hour)
   - Review Docker setup
   - Estimate ECS cost
   - Create migration checklist

---

**This analysis is ready for implementation. Start with Railway today, plan AWS for Month 4.**