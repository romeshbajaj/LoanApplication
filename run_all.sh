#!/bin/bash

echo "========================================="
echo "INTELLIGENT LOAN APPROVAL SYSTEM"
echo "Starting All Services"
echo "========================================="
echo ""

cd "$(dirname "$0")"

# Make scripts executable
chmod +x run_service.sh run_ui.sh run_mcp_servers.sh

echo "🔧 Starting MCP Servers (background)..."
./run_mcp_servers.sh > mcp_servers.log 2>&1 &
MCP_PID=$!
sleep 5

echo "✅ MCP Servers started (PID: $MCP_PID)"
echo ""

echo "🚀 Starting FastAPI Service (background)..."
./run_service.sh > fastapi_service.log 2>&1 &
SERVICE_PID=$!
sleep 3

echo "✅ FastAPI Service started (PID: $SERVICE_PID)"
echo ""

echo "========================================="
echo "SERVICE ENDPOINTS:"
echo "========================================="
echo ""
echo "📊 Streamlit UI:"
echo "   http://localhost:8501"
echo ""
echo "🔗 FastAPI Service:"
echo "   http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "🎛️  MCP Servers:"
echo "   ApplicantDB: http://127.0.0.1:8100"
echo "   RiskRulesDB: http://127.0.0.1:8101"
echo "   DecisionSynthesis: http://127.0.0.1:8102"
echo "   NotificationSystem: http://127.0.0.1:8103"
echo ""
echo "========================================="
echo ""
echo "📝 Log files:"
echo "   MCP Servers: mcp_servers.log"
echo "   FastAPI Service: fastapi_service.log"
echo ""
echo "To stop all services, press Ctrl+C or run:"
echo "   pkill -P $$"
echo ""

# Start Streamlit UI in foreground
echo "🎨 Starting Streamlit UI..."
echo ""
streamlit run ui/streamlit_app.py --logger.level=debug

# Cleanup on exit
trap "kill $MCP_PID $SERVICE_PID 2>/dev/null; echo 'All services stopped'" EXIT
