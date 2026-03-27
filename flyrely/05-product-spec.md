# FlyRely Product Specification

**14 screens, full wireframes, database schema, 20+ API endpoints, 12-week implementation roadmap, and 10+ edge cases solved**

---

## Executive Summary

**Product:** FlyRely is a mobile-first web app (iOS/Android/web) that predicts flight delays 1–2 hours in advance, giving business travelers time to rebook, reschedule, or rest.

**Core Loop:**
1. User books a flight
2. FlyRely analyzes 50+ real-time signals
3. App alerts user 1–2 hours before departure (if delay risk >30%)
4. User decides: rebook, reschedule, or wait
5. Historical prediction recorded (accuracy tracking)

**Target Users:** Business travelers (10+ flights/year), frequent flyers (UA/AA/DL elite), people who value their time.

**Success Metric:** 64.8% prediction accuracy, <5% monthly churn, 60%+ trial-to-paid conversion.

---

## Part 1: 14 Core Screens

### Screen 1: Onboarding / Welcome
```
Purpose: Introduce app, build trust, connect account
Elements:
- Hero image (plane, prediction visualization)
- 3 onboarding slides:
  1. "Know Before It Happens" + explanation
  2. "Accuracy You Can Trust" + 64.8% stat
  3. "Your Privacy Matters" + trust badges
- CTA: "Sign Up" (Google/Apple/email)
- Secondary: "Already have account? Log in"
```

**User flow:**
1. See welcome screen
2. Swipe through 3 slides
3. Tap "Sign Up"
4. Either:
   - OAuth (Google/Apple) — fastest
   - Email + password — traditional
   - Waitlist email + verification link
5. Next: Screen 2 (onboarding settings)

---

### Screen 2: Onboarding / Settings
```
Purpose: Personalize experience, request permissions
Elements:
- "Let's personalize your experience"
- Toggle: "Calendar integration" (connect Google Calendar/Outlook)
- Select: "Primary airline" (dropdown: UA/AA/DL/SW/B6/AS/F9/NK)
- Select: "Frequent flyer status" (dropdown: Economy/Silver/Gold/Platinum)
- Toggle: "Push notifications" (on/off)
- Toggle: "Email alerts" (on/off)
- Toggle: "SMS alerts" (on/off)
- Slider: "Alert threshold" (risk level: Low 20% / Medium 30% / High 50%+)
- CTA: "Continue"
- Secondary: "Skip for now"
```

**Logic:**
- Calendar integration scans for flights
- Frequent flyer status helps personalize messaging
- Alert thresholds let power users filter noise
- Skip option reduces friction

---

### Screen 3: Home / Flight Search
```
Purpose: Add flights, view upcoming predictions
Elements:
- Search bar: "Enter flight number or route (e.g., DCA-ORD)"
- Tabs: "Upcoming" | "Past" | "Saved"
- Search result cards (if flights exist):
  - Flight number + airline
  - Date + time
  - Risk indicator (green/yellow/red pill)
  - Confidence percentage (e.g., "72% confidence delay risk")
  - Tap to expand → Screen 4 (Details)
- Empty state (if no flights):
  - "No upcoming flights"
  - CTA: "Add your first flight"
  - Suggest: "Connect your calendar" (Screen 2)
- Bottom nav: Home | Search | Profile | Settings
```

**User flow:**
1. User on Home screen
2. Types flight number or route in search
3. API returns matching flights (real-time OpenSky data)
4. Taps flight → navigates to Screen 4 (details)
5. Swipe right to save flight for tracking

---

