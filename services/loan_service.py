import asyncio
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from models.loan_models import (
    LoanApplication,
    LoanApplicationResponse,
    LoanDecision
)
from orchestration.loan_orchestrator import LoanOrchestrator

load_dotenv(override=True)

app = FastAPI(
    title="Intelligent Loan Approval System",
    description="Multi-agent AI system for automated loan approval",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = LoanOrchestrator()
application_cache: Dict[str, Any] = {}

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    print("✅ Loan Service Started")
    print("   Endpoints available at /docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Intelligent Loan Approval System",
        "timestamp": datetime.utcnow().isoformat(),
        "total_applications": len(application_cache)
    }

@app.post("/apply-for-loan", response_model=LoanApplicationResponse)
async def apply_for_loan(application: LoanApplication, background_tasks: BackgroundTasks):
    """
    Submit a loan application for processing

    Args:
        application: Loan application details

    Returns:
        LoanApplicationResponse with decision and case ID
    """
    try:
        result = orchestrator.process_loan_application(application)

        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"Processing error: {result['error']}"
            )

        decision = result.get("loan_decision")
        if not decision:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate decision"
            )

        # Cache the application for later retrieval
        application_cache[decision.case_id] = {
            "application": application,
            "decision": decision,
            "compliance": result.get("compliance_action"),
            "processed_at": datetime.utcnow().isoformat()
        }

        response = LoanApplicationResponse(
            case_id=decision.case_id,
            classification=decision.classification,
            risk_score=decision.risk_score,
            confidence_level=decision.confidence_level,
            explanation=decision.explanation
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/loan-status/{case_id}")
async def get_loan_status(case_id: str):
    """
    Check status of a loan application

    Args:
        case_id: Unique case ID

    Returns:
        Complete decision details
    """
    if case_id not in application_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    cached = application_cache[case_id]
    decision = cached["decision"]

    return {
        "case_id": case_id,
        "classification": decision.classification,
        "risk_score": decision.risk_score,
        "confidence_level": decision.confidence_level,
        "key_decision_factors": decision.key_decision_factors,
        "explanation": decision.explanation,
        "recommendation": decision.recommendation,
        "processed_at": cached["processed_at"],
        "applicant_name": cached["application"].applicant_name,
        "applicant_id": cached["application"].applicant_id
    }

@app.get("/list-loans")
async def list_loans(skip: int = 0, limit: int = 10):
    """
    List all processed loan applications

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of loan decisions
    """
    cases = list(application_cache.items())
    total = len(cases)

    paginated = cases[skip:skip + limit]

    return {
        "total_applications": total,
        "skip": skip,
        "limit": limit,
        "loans": [
            {
                "case_id": case_id,
                "applicant_name": data["application"].applicant_name,
                "classification": data["decision"].classification,
                "risk_score": float(data["decision"].risk_score),
                "confidence_level": float(data["decision"].confidence_level),
                "processed_at": str(data["processed_at"])
            }
            for case_id, data in paginated
        ]
    }

@app.get("/case-summary/{case_id}")
async def get_case_summary(case_id: str):
    """
    Get a summary of a case with all agent outputs

    Args:
        case_id: Unique case ID

    Returns:
        Complete case information including all agent outputs
    """
    if case_id not in application_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    cached = application_cache[case_id]

    # Convert decision dict and handle datetime fields
    decision_dict = cached["decision"].dict()

    # Convert any datetime fields to strings
    for key, value in decision_dict.items():
        if isinstance(value, datetime):
            decision_dict[key] = value.isoformat()

    # Convert compliance dict if exists
    compliance_dict = None
    if cached["compliance"]:
        compliance_dict = cached["compliance"].dict()
        for key, value in compliance_dict.items():
            if isinstance(value, datetime):
                compliance_dict[key] = value.isoformat()

    # Convert application dict and handle any datetime fields
    application_dict = cached["application"].dict()
    for key, value in application_dict.items():
        if isinstance(value, datetime):
            application_dict[key] = value.isoformat()

    return {
        "case_id": case_id,
        "application": application_dict,
        "decision": decision_dict,
        "compliance": compliance_dict,
        "processed_at": cached["processed_at"]
    }

@app.get("/statistics")
async def get_statistics():
    """
    Get statistics about processed loans

    Returns:
        Statistics about approvals, rejections, reviews
    """
    total = len(application_cache)
    approved = sum(1 for data in application_cache.values() if data["decision"].classification == "approved")
    rejected = sum(1 for data in application_cache.values() if data["decision"].classification == "rejected")
    review = sum(1 for data in application_cache.values() if data["decision"].classification == "review")

    avg_risk_score = 0
    if total > 0:
        avg_risk_score = sum(data["decision"].risk_score for data in application_cache.values()) / total
        avg_confidence = sum(data["decision"].confidence_level for data in application_cache.values()) / total
    else:
        avg_confidence = 0

    return {
        "total_applications": total,
        "approved": approved,
        "rejected": rejected,
        "review": review,
        "approval_rate": f"{(approved/total*100):.1f}%" if total > 0 else "0%",
        "average_risk_score": round(avg_risk_score, 2),
        "average_confidence": round(avg_confidence, 3)
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Intelligent Loan Approval System",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "apply": "/apply-for-loan",
            "status": "/loan-status/{case_id}",
            "list": "/list-loans",
            "summary": "/case-summary/{case_id}",
            "statistics": "/statistics",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
