from fastmcp import Server
from typing import List, Dict, Any

server = Server("decision-synthesis")

@server.call_tool()
def synthesize_decision(
    income_stability_score: float,
    employment_risk_score: float,
    credit_risk_score: float,
    loan_risk_score: float,
    dti_ratio: float,
    credit_score: int,
    anomalies: List[str]
):
    """
    Synthesize all factors into final loan decision

    Args:
        income_stability_score: Income stability 0-100
        employment_risk_score: Employment risk 0-100
        credit_risk_score: Credit risk 0-100
        loan_risk_score: Loan amount risk 0-100
        dti_ratio: Debt-to-income ratio
        credit_score: Credit score
        anomalies: List of detected anomalies

    Returns:
        Decision classification with reasoning
    """
    weights = {
        "income_stability": 0.20,
        "employment_risk": 0.15,
        "credit_risk": 0.25,
        "loan_risk": 0.20,
        "dti_penalty": 0.20
    }

    dti_penalty = min(100, dti_ratio * 100)

    weighted_risk = (
        (100 - income_stability_score) * weights["income_stability"] +
        employment_risk_score * weights["employment_risk"] +
        credit_risk_score * weights["credit_risk"] +
        loan_risk_score * weights["loan_risk"] +
        dti_penalty * weights["dti_penalty"]
    )

    anomaly_penalty = len(anomalies) * 5

    total_risk_score = min(100, weighted_risk + anomaly_penalty)

    if total_risk_score < 30 and credit_score >= 700 and dti_ratio <= 0.43:
        classification = "approved"
        confidence = min(0.95, (100 - total_risk_score) / 100)
    elif total_risk_score > 70 or credit_score < 600 or dti_ratio > 0.60:
        classification = "rejected"
        confidence = min(0.95, total_risk_score / 100)
    else:
        classification = "review"
        confidence = 0.6

    key_factors = []
    if income_stability_score < 50:
        key_factors.append("Low income stability")
    if employment_risk_score > 60:
        key_factors.append("High employment risk")
    if credit_risk_score > 50:
        key_factors.append("Credit history concerns")
    if dti_ratio > 0.43:
        key_factors.append("High debt burden relative to income")
    if credit_score < 700:
        key_factors.append("Below-average credit score")

    return {
        "status": "success",
        "classification": classification,
        "risk_score": round(total_risk_score, 2),
        "confidence_level": round(confidence, 3),
        "key_factors": key_factors if key_factors else ["Application meets approval criteria"],
        "weighted_scores": {
            "income_stability_contribution": round((100 - income_stability_score) * weights["income_stability"], 2),
            "employment_risk_contribution": round(employment_risk_score * weights["employment_risk"], 2),
            "credit_risk_contribution": round(credit_risk_score * weights["credit_risk"], 2),
            "loan_risk_contribution": round(loan_risk_score * weights["loan_risk"], 2),
            "dti_contribution": round(dti_penalty * weights["dti_penalty"], 2),
        }
    }

@server.call_tool()
def calculate_confidence(
    classification: str,
    risk_score: float,
    data_completeness: float,
    anomaly_count: int
):
    """
    Calculate confidence level in the decision

    Args:
        classification: Decision type (approved, rejected, review)
        risk_score: Overall risk score
        data_completeness: Percentage of data available (0-100)
        anomaly_count: Number of anomalies detected

    Returns:
        Confidence score and explanation
    """
    base_confidence = 0.8

    data_confidence = (data_completeness / 100) * 0.2
    base_confidence += data_confidence - 0.2

    if classification == "approved":
        if risk_score < 20:
            base_confidence = 0.95
        elif risk_score < 30:
            base_confidence = 0.85
        else:
            base_confidence = 0.70
    elif classification == "rejected":
        if risk_score > 70:
            base_confidence = 0.95
        elif risk_score > 60:
            base_confidence = 0.85
        else:
            base_confidence = 0.70
    else:
        base_confidence = 0.65

    anomaly_penalty = min(0.25, anomaly_count * 0.08)
    final_confidence = max(0.3, min(0.99, base_confidence - anomaly_penalty))

    confidence_category = "high" if final_confidence > 0.8 else "medium" if final_confidence > 0.6 else "low"

    return {
        "status": "success",
        "confidence_level": round(final_confidence, 3),
        "confidence_category": confidence_category,
        "data_completeness_score": round(data_completeness, 2),
        "explanation": f"Decision made with {confidence_category} confidence based on available data"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="127.0.0.1", port=8102)