### Screen 4: Flight Details / Prediction
```
Purpose: Show detailed prediction, reasoning, recommended actions
Elements:
- Flight header:
  - Airline logo + flight number (UA 423)
  - Origin → Destination (DCA → ORD)
  - Date + departure time (Mar 15, 2:15 PM ET)
  - Delay status: ✅ "On Time" or 🔴 "High Risk" or 🟡 "Medium Risk"
  
- Risk score (large, center):
  - Circular progress: 72% (with confidence interval ±5%)
  - Below: "Delay Risk: 72% confidence"
  - Small text: "1–2 hour delay predicted"
  
- Reasoning section (collapsible):
  - "Why this prediction:"
  - Weather: "Strong headwinds expected (70% impact)"
  - Aircraft: "Turnover <45 min from previous flight (60% impact)"
  - Airline: "United's on-time rate: 75% (moderate factor)"
  - Time of day: "5 PM departure (peak congestion, 40% impact)"
  
- Recommended actions (if high risk):
  - Green button: "✈️ Rebook" (integrates with airline site)
  - Yellow button: "📅 Reschedule meeting" (calendar integration)
  - Blue button: "📞 Call airline" (auto-dials 1-800 number)
  - Gray button: "ℹ️ Wait for update" (set reminder in 30 min)
  
- Historical context (expandable):
  - "7 days ago: Predicted 68%, actual delay 90 min" ✅
  - "3 weeks ago: Predicted 45%, actual on-time" ✅
  - Accuracy track record for this flight/airline
  
- Passenger info (if connected via calendar):
  - "Your meeting: Sales sync 3:30 PM Chicago"
  - "Connection risk: HIGH" (if flight is leg 1)
  - "Time in Chicago: 90 minutes before next meeting"
  
- Share prediction:
  - "Share with [Passenger 1]" (email/SMS)
  - Generate sharable link: "flyrely.com/predict/xyz123"
```

**Logic:**
- Green (on-time): <20% delay risk
- Yellow (medium): 20–50% delay risk
- Red (high): >50% delay risk
- Confidence interval calculated from model uncertainty
- Reasoning weights shown as percentages (transparency)
- Actions change based on risk level

---

### Screen 5: Flight Search Results
```
Purpose: Show multiple flight options with predictions
Elements:
- Search bar (filled with previous search)
- Filter options (collapsible):
  - Departure time: [Slider: 12 AM – 11 PM]
  - Airline: [Checkboxes: UA, AA, DL, SW, etc.]
  - Delay risk: [High, Medium, Low]
  
- Flight result cards (list view):
  Each card shows:
  - Airline + flight number + duration
  - Departure/arrival time
  - Price (if available from partner API)
  - Risk indicator (green/yellow/red) + prediction %
  - Tap → Screen 4 (details)
  
- Sort options:
  - "Best price"
  - "Lowest delay risk" ⭐ (default for FlyRely)
  - "Earliest departure"
  - "Shortest flight"
```

---

### Screen 6: Upcoming Flights / Dashboard
```
Purpose: Overview of all upcoming trips
Elements:
- Date range selector: "This week" | "Next 7 days" | "Next 30 days" | "Custom"
- Flight cards (vertical list):
  Each shows:
  - Date + day of week (Mon, Mar 15)
  - Flight number + route + time
  - Risk status (green/yellow/red badge)
  - Prediction % + confidence
  - Dropdown arrow (expand → Screen 4 details)
  
- Summary stats (top of screen):
  - "3 upcoming flights"
  - "⚠️ 1 high-risk" (yellow alert)
  - "✅ 2 on-time predicted"
  
- Filters:
  - Airline: [Dropdown]
  - Route: [Dropdown]
  - Risk level: [Toggle]
  
- Empty state:
  - "No flights scheduled"
  - CTA: "Add your first flight" (Screen 3)
```

---

### Screen 7: Settings / Preferences
```
Purpose: Customize alerts, notifications, account
Elements:
- Account section:
  - Avatar + name + email
  - Edit profile
  - Frequent flyer accounts: [List of connected airlines]
    - Add new airline account
    - Remove
  
- Notifications:
  - Toggle: Push notifications
  - Toggle: Email alerts
  - Toggle: SMS alerts
  - Select: Quiet hours (e.g., 10 PM – 7 AM)
  - Select: Alert threshold (Low/Medium/High)
  
- Calendar:
  - Toggle: Google Calendar sync
  - Toggle: Outlook sync
  - Toggle: Apple Calendar sync
  
- Integrations:
  - Connected apps: [List]
    - Slack
    - Discord (notify when delay predicted)
  - Add integration CTA
  
- Privacy & Security:
  - Toggle: Data sharing with airlines (off by default)
  - View privacy policy
  - View terms of service
  - Export my data (GDPR)
  
- About:
  - App version: 1.0.0
  - Help & support
  - Contact us
  - Delete account (warning confirmation)
```

---

