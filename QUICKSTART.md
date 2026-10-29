# Quick Start Guide

Get the Intelligent Loan Approval System running in 5 minutes!

## Prerequisites
- Python 3.8+
- `pip` package manager
- API credentials configured in `.env` (already done)

## 1. Install Dependencies (1 minute)

```bash
cd /home/ubuntu/Desktop/demo
pip install -r requirements.txt
```

## 2. Start the System (30 seconds)

```bash
bash run_all.sh
```

This starts:
1. **4 MCP Servers** (background)
2. **FastAPI Service** (background) 
3. **Streamlit UI** (opens in browser)

Wait for message: "Streamlit app is running at http://localhost:8501"

## 3. Test the System (2 minutes)

### Option A: Use Streamlit UI (Easiest)

1. Browser opens automatically to http://localhost:8501
2. Go to **"Submit Application"** tab
3. Fill form with sample data:
   - Name: "John Doe"
   - Age: 35
   - Monthly Income: $5,000
   - Employment: employed (5 years)
   - Credit Score: 750
   - Loan Amount: $50,000
   - Tenure: 60 months
   - Existing Debt: $1,000

4. Click **"🚀 Submit Application"**
5. See instant decision with risk score and confidence
6. Copy Case ID and check status in **"Check Status"** tab

### Option B: Run Automated Tests

In another terminal:
```bash
cd /home/ubuntu/Desktop/demo
python tests/test_orchestrator.py
```

Should see: ✅ 5/5 tests passed

### Option C: Use curl (Advanced)

```bash
# Submit application
curl -X POST http://localhost:8000/apply-for-loan \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Jane Smith",
    "age": 35,
    "income": 6000,
    "employment_type": "employed",
    "employment_years": 5,
    "credit_score": 780,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "existing_liabilities": 500,
    "location": "California"
  }'
```

Response will include `case_id`. Use it to check status:
```bash
curl http://localhost:8000/loan-status/{case_id}
```

## 4. Explore the System (1 minute)

In Streamlit:
- **📋 Submit Application** - Try different applicants
- **🔍 Check Status** - Look up previous applications
- **📊 History** - See all applications submitted
- **📈 Statistics** - View approval rates and risk metrics

## 5. Stop the System

Press `Ctrl+C` in the terminal running Streamlit

## Test Cases to Try

### Strong Applicant (Should APPROVE)
```
Name: Jane Smith, Age: 35
Income: $8,000/month, Employed for 8 years
Credit Score: 780, Loan: $40,000, DTI: Low
```

### Weak Applicant (Should REJECT)
```
Name: Bob Wilson, Age: 28
Income: $2,000/month, Contract for 6 months
Credit Score: 580, Loan: $100,000, DTI: High
```

### Medium Applicant (Should REVIEW)
```
Name: Alice Johnson, Age: 42
Income: $4,500/month, Employed for 3 years
Credit Score: 680, Loan: $60,000, DTI: Medium
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/apply-for-loan` | POST | Submit application |
| `/loan-status/{case_id}` | GET | Check decision |
| `/list-loans` | GET | View history |
| `/statistics` | GET | View analytics |
| `/docs` | GET | API documentation |

## What's Happening Behind the Scenes

```
USER SUBMISSION
     ↓
[Streamlit UI] ← http://localhost:8501
     ↓ (HTTP POST)
[FastAPI Service] ← http://localhost:8000
     ↓
[LangGraph Orchestrator]
     ↓ (Sequential execution)
┌─────────────────────────────────┐
│ 4 AGENTS                        │
├─────────────────────────────────┤
│1. Applicant Profile Agent       │
│2. Financial Risk Agent          │
│3. Loan Decision Agent           │
│4. Compliance Orchestrator Agent │
└─────────────────────────────────┘
     ↓
[Decision Generated]
     ↓
[Response returned to UI]
     ↓
USER SEES DECISION ✓
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "API Service is not running" | Make sure FastAPI service started. Check port 8000. |
| "Cannot connect to localhost:8501" | Wait 10 seconds for Streamlit to start. Refresh browser. |
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` |
| "Port 8000 already in use" | `lsof -i :8000` then `kill -9 <PID>` |
| Different decisions each time | Normal - Claude adds slight variation. Test multiple times. |

## Architecture Overview

```
PRESENTATION
    ↓
Streamlit Web UI
    ↓
MICROSERVICES
    ↓
FastAPI REST Service
    ↓
ORCHESTRATION
    ↓
LangGraph State Graph
    ↓
AGENTS (4 Independent)
    ↓
MCP SERVERS (4 Data Sources)
    ↓
DECISION & RESPONSE
```

## Next Steps

1. **Try the UI** - Submit several applications
2. **Review decisions** - Understand why each was approved/rejected
3. **Read IMPLEMENTATION.md** - Understand full architecture
4. **Read TESTING.md** - Learn comprehensive testing
5. **Modify code** - Adjust decision rules, add features
6. **Deploy** - Move to production environment

## Support

For issues:
1. Check IMPLEMENTATION.md - Full documentation
2. Check TESTING.md - Testing procedures
3. Check logs in terminal output
4. Verify all services running: http://localhost:8000/health

## Success Indicators

You'll know it's working when:
- ✅ Streamlit page loads without errors
- ✅ API health check responds (http://localhost:8000/health)
- ✅ Loan submission shows decision in < 10 seconds
- ✅ Case ID appears and status can be checked
- ✅ History shows submitted applications
- ✅ Statistics show accurate counts

---

**You're ready!** Run `bash run_all.sh` and start testing. 🚀
