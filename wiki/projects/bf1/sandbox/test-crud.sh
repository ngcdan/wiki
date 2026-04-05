#!/bin/bash
# Test CDC: INSERT / UPDATE / DELETE trên MSSQL → xem message trên Kafka
# Thay thế cho BF1 app — dùng SQL queries trực tiếp
set -euo pipefail

SA_PASS="Bf1_Sandbox@2026"
CONTAINER="bf1-mssql"
SQLCMD="docker exec -i $CONTAINER /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $SA_PASS -C -d BEE_DB"

run_sql() {
  echo "$1" | $SQLCMD
}

echo "============================================"
echo "  BF1 CDC Test — INSERT / UPDATE / DELETE"
echo "============================================"
echo ""
echo "Mỗi thao tác sẽ tạo CDC message trên Kafka topic: cdc-bf1-sandbox.Partners"
echo "Mở Kafka UI để xem messages realtime:"
echo "  http://webui.of1-dev-kafka.svc.cluster.local/"
echo ""

# --- INSERT ---
echo "==> [1/4] INSERT: Thêm đối tác mới..."
run_sql "
INSERT INTO dbo.Partners (PartnerID, DateCreate, DateModify, PartnerName, PartnerName2, PartnerName3,
  PersonalContact, [Public], Email, [Address], Taxcode, Country, [Group], Category, [Status])
VALUES
  ('CDC_TEST_' + FORMAT(GETDATE(), 'HHmmss'), GETDATE(), GETDATE(),
   'CDC TEST PARTNER', 'CDC TEST PARTNER LTD', N'CÔNG TY TEST CDC',
   'Mr. CDC', 0, 'cdc@test.com', N'999 Đường Test, Q1, HCM',
   '0301111111', 'VIETNAM', 'CUSTOMERS', 'CUSTOMER', 1);
SELECT 'Inserted' AS [Op], PartnerID, PartnerName FROM dbo.Partners WHERE PartnerID LIKE 'CDC_TEST_%' ORDER BY DateCreate DESC;
"
echo ""
sleep 3

# --- UPDATE ---
echo "==> [2/4] UPDATE: Cập nhật email và tên..."
run_sql "
UPDATE dbo.Partners
SET Email = 'updated_' + FORMAT(GETDATE(), 'HHmmss') + '@test.com',
    PartnerName = 'UPDATED CDC PARTNER',
    DateModify = GETDATE()
WHERE PartnerID = 'TEST001';
SELECT 'Updated' AS [Op], PartnerID, PartnerName, Email FROM dbo.Partners WHERE PartnerID = 'TEST001';
"
echo ""
sleep 3

# --- UPDATE nhiều records ---
echo "==> [3/4] BATCH UPDATE: Cập nhật Country cho 2 records..."
run_sql "
UPDATE dbo.Partners
SET Country = 'SINGAPORE', DateModify = GETDATE()
WHERE PartnerID IN ('TEST002', 'TEST003');
SELECT 'Batch Updated' AS [Op], PartnerID, PartnerName, Country FROM dbo.Partners WHERE PartnerID IN ('TEST002', 'TEST003');
"
echo ""
sleep 3

# --- DELETE ---
echo "==> [4/4] DELETE: Xóa record test..."
run_sql "
DECLARE @del_id NVARCHAR(100) = (SELECT TOP 1 PartnerID FROM dbo.Partners WHERE PartnerID LIKE 'CDC_TEST_%' ORDER BY DateCreate ASC);
IF @del_id IS NOT NULL
BEGIN
  DELETE FROM dbo.Partners WHERE PartnerID = @del_id;
  SELECT 'Deleted' AS [Op], @del_id AS PartnerID;
END
ELSE
  SELECT 'Nothing to delete' AS [Op];
"

echo ""
echo "============================================"
echo "  Done! Kiểm tra Kafka UI xem 4 CDC events:"
echo "  - 1x INSERT (op=c)"
echo "  - 2x UPDATE (op=u) — 1 single + 1 batch"
echo "  - 1x DELETE (op=d)"
echo "============================================"
echo ""
echo "Current data:"
run_sql "SELECT PartnerID, PartnerName, Email, Country, [Status] FROM dbo.Partners ORDER BY PartnerID;"