### Screen 8: Historical Predictions / Accuracy
```
Purpose: Show user their prediction accuracy over time
Elements:
- Summary stats:
  - "Predictions made: 47"
  - "Accuracy: 72% (user's personal accuracy)"
  - "Delays caught: 18"
  - "Missed delays: 5"
  - "False alarms: 24"
  
- Chart (interactive):
  - Line graph: Predicted vs. Actual delay (time-series)
  - Hover for details
  - X-axis: Last 30 days
  - Y-axis: Delay in minutes
  
- Prediction history (list):
  - Date | Flight | Prediction | Actual | ✅/❌
  - Mar 15 | UA 423 | 72% | 90 min delay | ✅
  - Mar 13 | AA 101 | 45% | On-time | ❌
  - Mar 10 | DL 999 | 15% | On-time | ✅
  - Tap row → details + reasoning
  
- Export options:
  - Download CSV
  - Download PDF report
  - Share with airline/company
```

---

### Screen 9: Profile / Account
```
Purpose: View account info, subscription, billing
Elements:
- Profile header:
  - Avatar
  - Name
  - Email
  - Member since: [Date]
  
- Subscription section:
  - Current plan: "Premium Monthly" or "Free Trial"
  - Status: "Active" or "Trial ends in 5 days"
  - Renews: [Date]
  - CTA: "Upgrade" or "Manage billing"
  
- Stats:
  - Predictions made: 47
  - Flights tracked: 23
  - Delays avoided: 18
  
- Actions:
  - Edit profile
  - Referral link: "Invite friends → 50% off" (copy to clipboard)
  - Billing history (invoices)
  - Payment method (edit)
  
- Logout button
```

---

### Screen 10: Notification / Alert (In-App)
```
Purpose: Alert user in real-time to delay prediction
Elements:
- Full-screen modal (iOS) or snackbar (Android):
  - Top: Airline logo + flight number
  - Large text: "⚠️ DELAY ALERT"
  - Subtext: "UA 423 DCA→ORD | 72% delay risk"
  - Body: "You have ~90 minutes to rebook"
  
- Action buttons:
  - Primary: "View Details" (Screen 4)
  - Secondary: "Dismiss"
  - Tertiary: "Snooze 30 min"
  
- Sound/vibration: Yes (respects mute switch)
- Notification badge: Red dot on app icon
```

---

### Screen 11: Referral / Share Program
```
Purpose: Enable viral growth (referral loop)
Elements:
- Referral header:
  - "Invite friends & earn rewards"
  - "You both get 50% off for 1 month"
  
- Your referral link:
  - QR code + static URL
  - CTA: "Copy link" (to clipboard)
  - CTA: "Share" (opens share sheet: WhatsApp/SMS/Email/Twitter)
  
- Leaderboard (optional):
  - Top referrers this month
  - Your rank: #47
  - Referrals you've made: 3
  
- Referral history:
  - Invited [Friend 1] on Mar 10 → Status: Joined
  - Invited [Friend 2] on Mar 5 → Status: Joined
  - Invited [Friend 3] on Feb 28 → Status: Pending
  
- Rewards earned:
  - 1 free month (from 3 friends)
  - $20 credit remaining
```

---

### Screen 12: Comparison / Discovery
```
Purpose: Help users understand FlyRely vs. competitors
Elements:
- Hero: "How FlyRely Compares"
- Comparison table:
  - Columns: FlyRely | Flighty | Airline Apps
  - Rows:
    - Prediction timing
    - Accuracy
    - Real-time tracking
    - Multi-leg support
    - Calendar integration
    - Privacy
    - Price
  
- Detailed comparison (expandable)
- CTA: "Try FlyRely free for 7 days"
```

---

### Screen 13: Feedback / Bug Report
```
Purpose: Collect user feedback
Elements:
- Radio buttons:
  - "Report a bug"
  - "Suggest a feature"
  - "General feedback"
  
- Text area:
  - "Tell us what's on your mind..."
  - Max 500 characters
  
- Optional email:
  - "Email (optional, so we can follow up)"
  
- Attachment:
  - "Attach screenshot" (tap to add)
  
- Submit button
- Confirmation: "Thanks! We read every piece of feedback."
```

---

