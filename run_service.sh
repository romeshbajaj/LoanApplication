#!/bin/bash

echo "========================================="
echo "Starting Loan Approval FastAPI Service"
echo "========================================="
echo ""
echo "Service will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

cd "$(dirname "$0")"

python -m uvicorn services.loan_service:app --host 0.0.0.0 --port 8000 --reload
