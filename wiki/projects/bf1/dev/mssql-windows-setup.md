---
title: "MSSQL Server - Windows Setup"
tags:
  - bf1
  - dev
  - mssql
  - setup
---

# MSSQL Server 2022 Developer — Windows Setup Runbook

> **Mục đích:** Cài đặt SQL Server 2022 Developer trên máy Windows, backup/restore `HPS_TEST_DB`, và cấu hình CDC prerequisites cho Debezium.
>
> **Phạm vi:** Chỉ phần Windows/MSSQL. Phần Debezium + Docker xem `sandbox/` và `fms/cdc-architecture.md`.

---

## 0. Prerequisites

### Kiểm tra OS

Mở **PowerShell** và chạy:

```powershell
# Kiểm tra Windows version (cần >= Windows Server 2016 hoặc Windows 10)
winver

# Kiểm tra .NET Framework (cần >= 4.7.2)
Get-ChildItem "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP" -Recurse |
  Get-ItemProperty -Name Version -ErrorAction SilentlyContinue |
  Where-Object { $_.PSChildName -eq "Full" } |
  Select-Object PSChildName, Version
```

### Links tải

| Phần mềm | Link | Ghi chú |
|---|---|---|
| SQL Server 2022 Developer | https://www.microsoft.com/en-us/sql-server/sql-server-downloads | Chọn "Developer" |
| SSMS (mới nhất) | https://aka.ms/ssmsfullsetup | Trang chính thức |
| SQL Server 2022 Docs | https://learn.microsoft.com/en-us/sql/sql-server/?view=sql-server-ver16 | Reference |
| Debezium SQL Server Connector | https://debezium.io/documentation/reference/stable/connectors/sqlserver.html | CDC config |

---

## 1. Cài SQL Server 2022 Developer

### 1.1 Chạy installer

1. Tải file `SQL2022-SSEI-Dev.exe` từ link ở trên
2. Chạy với quyền Administrator
3. Chọn **"Custom"** (không chọn Basic) để kiểm soát feature

> `📸 Screenshot: chọn "Custom" trên màn hình đầu`

### 1.2 Chọn features

Trên màn hình **Feature Selection**, tick các mục sau:

| Feature | Bắt buộc | Lý do |
|---|---|---|
| **Database Engine Services** | ✅ | Core SQL Server |
| **SQL Server Agent** | ✅ | CDC phụ thuộc Agent jobs |
| Full-Text Search | Tuỳ | Nếu cần full-text search |
| Integration Services | Không | Không cần cho CDC |

> `📸 Screenshot: Feature Selection với Database Engine + SQL Server Agent được tick`

### 1.3 Cấu hình instance

- **Instance name:** `MSSQLSERVER` (default instance — để dùng port 1433 mà không cần tên instance)
- **Instance ID:** Giữ mặc định

> `📸 Screenshot: Instance Configuration`

### 1.4 Service Accounts

- **SQL Server Agent:** Đổi Startup Type thành **Automatic** ngay tại đây
- **SQL Server Database Engine:** Để mặc định (NT AUTHORITY\SYSTEM hoặc tạo service account)

> `📸 Screenshot: Service Accounts — SQL Server Agent startup type = Automatic`

### 1.5 Authentication Mode

- Chọn **"Mixed Mode (SQL Server and Windows Authentication)"**
- Đặt password cho `sa`: dùng password mạnh, ghi vào `env.sh`
- Click **"Add Current User"** để thêm Windows account làm sysadmin

> `📸 Screenshot: Authentication Mode — chọn Mixed Mode, nhập SA password`

**Lưu ý SA password:** Phải đáp ứng complexity (>=8 ký tự, có hoa/thường/số/ký tự đặc biệt).

> **Quan trọng:** SQL Server 2022 Developer mặc định disable `sa` login ngay cả khi chọn Mixed Mode. Cần enable thủ công sau khi cài xong:
>
> ```sql
> ALTER LOGIN sa ENABLE;
> ALTER LOGIN sa WITH PASSWORD = '<password đã đặt ở trên>';
> ```

### 1.6 Hoàn tất

- Click **Install** và chờ (~10-15 phút)
- Sau khi xong, kiểm tra status: tất cả features phải **Succeeded**

> `📸 Screenshot: Installation complete — tất cả Succeeded`

---

## 2. Cài SQL Server Management Studio (SSMS)