### Screen 14: Paywall / Subscription
```
Purpose: Convince users to upgrade
Elements:
- Hero headline:
  - "Unlock full power of FlyRely"
  
- Feature comparison (Free vs. Premium):
  - Free:
    - 5 predictions/month
    - Delay alerts (basic)
    - 7-day history
  - Premium:
    - ✅ Unlimited predictions
    - ✅ Advanced alerts
    - ✅ Full prediction history
    - ✅ Calendar integration
    - ✅ Email support
  
- Pricing options:
  - Monthly: $9.99/month (highlighted)
  - Annual: $99/year (save $20!)
  - Early access: 50% off (limited time)
  
- Social proof:
  - "47,000 travelers trust FlyRely"
  - "4.8 ⭐ rating"
  - "Saves 4+ hours/year"
  
- CTA: "Start free 7-day trial" (no card required)
- Subtext: "Renews at $9.99/month. Cancel anytime."
- Legal: "Terms" | "Privacy"
```

---

## Part 2: Wireframes (ASCII Mock-ups)

### Screen 4 Detailed Wireframe: Flight Details / Prediction

```
┌─────────────────────────────────────────┐
│  ← UA 423 | DCA → ORD | Mar 15, 2:15 PM │
├─────────────────────────────────────────┤
│                                         │
│           🟢 ON TIME PREDICTED          │
│                                         │
│              72% ± 5% CONFIDENCE        │
│         (Delay Risk: 1–2 hours)         │
│                                         │
│    ┌───────────────────────────────┐    │
│    │  Why this prediction?          │    │
│    │  • Weather: 70% impact         │    │
│    │  • Aircraft turnover: 60%      │    │
│    │  • Peak departure hours: 40%   │    │
│    │  • Airline metrics: 30%        │    │
│    └───────────────────────────────┘    │
│                                         │
│    ┌───────────────────────────────┐    │
│    │ ✈️ REBOOK                     │    │
│    │ (Opens airline booking)        │    │
│    └───────────────────────────────┘    │
│                                         │
│    ┌───────────────────────────────┐    │
│    │ 📅 RESCHEDULE MEETING        │    │
│    │ (Sales sync 3:30 PM Chicago)  │    │
│    └───────────────────────────────┘    │
│                                         │
│    ┌───────────────────────────────┐    │
│    │ 📞 CALL UNITED                │    │
│    │ (Auto-dial 1-800-UNITED)      │    │
│    └───────────────────────────────┘    │
│                                         │
│    Accuracy history:                    │
│    Mar 8: Predicted 68% → 90 min ✅     │
│    Mar 1: Predicted 40% → On-time ✅    │
│                                         │
└─────────────────────────────────────────┘
```

---

## Part 3: Database Schema

### Core Tables

**Table: users**
```sql
id (UUID, PK)
email (VARCHAR, unique)
password_hash (VARCHAR)
first_name (VARCHAR)
last_name (VARCHAR)
phone (VARCHAR, nullable)
profile_picture_url (VARCHAR, nullable)
primary_airline (ENUM: UA/AA/DL/SW/B6/AS/F9/NK)
frequent_flyer_status (ENUM: Economy/Silver/Gold/Platinum)
timezone (VARCHAR, default: America/New_York)
notification_settings_json (JSON) — push, email, SMS preferences
calendar_integrations_json (JSON) — Google/Outlook/Apple connections
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
deleted_at (TIMESTAMP, nullable) — soft delete
```

