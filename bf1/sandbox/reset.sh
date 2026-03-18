#!/bin/bash
# Reset toàn bộ sandbox
set -euo pipefail

echo "WARNING: Sẽ xóa toàn bộ data (MSSQL, Kafka, offsets)!"
read -p "Tiếp tục? (y/N) " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
  echo "Cancelled."
  exit 0
fi

echo "==> Stopping all containers..."
docker compose down -v

echo "==> Starting fresh..."
docker compose up -d

echo "==> Waiting 20s for services..."
sleep 20

echo "==> Init database..."
./init-db.sh

echo "==> Register connector..."
./register-connector.sh

echo ""
echo "==> Done! Kafka UI: http://localhost:8085"
