import streamlit as st
import requests
import json
from datetime import datetime
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.loan_models import LoanApplication

st.set_page_config(
    page_title="Intelligent Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .approved {
        color: #28a745;
        font-weight: bold;
    }
    .rejected {
        color: #dc3545;
        font-weight: bold;
    }
    .review {
        color: #ffc107;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def submit_loan_application(app_data):
    """Submit loan application to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/apply-for-loan",
            json=app_data.dict(),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Unknown error")}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Make sure the service is running on port 8000"}
    except Exception as e:
        return {"error": str(e)}

def get_loan_status(case_id):
    """Get status of submitted loan"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/loan-status/{case_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Case not found")}
    except Exception as e:
        return {"error": str(e)}

def get_all_loans():
    """Get list of all processed loans"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/list-loans",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Could not retrieve loans"}
    except Exception as e:
        return {"error": str(e)}

def get_statistics():
    """Get loan statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/statistics",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

st.title("💰 Intelligent Loan Approval System")
st.markdown("### Multi-Agent AI for Automated Loan Decisions")

if not check_api_health():
    st.error("⚠️ API Service is not running. Please start the FastAPI service on port 8000")
    st.info("Run: `python services/loan_service.py`")
else:
    st.success("✅ API Service is running")

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Submit Application",
    "🔍 Check Status",
    "📊 History",
    "📈 Statistics"
])

with tab1:
    st.header("Submit Loan Application")
    st.markdown("Fill in your details below to apply for a loan")

    with st.form("loan_application_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Personal Information")
            applicant_name = st.text_input(
                "Full Name",
                value="John Doe"
            )
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                value=35
            )
            employment_type = st.selectbox(
                "Employment Type",
                ["employed", "self_employed", "contract", "unemployed"],
                index=0
            )
            employment_years = st.number_input(
                "Years in Current Employment",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5
            )

        with col2:
            st.subheader("Income & Loan Details")
            income = st.number_input(
                "Monthly Income ($)",
                min_value=100,
                value=5000,
                step=100
            )
            loan_amount = st.number_input(
                "Loan Amount Requested ($)",
                min_value=1000,
                value=50000,
                step=1000
            )
            loan_tenure_months = st.number_input(
                "Loan Tenure (Months)",
                min_value=12,
                max_value=600,
                value=60,
                step=12
            )
            existing_liabilities = st.number_input(
                "Existing Monthly Liabilities ($)",
                min_value=0,
                value=1000,
                step=100
            )

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Credit & Location")
            credit_score = st.number_input(
                "Credit Score",
                min_value=300,
                max_value=850,
                value=750,
                step=10
            )
            location = st.text_input(
                "Location",
                value="New York"
            )

        submitted = st.form_submit_button(
            "🚀 Submit Application",
            use_container_width=True
        )

    if submitted:
        if not check_api_health():
            st.error("API Service is not available. Cannot submit application.")
        else:
            from models.loan_models import LoanApplication

            try:
                application = LoanApplication(
                    applicant_name=applicant_name,
                    age=age,
                    income=income,
                    employment_type=employment_type,
                    employment_years=employment_years,
                    credit_score=credit_score,
                    loan_amount=loan_amount,
                    loan_tenure_months=loan_tenure_months,
                    existing_liabilities=existing_liabilities,
                    location=location
                )

                with st.spinner("⏳ Processing your application..."):
                    result = submit_loan_application(application)

                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Application Processed!")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if result["classification"] == "approved":
                            st.markdown(f'<div class="approved">Decision: APPROVED ✅</div>', unsafe_allow_html=True)
                        elif result["classification"] == "rejected":
                            st.markdown(f'<div class="rejected">Decision: REJECTED ❌</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="review">Decision: REQUIRES REVIEW ⏳</div>', unsafe_allow_html=True)

                    with col2:
                        st.metric("Risk Score", f"{result['risk_score']:.1f}/100")

                    with col3:
                        st.metric("Confidence", f"{result['confidence_level']:.1%}")

                    st.info(f"**Case ID:** `{result['case_id']}`")
                    st.markdown(f"**Explanation:** {result['explanation']}")

                    st.session_state.last_case_id = result['case_id']

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("Check Loan Status")
    st.markdown("Enter your Case ID to check the status of your application")

    col1, col2 = st.columns([3, 1])

    with col1:
        case_id = st.text_input(
            "Case ID",
            placeholder="Enter your Case ID from the application submission",
            value=st.session_state.get("last_case_id", "")
        )

    with col2:
        search_button = st.button("🔍 Search", use_container_width=True)

    if search_button and case_id:
        if not check_api_health():
            st.error("API Service is not available.")
        else:
            with st.spinner("Retrieving case information..."):
                status = get_loan_status(case_id)

            if "error" in status:
                st.error(f"❌ {status['error']}")
            else:
                col1, col2, col3 = st.columns(3)

                with col1:
                    if status["classification"] == "approved":
                        st.markdown(f'<div class="approved">✅ APPROVED</div>', unsafe_allow_html=True)
                    elif status["classification"] == "rejected":
                        st.markdown(f'<div class="rejected">❌ REJECTED</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="review">⏳ REQUIRES REVIEW</div>', unsafe_allow_html=True)

                with col2:
                    st.metric("Risk Score", f"{status['risk_score']:.1f}/100")

                with col3:
                    st.metric("Confidence", f"{status['confidence_level']:.1%}")

                st.markdown("---")

                st.subheader("Application Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Applicant:** {status['applicant_name']}")
                    st.write(f"**ID:** {status['applicant_id']}")
                with col2:
                    st.write(f"**Processed:** {status['processed_at']}")

                st.subheader("Decision Factors")
                for factor in status.get("key_decision_factors", []):
                    st.info(f"• {factor}")

                st.subheader("Explanation")
                st.write(status["explanation"])

                if status.get("recommendation"):
                    st.warning(f"**Recommendation:** {status['recommendation']}")