**Table: flights**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
iata_flight_number (VARCHAR, e.g., "UA423")
aircraft_icao (VARCHAR, e.g., "B789")
origin_airport (VARCHAR, e.g., "DCA")
destination_airport (VARCHAR, e.g., "ORD")
scheduled_departure_utc (TIMESTAMP)
scheduled_arrival_utc (TIMESTAMP)
airline_code (VARCHAR, e.g., "UA")
is_saved (BOOLEAN) — user saved for tracking
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
opensky_flight_id (VARCHAR, nullable) — for live tracking
```

**Table: predictions**
```sql
id (UUID, PK)
flight_id (UUID, FK → flights)
user_id (UUID, FK → users)
delay_probability (FLOAT, 0.0–1.0) — e.g., 0.72 = 72%
confidence_interval (FLOAT) — ±5%
predicted_delay_minutes (INT, nullable) — e.g., 75
reasoning_json (JSON) — breakdown of factors
- { "weather": 0.70, "aircraft_turnover": 0.60, "airline_metrics": 0.30 }
model_version (VARCHAR, e.g., "v2_weather")
created_at (TIMESTAMP)
prediction_made_at (TIMESTAMP) — when prediction was generated (1-2h before departure)
actual_delay_minutes (INT, nullable) — filled after flight lands
is_accurate (BOOLEAN, nullable) — true if |predicted - actual| < 30 min
created_at (TIMESTAMP)
```

**Table: notifications**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
prediction_id (UUID, FK → predictions)
flight_id (UUID, FK → flights)
notification_type (ENUM: PUSH/EMAIL/SMS)
status (ENUM: SENT/FAILED/BOUNCED/DELIVERED)
message_text (TEXT)
sent_at (TIMESTAMP)
delivered_at (TIMESTAMP, nullable)
opened_at (TIMESTAMP, nullable)
clicked_at (TIMESTAMP, nullable)
created_at (TIMESTAMP)
```

**Table: subscriptions**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
plan_type (ENUM: FREE/MONTHLY/ANNUAL/EARLY_ACCESS)
status (ENUM: ACTIVE/CANCELLED/EXPIRED)
started_at (TIMESTAMP)
expires_at (TIMESTAMP)
stripe_subscription_id (VARCHAR, nullable)
stripe_customer_id (VARCHAR, nullable)
monthly_charge_cents (INT, e.g., 999 = $9.99)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Table: referrals**
```sql
id (UUID, PK)
referrer_user_id (UUID, FK → users)
referred_user_id (UUID, FK → users, nullable) — NULL until friend signs up
referral_code (VARCHAR, unique)
reward_type (ENUM: CREDIT/DISCOUNT/FREE_MONTH)
reward_amount (INT, in cents or count)
status (ENUM: PENDING/COMPLETED)
created_at (TIMESTAMP)
completed_at (TIMESTAMP, nullable)
```

---

## Part 4: API Endpoints (20+ endpoints)

### Authentication

**POST /auth/signup**
```
Request:
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
Response:
{
  "user_id": "uuid",
  "email": "user@example.com",
  "access_token": "jwt",
  "refresh_token": "jwt"
}
```

**POST /auth/login**
```
Request:
{
  "email": "user@example.com",
  "password": "secure_password"
}
Response:
{
  "user_id": "uuid",
  "access_token": "jwt",
  "refresh_token": "jwt"
}
```

**POST /auth/logout**
```
Auth: Bearer [access_token]
Response: { "status": "logged_out" }
```

---

### Flights

**GET /flights/search**
```
Query params:
- origin (required): "DCA"
- destination (required): "ORD"
- departure_date (required): "2026-03-15"
- airline (optional): "UA"

Response:
{
  "flights": [
    {
      "id": "uuid",
      "flight_number": "UA423",
      "aircraft": "B789",
      "departure_utc": "2026-03-15T18:15:00Z",
      "arrival_utc": "2026-03-15T21:45:00Z",
      "airline_code": "UA"
    }
  ]
}
```

**POST /flights/add**
```
Auth: Bearer [access_token]
Request:
{
  "flight_number": "UA423",
  "departure_date": "2026-03-15",
  "origin": "DCA",
  "destination": "ORD"
}
Response:
{
  "flight_id": "uuid",
  "saved": true
}
```

**GET /flights/:id**
```
Auth: Bearer [access_token]
Response:
{
  "id": "uuid",
  "flight_number": "UA423",
  "origin": "DCA",
  "destination": "ORD",
  "scheduled_departure": "2026-03-15T18:15:00Z",
  "is_saved": true
}
```

**GET /flights**
```
Auth: Bearer [access_token]
Query params:
- status: "upcoming" | "past" | "all"
- limit: 20
- offset: 0

Response:
{
  "flights": [...],
  "total": 47,
  "limit": 20,
  "offset": 0
}
```

**DELETE /flights/:id**
```
Auth: Bearer [access_token]
Response: { "status": "deleted" }
```

---

### Predictions

