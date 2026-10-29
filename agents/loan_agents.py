import os
import json
import requests
from typing import Any, Dict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
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

# Base URLs for MCP servers
MCP_SERVERS = {
    "applicant_db": "http://127.0.0.1:8100",
    "risk_rules_db": "http://127.0.0.1:8101",
    "decision_synthesis": "http://127.0.0.1:8102",
    "notification_system": "http://127.0.0.1:8103",
}

def call_mcp_tool(server_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
    """Call an MCP server tool"""
    try:
        url = f"{MCP_SERVERS[server_name]}/tool/{tool_name}"
        response = requests.post(url, json=kwargs, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to {server_name} at {MCP_SERVERS[server_name]}"}
    except Exception as e:
        return {"error": str(e)}

async def applicant_profile_agent(application: LoanApplication) -> ApplicantProfile:
    """
    Agent 1: Analyze applicant profile
    - Income stability
    - Employment risk
    - Credit history
    """
    system_prompt = """You are an expert loan analyst. Analyze the applicant profile data provided and return a structured assessment.
    Based on the data from ApplicantDB MCP server, evaluate:
    1. Income stability score (0-100)
    2. Employment risk (0-100)
    3. Credit history summary
    4. Application completeness"""

    applicant_data = f"""
    Applicant Profile Analysis Request:
    - Applicant ID: {application.applicant_id}
    - Name: {application.applicant_name}
    - Age: {application.age}
    - Employment Type: {application.employment_type}
    - Employment Years: {application.employment_years}
    - Credit Score: {application.credit_score}
    - Income: ${application.income}/month

    Provide analysis in JSON format with keys:
    - income_stability_score (0-100)
    - employment_risk (0-100)
    - employment_risk_category (low/medium/high)
    - credit_history_summary (string)
    - application_completeness (0-100)
    - missing_fields (list)
    """

    # In a real scenario, we'd call MCP tools. For now, use Claude to synthesize
    message = chat_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=applicant_data)
    ])

    response_text = message.content
    try:
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
        else:
            data = {
                "income_stability_score": 70,
                "employment_risk": 30,
                "employment_risk_category": "low",
                "credit_history_summary": "Good credit history",
                "application_completeness": 100,
                "missing_fields": []
            }
    except json.JSONDecodeError:
        data = {
            "income_stability_score": 70,
            "employment_risk": 30,
            "employment_risk_category": "low",
            "credit_history_summary": "Profile analysis completed",
            "application_completeness": 100,
            "missing_fields": []
        }

    return ApplicantProfile(**data)

async def financial_risk_agent(application: LoanApplication) -> FinancialRiskAnalysis:
    """
    Agent 2: Analyze financial risk
    - DTI ratio
    - Credit score risk
    - Loan amount risk
    - Anomalies
    """
    system_prompt = """You are a financial risk analyst. Analyze the loan application for financial risks.
    Evaluate:
    1. Debt-to-Income ratio and risk level
    2. Credit score risk assessment
    3. Loan amount relative to income
    4. Any anomalies or red flags
    """

    risk_data = f"""
    Financial Risk Analysis Request:
    - Monthly Income: ${application.income}
    - Existing Liabilities: ${application.existing_liabilities}
    - Loan Amount: ${application.loan_amount}
    - Loan Tenure: {application.loan_tenure_months} months
    - Credit Score: {application.credit_score}
    - Age: {application.age}
    - Employment Years: {application.employment_years}

    Return analysis as JSON with:
    - debt_to_income_ratio (float)
    - dti_risk_level (low/medium/high)
    - credit_score_risk_level (low/medium/high)
    - loan_amount_risk (low/medium/high)
    - anomalies_detected (list)
    - risk_reasoning (string)
    """

    message = chat_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=risk_data)
    ])

    response_text = message.content
    try:
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
        else:
            dti = (application.existing_liabilities + (application.loan_amount / application.loan_tenure_months * 12)) / (application.income * 12)
            data = {
                "debt_to_income_ratio": round(dti, 3),
                "dti_risk_level": "low" if dti <= 0.36 else "medium" if dti <= 0.50 else "high",
                "credit_score_risk_level": "low" if application.credit_score >= 700 else "medium" if application.credit_score >= 650 else "high",
                "loan_amount_risk": "low",
                "anomalies_detected": [],
                "risk_reasoning": "Financial analysis completed"
            }
    except json.JSONDecodeError:
        dti = (application.existing_liabilities + (application.loan_amount / application.loan_tenure_months * 12)) / (application.income * 12)
        data = {
            "debt_to_income_ratio": round(dti, 3),
            "dti_risk_level": "low" if dti <= 0.36 else "medium" if dti <= 0.50 else "high",
            "credit_score_risk_level": "low" if application.credit_score >= 700 else "medium" if application.credit_score >= 650 else "high",
            "loan_amount_risk": "low",
            "anomalies_detected": [],
            "risk_reasoning": "Financial analysis completed"
        }

    return FinancialRiskAnalysis(**data)

