from fastmcp import Server
from datetime import datetime
import json

server = Server("notification-system")

# In-memory storage for cases
CASE_STORAGE = {}

@server.call_tool()
def send_notification(
    case_id: str,
    applicant_name: str,
    applicant_id: str,
    classification: str,
    risk_score: float
):
    """
    Send notification about loan decision

    Args:
        case_id: Unique case ID
        applicant_name: Name of applicant
        applicant_id: Applicant ID
        classification: Decision type (approved, rejected, review)
        risk_score: Risk score of application

    Returns:
        Notification status
    """
    timestamp = datetime.utcnow().isoformat()

    notification_message = f"Loan application {case_id} for {applicant_name} has been {classification.upper()}"

    notification_status = "sent"

    return {
        "status": "success",
        "case_id": case_id,
        "notification_status": notification_status,
        "message": notification_message,
        "timestamp": timestamp
    }

@server.call_tool()
def log_decision(
    case_id: str,
    applicant_id: str,
    applicant_name: str,
    classification: str,
    risk_score: float,
    confidence_level: float,
    key_factors: list,
    explanation: str
):
    """
    Log the loan decision for audit trail

    Args:
        case_id: Unique case ID
        applicant_id: Applicant ID
        applicant_name: Applicant name
        classification: Decision classification
        risk_score: Risk score
        confidence_level: Confidence in decision
        key_factors: Key decision factors
        explanation: Decision explanation

    Returns:
        Confirmation of logged decision
    """
    timestamp = datetime.utcnow().isoformat()

    case_record = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "applicant_name": applicant_name,
        "classification": classification,
        "risk_score": risk_score,
        "confidence_level": confidence_level,
        "key_factors": key_factors,
        "explanation": explanation,
        "logged_at": timestamp,
        "status": "logged"
    }

    CASE_STORAGE[case_id] = case_record

    return {
        "status": "success",
        "case_id": case_id,
        "logged": True,
        "timestamp": timestamp,
        "message": f"Decision for case {case_id} logged successfully"
    }

@server.call_tool()
def update_case(case_id: str, status: str, notes: str = ""):
    """
    Update case status

    Args:
        case_id: Unique case ID
        status: New status (open, in_review, closed, appealed)
        notes: Any additional notes

    Returns:
        Updated case information
    """
    if case_id in CASE_STORAGE:
        CASE_STORAGE[case_id]["status"] = status
        if notes:
            CASE_STORAGE[case_id]["notes"] = notes
        CASE_STORAGE[case_id]["last_updated"] = datetime.utcnow().isoformat()

        return {
            "status": "success",
            "case_id": case_id,
            "case_status": status,
            "message": f"Case {case_id} updated to {status}",
            "updated_at": CASE_STORAGE[case_id]["last_updated"]
        }
    else:
        return {
            "status": "error",
            "case_id": case_id,
            "message": f"Case {case_id} not found"
        }

@server.call_tool()
def get_case_details(case_id: str):
    """
    Retrieve case details from audit log

    Args:
        case_id: Unique case ID

    Returns:
        Complete case information
    """
    if case_id in CASE_STORAGE:
        return {
            "status": "success",
            "case": CASE_STORAGE[case_id]
        }
    else:
        return {
            "status": "not_found",
            "case_id": case_id,
            "message": f"Case {case_id} not found in system"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="127.0.0.1", port=8103)