**GET /predictions/:flight_id**
```
Auth: Bearer [access_token]
Response:
{
  "prediction_id": "uuid",
  "flight_id": "uuid",
  "delay_probability": 0.72,
  "confidence_interval": 0.05,
  "predicted_delay_minutes": 75,
  "reasoning": {
    "weather": 0.70,
    "aircraft_turnover": 0.60,
    "airline_metrics": 0.30,
    "time_of_day": 0.40
  },
  "model_version": "v2_weather",
  "created_at": "2026-03-15T16:15:00Z"
}
```

**GET /predictions**
```
Auth: Bearer [access_token]
Query params:
- flight_id (optional)
- limit: 20
- offset: 0

Response:
{
  "predictions": [...],
  "total": 47
}
```

**POST /predictions/:flight_id/feedback**
```
Auth: Bearer [access_token]
Request:
{
  "actual_delay_minutes": 90,
  "notes": "Flight was delayed due to weather"
}
Response:
{
  "prediction_id": "uuid",
  "is_accurate": true,
  "accuracy_percentage": 72.5
}
```

---

### Notifications

**GET /notifications**
```
Auth: Bearer [access_token]
Query params:
- limit: 20
- offset: 0

Response:
{
  "notifications": [
    {
      "id": "uuid",
      "flight_id": "uuid",
      "message": "UA423 DCA→ORD flagged for 72% delay risk",
      "type": "PUSH",
      "sent_at": "2026-03-15T16:15:00Z",
      "opened": true
    }
  ]
}
```

**POST /notifications/preferences**
```
Auth: Bearer [access_token]
Request:
{
  "push_enabled": true,
  "email_enabled": true,
  "sms_enabled": false,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "07:00",
  "alert_threshold": "HIGH"
}
Response: { "status": "updated" }
```

---

### Subscriptions

**GET /subscriptions/current**
```
Auth: Bearer [access_token]
Response:
{
  "plan_type": "MONTHLY",
  "status": "ACTIVE",
  "started_at": "2026-03-01T00:00:00Z",
  "expires_at": "2026-04-01T00:00:00Z",
  "amount_cents": 999
}
```

**POST /subscriptions/upgrade**
```
Auth: Bearer [access_token]
Request:
{
  "plan_type": "ANNUAL",
  "stripe_token": "tok_visa"
}
Response:
{
  "subscription_id": "uuid",
  "plan_type": "ANNUAL",
  "status": "ACTIVE"
}
```

**POST /subscriptions/cancel**
```
Auth: Bearer [access_token]
Response: { "status": "cancelled", "effective_date": "2026-04-01" }
```

---

### Account / User

**GET /user/profile**
```
Auth: Bearer [access_token]
Response:
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "primary_airline": "UA",
  "frequent_flyer_status": "Gold",
  "timezone": "America/New_York"
}
```

**PATCH /user/profile**
```
Auth: Bearer [access_token]
Request:
{
  "first_name": "Jane",
  "primary_airline": "AA"
}
Response: { "status": "updated" }
```

**POST /user/calendar/connect**
```
Auth: Bearer [access_token]
Request:
{
  "provider": "google", — or "outlook", "apple"
  "auth_code": "4/..." — OAuth code from provider
}
Response: { "status": "connected" }
```

---

### Referrals

**GET /referrals**
```
Auth: Bearer [access_token]
Response:
{
  "referral_code": "JOHN_ABC123",
  "referrals_made": 3,
  "referrals_converted": 2,
  "reward_balance": "$20 credit",
  "referral_link": "https://flyrely.com?ref=JOHN_ABC123"
}
```

**POST /referrals/share**
```
Auth: Bearer [access_token]
Request:
{
  "platform": "email" — or "sms", "twitter", "facebook"
}
Response:
{
  "share_url": "https://flyrely.com?ref=JOHN_ABC123",
  "message": "I just joined FlyRely..."
}
```

---

### Analytics

**GET /analytics/accuracy**
```
Auth: Bearer [access_token]
Query params:
- days: 30 (default)

Response:
{
  "total_predictions": 47,
  "accurate_predictions": 34,
  "accuracy_percentage": 72.3,
  "false_alarms": 13,
  "missed_delays": 5,
  "by_airline": {
    "UA": { "accuracy": 75.0, "count": 20 },
    "AA": { "accuracy": 68.0, "count": 15 },
    "DL": { "accuracy": 70.0, "count": 12 }
  }
}
```

---

## Part 5: 12-Week Implementation Roadmap

