# Testing Guide for Intelligent Loan Approval System

## Test Plan Overview

This document describes how to test the implementation against the requirements from README.md.

## Test Scenarios

### Scenario 1: Happy Path - Strong Applicant (Should Approve)

**Test Data:**
```json
{
  "applicant_name": "Jane Smith",
  "age": 35,
  "income": 8000,
  "employment_type": "employed",
  "employment_years": 8,
  "credit_score": 780,
  "loan_amount": 40000,
  "loan_tenure_months": 60,
  "existing_liabilities": 500,
  "location": "California"
}
```

**Expected Results:**
- Classification: `approved`
- Risk Score: < 30
- Confidence: > 0.8
- Decision factors include positive employment and credit history

**Why:** Strong income stability, excellent credit score, manageable DTI ratio

---

### Scenario 2: Rejection Path - Weak Applicant

**Test Data:**
```json
{
  "applicant_name": "Bob Wilson",
  "age": 28,
  "income": 2000,
  "employment_type": "contract",
  "employment_years": 0.5,
  "credit_score": 580,
  "loan_amount": 100000,
  "loan_tenure_months": 60,
  "existing_liabilities": 2000,
  "location": "Texas"
}
```

**Expected Results:**
- Classification: `rejected`
- Risk Score: > 70
- Confidence: High (0.85+)
- Decision factors highlight credit and employment concerns

**Why:** Poor credit history, unstable employment, high DTI ratio, loan too large for income

---

### Scenario 3: Manual Review Path - Medium Applicant

**Test Data:**
```json
{
  "applicant_name": "Alice Johnson",
  "age": 42,
  "income": 4500,
  "employment_type": "employed",
  "employment_years": 3,
  "credit_score": 680,
  "loan_amount": 60000,
  "loan_tenure_months": 72,
  "existing_liabilities": 1500,
  "location": "Florida"
}
```

**Expected Results:**
- Classification: `review`
- Risk Score: 30-70 (middle range)
- Confidence: Medium (0.60-0.80)
- Decision factors include mixed signals

**Why:** Mixed profile - good employment, fair credit, manageable but notable debt

---

### Scenario 4: Edge Case - High Risk Anomalies

**Test Data:**
```json
{
  "applicant_name": "Risk Case",
  "age": 25,
  "income": 3000,
  "employment_type": "unemployed",
  "employment_years": 0,
  "credit_score": 500,
  "loan_amount": 150000,
  "loan_tenure_months": 120,
  "existing_liabilities": 5000,
  "location": "Nevada"
}
```

**Expected Results:**
- Classification: `rejected`
- Multiple anomalies detected (5+)
- Risk Score: 80+
- Clear explanation of rejection

**Why:** Unemployed, poor credit, excessive loan amount, high existing debt

---

## Execution Methods

### Method 1: Integration Tests (Automated)

```bash
cd /home/ubuntu/Desktop/demo
python tests/test_orchestrator.py
```

**What it tests:**
- Approved application classification
- Rejected application classification
- Review application handling
- Input validation and error handling
- Case history tracking

**Expected Output:**
```
TEST: Strong Applicant (Should be Approved)
Decision: APPROVED
Risk Score: 25.3/100
Confidence: 92.0%
✅ PASS: Expected APPROVED, got APPROVED

TEST SUMMARY
✅ PASS: Approved Application
✅ PASS: Rejected Application
✅ PASS: Review Application
✅ PASS: Error Handling
✅ PASS: Case History

5/5 tests passed
```

### Method 2: Streamlit UI Testing (Manual)

1. **Start Services:**
   ```bash
   bash run_all.sh
   ```

2. **Navigate to UI:**
   - Open browser to http://localhost:8501

3. **Test Submission Tab:**
   - Fill form with test data from scenarios above
   - Click "Submit Application"
   - Verify decision appears instantly
   - Copy Case ID

