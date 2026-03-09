# Backend Testing Guide

Step-by-step guide to manually test every endpoint. Tests are in chronological order — **follow them in sequence** because later steps depend on data created by earlier ones.

> **Prerequisites**:
> 1. Delete the old `lab_reports.db` file from `server/` (schema changed)
> 2. Server running at `http://localhost:8000` via `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
> 3. Open **http://localhost:8000/docs** (Swagger UI)
>
> **Email Note**: SMTP is disabled by default (`SMTP_ENABLED=false`). Emails are logged to the console instead of being sent. To test real email delivery, configure the SMTP settings in `.env` and set `SMTP_ENABLED=true`.
>
> **Getting the OTP**: Since SMTP is disabled, the OTP won't arrive by email. Instead, check the server console logs — the OTP is logged as `[EMAIL DISABLED] Would send 'Verify Your Email...'`. For testing, you can also query the database directly:
> ```
> python -c "import sqlite3; c=sqlite3.connect('lab_reports.db'); print(c.execute('SELECT email, otp_code FROM users').fetchall())"
> ```

---

## 1. Authentication (with OTP Verification)

### 1.1 Register a New User

**Endpoint**: `POST /auth/register`

**Body**:
```json
{
  "name": "Sameh Test",
  "email": "sameh@test.com",
  "password": "password123",
  "date_of_birth": "1995-06-15"
}
```

**Expected**: `201 Created` with user profile.

**Verification**:
- ✅ `is_verified` is `false`
- ✅ Password is NOT returned
- ✅ Server console shows: `[EMAIL DISABLED] Would send 'Verify Your Email...'`
- ✅ 📧 **OTP Verification Email** would be sent

### 1.2 Try to Login Before Verification (Error Case)

**Endpoint**: `POST /auth/login`

**Body**:
```json
{
  "email": "sameh@test.com",
  "password": "password123"
}
```

**Expected**: `403 Forbidden` — `"Email not verified. Please check your inbox for the OTP code."`

### 1.3 Verify OTP with Wrong Code (Error Case)

**Endpoint**: `POST /auth/verify-otp`

**Body**:
```json
{
  "email": "sameh@test.com",
  "otp_code": "000000"
}
```

**Expected**: `400 Bad Request` — `"Invalid OTP code."`

### 1.4 Get the OTP Code

Run this command in a separate terminal to retrieve the OTP:
```
cd server
.\venv\Scripts\activate
python -c "import sqlite3; c=sqlite3.connect('lab_reports.db'); print(c.execute('SELECT otp_code FROM users WHERE email=\"sameh@test.com\"').fetchone())"
```

### 1.5 Verify OTP (Correct Code)

**Endpoint**: `POST /auth/verify-otp`

**Body** (replace `123456` with the real OTP from step 1.4):
```json
{
  "email": "sameh@test.com",
  "otp_code": "123456"
}
```

**Expected**: `200 OK` with JWT token (auto-login after verification):
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "message": "Email verified successfully. Welcome!"
}
```

**Verification**:
- ✅ `access_token` is returned
- ✅ Console shows: `[EMAIL DISABLED] Would send 'Welcome to LabReport Interpreter!...'`
- ✅ 📧 **Welcome Email** would be sent

**⚠️ IMPORTANT**: Copy the `access_token`. Click the **🔒 Authorize** button in Swagger, paste the token, and click "Authorize".

### 1.6 Try to Verify Again (Error Case)

**Endpoint**: `POST /auth/verify-otp`

**Body**: Same as step 1.5.

**Expected**: `400 Bad Request` — `"Account is already verified."`

### 1.7 Register Duplicate Email (Error Case)

**Endpoint**: `POST /auth/register`

**Body**: Same as step 1.1.

**Expected**: `400 Bad Request` — `"An account with this email already exists."`

### 1.8 Register Short Password (Error Case)

**Endpoint**: `POST /auth/register`

**Body**:
```json
{
  "name": "Short Pass",
  "email": "short@test.com",
  "password": "123"
}
```

**Expected**: `422 Unprocessable Entity` — Validation error.

### 1.9 Resend OTP (for a new unverified user)

First register a second user:

**Endpoint**: `POST /auth/register`
```json
{
  "name": "Second User",
  "email": "second@test.com",
  "password": "password456",
  "date_of_birth": "2000-01-01"
}
```

Then resend OTP:

**Endpoint**: `POST /auth/resend-otp`
```json
{
  "email": "second@test.com"
}
```

**Expected**: `200 OK` — `"A new OTP has been sent to your email."`

### 1.10 Login (Verified User)

**Endpoint**: `POST /auth/login`

**Body**:
```json
{
  "email": "sameh@test.com",
  "password": "password123"
}
```

**Expected**: `200 OK` with JWT token.

### 1.11 Login Wrong Password (Error Case)

**Endpoint**: `POST /auth/login`

**Body**:
```json
{
  "email": "sameh@test.com",
  "password": "wrongpassword"
}
```

**Expected**: `401 Unauthorized` — `"Invalid email or password."`

### 1.12 Get My Profile

**Endpoint**: `GET /auth/me`