### Phase 1: Auth & Core (Weeks 1–2)
**Goal:** Users can sign up, log in, manage account

Deliverables:
- [x] User authentication (email + OAuth)
- [x] User database + schema
- [x] JWT token management
- [x] Password reset flow
- [x] Onboarding screens (1–2)
- [x] Profile settings

**Tech stack:**
- Backend: Next.js API routes + Supabase/Firebase Auth
- Frontend: React + TypeScript + Zustand (state management)
- Database: PostgreSQL

---

### Phase 2: Flight Integration (Weeks 3–4)
**Goal:** Users can search, add, and save flights

Deliverables:
- [x] Flight search API (OpenSky integration)
- [x] Flight database schema
- [x] Home screen + flight list
- [x] Flight details screen
- [x] Save/unsave flights
- [x] Calendar sync (Google/Outlook)

**APIs integrated:**
- OpenSky Network (real-time flight data)
- Google Calendar API

---

### Phase 3: Predictions (Weeks 5–6)
**Goal:** Generate and display delay predictions

Deliverables:
- [x] Prediction model API endpoint (calls to backend ML service)
- [x] Real-time prediction generation
- [x] Prediction display screen
- [x] Confidence intervals
- [x] Reasoning breakdown
- [x] Prediction history tracking

**Integration:**
- ML model server (calls to `/predict` endpoint)
- Weather API (Tomorrow.io)
- Historical delay data (BTS)

---

### Phase 4: Notifications (Weeks 7–8)
**Goal:** Alert users about delays in real-time

Deliverables:
- [x] Push notifications (Firebase Cloud Messaging)
- [x] Email notifications (SendGrid)
- [x] SMS notifications (Twilio)
- [x] Notification preferences screen
- [x] Quiet hours + alert thresholds
- [x] Notification history

**Services:**
- Firebase Cloud Messaging
- SendGrid
- Twilio

---

### Phase 5: Dashboard & Analytics (Weeks 9–10)
**Goal:** Users see their prediction accuracy

Deliverables:
- [x] Upcoming flights dashboard
- [x] Prediction accuracy tracking
- [x] Historical prediction list
- [x] Analytics charts (accuracy over time)
- [x] Export functionality (CSV/PDF)
- [x] Referral program screen

**Metrics tracked:**
- Predictions made
- Accuracy percentage
- Delays caught
- False alarms
- Missed delays

---

### Phase 6: Monetization & Polish (Weeks 11–12)
**Goal:** Enable subscriptions and refine UX

Deliverables:
- [x] Paywall screen
- [x] Stripe integration (payment processing)
- [x] Subscription management
- [x] Trial period logic (7 days, no card)
- [x] Plan limits (Free vs. Premium)
- [x] Bug fixes + UI polish
- [x] Performance optimization
- [x] Security audit

**Payment processing:**
- Stripe (subscriptions, invoicing)
- Stripe webhooks (subscription events)

---

## Part 6: State Management (Zustand Stores)

### Store 1: authStore
```typescript
{
  // State
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  signUp(email, password, name)
  login(email, password)
  logout()
  updateProfile(updates)
  refreshAccessToken()
}
```

### Store 2: flightStore
```typescript
{
  // State
  flights: Flight[]
  selectedFlight: Flight | null
  isLoading: boolean
  filters: { airline, departure_date, origin, destination }
  
  // Actions
  searchFlights(origin, destination, date)
  addFlight(flight)
  removeFlight(flightId)
  selectFlight(flightId)
  filterFlights(filters)
}
```

### Store 3: predictionStore
```typescript
{
  // State
  predictions: Prediction[]
  selectedPrediction: Prediction | null
  isLoading: boolean
  accuracy: { total, accurate, percentage }
  
  // Actions
  fetchPrediction(flightId)
  fetchPredictions(limit, offset)
  submitFeedback(predictionId, actualDelay)
  calculateAccuracy()
}
```

### Store 4: notificationStore
```typescript
{
  // State
  notifications: Notification[]
  preferences: NotificationPreferences
  unreadCount: number
  
  // Actions
  fetchNotifications()
  markAsRead(notificationId)
  updatePreferences(preferences)
  deleteNotification(notificationId)
}
```

