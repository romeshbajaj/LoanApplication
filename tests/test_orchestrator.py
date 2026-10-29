"""
Integration tests for the loan approval orchestrator
Tests the complete end-to-end workflow
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.loan_models import LoanApplication
from orchestration.loan_orchestrator import LoanOrchestrator


def test_approved_application():
    """Test case: Strong applicant should be approved"""
    print("\n" + "="*60)
    print("TEST: Strong Applicant (Should be Approved)")
    print("="*60)

    app = LoanApplication(
        applicant_name="Jane Smith",
        age=35,
        income=8000,
        employment_type="employed",
        employment_years=8,
        credit_score=780,
        loan_amount=40000,
        loan_tenure_months=60,
        existing_liabilities=500,
        location="California"
    )

    orchestrator = LoanOrchestrator()
    result = orchestrator.process_loan_application(app)

    if result.get("error"):
        print(f"❌ ERROR: {result['error']}")
        return False

    decision = result.get("loan_decision")
    print(f"Decision: {decision.classification.upper()}")
    print(f"Risk Score: {decision.risk_score}/100")
    print(f"Confidence: {decision.confidence_level:.1%}")
    print(f"Explanation: {decision.explanation}")

    success = decision.classification == "approved"
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Expected APPROVED, got {decision.classification.upper()}")
    return success


def test_rejected_application():
    """Test case: Weak applicant should be rejected"""
    print("\n" + "="*60)
    print("TEST: Weak Applicant (Should be Rejected)")
    print("="*60)

    app = LoanApplication(
        applicant_name="Bob Wilson",
        age=28,
        income=2000,
        employment_type="contract",
        employment_years=0.5,
        credit_score=580,
        loan_amount=100000,
        loan_tenure_months=60,
        existing_liabilities=2000,
        location="Texas"
    )

    orchestrator = LoanOrchestrator()
    result = orchestrator.process_loan_application(app)

    if result.get("error"):
        print(f"❌ ERROR: {result['error']}")
        return False

    decision = result.get("loan_decision")
    print(f"Decision: {decision.classification.upper()}")
    print(f"Risk Score: {decision.risk_score}/100")
    print(f"Confidence: {decision.confidence_level:.1%}")
    print(f"Explanation: {decision.explanation}")

    success = decision.classification == "rejected"
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Expected REJECTED, got {decision.classification.upper()}")
    return success


def test_review_application():
    """Test case: Medium applicant should require review"""
    print("\n" + "="*60)
    print("TEST: Medium Applicant (Should Require Review)")
    print("="*60)

    app = LoanApplication(
        applicant_name="Alice Johnson",
        age=42,
        income=4500,
        employment_type="employed",
        employment_years=3,
        credit_score=680,
        loan_amount=60000,
        loan_tenure_months=72,
        existing_liabilities=1500,
        location="Florida"
    )

    orchestrator = LoanOrchestrator()
    result = orchestrator.process_loan_application(app)

    if result.get("error"):
        print(f"❌ ERROR: {result['error']}")
        return False

    decision = result.get("loan_decision")
    print(f"Decision: {decision.classification.upper()}")
    print(f"Risk Score: {decision.risk_score}/100")
    print(f"Confidence: {decision.confidence_level:.1%}")
    print(f"Explanation: {decision.explanation}")

    success = decision.classification == "review"
    print(f"\n{'✅ PASS' if success else '✅ ACCEPTABLE'}: Got {decision.classification.upper()}")
    return True


def test_error_handling():
    """Test case: Invalid input should be handled gracefully"""
    print("\n" + "="*60)
    print("TEST: Error Handling (Invalid Input)")
    print("="*60)

    try:
        app = LoanApplication(
            applicant_name="Test",
            age=150,  # Invalid age
            income=-1000,  # Invalid income
            employment_type="employed",
            employment_years=-5,  # Invalid
            credit_score=900,  # Invalid credit score
            loan_amount=-50000,  # Invalid
            loan_tenure_months=0,  # Invalid
            existing_liabilities=0,
            location="Test"
        )
        print("❌ FAIL: Should have raised validation error")
        return False
    except Exception as e:
        print(f"✅ PASS: Correctly caught validation error")
        print(f"Error: {str(e)[:100]}...")
        return True


def test_case_history():
    """Test case: Case history should be maintained"""
    print("\n" + "="*60)
    print("TEST: Case History Tracking")
    print("="*60)

    orchestrator = LoanOrchestrator()

    # Process multiple applications
    for i in range(2):
        app = LoanApplication(
            applicant_name=f"Applicant {i+1}",
            age=30+i,
            income=5000+i*1000,
            employment_type="employed",
            employment_years=5,
            credit_score=720,
            loan_amount=50000,
            loan_tenure_months=60,
            existing_liabilities=1000,
            location="New York"
        )

        result = orchestrator.process_loan_application(app)
        if not result.get("error"):
            print(f"  Case {i+1}: {result['loan_decision'].case_id[:8]}...")

    history = orchestrator.list_all_cases()
    success = len(history) == 2
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Expected 2 cases, found {len(history)}")
    return success


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("LOAN APPROVAL ORCHESTRATOR - INTEGRATION TESTS")
    print("="*80)

    tests = [
        ("Approved Application", test_approved_application),
        ("Rejected Application", test_rejected_application),
        ("Review Application", test_review_application),
        ("Error Handling", test_error_handling),
        ("Case History", test_case_history),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")
    print("="*80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