1. Tải `SSMS-Setup-ENU.exe` từ https://aka.ms/ssmsfullsetup
2. Chạy installer, chọn thư mục cài (mặc định OK)
3. Chờ cài xong (~5 phút)

### Verify kết nối

Mở SSMS:
- **Server name:** `localhost` hoặc `.\MSSQLSERVER`
- **Authentication:** SQL Server Authentication
- **Login:** `sa` / (password đã đặt ở bước 1.5)

> `📸 Screenshot: SSMS Connect to Server dialog`
> `📸 Screenshot: SSMS Object Explorer — thấy Databases, Security, etc.`

---

## 3. Backup `HPS_TEST_DB` từ server hiện tại

### Thông tin kết nối server nguồn

```
Server:    win-server-vm.of1-dev-crm.svc.cluster.local
Port:      1433
Login:     sa
Password:  <WIN_MSSQL_SA_PASS — xem env.sh>
Database:  HPS_TEST_DB
```

> **Lưu ý:** Server này chỉ accessible từ trong K8s cluster hoặc qua VPN.

### 3.1 Kết nối SSMS tới server nguồn

Mở SSMS, New Connection:
- Server name: `win-server-vm.of1-dev-crm.svc.cluster.local`
- Authentication: SQL Server Authentication
- Login: `sa` / `<WIN_MSSQL_SA_PASS — xem env.sh>`

> `📸 Screenshot: kết nối thành công, thấy HPS_TEST_DB trong Object Explorer`

### 3.2 Backup qua SSMS (GUI)

1. Right-click **HPS_TEST_DB** → **Tasks** → **Back Up...**
2. Cấu hình:
   - **Backup type:** Full
   - **Backup component:** Database
   - **Destination:** chọn **Disk**, thêm path ví dụ `C:\Backup\HPS_TEST_DB.bak`
3. Click **OK**

> `📸 Screenshot: Back Up Database dialog`
> `📸 Screenshot: "The backup of database 'HPS_TEST_DB' completed successfully."`

### 3.3 Backup qua T-SQL (thay thế)

```sql
BACKUP DATABASE [HPS_TEST_DB]
TO DISK = N'C:\Backup\HPS_TEST_DB.bak'
WITH
    FORMAT,              -- overwrite existing backup sets
    INIT,                -- overwrite existing backup file
    NAME = N'HPS_TEST_DB-Full',
    STATS = 10;          -- progress mỗi 10%
GO
```

### 3.4 Copy file .bak sang máy mới

Sau khi backup xong, copy file `HPS_TEST_DB.bak` sang máy Win mới (dùng shared folder, SCP, hoặc USB).

---

## 4. Restore `HPS_TEST_DB` lên máy Win mới

Kết nối SSMS tới `localhost` (máy mới) trước khi restore.

### 4.1 Kiểm tra logical file names

Trước khi restore, xem tên logical files trong file .bak:

```sql
RESTORE FILELISTONLY
FROM DISK = N'C:\Backup\HPS_TEST_DB.bak';
```

Ghi lại giá trị cột `LogicalName` (thường là `HPS_TEST_DB` và `HPS_TEST_DB_log`).

### 4.2 Restore qua SSMS (GUI)

1. Right-click **Databases** → **Restore Database...**
2. **Source:** chọn **Device**, browse tới `HPS_TEST_DB.bak`
3. Kiểm tra tab **Files** — chỉnh đường dẫn ROWS/LOG nếu cần:
   - Data file: `C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\HPS_TEST_DB.mdf`
   - Log file: `C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\HPS_TEST_DB_log.ldf`
4. Tab **Options:** tick **"Overwrite the existing database (WITH REPLACE)"** nếu restore lại
5. Click **OK**

> `📸 Screenshot: Restore Database — General tab, source file`
> `📸 Screenshot: Restore Database — Files tab, data/log paths`
> `📸 Screenshot: "Database 'HPS_TEST_DB' restored successfully."`

### 4.3 Restore qua T-SQL (thay thế)

```sql
-- Thay đổi logical names nếu khác (lấy từ bước 4.1)
RESTORE DATABASE [HPS_TEST_DB]
FROM DISK = N'C:\Backup\HPS_TEST_DB.bak'
WITH
    MOVE N'HPS_TEST_DB'     TO N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\HPS_TEST_DB.mdf',
    MOVE N'HPS_TEST_DB_log' TO N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\HPS_TEST_DB_log.ldf',
    REPLACE,
    STATS = 10;
GO
```

### 4.4 Verify restore

