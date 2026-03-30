# MSSQL Windows CDC Setup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cài SQL Server 2022 Developer trên máy Windows, backup/restore HPS_TEST_DB từ server hiện tại, bật Agent + TCP, cấu hình CDC prerequisites sẵn sàng cho Debezium connector.

**Architecture:** Thực hiện tuần tự theo runbook `projects/bf1/dev/mssql-windows-setup.md`. Mỗi task kết thúc bằng verification query/command trước khi qua task tiếp theo. Không cần rollback — nếu một bước fail thì dừng và debug ngay tại đó.

**Tech Stack:** SQL Server 2022 Developer, SSMS, SQL Server Configuration Manager, Windows Firewall, PowerShell

**Reference:** `projects/bf1/dev/mssql-windows-setup.md` — đọc section tương ứng trước mỗi task.

---

### Task 1: Kiểm tra prerequisites và tải phần mềm

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 0

- [ ] **Step 1: Kiểm tra Windows version**

  Mở PowerShell, chạy:
  ```powershell
  winver
  ```
  Expected: Windows Server 2016+ hoặc Windows 10+

- [ ] **Step 2: Kiểm tra .NET Framework**

  ```powershell
  Get-ChildItem "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP" -Recurse |
    Get-ItemProperty -Name Version -ErrorAction SilentlyContinue |
    Where-Object { $_.PSChildName -eq "Full" } |
    Select-Object PSChildName, Version
  ```
  Expected: Version >= 4.7.2

- [ ] **Step 3: Tải SQL Server 2022 Developer**

  Vào https://www.microsoft.com/en-us/sql-server/sql-server-downloads → click **"Download now"** dưới mục Developer
  File tải về: `SQL2022-SSEI-Dev.exe`

- [ ] **Step 4: Tải SSMS**

  Vào https://aka.ms/ssmsfullsetup → tải file `SSMS-Setup-ENU.exe`

---

### Task 2: Cài SQL Server 2022 Developer

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 1

- [ ] **Step 1: Chạy installer với Custom mode**

  Right-click `SQL2022-SSEI-Dev.exe` → Run as administrator → chọn **"Custom"**
  📸 Screenshot: màn hình chọn Custom

- [ ] **Step 2: Chọn features**

  Feature Selection: tick **Database Engine Services** + **SQL Server Agent**. Bỏ các features không cần.
  📸 Screenshot: Feature Selection

- [ ] **Step 3: Cấu hình Instance**

  - Instance name: `MSSQLSERVER` (default)
  - Không đổi gì thêm
  📸 Screenshot: Instance Configuration

- [ ] **Step 4: Cấu hình Service Accounts**

  SQL Server Agent → Startup Type: **Automatic**
  📸 Screenshot: Service Accounts

- [ ] **Step 5: Cấu hình Authentication Mode**

  - Chọn **Mixed Mode**
  - Nhập SA password (ghi vào `env.sh`)
  - Click **"Add Current User"**
  📸 Screenshot: Authentication Mode

- [ ] **Step 6: Hoàn tất install**

  Click Install, chờ xong → tất cả features phải **Succeeded**
  📸 Screenshot: Installation complete

- [ ] **Step 7: Enable SA login**

  Mở SSMS (nếu chưa cài thì dùng sqlcmd), kết nối Windows Auth, chạy:
  ```sql
  ALTER LOGIN sa ENABLE;
  ALTER LOGIN sa WITH PASSWORD = '<password đã đặt>';
  GO
  ```

- [ ] **Step 8: Verify SQL Server đang chạy**

  ```powershell
  Get-Service -Name MSSQLSERVER
  # Expected: Status = Running
  ```

---

### Task 3: Cài SSMS và verify kết nối

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 2

- [ ] **Step 1: Cài SSMS**

  Chạy `SSMS-Setup-ENU.exe` as Administrator → Next, Next, Install (~5 phút)

- [ ] **Step 2: Kết nối localhost**

  Mở SSMS:
  - Server name: `localhost`
  - Authentication: SQL Server Authentication
  - Login: `sa` / (password ở env.sh)
  📸 Screenshot: Connect dialog

- [ ] **Step 3: Verify Object Explorer**

  Expand Databases, Security → thấy default system databases
  📸 Screenshot: SSMS Object Explorer

---

### Task 4: Backup `HPS_TEST_DB` từ server hiện tại

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 3
- Server nguồn: `win-server-vm.of1-dev-crm.svc.cluster.local` (SA / xem env.sh)
- Database: `HPS_TEST_DB`

> Cần kết nối được tới server nguồn (qua VPN hoặc trong K8s network)