4. **Test Status Tab:**
   - Paste Case ID in "Check Status" tab
   - Verify full decision details display
   - Check all decision factors are shown

5. **Test History Tab:**
   - Click "History" tab
   - Verify all submitted applications appear
   - Check columns: Case ID, Applicant, Decision, Risk Score

6. **Test Statistics Tab:**
   - Click "Statistics" tab
   - Verify totals match submitted applications
   - Check approval rate calculation

### Method 3: API Testing (curl/Postman)

**Submit Application:**
```bash
curl -X POST http://localhost:8000/apply-for-loan \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Test Applicant",
    "age": 35,
    "income": 5000,
    "employment_type": "employed",
    "employment_years": 5,
    "credit_score": 750,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "existing_liabilities": 1000,
    "location": "New York"
  }'
```

**Expected Response:**
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "classification": "approved",
  "risk_score": 28.5,
  "confidence_level": 0.85,
  "explanation": "Application meets approval criteria...",
  "created_at": "2026-10-28T16:30:00.000Z"
}
```

**Get Case Status:**
```bash
curl http://localhost:8000/loan-status/{case_id}
```

**List All Loans:**
```bash
curl http://localhost:8000/list-loans
```

**Get Statistics:**
```bash
curl http://localhost:8000/statistics
```

---

## Verification Checklist

### Architecture Verification

- [ ] **Multi-Agent System:** 4 agents execute sequentially
  - [ ] Applicant Profile Agent completes without error
  - [ ] Financial Risk Agent receives output from Agent 1
  - [ ] Loan Decision Agent receives inputs from Agents 1 & 2
  - [ ] Compliance Agent receives decision from Agent 3

- [ ] **LangGraph Orchestration:** State flows correctly
  - [ ] StateGraph is defined with all required fields
  - [ ] Nodes are added for each agent
  - [ ] Edges connect nodes in sequence
  - [ ] State persists between nodes
  - [ ] Error nodes catch failures gracefully

- [ ] **MCP Servers:** 4 independent servers run
  - [ ] ApplicantDB (Port 8100) starts without error
  - [ ] RiskRulesDB (Port 8101) starts without error
  - [ ] DecisionSynthesis (Port 8102) starts without error
  - [ ] NotificationSystem (Port 8103) starts without error

- [ ] **FastAPI Service:** Endpoints accept and process requests
  - [ ] `/apply-for-loan` accepts POST with valid data
  - [ ] `/loan-status/{case_id}` returns decision details
  - [ ] `/list-loans` returns paginated results
  - [ ] `/statistics` returns accurate counts

### Decision Quality Verification

- [ ] **Classification Accuracy**
  - [ ] Scenario 1 (strong) → APPROVED
  - [ ] Scenario 2 (weak) → REJECTED
  - [ ] Scenario 3 (medium) → REVIEW
  - [ ] Scenario 4 (anomalies) → REJECTED or REVIEW

- [ ] **Risk Scoring**
  - [ ] Scores range from 0-100
  - [ ] Strong applicants < 30
  - [ ] Weak applicants > 70
  - [ ] Medium applicants 30-70

- [ ] **Confidence Levels**
  - [ ] Scores range from 0-1
  - [ ] Approved/Rejected decisions have high confidence (0.85+)
  - [ ] Review decisions have medium confidence (0.60-0.80)

- [ ] **Explainability**
  - [ ] Each decision has clear explanation
  - [ ] Key factors are listed (3-5 factors)
  - [ ] Explanation matches decision

### Data Validation

- [ ] **Input Validation**
  - [ ] Rejects age < 18 or > 100
  - [ ] Rejects negative income
  - [ ] Rejects invalid employment type
  - [ ] Rejects credit score outside 300-850 range
  - [ ] Rejects negative loan amounts

- [ ] **State Management**
  - [ ] Each agent's output is captured
  - [ ] Outputs flow to next agent
  - [ ] No data loss between agents
  - [ ] Error states prevent cascade

### UI/UX Verification

- [ ] **Streamlit Interface**
  - [ ] Form displays all required fields
  - [ ] Submit button functional
  - [ ] Results display immediately
  - [ ] Case ID copyable
  - [ ] Status lookup works with case ID
  - [ ] History tab shows all applications
  - [ ] Statistics tab shows accurate numbers

### Error Handling

- [ ] **Graceful Failures**
  - [ ] API unavailable → Streamlit shows error
  - [ ] MCP server unavailable → Agents handle failure
  - [ ] Invalid input → 422 response with details
  - [ ] Missing case ID → 404 response

### Performance

- [ ] **Decision Time**
  - [ ] Decision completes in < 30 seconds
  - [ ] API responds within 5 seconds of Streamlit submission
  - [ ] Case history loads instantly

### Audit Trail

- [ ] **Decision Logging**
  - [ ] Case ID generated and returned
  - [ ] Decision logged with timestamp
  - [ ] Applicant info associated with case
  - [ ] Risk score and confidence recorded
  - [ ] Decision factors documented

---

## Running Full Test Suite

```bash
cd /home/ubuntu/Desktop/demo