**Auth**: Bearer token.

**Expected**: `200 OK`:
```json
{
  "id": 1,
  "name": "Sameh Test",
  "email": "sameh@test.com",
  "is_verified": true,
  ...
}
```

### 1.13 Get Profile Without Token (Error Case)

**Endpoint**: `GET /auth/me`

Remove the token (Authorize → Logout).

**Expected**: `401 Unauthorized`

### 1.14 Change Password

**Endpoint**: `PUT /auth/password`

**Auth**: Bearer token.

**Body**:
```json
{
  "current_password": "password123",
  "new_password": "newpassword456"
}
```

**Expected**: `200 OK` — `"Password updated successfully."`

**Verification**:
- ✅ Console shows: `[EMAIL DISABLED] Would send 'Password Changed...'`
- ✅ 📧 **Password Changed Email** would be sent

Re-login with `newpassword456`, then change back to `password123` for convenience.

---

## 2. Reports

### 2.1 Submit a Manual Report (Mixed Normal+Abnormal)

**Endpoint**: `POST /reports/manual`

**Auth**: Bearer token.

**Body**:
```json
{
  "report_date": "2024-06-15",
  "notes": "Routine annual checkup",
  "lab_values": [
    {"test_name": "Hemoglobin", "value": 14.2, "unit": "g/dL"},
    {"test_name": "Glucose", "value": 130, "unit": "mg/dL"},
    {"test_name": "Total Cholesterol", "value": 245, "unit": "mg/dL"},
    {"test_name": "LDL Cholesterol", "value": 160, "unit": "mg/dL"},
    {"test_name": "HDL Cholesterol", "value": 35, "unit": "mg/dL"},
    {"test_name": "Triglycerides", "value": 200, "unit": "mg/dL"},
    {"test_name": "Creatinine", "value": 1.0, "unit": "mg/dL"},
    {"test_name": "ALT", "value": 30, "unit": "U/L"},
    {"test_name": "TSH", "value": 2.5, "unit": "mIU/L"}
  ]
}
```

**Expected**: `201 Created`

**Verification**:
- ✅ `summary_text` is generated
- ✅ Hemoglobin, Creatinine, ALT, TSH → `"normal"`
- ✅ Glucose, Total Cholesterol, LDL → `"high"`
- ✅ HDL → `"low"` (35 < 40)
- ✅ Triglycerides → `"high"` (200 > 150)
- ✅ Console shows: `[EMAIL DISABLED] Would send 'Your Lab Report is Ready...'`
- ✅ 📧 **Report Ready Email** would be sent
- ✅ Note the report `id` for later steps

### 2.2 Submit a Second Report (All Normal — for Trends)

**Endpoint**: `POST /reports/manual`

**Body**:
```json
{
  "report_date": "2024-12-01",
  "notes": "Follow-up after lifestyle changes",
  "lab_values": [
    {"test_name": "Hemoglobin", "value": 15.0, "unit": "g/dL"},
    {"test_name": "Glucose", "value": 95, "unit": "mg/dL"},
    {"test_name": "Total Cholesterol", "value": 190, "unit": "mg/dL"},
    {"test_name": "LDL Cholesterol", "value": 95, "unit": "mg/dL"},
    {"test_name": "HDL Cholesterol", "value": 52, "unit": "mg/dL"},
    {"test_name": "Triglycerides", "value": 120, "unit": "mg/dL"},
    {"test_name": "Creatinine", "value": 0.9, "unit": "mg/dL"},
    {"test_name": "ALT", "value": 25, "unit": "U/L"},
    {"test_name": "TSH", "value": 2.0, "unit": "mIU/L"}
  ]
}
```

**Expected**: `201 Created` — all values `"normal"`.

### 2.3 Submit a CKD-Pattern Report

**Endpoint**: `POST /reports/manual`

**Body**:
```json
{
  "report_date": "2024-03-01",
  "notes": "Testing CKD pattern detection",
  "lab_values": [
    {"test_name": "Creatinine", "value": 3.5, "unit": "mg/dL"},
    {"test_name": "BUN", "value": 45, "unit": "mg/dL"},
    {"test_name": "Hemoglobin", "value": 9.5, "unit": "g/dL"},
    {"test_name": "Albumin", "value": 2.8, "unit": "g/dL"},
    {"test_name": "Potassium", "value": 5.8, "unit": "mEq/L"},
    {"test_name": "Calcium", "value": 7.5, "unit": "mg/dL"},
    {"test_name": "Glucose", "value": 90, "unit": "mg/dL"}
  ]
}
```

**Expected**: `201 Created` with multiple flagged values and correlation hints.

### 2.4 List All Reports

**Endpoint**: `GET /reports`

**Expected**: `200 OK` — 3 reports, newest first.

### 2.5 Dashboard Stats

**Endpoint**: `GET /reports/dashboard`

**Expected**: `200 OK` — `total_reports: 3`, `flagged_values` > 0.

### 2.6 Get Report Detail

**Endpoint**: `GET /reports/{report_id}` (use id from step 2.1)

**Expected**: `200 OK` with `lab_values`, `summary_text`, `predicted_conditions`, `correlation_hints`.

