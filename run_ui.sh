#!/bin/bash

echo "========================================="
echo "Starting Streamlit UI Application"
echo "========================================="
echo ""
echo "UI will be available at: http://localhost:8501"
echo ""
echo "Make sure the FastAPI service is running on port 8000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

cd "$(dirname "$0")"

streamlit run ui/streamlit_app.py --logger.level=debug
