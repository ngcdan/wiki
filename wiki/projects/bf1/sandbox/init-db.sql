-- ============================================================
-- BF1 Sandbox: Tạo BEE_DB, bảng Partners, bật CDC
-- Chạy bằng: ./init-db.sh
-- ============================================================

-- 1. Tạo database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'BEE_DB')
  CREATE DATABASE BEE_DB;
GO

USE BEE_DB;
GO

-- 2. Tạo bảng Partners (schema giống prod)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Partners')
CREATE TABLE dbo.Partners (
  PartnerID           NVARCHAR(100)  NOT NULL PRIMARY KEY,
  DateCreate          DATETIME       NULL,
  DateModify          DATETIME       NULL,
  PartnerName         NVARCHAR(300)  NULL,
  PartnerName2        NVARCHAR(300)  NULL,
  PartnerName3        NVARCHAR(510)  NULL,
  PersonalContact     NVARCHAR(300)  NULL,
  [Public]            BIT            NOT NULL DEFAULT 0,
  Email               NVARCHAR(510)  NULL,
  [Address]           NVARCHAR(510)  NULL,
  Address2            NVARCHAR(510)  NULL,
  Homephone           NVARCHAR(100)  NULL,
  Workphone           NVARCHAR(100)  NULL,
  Fax                 NVARCHAR(100)  NULL,
  Cell                NVARCHAR(100)  NULL,
  Taxcode             NVARCHAR(100)  NULL,
  NotesLess           NVARCHAR(MAX)  NULL,
  Notes               NVARCHAR(MAX)  NULL,
  Country             NVARCHAR(100)  NULL,
  Website             NVARCHAR(300)  NULL,
  [Group]             NVARCHAR(100)  NULL,
  GroupType           NVARCHAR(300)  NULL,
  ContactID           NVARCHAR(100)  NULL,
  FirstName           NVARCHAR(100)  NULL,
  MiddleName          NVARCHAR(100)  NULL,
  Lastname            NVARCHAR(100)  NULL,
  NickName            NVARCHAR(100)  NULL,
  JobTitle            NVARCHAR(300)  NULL,
  OnlineChat          NVARCHAR(300)  NULL,
  PhonePager          NVARCHAR(300)  NULL,
  OtherPhone          NVARCHAR(510)  NULL,
  AlternateMail1      NVARCHAR(300)  NULL,
  AlternateMail2      NVARCHAR(300)  NULL,
  FieldInterested     NVARCHAR(300)  NULL,
  VIP                 NVARCHAR(510)  NULL,
  WorkAddress         NVARCHAR(510)  NULL,
  WorkCity            NVARCHAR(300)  NULL,
  WorkState           NVARCHAR(300)  NULL,
  WorkZipcode         NVARCHAR(300)  NULL,
  Spouse              NVARCHAR(300)  NULL,
  Childrent1          NVARCHAR(300)  NULL,
  Childrent2          NVARCHAR(300)  NULL,
  SpouseBirthday      DATETIME       NULL,
  ChildrentBirthday1  DATETIME       NULL,
  ChildrentBirthday2  DATETIME       NULL,
  HomeAddress         NVARCHAR(300)  NULL,
  HomeCity            NVARCHAR(300)  NULL,
  HomeState           NVARCHAR(300)  NULL,
  HomeZipCode         NVARCHAR(300)  NULL,
  HomeCountry         NVARCHAR(300)  NULL,
  Birthday_day        NVARCHAR(100)  NULL,
  Birthday_Month      NVARCHAR(100)  NULL,
  Birthday_Year       NVARCHAR(100)  NULL,
  Anni_day            NVARCHAR(100)  NULL,
  Anni_Month          NVARCHAR(100)  NULL,
  Anni_Year           NVARCHAR(100)  NULL,
  BankAccsNo          NVARCHAR(100)  NULL,
  BankName            NVARCHAR(MAX)  NULL,
  BankAddress         NVARCHAR(510)  NULL,
  SwiftCode           NVARCHAR(100)  NULL,
  Denied              BIT            NULL DEFAULT 0,
  Warning             BIT            NULL DEFAULT 0,
  WarningMasg         NVARCHAR(510)  NULL,
  PaymentTerm         INT            NULL,
  PaymentAmount       FLOAT          NULL,
  [Location]          NVARCHAR(300)  NULL,
  Category            NVARCHAR(300)  NULL,
  CusTypeService      NVARCHAR(100)  NULL,
  GroupID             NVARCHAR(100)  NULL,
  AccRef              NVARCHAR(100)  NULL,
  InputPeople         NVARCHAR(100)  NULL,
  CompIDLinked        NVARCHAR(100)  NULL,
  PartnerRating       NVARCHAR(100)  NULL,
  PartnerRevenuePerMonth FLOAT       NULL,
  RoundupKGSMountFrom FLOAT          NULL,
  KGSRoundUpNumber    INT            NULL,
  RoundupCBMMountFrom FLOAT          NULL,
  CBMRoundUpNumber    INT            NULL,
  RounddownKGSMountFrom FLOAT        NULL,
  KGSRounddownNumber  FLOAT          NULL,
  RounddownCBMMountFrom FLOAT        NULL,
  CBMRounddownNumber  FLOAT          NULL,
  PotentialCS         BIT            NULL,
  Industry            NVARCHAR(100)  NULL,
  NoDebt              BIT            NULL,
  DateConvert         DATETIME       NULL,
  [Status]            BIT            NULL DEFAULT 0,
  SalesmanDateAssigned DATETIME      NULL,
  PaymentTerm_Inv     INT            NULL,
  SaleManEmail        NVARCHAR(400)  NULL,
  PaymentTerm_Monthly FLOAT          NULL,
  isRefund            BIT            NULL,
  DNDeadline          VARCHAR(255)   NULL,
  IATACode            NVARCHAR(100)  NULL,
  AssGroupID          DECIMAL(18,0)  NULL,
  Industy_VAT         FLOAT          NULL,
  CustomertypeID      DECIMAL(18,0)  NULL,
  RePresenttative     NVARCHAR(510)  NULL,
  BusinessStatus      NVARCHAR(510)  NULL,
  TypeOfBusiness      NVARCHAR(510)  NULL,
  PosCode             NVARCHAR(100)  NULL,
  StateCode           NVARCHAR(100)  NULL,
  AMSCode             NVARCHAR(100)  NULL,
  ACICode             NVARCHAR(100)  NULL,
  AccessCode          NVARCHAR(MAX)  NULL,
  TinCode             NVARCHAR(100)  NULL,
  Issue_inv_LC        BIT            NULL
);
GO

