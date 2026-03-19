#!/bin/bash
set -euo pipefail

SA_PASS="Bf1_Sandbox@2026"
DEBEZIUM_URL="http://localhost:8083"
CONNECTOR_NAME="mssql-bf1-sandbox"

echo "=== Containers ==="
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "(not running)"

echo ""
echo "=== MSSQL ==="
docker exec -i bf1-mssql /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASS" -C -d BEE_DB \
  -Q "SELECT COUNT(*) AS partners FROM dbo.Partners" 2>/dev/null \
  || echo "(not reachable)"

echo ""
echo "=== Debezium Connector ==="
curl -s "$DEBEZIUM_URL/connectors/$CONNECTOR_NAME/status" 2>/dev/null | jq '{
  connector: .connector.state,
  tasks: [.tasks[] | {id: .id, state: .state}]
}' || echo "(not registered)"

echo ""
echo "=== Topics ==="
curl -s "$DEBEZIUM_URL/connectors/$CONNECTOR_NAME/topics" 2>/dev/null | jq . || echo "(none)"

echo ""
echo "=== UIs ==="
echo "  Debezium REST: http://localhost:8083"
echo "  Kafka UI:      http://webui.of1-dev-kafka.svc.cluster.local/"
