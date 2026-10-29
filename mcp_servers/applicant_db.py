import json
from fastmcp import Server
from fastmcp.context import Request
import random

server = Server("applicant-db")

# Mock applicant database with simulated data
APPLICANT_DB = {
    "applicant_001": {
        "name": "John Doe",
        "age": 35,
        "income_history": [45000, 46000, 47000, 48000, 50000],
        "employment_type": "employed",
        "employment_years": 5,
        "previous_loans": 2,
        "loan_repayment_history": "good",
        "account_age_months": 120
    },
    "applicant_002": {
        "name": "Jane Smith",
        "age": 28,
        "income_history": [35000, 35000, 36000, 37000],
        "employment_type": "employed",
        "employment_years": 2,
        "previous_loans": 0,
        "loan_repayment_history": "none",
        "account_age_months": 36
    }
}

@server.call_tool()
def get_applicant_profile(applicant_id: str):
    """
    Retrieve comprehensive applicant profile from database

    Args:
        applicant_id: Unique identifier for the applicant

    Returns:
        Dictionary containing applicant profile information
    """
    if applicant_id in APPLICANT_DB:
        profile = APPLICANT_DB[applicant_id]
    else:
        profile = {
            "name": "New Applicant",
            "age": 30,
            "income_history": [40000],
            "employment_type": "employed",
            "employment_years": 3,
            "previous_loans": 0,
            "loan_repayment_history": "none",
            "account_age_months": 0
        }

    return {
        "status": "success",
        "profile": profile
    }

@server.call_tool()
def analyze_employment(applicant_id: str, employment_type: str, employment_years: float):
    """
    Analyze employment stability and risk

    Args:
        applicant_id: Applicant ID
        employment_type: Type of employment (employed, self_employed, contract, unemployed)
        employment_years: Years in current employment

    Returns:
        Employment analysis with stability score and risk assessment
    """
    employment_risk_map = {
        "employed": 0.2,
        "self_employed": 0.5,
        "contract": 0.6,
        "unemployed": 1.0
    }

    base_risk = employment_risk_map.get(employment_type, 0.5)

    if employment_years >= 5:
        stability_bonus = -0.3
    elif employment_years >= 2:
        stability_bonus = -0.1
    else:
        stability_bonus = 0.1

    employment_risk = min(1.0, max(0.1, base_risk + stability_bonus))
    income_stability_score = (1 - employment_risk) * 100

    return {
        "status": "success",
        "income_stability_score": round(income_stability_score, 2),
        "employment_risk": round(employment_risk * 100, 2),
        "employment_risk_category": "low" if employment_risk < 0.33 else "medium" if employment_risk < 0.67 else "high",
        "years_in_employment": employment_years
    }

@server.call_tool()
def get_credit_history(applicant_id: str, credit_score: int):
    """
    Retrieve and analyze credit history

    Args:
        applicant_id: Applicant ID
        credit_score: Current credit score (300-850)

    Returns:
        Credit history summary and analysis
    """
    if credit_score >= 750:
        credit_category = "excellent"
        history_summary = "Strong credit history with consistent on-time payments"
    elif credit_score >= 700:
        credit_category = "good"
        history_summary = "Good credit history with occasional late payments"
    elif credit_score >= 650:
        credit_category = "fair"
        history_summary = "Fair credit history with some payment issues"
    else:
        credit_category = "poor"
        history_summary = "Poor credit history with multiple delinquencies"

    profile = APPLICANT_DB.get(applicant_id, {})
    repayment_history = profile.get("loan_repayment_history", "none")

    return {
        "status": "success",
        "credit_score": credit_score,
        "credit_category": credit_category,
        "credit_history_summary": history_summary,
        "previous_loans": profile.get("previous_loans", 0),
        "loan_repayment_history": repayment_history,
        "account_age_months": profile.get("account_age_months", 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="127.0.0.1", port=8100)
