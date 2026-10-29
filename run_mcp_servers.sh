#!/bin/bash

echo "========================================="
echo "Starting All MCP Servers"
echo "========================================="
echo ""
echo "ApplicantDB MCP Server: http://127.0.0.1:8100"
echo "RiskRulesDB MCP Server: http://127.0.0.1:8101"
echo "DecisionSynthesis MCP Server: http://127.0.0.1:8102"
echo "NotificationSystem MCP Server: http://127.0.0.1:8103"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

cd "$(dirname "$0")"

echo "Starting ApplicantDB Server..."
python -m uvicorn mcp_servers.applicant_db:server --host 127.0.0.1 --port 8100 &
sleep 2

echo "Starting RiskRulesDB Server..."
python -m uvicorn mcp_servers.risk_rules_db:server --host 127.0.0.1 --port 8101 &
sleep 2

echo "Starting DecisionSynthesis Server..."
python -m uvicorn mcp_servers.decision_synthesis:server --host 127.0.0.1 --port 8102 &
sleep 2

echo "Starting NotificationSystem Server..."
python -m uvicorn mcp_servers.notification_system:server --host 127.0.0.1 --port 8103 &

echo ""
echo "All MCP servers started!"
echo "Press Ctrl+C to stop all services"

wait
