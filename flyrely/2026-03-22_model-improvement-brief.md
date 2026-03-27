# FlyRely Model Improvement Brief
**Author:** Bruce | **Date:** 2026-03-15 | **Updated:** 2026-03-22

---

## Problem Statement

The current ML model has critically low recall: **30.5%** — it misses 7 out of 10 actual delays. This undermines the core value proposition. A user who gets a "Low Risk" prediction and then experiences a severe delay loses trust immediately.

**Note (discovered 2026-03-15):** The live API on Railway is running an older stub version — the real model (fr-engineer's main.py with joblib inference) has not been deployed yet. First priority is deploying the real model, then running this improvement plan.

**Current baseline (threshold 0.30):**
| Metric | Value | Target |
|--------|-------|--------|
| Accuracy | 73.3% | — |
| Precision | 33.0% | ≥40% |
| Recall | **30.5%** | **≥55%** |
| F1 | 31.7% | ≥45% |

Real delay rate: 20.3% | Predicted rate: 18.7%

---

## Step 0: Deploy Real Model (Prerequisite)
fr-engineer must deploy `workspace-flyrely/fr-engineer/flyrely-api/main.py` to Railway before any eval is meaningful. Brief in fr-engineer's memory: `memory/2026-03-15-deploy-task.md`.

---

## Proposed Improvement Plan (Priority Order)

### 1. Threshold Tuning (Fastest, Zero Retraining)
Lower decision threshold from 0.30 → 0.20–0.25. Run sweep at 0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30. Find threshold that maximizes F1 while keeping recall ≥55%.
**Expected:** +15-25 recall points. **Effort:** Low.

### 2. Class Imbalance Fix
Retrain with `class_weight='balanced'`. **Expected:** +10-20 recall points. **Effort:** Low.

### 3. Feature Importance Analysis
Extract importances, identify top/bottom features, retrain on top features only. **Effort:** Low.

### 4. Algorithm Upgrade
Compare GradientBoosting vs XGBoost vs current. Keep winner on F1+recall. **Effort:** Medium.

### 5. Phase 1 Retraining (Visual Crossing Weather)
Run `phase1_retraining.py` — uses BTS data + Visual Crossing historical weather. No AeroAPI needed. **Effort:** Medium.

### 6. AeroAPI Integration (Future)
Blocked on Sean signing up at flightaware.com/aeroapi/

---

## Weekly Eval (OpenSky)
Use `weekly_evaluation.py` to fetch real flight actuals from OpenSky Network (free). Run after real model is deployed to get genuine accuracy metrics.

---

## Approval Protocol
- All model changes on feature branches
- fr-engineer posts before/after metrics to fr-chief → Sean approves before merge to master

---

## Success Criteria
- Recall ≥ 55% | F1 ≥ 45% | Precision ≥ 35% | Accuracy ≥ 70%