### Store 5: uiStore
```typescript
{
  // State
  theme: "light" | "dark"
  showPaywall: boolean
  activeTab: string
  
  // Actions
  toggleTheme()
  showPaywall()
  closePaywall()
  setActiveTab(tab)
}
```

---

## Part 7: 10+ Edge Cases Solved

### Edge Case 1: Flight doesn't exist in OpenSky
**Problem:** User enters flight number that's not scheduled yet
**Solution:**
- API returns empty result
- UI shows: "Flight not found. Try a different date or airline."
- Suggest: "Check your flight number (e.g., UA423)"

### Edge Case 2: User has no upcoming flights
**Problem:** Dashboard shows empty state
**Solution:**
- Show: "No upcoming flights"
- CTA: "Add your first flight" + link to search
- Suggest: "Connect your calendar to auto-import flights"

### Edge Case 3: Prediction changes between checks
**Problem:** User checks same flight twice, gets different prediction (as departure gets closer, model refines)
**Solution:**
- Show prediction history: "Mar 15, 4 PM: 72% | Mar 15, 5 PM: 85%"
- Explain: "Prediction refined as departure approaches"
- Allow user to dismiss old prediction notification

### Edge Case 4: Flight is already delayed when user checks
**Problem:** Flight is already delayed by airlines (user can't rebook)
**Solution:**
- API detects: live delay status from OpenSky
- UI shows: "Flight already delayed by [X] minutes"
- Actions change: Instead of "Rebook," show "Check rebooking options"
- Suggest: "Call airline for compensation options"

### Edge Case 5: User's calendar sync fails
**Problem:** Google Calendar API returns 401 (token expired)
**Solution:**
- UI shows: "Calendar sync failed. Re-authorize?"
- CTA: "Reconnect Google" → OAuth flow
- Graceful degradation: App still works without calendar

### Edge Case 6: Payment fails on subscription renewal
**Problem:** User's card is declined at renewal time
**Solution:**
- Email user: "Your subscription renewal failed"
- In-app banner: "Update payment method to continue"
- Grace period: 7 days to update before subscription cancels
- After 7 days: Downgrade to free tier

### Edge Case 7: User has no frequent flyer number
**Problem:** Flight connects to airline account, but user doesn't have FF number
**Solution:**
- Settings: "Frequent flyer accounts (optional)"
- Allow null values
- Don't require FF number
- Personalization still works (by airline choice)

### Edge Case 8: Prediction model is unavailable
**Problem:** ML model server is down
**Solution:**
- API returns cached prediction (if available from <1h ago)
- If no cache: Show "Prediction service temporarily unavailable. Try again in a few minutes."
- Show last known state (e.g., "72% as of 4:00 PM")

### Edge Case 9: User deletes account
**Problem:** User requests account deletion (GDPR)
**Solution:**
- Soft delete: Set `deleted_at` timestamp
- Keep user data (for audit/legal)
- Hard delete after 30-day grace period
- Cancel subscription immediately
- Send confirmation email

### Edge Case 10: Referral link is invalid
**Problem:** User clicks old/invalid referral code
**Solution:**
- Check if referral code exists and is valid
- If invalid: Show "This referral code has expired"
- Offer: "Sign up normally or ask your friend for a new code"
- Track invalid codes (for support team to investigate)

---

## Part 8: Success Metrics & KPIs

### User Acquisition
- Target: 200–300 trial signups by end of Month 3
- CAC (Cost Acquisition): $0–15
- Organic vs. Paid: 70% organic, 30% paid

### Engagement
- DAU (Daily Active Users): 60%+ of monthly users
- Predictions per user per month: 15+ (on average)
- Flights tracked per user: 10+
- Session duration: 3–5 minutes (average)

### Retention
- Day 1 retention: 70%
- Day 7 retention: 50%
- Day 30 retention: 35%
- Churn rate: <5% monthly (paid customers)

### Revenue
- Trial-to-paid conversion: 25–40%
- Monthly churn: <5%
- LTV (Lifetime Value): $297 (3 years at $99/year)
- MRR (Month 3): $5–10K

### Product Quality
- App store rating: 4.5+ (iOS/Android)
- Crash rate: <0.1%
- Prediction accuracy: 64.8%+ (published)
- Notification delivery: 95%+ (push), 99%+ (email)

---

**This product specification is ready for engineering implementation.**