from fastmcp import Server
import json

server = Server("risk-rules-db")

@server.call_tool()
def calculate_dti_ratio(income: float, existing_liabilities: float, loan_amount: float, loan_tenure_months: int):
    """
    Calculate Debt-to-Income (DTI) ratio

    Args:
        income: Monthly income
        existing_liabilities: Total monthly existing debt obligations
        loan_amount: Requested loan amount
        loan_tenure_months: Loan tenure in months

    Returns:
        DTI ratio and risk assessment
    """
    monthly_loan_payment = loan_amount / loan_tenure_months
    total_monthly_debt = existing_liabilities + monthly_loan_payment

    if income <= 0:
        dti_ratio = 1.0
    else:
        dti_ratio = total_monthly_debt / income

    if dti_ratio <= 0.36:
        dti_risk = "low"
    elif dti_ratio <= 0.50:
        dti_risk = "medium"
    else:
        dti_risk = "high"

    return {
        "status": "success",
        "dti_ratio": round(dti_ratio, 3),
        "dti_risk_level": dti_risk,
        "monthly_debt": round(total_monthly_debt, 2),
        "monthly_income": round(income, 2),
        "monthly_loan_payment": round(monthly_loan_payment, 2)
    }

@server.call_tool()
def check_credit_risk(credit_score: int):
    """
    Assess credit score risk level

    Args:
        credit_score: Credit score (300-850)

    Returns:
        Credit risk assessment
    """
    if credit_score >= 750:
        risk_level = "low"
        risk_score = 10
    elif credit_score >= 700:
        risk_level = "low"
        risk_score = 20
    elif credit_score >= 650:
        risk_level = "medium"
        risk_score = 40
    elif credit_score >= 600:
        risk_level = "medium"
        risk_score = 60
    else:
        risk_level = "high"
        risk_score = 80

    return {
        "status": "success",
        "credit_score": credit_score,
        "credit_score_risk_level": risk_level,
        "credit_risk_score": risk_score
    }

@server.call_tool()
def assess_loan_amount_risk(loan_amount: float, income: float, age: int):
    """
    Assess risk based on loan amount relative to income

    Args:
        loan_amount: Requested loan amount
        income: Monthly income
        age: Applicant age

    Returns:
        Loan amount risk assessment
    """
    if income <= 0:
        loan_to_income_ratio = float('inf')
    else:
        loan_to_income_ratio = loan_amount / (income * 12)

    if loan_to_income_ratio <= 2.5:
        risk_level = "low"
        risk_score = 15
    elif loan_to_income_ratio <= 4.0:
        risk_level = "medium"
        risk_score = 35
    else:
        risk_level = "high"
        risk_score = 70

    age_penalty = 0
    if age < 25 or age > 65:
        age_penalty = 10

    return {
        "status": "success",
        "loan_to_income_ratio": round(loan_to_income_ratio, 2),
        "loan_amount_risk": risk_level,
        "loan_risk_score": risk_score + age_penalty,
        "age_penalty": age_penalty
    }

@server.call_tool()
def detect_anomalies(credit_score: int, employment_years: float, dti_ratio: float, loan_to_income: float):
    """
    Detect unusual patterns or anomalies in application

    Args:
        credit_score: Credit score
        employment_years: Years in employment
        dti_ratio: DTI ratio
        loan_to_income: Loan to income ratio

    Returns:
        List of detected anomalies
    """
    anomalies = []

    if credit_score < 550:
        anomalies.append("Very low credit score indicates significant credit issues")

    if employment_years < 1:
        anomalies.append("Less than 1 year in current employment - high job transition risk")

    if dti_ratio > 0.50:
        anomalies.append("High DTI ratio - debt obligations exceed 50% of income")

    if loan_to_income > 5.0:
        anomalies.append("Extremely high loan amount relative to annual income")

    if dti_ratio > 0.80:
        anomalies.append("Critical DTI ratio - likely unmanageable debt burden")

    return {
        "status": "success",
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies),
        "risk_level": "high" if len(anomalies) >= 3 else "medium" if len(anomalies) >= 1 else "low"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="127.0.0.1", port=8101)