with tab3:
    st.header("Application History")
    st.markdown("View all processed loan applications")

    refresh_button = st.button("🔄 Refresh", use_container_width=True)

    if refresh_button or True:
        if not check_api_health():
            st.error("API Service is not available.")
        else:
            with st.spinner("Loading applications..."):
                data = get_all_loans()

            if "error" in data:
                st.error(f"❌ {data['error']}")
            elif data["total_applications"] == 0:
                st.info("No applications processed yet.")
            else:
                st.markdown(f"**Total Applications:** {data['total_applications']}")

                loans = data.get("loans", [])
                if loans:
                    df_data = []
                    for loan in loans:
                        df_data.append({
                            "Case ID": loan["case_id"][:8] + "...",
                            "Applicant": loan["applicant_name"],
                            "Decision": loan["classification"].upper(),
                            "Risk Score": f"{loan['risk_score']:.1f}",
                            "Confidence": f"{loan['confidence_level']:.1%}",
                            "Processed": loan["processed_at"][:10]
                        })

                    import pandas as pd
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)

with tab4:
    st.header("System Statistics")

    refresh_stats = st.button("📊 Refresh Statistics", use_container_width=True)

    if refresh_stats or True:
        if not check_api_health():
            st.error("API Service is not available.")
        else:
            stats = get_statistics()

            if stats:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Total Applications",
                        stats["total_applications"]
                    )

                with col2:
                    st.metric(
                        "Approved",
                        stats["approved"],
                        delta=None
                    )

                with col3:
                    st.metric(
                        "Rejected",
                        stats["rejected"],
                        delta=None
                    )

                with col4:
                    st.metric(
                        "Under Review",
                        stats["review"],
                        delta=None
                    )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Approval Rate",
                        stats["approval_rate"]
                    )

                with col2:
                    st.metric(
                        "Avg Risk Score",
                        f"{stats['average_risk_score']:.1f}/100"
                    )

                with col3:
                    st.metric(
                        "Avg Confidence",
                        f"{stats['average_confidence']:.1%}"
                    )

st.markdown("---")
st.markdown("""
    <center>
    <small>
    Intelligent Loan Approval System v1.0 | Powered by Multi-Agent AI
    </small>
    </center>
    """, unsafe_allow_html=True)
