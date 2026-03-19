#!/bin/bash
# Mở interactive SQL prompt vào BEE_DB
# Usage:
#   ./sql.sh                    # interactive mode
#   ./sql.sh "SELECT * FROM ..."  # one-shot query
set -euo pipefail

SA_PASS="Bf1_Sandbox@2026"
CONTAINER="bf1-mssql"

if [ $# -gt 0 ]; then
  echo "$*" | docker exec -i "$CONTAINER" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$SA_PASS" -C -d BEE_DB
else
  docker exec -it "$CONTAINER" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$SA_PASS" -C -d BEE_DB
fi