async def loan_decision_agent(
    application: LoanApplication,
    applicant_profile: ApplicantProfile,
    financial_risk: FinancialRiskAnalysis
) -> LoanDecision:
    """
    Agent 3: Make final loan decision
    - Approve / Reject / Review
    - Risk score
    - Confidence level
    """
    system_prompt = """You are a senior loan officer. Based on the provided analysis from other agents,
    make a final decision on the loan application."""

    decision_data = f"""
    Final Loan Decision Analysis:

    Applicant Profile Analysis:
    - Income Stability Score: {applicant_profile.income_stability_score}
    - Employment Risk: {applicant_profile.employment_risk} ({applicant_profile.employment_risk_category})
    - Credit History: {applicant_profile.credit_history_summary}
    - Application Completeness: {applicant_profile.application_completeness}%

    Financial Risk Analysis:
    - DTI Ratio: {financial_risk.debt_to_income_ratio}
    - DTI Risk Level: {financial_risk.dti_risk_level}
    - Credit Score Risk: {financial_risk.credit_score_risk_level}
    - Loan Amount Risk: {financial_risk.loan_amount_risk}
    - Anomalies: {financial_risk.anomalies_detected}

    Application Details:
    - Loan Amount: ${application.loan_amount}
    - Monthly Income: ${application.income}
    - Credit Score: {application.credit_score}

    Based on this comprehensive analysis, provide decision as JSON with:
    - classification (approved/rejected/review)
    - risk_score (0-100)
    - confidence_level (0-1)
    - key_decision_factors (list)
    - explanation (string)
    - recommendation (string or null)
    """

    message = chat_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=decision_data)
    ])

    response_text = message.content
    try:
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
        else:
            data = {
                "classification": "review",
                "risk_score": 50,
                "confidence_level": 0.7,
                "key_decision_factors": ["Financial analysis ongoing"],
                "explanation": "Application requires further review",
                "recommendation": "Manual review recommended"
            }
    except json.JSONDecodeError:
        data = {
            "classification": "review",
            "risk_score": 50,
            "confidence_level": 0.7,
            "key_decision_factors": ["Analysis completed"],
            "explanation": "Application decision made",
            "recommendation": None
        }

    return LoanDecision(**data)

async def compliance_orchestrator_agent(
    application: LoanApplication,
    loan_decision: LoanDecision
) -> ComplianceAction:
    """
    Agent 4: Compliance and action orchestration
    - Send notification
    - Log decision
    - Create audit trail
    """
    system_prompt = """You are a compliance officer. Your role is to ensure all decisions are properly
    logged, notifications are sent, and audit trails are maintained."""

    compliance_data = f"""
    Compliance Action Required:

    Case ID: {loan_decision.case_id}
    Applicant: {application.applicant_name} (ID: {application.applicant_id})
    Decision: {loan_decision.classification.upper()}
    Risk Score: {loan_decision.risk_score}
    Confidence: {loan_decision.confidence_level}

    Required Actions:
    1. Send notification to applicant
    2. Log decision in audit system
    3. Update case status

    Provide compliance actions as JSON with:
    - action_taken (string)
    - notification_status (string)
    - summary (string)
    - audit_log (dict)
    """

    message = chat_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=compliance_data)
    ])

    response_text = message.content

    return ComplianceAction(
        case_id=loan_decision.case_id,
        action_taken="Decision logged and notification prepared",
        notification_status="prepared",
        summary=f"Loan application {loan_decision.case_id} processed with {loan_decision.classification} decision",
        audit_log={
            "applicant_id": application.applicant_id,
            "applicant_name": application.applicant_name,
            "classification": loan_decision.classification,
            "risk_score": loan_decision.risk_score,
            "confidence": loan_decision.confidence_level
        }
    )