```sql
USE [HPS_TEST_DB];
GO
-- Kiểm tra số lượng tables
SELECT COUNT(*) AS table_count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';

-- Kiểm tra size
EXEC sp_spaceused;
```

---

## 5. Bật SQL Server Agent

SQL Server Agent bắt buộc phải chạy — CDC dùng Agent jobs để capture changes.

### 5.1 Kiểm tra trạng thái

Mở **SQL Server Configuration Manager** (tìm trong Start Menu hoặc chạy `SQLServerManager16.msc`):

1. Vào **SQL Server Services**
2. Tìm **SQL Server Agent (MSSQLSERVER)**

> `📸 Screenshot: SQL Server Configuration Manager — SQL Server Services`

### 5.2 Bật Agent

Nếu Agent đang **Stopped**:

1. Right-click **SQL Server Agent (MSSQLSERVER)** → **Properties**
2. Tab **Service** → **Start Mode:** đổi thành **Automatic**
3. Click **OK**
4. Right-click lại → **Start**

> `📸 Screenshot: Agent Properties — Start Mode = Automatic`
> `📸 Screenshot: Agent đang Running (icon xanh)`

### 5.3 Verify qua SSMS

Trong SSMS Object Explorer, expand **SQL Server Agent** — phải thấy icon không có dấu X đỏ.

```sql
-- Kiểm tra Agent đang chạy
SELECT
    servicename,
    status_desc,
    startup_type_desc
FROM sys.dm_server_services
WHERE servicename LIKE '%Agent%';
```

Expected: `status_desc = 'Running'`, `startup_type_desc = 'Automatic'`

---

## 6. Mở TCP/IP Port 1433

Debezium kết nối qua TCP/IP — phải bật và fix port 1433.

### 6.1 Bật TCP/IP trong SQL Server Configuration Manager

1. Mở **SQL Server Configuration Manager**
2. Vào **SQL Server Network Configuration** → **Protocols for MSSQLSERVER**
3. Right-click **TCP/IP** → **Enable**

> `📸 Screenshot: Protocols — TCP/IP Enabled`

### 6.2 Fix port 1433

1. Double-click **TCP/IP** → tab **IP Addresses**
2. Scroll xuống **IPAll**:
   - **TCP Dynamic Ports:** xoá hết (để trống)
   - **TCP Port:** nhập `1433`
3. Click **OK**

> `📸 Screenshot: TCP/IP Properties — IPAll, port 1433`

### 6.3 Restart SQL Server service

Sau khi thay đổi network config, phải restart:

1. SQL Server Configuration Manager → **SQL Server Services**
2. Right-click **SQL Server (MSSQLSERVER)** → **Restart**

> `📸 Screenshot: Restart SQL Server service`

### 6.4 Mở Windows Firewall

Mở **PowerShell as Administrator**:

```powershell
# Tạo inbound rule cho SQL Server port 1433
New-NetFirewallRule `
    -DisplayName "SQL Server 1433" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 1433 `
    -Action Allow

# Verify
Get-NetFirewallRule -DisplayName "SQL Server 1433" | Select DisplayName, Enabled, Direction, Action
```

> `📸 Screenshot: Windows Firewall — rule SQL Server 1433 xuất hiện và Enabled`

### 6.5 Test kết nối TCP

Từ máy khác (hoặc chạy local):

```powershell
# Test port 1433 có mở không
Test-NetConnection -ComputerName localhost -Port 1433
# TcpTestSucceeded phải là True
```

---

## 7. Cấu hình CDC Prerequisites

### 7.1 Tạo Debezium login và user

Kết nối SSMS tới `localhost` với `sa`, chạy:

```sql
-- Tạo login ở cấp Server
CREATE LOGIN debezium WITH PASSWORD = 'Dbz_Sandbox@2026';

-- Tạo user trong HPS_TEST_DB
USE [HPS_TEST_DB];
CREATE USER debezium FOR LOGIN debezium;

-- Shortcut cho sandbox: db_owner bao gồm tất cả permissions cần thiết
-- Production nên dùng minimal permissions: db_datareader + các grant ở bước 7.2
ALTER ROLE db_owner ADD MEMBER debezium;
GO
```

### 7.2 Grant CDC permissions

