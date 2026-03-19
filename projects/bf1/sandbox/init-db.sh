#!/bin/bash
# Khởi tạo BEE_DB trong MSSQL container
# Tạo database, bảng Partners, bật CDC, seed data, tạo user debezium
set -euo pipefail

SA_PASS="Bf1_Sandbox@2026"
CONTAINER="bf1-mssql"

echo "==> Waiting for MSSQL to be ready..."
until docker exec "$CONTAINER" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASS" -C \
  -Q "SELECT 1" > /dev/null 2>&1; do
  sleep 3
  echo "    waiting..."
done
echo "==> MSSQL is ready"

echo "==> Running init-db.sql..."
docker exec -i "$CONTAINER" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASS" -C \
  < init-db.sql

echo ""
echo "==> Done! MSSQL sandbox:"
echo "    Host:     localhost:1433"
echo "    Database: BEE_DB"
echo "    SA pass:  $SA_PASS"
echo "    Debezium: debezium / Debezium@2026"
echo ""
echo "    Next: ./register-connector.sh"
