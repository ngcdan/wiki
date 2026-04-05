# 🎖️ BF1 - Web Upgrade

> Notion ID: `326f924d5d7b80b2bd70c83bc68f3055`
> Parent: Data TP Database → Status: Planning/TODO
> Synced: 2026-04-05

## Nhiệm vụ chính
Tạo task mới. Cài đặt, setup dự án, môi trường. Sample data để mỗi bảng 2 records là đủ.

*(screenshot: project setup)*

## Telegram Group
- **Group Name:** `OF1-Dev`
- **Group ID:** `1001991820626`

## Cập nhật trạng thái cho anh Hải

### 1. Agent Conference & Meeting trong Task Calendar (BIA)
- Ưu tiên làm trước
- Tập trung phần input nhập liệu, dự kiến hoàn thành tháng 5 (có thể sớm cuối tháng 4)
- Phần biểu đồ triển khai sau khi user đã input đủ dữ liệu

### 2. SPM – Sales Performance Management
- **Report của MNG:** Đã hoàn thành và cập nhật
- **Report của từng salesman:** Release trên phần mềm vào tuần sau
- Biểu đồ sẽ làm sau, cần đủ data từ phía user
- Báo cáo ưu tiên triển khai trên CRM; IT sẽ tự cập nhật thêm nếu phát triển trên BF1

### 3. Agent / Customer Hub
- Sau khi BD duyệt và đảm bảo record đủ data
- Dự kiến IT thực hiện sau tháng 9

## Chi phí ước tính
- 150tr
- 50/tháng
- 43
- 30tr

*(screenshot: cost breakdown)*

## Dev Account & API
- Tạo account `devhcm` → phân quyền dùng chung cho toàn bộ các app
- An tạo API trong Postman:
  - **Base URL:** `https://beelogistics.cloud/platform/plugin/crm/rest/v1.0.0/rpc/internal/call`
  - **Method:** POST
  - **Param:**
    ```json
    {
       "component": "BFSOneSyncService",
       "endpoint": "syncExchangeRates",
       "userParams": {}
    }
    ```

## Meeting Note
1. Danh sách Transactions - Master Bill (show 1 tháng gần nhất)
2. Express - Chuyên phát nhanh: Khác gì so với hàng Air? Có thể gộp vào được không? Hoặc cân nhắc bỏ.
3. Thêm bảng để lưu thông tin, tracking debit riêng (thông tin các khoản phí được xuất debit/credit)

## Kiến trúc Data Sync
- **CDC:** Debezium MSSQL → Kafka → CDCListener → CDCEventHandler → save PostgreSQL
- **Batch Sync:** CronJob query MSSQL → Producer → Kafka → Consumer → save PostgreSQL
- **Write back:** Fms Entity → save PostgreSQL → Kafka → Consumer call BF1 API → MSSQL
