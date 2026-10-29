import asyncio
import json
import os
from typing import TypedDict, Optional, Any, Literal
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from models.loan_models import (
    LoanApplication,
    ApplicantProfile,
    FinancialRiskAnalysis,
    LoanDecision,
    ComplianceAction
)

load_dotenv(override=True)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")
model_name = os.getenv("MODEL_NAME", "claude-opus-4-5-20251101-v1:0")

chat_model = ChatAnthropic(
    model=model_name,
    temperature=0.3,
    anthropic_api_key=anthropic_api_key,
    base_url=base_url,
)

class LoanProcessState(TypedDict, total=False):
    """State management for loan approval workflow"""
    loan_application: LoanApplication
    applicant_profile: Optional[ApplicantProfile]
    financial_risk: Optional[FinancialRiskAnalysis]
    loan_decision: Optional[LoanDecision]
    compliance_action: Optional[ComplianceAction]
    error: Optional[str]
    status: Literal["pending", "processing", "completed", "failed"]

def applicant_node(state: LoanProcessState) -> LoanProcessState:
    """Node 1: Applicant Profile Agent - Synchronous"""
    try:
        application = state["loan_application"]

        # Calculate stability based on employment years
        if application.employment_years >= 5:
            stability = 85
            risk_category = "low"
        elif application.employment_years >= 2:
            stability = 70
            risk_category = "medium"
        else:
            stability = 50
            risk_category = "high"

        # Adjust for employment type
        if application.employment_type == "employed":
            employment_risk = 20
        elif application.employment_type == "self_employed":
            employment_risk = 50
        elif application.employment_type == "contract":
            employment_risk = 60
        else:
            employment_risk = 90

        profile = ApplicantProfile(
            income_stability_score=stability,
            employment_risk=employment_risk,
            employment_risk_category=risk_category,
            credit_history_summary=f"Credit score {application.credit_score}. {'Excellent history' if application.credit_score >= 750 else 'Good history' if application.credit_score >= 700 else 'Fair history' if application.credit_score >= 650 else 'Poor credit history'}",
            application_completeness=100,
            missing_fields=[]
        )

        state["applicant_profile"] = profile
        state["status"] = "processing"
        return state
    except Exception as e:
        state["error"] = f"Applicant profile agent failed: {str(e)}"
        state["status"] = "failed"
        return state

def financial_risk_node(state: LoanProcessState) -> LoanProcessState:
    """Node 2: Financial Risk Agent - Synchronous"""
    if state.get("error"):
        return state

    try:
        application = state["loan_application"]

        dti = (application.existing_liabilities + (application.loan_amount / application.loan_tenure_months * 12)) / (application.income * 12)
        dti_risk = "low" if dti <= 0.36 else "medium" if dti <= 0.50 else "high"
        credit_risk = "low" if application.credit_score >= 700 else "medium" if application.credit_score >= 650 else "high"

        risk = FinancialRiskAnalysis(
            debt_to_income_ratio=round(dti, 3),
            dti_risk_level=dti_risk,
            credit_score_risk_level=credit_risk,
            loan_amount_risk="low" if application.loan_amount <= application.income * 12 * 2.5 else "medium" if application.loan_amount <= application.income * 12 * 4 else "high",
            anomalies_detected=[],
            risk_reasoning=f"DTI: {dti:.2f}, Credit: {application.credit_score}"
        )

        state["financial_risk"] = risk
        return state
    except Exception as e:
        state["error"] = f"Financial risk agent failed: {str(e)}"
        state["status"] = "failed"
        return state

def loan_decision_node(state: LoanProcessState) -> LoanProcessState:
    """Node 3: Loan Decision Agent - Synchronous"""
    if state.get("error"):
        return state

    try:
        application = state["loan_application"]
        profile = state["applicant_profile"]
        risk = state["financial_risk"]

        if not profile or not risk:
            state["error"] = "Missing data from previous agents"
            state["status"] = "failed"
            return state

        weighted_risk = (
            (100 - profile.income_stability_score) * 0.20 +
            profile.employment_risk * 0.15 +
            (0 if risk.credit_score_risk_level == "low" else 40 if risk.credit_score_risk_level == "medium" else 80) * 0.25 +
            (0 if risk.loan_amount_risk == "low" else 35 if risk.loan_amount_risk == "medium" else 70) * 0.20 +
            min(100, risk.debt_to_income_ratio * 100) * 0.20
        )

        risk_score = min(100, weighted_risk)

        if risk_score < 30 and application.credit_score >= 700 and risk.debt_to_income_ratio <= 0.43:
            classification = "approved"
            confidence = 0.85
        elif risk_score > 70 or application.credit_score < 600 or risk.debt_to_income_ratio > 0.60:
            classification = "rejected"
            confidence = 0.90
        else:
            classification = "review"
            confidence = 0.65

        key_factors = []
        if profile.income_stability_score < 50:
            key_factors.append("Low income stability")
        if application.credit_score < 700:
            key_factors.append("Below-average credit score")
        if risk.debt_to_income_ratio > 0.43:
            key_factors.append("High debt burden")
        if application.employment_years < 2:
            key_factors.append("Unstable employment history")

        if not key_factors:
            key_factors = ["Strong financial profile"]

        decision = LoanDecision(
            classification=classification,
            risk_score=risk_score,
            confidence_level=confidence,
            key_decision_factors=key_factors,
            explanation=f"Decision based on comprehensive financial analysis. Risk score: {risk_score:.1f}/100"
        )

        state["loan_decision"] = decision
        return state
    except Exception as e:
        state["error"] = f"Loan decision agent failed: {str(e)}"
        state["status"] = "failed"
        return state