```sql
-- Server-level permission (chạy ở master)
USE [master];
GRANT VIEW SERVER STATE TO debezium;  -- cần để Debezium query sys.dm_server_services
GO

USE [HPS_TEST_DB];
GO

-- Permissions cho CDC tables
GRANT SELECT ON SCHEMA::cdc TO debezium;
GRANT EXECUTE ON SCHEMA::cdc TO debezium;

-- Permissions để đọc transaction log
GRANT VIEW DATABASE STATE TO debezium;

-- Permissions đọc system tables
GRANT SELECT ON SCHEMA::sys TO debezium;
GO
```

### 7.3 Enable CDC ở database level

```sql
USE [HPS_TEST_DB];
GO

-- Bật CDC cho database (cần SQL Server Agent đang chạy)
EXEC sys.sp_cdc_enable_db;
GO

-- Verify
SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'HPS_TEST_DB';
-- is_cdc_enabled phải = 1
```

### 7.4 Enable CDC cho từng table

```sql
USE [HPS_TEST_DB];
GO

-- Ví dụ enable CDC cho table Partners (thay tên table phù hợp)
EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name   = N'Partners',
    @role_name     = NULL;
GO

-- Verify: CDC tables được tạo trong schema cdc
SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID('cdc');
```

### 7.5 Verify Agent CDC jobs

Sau khi enable CDC, SQL Server Agent tự tạo 2 jobs:

```sql
-- Kiểm tra CDC jobs
SELECT
    j.name,
    j.enabled,
    ja.last_run_date,
    ja.last_run_time,
    ja.last_run_outcome
FROM msdb.dbo.sysjobs j
JOIN msdb.dbo.sysjobactivity ja ON j.job_id = ja.job_id
WHERE j.name LIKE 'cdc%'
ORDER BY j.name;
```

Expected: 2 jobs — `cdc.HPS_TEST_DB_capture` và `cdc.HPS_TEST_DB_cleanup`, cả hai `enabled = 1`.

> `📸 Screenshot: SSMS — SQL Server Agent → Jobs → thấy 2 CDC jobs`

---

## 8. Verify & Smoke Test

### 8.1 Checklist

```
[ ] SQL Server 2022 Developer — installed, service Running
[ ] SSMS — installed, kết nối localhost thành công
[ ] HPS_TEST_DB — restored, table count khớp với server gốc
[ ] SQL Server Agent — Running, Startup = Automatic
[ ] TCP/IP port 1433 — Enabled, no dynamic port
[ ] Windows Firewall — rule 1433 Inbound Allow
[ ] debezium login — tạo thành công, trong db_owner
[ ] CDC enabled — is_cdc_enabled = 1 trên HPS_TEST_DB
[ ] CDC Agent jobs — 2 jobs enabled và chạy
```

### 8.2 Quick smoke test CDC

```sql
USE [HPS_TEST_DB];
GO

-- 1. Kiểm tra CDC config
EXEC sys.sp_cdc_help_change_data_capture;    -- list tables đang CDC

-- 2. Kiểm tra debezium user có query được CDC tables không
EXECUTE AS USER = 'debezium';
SELECT TOP 1 * FROM cdc.dbo_Partners_CT;     -- thay tên table
REVERT;
```

### 8.3 Test kết nối từ Debezium config

Khi chạy connector (xem `sandbox/`), dùng config:

```json
{
  "database.hostname": "<IP máy Win này>",
  "database.port": "1433",
  "database.user": "debezium",
  "database.password": "Dbz_Sandbox@2026",
  "database.names": "HPS_TEST_DB"
}
```

---

## Appendix — Links & Downloads

| Resource | URL |
|---|---|
| SQL Server 2022 Developer | https://www.microsoft.com/en-us/sql-server/sql-server-downloads |
| SSMS Latest | https://aka.ms/ssmsfullsetup |
| SQL Server 2022 Release Notes | https://learn.microsoft.com/en-us/sql/sql-server/sql-server-2022-release-notes |
| CDC Enable/Disable Reference | https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/enable-and-disable-change-data-capture-sql-server |
| Debezium SQL Server Connector | https://debezium.io/documentation/reference/stable/connectors/sqlserver.html |
| Debezium SQL Server Prerequisites | https://debezium.io/documentation/reference/stable/connectors/sqlserver.html#sqlserver-prerequisites |
| SQL Server Firewall Config | https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-a-windows-firewall-for-database-engine-access |

## Xem thêm

- [[cdc-architecture|CDC Architecture]]
- [[devlog|Developer Log]]
- [[query-reference|Query Reference]]
- [[db-schema|BEE_DB Schema]]
- Sandbox Docker setup: `../sandbox/`
- Credentials: `../env.sh` (gitignored)