- [ ] **Step 1: Kết nối SSMS tới server nguồn**

  New Connection:
  - Server: `win-server-vm.of1-dev-crm.svc.cluster.local`
  - Login: `sa` / (password từ env.sh)
  📸 Screenshot: kết nối thành công, thấy HPS_TEST_DB

- [ ] **Step 2: Backup qua T-SQL**

  ```sql
  BACKUP DATABASE [HPS_TEST_DB]
  TO DISK = N'C:\Backup\HPS_TEST_DB.bak'
  WITH FORMAT, INIT,
       NAME = N'HPS_TEST_DB-Full',
       STATS = 10;
  GO
  ```
  Expected: xuất hiện progress mỗi 10%, kết thúc bằng "processed X pages"

  📸 Screenshot: backup completed successfully

- [ ] **Step 3: Copy file .bak sang máy mới**

  Dùng shared folder, SCP, hoặc USB để copy `C:\Backup\HPS_TEST_DB.bak` sang máy Win mới.
  Đặt vào `C:\Backup\` trên máy mới.

---

### Task 5: Restore `HPS_TEST_DB` lên máy mới

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 4

- [ ] **Step 1: Kiểm tra logical file names**

  Kết nối SSMS tới `localhost`, chạy:
  ```sql
  RESTORE FILELISTONLY
  FROM DISK = N'C:\Backup\HPS_TEST_DB.bak';
  ```
  Ghi lại giá trị cột `LogicalName` (thường `HPS_TEST_DB` và `HPS_TEST_DB_log`)

- [ ] **Step 2: Restore database**

  ```sql
  RESTORE DATABASE [HPS_TEST_DB]
  FROM DISK = N'C:\Backup\HPS_TEST_DB.bak'
  WITH
      MOVE N'HPS_TEST_DB'     TO N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\HPS_TEST_DB.mdf',
      MOVE N'HPS_TEST_DB_log' TO N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\HPS_TEST_DB_log.ldf',
      REPLACE,
      STATS = 10;
  GO
  ```
  📸 Screenshot: "Database 'HPS_TEST_DB' restored successfully."

- [ ] **Step 3: Verify restore**

  ```sql
  USE [HPS_TEST_DB];
  GO
  SELECT COUNT(*) AS table_count
  FROM INFORMATION_SCHEMA.TABLES
  WHERE TABLE_TYPE = 'BASE TABLE';

  EXEC sp_spaceused;
  ```
  Expected: table count và size khớp với server nguồn

---

### Task 6: Bật SQL Server Agent

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 5

- [ ] **Step 1: Mở SQL Server Configuration Manager**

  Start Menu → tìm "SQL Server Configuration Manager" hoặc chạy:
  ```
  SQLServerManager16.msc
  ```

- [ ] **Step 2: Set Agent startup = Automatic và Start**

  SQL Server Services → right-click **SQL Server Agent (MSSQLSERVER)** → Properties → Start Mode: **Automatic** → OK
  Right-click lại → **Start**
  📸 Screenshot: Agent Properties, Start Mode = Automatic
  📸 Screenshot: Agent đang Running (icon xanh)

- [ ] **Step 3: Verify qua T-SQL**

  ```sql
  SELECT servicename, status_desc, startup_type_desc
  FROM sys.dm_server_services
  WHERE servicename LIKE '%Agent%';
  ```
  Expected: `status_desc = 'Running'`, `startup_type_desc = 'Automatic'`

---

### Task 7: Mở TCP/IP port 1433

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 6

- [ ] **Step 1: Enable TCP/IP**

  SQL Server Configuration Manager → SQL Server Network Configuration → Protocols for MSSQLSERVER
  Right-click **TCP/IP** → **Enable**
  📸 Screenshot: TCP/IP = Enabled

- [ ] **Step 2: Fix port 1433**

  Double-click TCP/IP → tab IP Addresses → scroll xuống **IPAll**:
  - TCP Dynamic Ports: xoá hết (để trống)
  - TCP Port: `1433`
  📸 Screenshot: IPAll, port 1433

- [ ] **Step 3: Restart SQL Server service**

  SQL Server Services → right-click **SQL Server (MSSQLSERVER)** → **Restart**
  📸 Screenshot: service restarted

- [ ] **Step 4: Tạo Windows Firewall rule**

  PowerShell as Administrator:
  ```powershell
  New-NetFirewallRule `
      -DisplayName "SQL Server 1433" `
      -Direction Inbound `
      -Protocol TCP `
      -LocalPort 1433 `
      -Action Allow

  Get-NetFirewallRule -DisplayName "SQL Server 1433" | Select DisplayName, Enabled, Direction, Action
  ```
  Expected: `Enabled = True`, `Direction = Inbound`, `Action = Allow`
  📸 Screenshot: firewall rule xuất hiện

