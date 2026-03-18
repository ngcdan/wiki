#!/bin/bash
# Đăng ký Debezium connector
# Debezium: local Docker (:8083)
# MSSQL: local Docker (hostname "mssql" trong Docker network)
# Kafka: K8s cluster (of1-dev-kafka)
set -euo pipefail

DEBEZIUM_URL="http://localhost:8083"
CONNECTOR_NAME="mssql-bf1-sandbox"

echo "==> Waiting for Debezium Connect..."
until curl -s "$DEBEZIUM_URL/" > /dev/null 2>&1; do
  sleep 3
  echo "    waiting..."
done
echo "==> Debezium Connect is ready"

echo "==> Deleting old connector (if exists)..."
curl -s -X DELETE "$DEBEZIUM_URL/connectors/$CONNECTOR_NAME" 2>/dev/null || true
sleep 2

echo "==> Registering connector: $CONNECTOR_NAME"
curl -s -X POST "$DEBEZIUM_URL/connectors/" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "'"$CONNECTOR_NAME"'",
  "config": {
    "connector.class": "io.debezium.connector.sqlserver.SqlServerConnector",
    "tasks.max": "1",

    "database.hostname": "mssql",
    "database.port": "1433",
    "database.user": "debezium",
    "database.password": "Dbz_Sandbox@2026",
    "database.names": "BEE_DB",
    "database.applicationName": "Debezium-BF1-Sandbox",
    "database.encrypt": "false",

    "topic.prefix": "cdc-bf1-sandbox",
    "table.include.list": "dbo.Partners",

    "schema.history.internal.kafka.bootstrap.servers": "server-01.of1-dev-kafka.svc:9092,server-02.of1-dev-kafka.svc:9092,server-03.of1-dev-kafka.svc:9092",
    "schema.history.internal.kafka.topic": "dbhistory.cdc-bf1-sandbox",

    "snapshot.mode": "initial",
    "decimal.handling.mode": "string",
    "time.precision.mode": "adaptive",

    "query.fetch.size": "10000",
    "max.batch.size": "1024",
    "max.queue.size": "2048",
    "poll.interval.ms": "1000",

    "producer.override.max.request.size": "52428800",
    "producer.override.compression.type": "snappy",

    "transforms": "unwrap_schema",
    "transforms.unwrap_schema.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.unwrap_schema.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.unwrap_schema.replacement": "$1.$3"
  }
}' | jq .

sleep 5

echo ""
echo "==> Connector status:"
curl -s "$DEBEZIUM_URL/connectors/$CONNECTOR_NAME/status" | jq '{
  connector: .connector.state,
  tasks: [.tasks[] | {id: .id, state: .state}]
}'

echo ""
echo "==> Topics:"
curl -s "$DEBEZIUM_URL/connectors/$CONNECTOR_NAME/topics" 2>/dev/null | jq . || echo "(waiting...)"

echo ""
echo "============================================"
echo "  Debezium:  http://localhost:8083"
echo "  Kafka UI:  http://webui.of1-dev-kafka.svc.cluster.local/"
echo "  Topic:     cdc-bf1-sandbox.*"
echo "============================================"