### 2.7 Non-Existent Report (Error Case)

**Endpoint**: `GET /reports/999`

**Expected**: `404 Not Found`

### 2.8 Delete a Report

**Endpoint**: `DELETE /reports/{report_id}` (use the CKD report id)

**Expected**: `200 OK` — then `GET /reports` should return 2 reports.

---

## 3. Metrics & Trends

### 3.1 List Available Metrics

**Endpoint**: `GET /metrics/available`

**Expected**: `200 OK` — list of test names with counts and latest values.

### 3.2 Hemoglobin Trend

**Endpoint**: `GET /metrics/Hemoglobin/trend`

**Expected**: `200 OK` — 2 data points: 14.2 then 15.0, both normal.

### 3.3 Glucose Trend

**Endpoint**: `GET /metrics/Glucose/trend`

**Expected**: 2 data points: 130 (high) then 95 (normal) — shows improvement.

### 3.4 Non-Existent Test Trend

**Endpoint**: `GET /metrics/FakeTest/trend`

**Expected**: `200 OK` with empty `data_points: []`.

---

## 4. Summary & PDF

### 4.1 Regenerate Summary

**Endpoint**: `POST /summary/{report_id}`

**Expected**: `200 OK` with updated `summary_text`, `predicted_conditions`, `correlation_hints`.

### 4.2 Download PDF

**Endpoint**: `GET /summary/{report_id}/pdf`

**Expected**: PDF file download. Open it and verify:
- ✅ Patient name, report date
- ✅ Color-coded test results table
- ✅ Summary text and disclaimer

### 4.3 PDF for Non-Existent Report

**Endpoint**: `GET /summary/999/pdf`

**Expected**: `404 Not Found`

---

## 5. Account Deletion (Do This Last!)

### 5.1 Delete Account

**Endpoint**: `DELETE /auth/account`

**Auth**: Bearer token.

**Expected**: `200 OK` — `"Account deleted successfully."`

**Verification**:
- ✅ Console shows: `[EMAIL DISABLED] Would send 'Account Deleted...'`
- ✅ 📧 **Account Deleted Email** would be sent
- ✅ `GET /auth/me` with same token → `401 Unauthorized`

---

## Email Summary

| Trigger | Email Sent | Template |
|---|---|---|
| Registration | OTP Verification | 6-digit code, 10min expiry |
| OTP Verified | Welcome | Feature overview |
| Report Processed | Report Ready | Stats cards (tests/flagged) |
| Critical Values Found | Critical Alert 🚨 | Red table of critical values |
| Password Changed | Security Notice | "Wasn't you?" warning |
| Account Deleted | Farewell | Confirmation |

---

## Quick Checklist

| # | Endpoint | Method | Expected | ✓ |
|---|----------|--------|----------|---|
| 1.1 | `/auth/register` | POST | 201 | ☐ |
| 1.2 | `/auth/login` (unverified) | POST | 403 | ☐ |
| 1.3 | `/auth/verify-otp` (wrong) | POST | 400 | ☐ |
| 1.5 | `/auth/verify-otp` (correct) | POST | 200 + JWT | ☐ |
| 1.6 | `/auth/verify-otp` (again) | POST | 400 | ☐ |
| 1.7 | `/auth/register` (dup) | POST | 400 | ☐ |
| 1.8 | `/auth/register` (short pw) | POST | 422 | ☐ |
| 1.9 | `/auth/resend-otp` | POST | 200 | ☐ |
| 1.10 | `/auth/login` | POST | 200 | ☐ |
| 1.11 | `/auth/login` (wrong pw) | POST | 401 | ☐ |
| 1.12 | `/auth/me` | GET | 200 | ☐ |
| 1.13 | `/auth/me` (no token) | GET | 401 | ☐ |
| 1.14 | `/auth/password` | PUT | 200 | ☐ |
| 2.1 | `/reports/manual` | POST | 201 | ☐ |
| 2.2 | `/reports/manual` (2nd) | POST | 201 | ☐ |
| 2.3 | `/reports/manual` (CKD) | POST | 201 | ☐ |
| 2.4 | `/reports` | GET | 200 | ☐ |
| 2.5 | `/reports/dashboard` | GET | 200 | ☐ |
| 2.6 | `/reports/{id}` | GET | 200 | ☐ |
| 2.7 | `/reports/999` | GET | 404 | ☐ |
| 2.8 | `/reports/{id}` | DELETE | 200 | ☐ |
| 3.1 | `/metrics/available` | GET | 200 | ☐ |
| 3.2 | `/metrics/Hemoglobin/trend` | GET | 200 | ☐ |
| 3.3 | `/metrics/Glucose/trend` | GET | 200 | ☐ |
| 3.4 | `/metrics/FakeTest/trend` | GET | 200 | ☐ |
| 4.1 | `/summary/{id}` | POST | 200 | ☐ |
| 4.2 | `/summary/{id}/pdf` | GET | PDF | ☐ |
| 4.3 | `/summary/999/pdf` | GET | 404 | ☐ |
| 5.1 | `/auth/account` | DELETE | 200 | ☐ |
