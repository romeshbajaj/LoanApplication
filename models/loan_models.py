from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid

class LoanApplication(BaseModel):
    """Input: Loan application from user"""
    applicant_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique applicant ID")
    applicant_name: str = Field(..., description="Full name of applicant")
    age: int = Field(..., ge=18, le=100, description="Age of applicant")
    income: float = Field(..., gt=0, description="Monthly income in currency units")
    employment_type: Literal["employed", "self_employed", "contract", "unemployed"] = Field(..., description="Employment type")
    employment_years: float = Field(..., ge=0, description="Years in current employment")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_tenure_months: int = Field(..., gt=0, le=600, description="Loan tenure in months")
    existing_liabilities: float = Field(default=0, ge=0, description="Total existing loan/debt obligations")
    location: str = Field(..., description="Applicant location")
    application_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="When application was submitted")

class ApplicantProfile(BaseModel):
    """Agent 1 Output: Applicant profile analysis"""
    income_stability_score: float = Field(..., description="Score 0-100 indicating income stability")
    employment_risk: float = Field(..., description="Risk score 0-100 for employment")
    employment_risk_category: Literal["low", "medium", "high"] = Field(..., description="Employment risk category")
    credit_history_summary: str = Field(..., description="Summary of credit history")
    application_completeness: float = Field(..., description="Percentage of application completeness")
    missing_fields: List[str] = Field(default_factory=list, description="Any missing required fields")

class FinancialRiskAnalysis(BaseModel):
    """Agent 2 Output: Financial risk analysis"""
    debt_to_income_ratio: float = Field(..., description="DTI ratio as decimal (e.g., 0.35)")
    dti_risk_level: Literal["low", "medium", "high"] = Field(..., description="DTI risk level")
    credit_score_risk_level: Literal["low", "medium", "high"] = Field(..., description="Credit score risk")
    loan_amount_risk: Literal["low", "medium", "high"] = Field(..., description="Loan amount relative to income risk")
    anomalies_detected: List[str] = Field(default_factory=list, description="Any anomalies in application")
    risk_reasoning: str = Field(..., description="Explanation of risk assessment")

class LoanDecision(BaseModel):
    """Agent 3 Output: Final loan decision"""
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique case ID")
    classification: Literal["approved", "rejected", "review"] = Field(..., description="Final decision")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score 0-100")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in decision 0-1")
    key_decision_factors: List[str] = Field(..., description="Key factors influencing decision")
    explanation: str = Field(..., description="Explanation of decision")
    recommendation: Optional[str] = Field(default=None, description="Next steps if review required")

class ComplianceAction(BaseModel):
    """Agent 4 Output: Compliance and action taken"""
    case_id: str = Field(..., description="Reference to loan decision case ID")
    action_taken: str = Field(..., description="Action taken (notification sent, case logged, etc.)")
    notification_status: str = Field(..., description="Status of notification")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="When action was taken")
    summary: str = Field(..., description="Summary of actions taken")
    audit_log: dict = Field(default_factory=dict, description="Audit trail information")

class LoanApplicationResponse(BaseModel):
    """Response returned from submit loan application"""
    case_id: str
    classification: Literal["approved", "rejected", "review"]
    risk_score: float
    confidence_level: float
    explanation: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