def compliance_node(state: LoanProcessState) -> LoanProcessState:
    """Node 4: Compliance Orchestrator Agent - Synchronous"""
    if state.get("error"):
        return state

    try:
        application = state["loan_application"]
        decision = state["loan_decision"]

        if not decision:
            state["error"] = "Missing loan decision"
            state["status"] = "failed"
            return state

        compliance = ComplianceAction(
            case_id=decision.case_id,
            action_taken="Decision logged and notification prepared",
            notification_status="prepared",
            summary=f"Loan application {decision.case_id} processed with {decision.classification} decision",
            audit_log={
                "applicant_id": application.applicant_id,
                "applicant_name": application.applicant_name,
                "classification": decision.classification,
                "risk_score": decision.risk_score,
                "confidence": decision.confidence_level
            }
        )

        state["compliance_action"] = compliance
        state["status"] = "completed"
        return state
    except Exception as e:
        state["error"] = f"Compliance agent failed: {str(e)}"
        state["status"] = "failed"
        return state

def build_loan_workflow():
    """Build the LangGraph workflow for loan approval"""
    workflow = StateGraph(LoanProcessState)

    # Add nodes
    workflow.add_node("applicant_profile", applicant_node)
    workflow.add_node("financial_risk", financial_risk_node)
    workflow.add_node("loan_decision", loan_decision_node)
    workflow.add_node("compliance", compliance_node)

    # Add edges - sequential workflow
    workflow.add_edge(START, "applicant_profile")
    workflow.add_edge("applicant_profile", "financial_risk")
    workflow.add_edge("financial_risk", "loan_decision")
    workflow.add_edge("loan_decision", "compliance")
    workflow.add_edge("compliance", END)

    return workflow.compile()

class LoanOrchestrator:
    """Orchestrator for loan approval process"""

    def __init__(self):
        self.workflow = build_loan_workflow()
        self.case_history = {}

    def process_loan_application(self, application: LoanApplication) -> dict:
        """
        Process a loan application through all agents

        Args:
            application: Loan application data

        Returns:
            Complete state with decision
        """
        initial_state: LoanProcessState = {
            "loan_application": application,
            "applicant_profile": None,
            "financial_risk": None,
            "loan_decision": None,
            "compliance_action": None,
            "error": None,
            "status": "pending"
        }

        # Run the workflow
        result = self._run_workflow(initial_state)

        # Store in case history
        if result.get("loan_decision"):
            case_id = result["loan_decision"].case_id
            self.case_history[case_id] = result

        return result

    def _run_workflow(self, state: LoanProcessState) -> LoanProcessState:
        """Execute the workflow"""
        try:
            result_state = self.workflow.invoke(state)
            return result_state
        except Exception as e:
            state["error"] = f"Workflow execution failed: {str(e)}"
            state["status"] = "failed"
            return state

    def get_case_status(self, case_id: str) -> Optional[Any]:
        """Retrieve case status and details"""
        return self.case_history.get(case_id)

    def list_all_cases(self) -> dict:
        """List all processed cases"""
        return self.case_history


def demo():
    """Demo function to test the orchestrator"""
    from models.loan_models import LoanApplication
    from datetime import datetime

    # Create sample application
    app = LoanApplication(
        applicant_id="APP001",
        applicant_name="John Doe",
        age=35,
        income=5000,
        employment_type="employed",
        employment_years=5,
        credit_score=750,
        loan_amount=50000,
        loan_tenure_months=60,
        existing_liabilities=1000,
        location="New York"
    )

    orchestrator = LoanOrchestrator()
    result = orchestrator.process_loan_application(app)

    print(f"Decision: {result.get('loan_decision', {}).classification if result.get('loan_decision') else 'ERROR'}")
    print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    demo()