-- 3. Tạo indexes (giống prod)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Partners_PartnerName')
  CREATE NONCLUSTERED INDEX IX_Partners_PartnerName ON dbo.Partners(PartnerName, PartnerID);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Partners_Taxcode')
  CREATE NONCLUSTERED INDEX IX_Partners_Taxcode ON dbo.Partners(Taxcode);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Partners_ContactID')
  CREATE NONCLUSTERED INDEX IX_Partners_ContactID ON dbo.Partners(ContactID);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Partners_AccRef')
  CREATE NONCLUSTERED INDEX IX_Partners_AccRef ON dbo.Partners(AccRef);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Partners_GroupID')
  CREATE NONCLUSTERED INDEX IX_Partners_GroupID ON dbo.Partners(GroupID);
GO

-- 4. Bật CDC ở mức database
EXEC sys.sp_cdc_enable_db;
GO

-- 5. Bật CDC cho bảng Partners
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name   = N'Partners',
  @role_name     = NULL,
  @supports_net_changes = 0;
GO

-- 6. Tạo user debezium
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'debezium')
  CREATE LOGIN debezium WITH PASSWORD = 'Dbz_Sandbox@2026';
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'debezium')
  CREATE USER debezium FOR LOGIN debezium;
GO

GRANT SELECT ON SCHEMA::cdc TO debezium;
GRANT EXECUTE ON SCHEMA::cdc TO debezium;
GRANT VIEW DATABASE STATE TO debezium;
ALTER ROLE db_datareader ADD MEMBER debezium;
ALTER ROLE db_owner ADD MEMBER debezium;
GO

-- 7. Seed data mẫu
INSERT INTO dbo.Partners (PartnerID, DateCreate, DateModify, PartnerName, PartnerName2, PartnerName3,
  PersonalContact, [Public], Email, [Address], Taxcode, Country, [Group], Category, AccRef, [Status])
VALUES
  ('TEST001', GETDATE(), GETDATE(), 'CONG TY ABC', 'ABC COMPANY LTD', N'CÔNG TY TNHH ABC',
   'Mr. Nguyen', 0, 'abc@test.com', N'123 Nguyễn Huệ, Q1, HCM', '0301234567', 'VIETNAM', 'CUSTOMERS', 'CUSTOMER', 'TEST001', 1),
  ('TEST002', GETDATE(), GETDATE(), 'LOGISTICS XYZ', 'XYZ LOGISTICS CO', N'CÔNG TY VẬN TẢI XYZ',
   'Ms. Tran', 0, 'xyz@test.com', N'456 Lê Lợi, Q1, HCM', '0307654321', 'VIETNAM', 'CUSTOMERS', 'AIRLINE', 'TEST002', 1),
  ('TEST003', GETDATE(), GETDATE(), 'SHIPPING GLOBAL', 'GLOBAL SHIPPING INC', N'CÔNG TY CỔ PHẦN GLOBAL SHIPPING',
   'Mr. Le', 0, 'global@test.com', N'789 Hai Bà Trưng, Q3, HCM', '0309999888', 'VIETNAM', 'CUSTOMERS', 'CUSTOMER', 'TEST003', 0);
GO

-- 8. Kiểm tra
SELECT 'Database CDC' AS [Check], is_cdc_enabled AS [Value] FROM sys.databases WHERE name = 'BEE_DB';
SELECT 'Table CDC' AS [Check], is_tracked_by_cdc AS [Value] FROM sys.tables WHERE name = 'Partners';
SELECT 'Row count' AS [Check], COUNT(*) AS [Value] FROM dbo.Partners;
SELECT 'CDC jobs' AS [Check], job_type AS [Value] FROM msdb.dbo.cdc_jobs;
GO

PRINT '=== BEE_DB initialized: Partners table + CDC enabled + 3 seed rows ==='
GO