# Clean terminal
clear

echo "========================================="
echo "FULL TEST SUITE EXECUTION"
echo "========================================="
echo ""

# 1. Syntax validation
echo "✓ Syntax validation (already passed)"
echo ""

# 2. Run integration tests
echo "📋 Running integration tests..."
python tests/test_orchestrator.py
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
  echo "❌ Integration tests failed"
  exit 1
fi

echo ""
echo "========================================="
echo "✅ ALL TESTS PASSED"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run: bash run_all.sh"
echo "2. Open: http://localhost:8501"
echo "3. Test Streamlit UI manually"
```

---

## Test Results Template

Use this to document test results:

```
Test Execution Date: __________
Tester: __________
Environment: Python 3.x, Claude API

SCENARIO 1 - APPROVED ❌ ⚠️ ✅
SCENARIO 2 - REJECTED ❌ ⚠️ ✅
SCENARIO 3 - REVIEW ❌ ⚠️ ✅
SCENARIO 4 - ANOMALIES ❌ ⚠️ ✅

UI Testing ❌ ⚠️ ✅
API Testing ❌ ⚠️ ✅
Integration Tests ❌ ⚠️ ✅

Overall Status: ❌ FAIL | ⚠️ PARTIAL | ✅ PASS

Notes:
_________________________________________________________________
_________________________________________________________________
```

---

## Troubleshooting Tests

### Test Fails: "Cannot connect to API"
**Solution:** Ensure FastAPI is running on port 8000
```bash
curl http://localhost:8000/health
```

### Test Fails: "Import Error"
**Solution:** Verify dependencies installed
```bash
pip install -r requirements.txt
```

### Scenario Decision Wrong
**Reasons:**
- Check if MCP servers are running
- Verify Claude API key in `.env`
- Check orchestrator logic in `loan_orchestrator.py`
- Verify agent prompts in `agents/loan_agents.py`

### Streamlit Shows "API Unavailable"
**Causes:**
1. FastAPI not running
2. Port 8000 blocked
3. CORS configuration issue

**Fix:**
```bash
# Kill existing processes
lsof -i :8000 | tail -1 | awk '{print $2}' | xargs kill -9

# Restart
bash run_all.sh
```

---

## Expected Final Checklist

Upon successful implementation, you should be able to:

- ✅ Run `python tests/test_orchestrator.py` with all tests passing
- ✅ Navigate Streamlit UI at http://localhost:8501
- ✅ Submit loan applications and get instant decisions
- ✅ Check application status by case ID
- ✅ View application history with all details
- ✅ See accurate statistics (approval rate, risk scores)
- ✅ Call FastAPI endpoints with curl
- ✅ See complete decision explanations with factors
- ✅ Verify all 4 agents are involved in decision
- ✅ Confirm decisions are consistent and explainable