- [ ] **Step 5: Test TCP connection**

  ```powershell
  Test-NetConnection -ComputerName localhost -Port 1433
  ```
  Expected: `TcpTestSucceeded : True`

---

### Task 8: Cấu hình CDC Prerequisites

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 7

- [ ] **Step 1: Tạo Debezium login và user**

  Kết nối SSMS tới `localhost` với `sa`:
  ```sql
  CREATE LOGIN debezium WITH PASSWORD = 'Dbz_Sandbox@2026';

  USE [HPS_TEST_DB];
  CREATE USER debezium FOR LOGIN debezium;
  ALTER ROLE db_owner ADD MEMBER debezium;
  GO
  ```

- [ ] **Step 2: Grant server-level permission**

  ```sql
  USE [master];
  GRANT VIEW SERVER STATE TO debezium;
  GO
  ```

- [ ] **Step 3: Grant CDC permissions**

  ```sql
  USE [HPS_TEST_DB];
  GO
  GRANT SELECT ON SCHEMA::cdc TO debezium;
  GRANT EXECUTE ON SCHEMA::cdc TO debezium;
  GRANT VIEW DATABASE STATE TO debezium;
  GRANT SELECT ON SCHEMA::sys TO debezium;
  GO
  ```

- [ ] **Step 4: Enable CDC ở database level**

  ```sql
  USE [HPS_TEST_DB];
  GO
  EXEC sys.sp_cdc_enable_db;
  GO

  SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'HPS_TEST_DB';
  -- Expected: is_cdc_enabled = 1
  ```

- [ ] **Step 5: Enable CDC cho table cụ thể**

  Thay `Partners` bằng tên table thực tế cần CDC:
  ```sql
  USE [HPS_TEST_DB];
  GO
  EXEC sys.sp_cdc_enable_table
      @source_schema = N'dbo',
      @source_name   = N'Partners',
      @role_name     = NULL;
  GO

  -- Verify CDC table được tạo
  SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID('cdc');
  ```

- [ ] **Step 6: Verify CDC Agent jobs**

  ```sql
  SELECT j.name, j.enabled, ja.last_run_outcome
  FROM msdb.dbo.sysjobs j
  JOIN msdb.dbo.sysjobactivity ja ON j.job_id = ja.job_id
  WHERE j.name LIKE 'cdc%'
  ORDER BY j.name;
  ```
  Expected: 2 jobs (`cdc.HPS_TEST_DB_capture` và `cdc.HPS_TEST_DB_cleanup`), cả hai `enabled = 1`
  📸 Screenshot: SQL Server Agent → Jobs → 2 CDC jobs

---

### Task 9: Final Verify & Checklist

**Files/Resources:**
- Runbook: `projects/bf1/dev/mssql-windows-setup.md` — Section 8

- [ ] **Step 1: Chạy smoke test CDC**

  ```sql
  USE [HPS_TEST_DB];
  GO
  EXEC sys.sp_cdc_help_change_data_capture;

  -- Verify debezium user có query được CDC tables
  EXECUTE AS USER = 'debezium';
  SELECT TOP 1 * FROM cdc.dbo_Partners_CT;  -- đổi tên table nếu khác
  REVERT;
  ```

- [ ] **Step 2: Tick checklist cuối runbook**

  Mở `projects/bf1/dev/mssql-windows-setup.md` Section 8.1 và tick từng mục.

- [ ] **Step 3: Ghi lại IP máy Windows**

  ```powershell
  ipconfig
  ```
  Ghi IP vào `env.sh` để dùng khi config Debezium connector:
  ```
  WIN_MSSQL_HOST=<IP>
  WIN_MSSQL_PORT=1433
  WIN_MSSQL_USER=debezium
  WIN_MSSQL_PASS=Dbz_Sandbox@2026
  WIN_MSSQL_DB=HPS_TEST_DB
  ```

- [ ] **Step 4: Setup Debezium (task tiếp theo)**

  Khi ready, xem `projects/bf1/sandbox/` và `projects/bf1/fms/cdc-architecture.md` để config Debezium connector trỏ tới máy này.

---

## Notes

- **env.sh** chứa credentials — không commit vào git
- **Debezium password** dùng trong plan này: `Dbz_Sandbox@2026` — đổi nếu cần
- **db_owner grant** là shortcut cho sandbox. Production nên dùng `db_datareader` + minimal grants
- **Phần Debezium/Docker**: plan riêng, xem `projects/bf1/sandbox/`
