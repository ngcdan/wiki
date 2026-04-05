# 💿 Nhật - Enhance / Fix Bugs - Week 1

> Notion ID: `2cdf924d5d7b8041ad6ddffb254131ea`
> Parent: Tasks Database → Status: Done
> Synced: 2026-04-05

## Lỗi filter data báo cáo trường hợp user bình thường [DONE]

Màn hình report ok, nút view all thì chưa được.

*(screenshot)*

## Normalize partner name, lead name [DONE]

Override setter, luôn đảm bảo partner name, lead name save xuống db luôn là upper case, loại bỏ ký tự đặc biệt. Điều này support cho search, check tax code sau này.

Viết script để cập nhật các data hiện tại.

## Check account này đang ở HCM, phân lại thành beeHAN [DONE]

Tài khoản: roxana.vnhan
Email: roxana.vnhan@beelogistics.com

## Xoá các app feature [DONE]

- company-logistics-prices ⇒ Xoá
- company-logistics-sales ⇒ rename thành `name: crm-settings` `module: crm`
- user-logistics-prices ⇒ rename thành `name: crm-pricing` `module: crm`
- user-logistics-sales ⇒ rename thành `name: crm-basic` `module: crm`

**Script:**

```javascript
DELETE FROM security_user_app_feature
WHERE app_id = 81;

DELETE FROM security_app_feature
WHERE id = 81;

UPDATE security_app_feature
SET name = 'crm-pricing',
    label = 'crm-pricing',
    module = 'crm'
WHERE name = 'user-logistics-prices';

UPDATE security_app_feature
SET name = 'crm-settings',
    label = 'crm-settings',
    module = 'crm'
WHERE name = 'company-logistics-sales';

UPDATE security_app_feature
SET name = 'crm-basic',
    label = 'crm-basic',
    module = 'crm'
WHERE name = 'user-logistics-sales';
```

## Cập nhật SaleOwnerAccount + InputAccount khi save CRMPartner [DONE]

Bổ sung field: `saleOwnerAccountId, saleOwnerFullName, requestByAccountId, requestByFullName, approveByAccountId, approveByFullName`

Remove field: `saleOwnerUsername, saleOwnerContactCode, inputUsername`

```sql
DROP INDEX IF EXISTS public.lgc_forwarder_crm_partner_input_account_id_idx;
ALTER TABLE public.lgc_forwarder_crm_partner DROP COLUMN IF EXISTS input_username;
ALTER TABLE public.lgc_forwarder_crm_partner DROP COLUMN IF EXISTS sale_owner_username;
ALTER TABLE public.lgc_forwarder_crm_partner DROP COLUMN IF EXISTS sale_owner_contact_code;

ALTER TABLE public.lgc_forwarder_crm_partner RENAME COLUMN input_account_id TO approved_by_account_id;
ALTER TABLE public.lgc_forwarder_crm_partner RENAME COLUMN input_full_name TO approved_by_full_name;

ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS request_by_account_id BIGINT;
ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS request_by_full_name VARCHAR(255);

CREATE INDEX IF NOT EXISTS lgc_forwarder_crm_partner_approved_by_account_id_idx ON public.lgc_forwarder_crm_partner(approved_by_account_id);
CREATE INDEX IF NOT EXISTS lgc_forwarder_crm_partner_request_by_account_id_idx ON public.lgc_forwarder_crm_partner(request_by_account_id);

UPDATE lgc_forwarder_crm_partner p
SET
  request_by_account_id = pr.request_by_account_id,
  request_by_full_name = pr.request_by_label,
  approved_by_account_id = pr.approved_by_account_id,
  approved_by_full_name = pr.approved_by_label
FROM lgc_forwarder_partner_request pr
WHERE p.id = pr.partner_id
  AND pr.request_by_account_id IS NOT NULL;

UPDATE lgc_forwarder_crm_partner p
SET
  request_by_account_id = p.sale_owner_account_id,
  request_by_full_name = p.sale_owner_full_name
WHERE p.request_by_account_id IS NULL
  AND p.sale_owner_account_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1
    FROM lgc_forwarder_partner_request pr
    WHERE pr.partner_id = p.id
  );
```

## Review code Partner [DONE]

### 1. Submit Tạo Partner

#### Tạo Draft Partner

```json
{
  "id": 79980,
  "created_by": "huedt",
  "created_time": "2025-12-23T14:39:33.095Z",
  "modified_by": "huedt",
  "modified_time": "2025-12-23T14:39:33.095Z",
  "storage_state": "ACTIVE",
  "version": 0,
  "account_id": null,
  "address": "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
  "bank_accs_no": null,
  "bank_address": "",
  "bank_name": "",
  "partner_code": "CS000536_TEMP",
  "category": "CUSTOMER",
  "cell": "test phone",
  "country_label": "VIETNAM",
  "email": "testmail@gmail.com",
  "fax": "",
  "partner_group": "CUSTOMERS",
  "industry_code": "I018",
  "industry_label": "Shipping; ports; fisheries; inland waterways",
  "input_username": "HPHUEDT",
  "label": "test partner",
  "localized_address": "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
  "localized_label": "test partner",
  "name": "TEST PARTNER",
  "note": "",
  "personal_contact": "test contact",
  "print_custom_confirm_bill_info": "TEST PARTNER\nXã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An\ntest contact\nTEL :test phone",
  "sale_owner_contact_code": null,
  "scope": "Domestic",
  "shareable": null,
  "source": null,
  "swift_code": "",
  "tax_code": null,
  "kcn_code": "41282",
  "kcn_label": "Khu công nghiệp Bắc Vinh",
  "investment_origin": "",
  "province_label": "Tỉnh Nghệ An",
  "lead_code": null,
  "country_id": 244,
  "province_id": 129,
  "routing": null,
  "date_created": null,
  "date_modified": null,
  "home_phone": "",
  "sale_owner_username": null,
  "work_phone": "",
  "partner_code_temp": "CS000536_TEMP",
  "group_name": "NORMAL",
  "bfsone_group_id": null,
  "is_refund": false,
  "bank_account": "",
  "status": "NEW",
  "bank_currency": null,
  "position": "test position",
  "suggestion": "",
  "vip_cellphone": null,
  "vip_contact": null,
  "vip_email": null,
  "vip_position": null,
  "work_address": null,
  "sale_owner_account_id": 62378,
  "sale_owner_full_name": "BEE HPH",
  "input_account_id": 10846,
  "input_full_name": "ĐẶNG THỊ HUẾ - HPHUEDT"
}
```

#### Tạo new Partner Request

```json
{
  "id": 337,
  "created_by": "huedt",
  "created_time": "2025-12-23T14:39:33.590Z",
  "modified_by": "huedt",
  "modified_time": "2025-12-23T14:39:33.590Z",
  "storage_state": "ACTIVE",
  "version": 0,
  "approved_by_account_id": 3,
  "approved_by_label": "LÊ NGỌC ĐÀN - JESSE.VNHPH",
  "approved_date": null,
  "approved_note": null,
  "bfsone_partner_code_temp": "CS000536_TEMP",
  "partner_id": 79980,
  "partner_label": "test partner",
  "partner_name": "TEST PARTNER",
  "request_by_account_id": 10846,
  "request_by_label": "ĐẶNG THỊ HUẾ - HPHUEDT",
  "request_date": "2025-12-23T14:39:33.475Z",
  "status": "NEW",
  "mail_cc": null,
  "mail_to": "jesse.vnhph@openfreightone.com",
  "owner_account_id": 62378,
  "owner_by_email": "beehph@beelogistics.com",
  "owner_by_label": "BEE HPH"
}
```

#### Send email request

*(screenshot)*

### 2. Kế toán approve

#### Change Partner Request to APPROVED

```json
{
  "id": 337,
  "created_by": "huedt",
  "created_time": "2025-12-23T14:39:33.590Z",
  "modified_by": "dan",
  "modified_time": "2025-12-23T14:46:32.738Z",
  "storage_state": "ACTIVE",
  "version": 1,
  "approved_by_account_id": 3,
  "approved_by_label": "LÊ NGỌC ĐÀN - JESSE.VNHPH",
  "approved_date": "2025-12-23T14:46:27.000Z",
  "approved_note": "apprpve",
  "bfsone_partner_code_temp": "CS000536_TEMP",
  "partner_id": 79980,
  "partner_label": "test partner",
  "partner_name": "TEST PARTNER",
  "request_by_account_id": 10846,
  "request_by_label": "ĐẶNG THỊ HUẾ - HPHUEDT",
  "request_date": "2025-12-23T14:39:33.475Z",
  "status": "APPROVED",
  "mail_cc": null,
  "mail_to": "jesse.vnhph@openfreightone.com",
  "owner_account_id": 62378,
  "owner_by_email": "beehph@beelogistics.com",
  "owner_by_label": "BEE HPH"
}
```

#### Send email approved

*(screenshot)*

#### Partner record có status = APPROVED

```json
{
  "id": 79980,
  "created_by": "huedt",
  "created_time": "2025-12-23T14:39:33.000Z",
  "modified_by": "dan",
  "modified_time": "2025-12-23T14:46:32.557Z",
  "storage_state": "ACTIVE",
  "version": 3,
  "account_id": null,
  "address": "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
  "partner_code": "CS000536_APPROVED",
  "category": "CUSTOMER",
  "cell": "test phone",
  "email": "testmail@gmail.com",
  "name": "TEST PARTNER",
  "status": "APPROVED",
  "sale_owner_account_id": null,
  "sale_owner_full_name": "BEE HPH",
  "input_account_id": 10846,
  "input_full_name": "ĐẶNG THỊ HUẾ - HPHUEDT"
}
```

#### Tạo partner account

```json
{
  "id": 90088,
  "created_by": "dan",
  "created_time": "2025-12-23T14:46:33.138Z",
  "modified_by": "dan",
  "modified_time": "2025-12-23T14:46:33.138Z",
  "storage_state": "ACTIVE",
  "version": 0,
  "account_type": "ORGANIZATION",
  "email": null,
  "full_name": "TEST PARTNER",
  "last_login_time": null,
  "login_id": "bee_vn.cs000536_approved",
  "mobile": null,
  "password": "$2a$10$41NDtdF6Qht9/jrzP3CinexZ.VmbeZ66SVolJmF4wEI4RtXv8Cuma",
  "legacy_login_id": "BEE_VN.CS000536_APPROVED",
  "legacy_company_login_id": null,
  "move_to_login_id": null
}
```

#### Tạo partner reference

```json
{
  "id": 66653,
  "created_by": "dan",
  "created_time": "2025-12-23T14:46:33.356Z",
  "modified_by": "dan",
  "modified_time": "2025-12-23T14:46:33.356Z",
  "storage_state": "ACTIVE",
  "version": 0,
  "account_id": 90088,
  "lead_code": null,
  "note": "",
  "partner_code": "CS000536_APPROVED",
  "partner_code_temp": "CS000536_TEMP",
  "partner_group": "CUSTOMERS",
  "partner_id": 79980,
  "partner_name": "TEST PARTNER",
  "partner_source": "BEE_VN"
}
```

### 3. Kế toán Reject

#### Change Partner Request to REJECTED

```json
{
  "id": 338,
  "created_by": "huedt",
  "created_time": "2025-12-23T14:51:58.403Z",
  "modified_by": "dan",
  "modified_time": "2025-12-23T14:52:19.669Z",
  "storage_state": "ACTIVE",
  "version": 1,
  "approved_by_account_id": 3,
  "approved_by_label": "LÊ NGỌC ĐÀN - JESSE.VNHPH",
  "approved_date": "2025-12-23T14:52:16.000Z",
  "approved_note": "reject",
  "bfsone_partner_code_temp": "CS000541_TEMP",
  "partner_id": 79981,
  "partner_label": "TEST PARTNER 2",
  "partner_name": "TEST PARTNER 2",
  "request_by_account_id": 10846,
  "request_by_label": "ĐẶNG THỊ HUẾ - HPHUEDT",
  "request_date": "2025-12-23T14:51:58.294Z",
  "status": "REJECTED",
  "mail_cc": null,
  "mail_to": "jesse.vnhph@openfreightone.com",
  "owner_account_id": 62378,
  "owner_by_email": "beehph@beelogistics.com",
  "owner_by_label": "BEE HPH"
}
```

#### Send email rejected

*(screenshot)*

## Viết script xoá toàn bộ data rác partner tạo test hôm qua [DONE]

**Script: run before start server**

```javascript
DELETE FROM lgc_forwarder_crm_message_system
WHERE reference_type = 'lgc_forwarder_partner_request'
  AND reference_id IN (
    SELECT r.id FROM lgc_forwarder_partner_request r
    LEFT JOIN lgc_forwarder_crm_partner p ON p.id = r.partner_id
    WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044)
  );

DELETE FROM lgc_forwarder_partner_request
WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);

DELETE FROM lgc_forwarder_crm_partner_reference
WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);

DELETE FROM lgc_forwarder_crm_partner_source
WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);

DELETE FROM lgc_forwarder_crm_partner
WHERE id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);
```

**Script: run after start server**

`server:migrate:run --script crm/DeletePartner.groovy`

## Review lại partner reference, chỉ review data do người dùng tạo [DONE]

Các thông tin account id, check account có trùng, đúng thông tin với partner hay không?

## Clean account entity [DONE]

*(screenshot)*

**Script:**

```javascript
ALTER TABLE public.account_account DROP COLUMN password;
ALTER TABLE public.account_account DROP COLUMN legacy_login_id;
ALTER TABLE public.account_account DROP COLUMN legacy_company_login_id;
ALTER TABLE public.account_account DROP COLUMN move_to_login_id;
ALTER TABLE public.account_account DROP COLUMN last_login_time;
```

## Review code Project [DONE]

*(screenshot)*

- Tách query searchProject riêng ra: searchProject chỉ làm đúng search projects, make it simple.
- Bỏ query trên, sau khi load list project theo phân quyền lên UI, tiếp theo select project nào thì lấy data list permission + list tasks (tạo dto gom chung vào 1 service)
- Add Permission: thêm 1 nút có chức năng custom permission, edit được chi tiết permission, thêm chức năng edit permission
- Project Attachment: storage file theo companyId userRole của project host

**Project Attachment Management:**

```
Attachment ID: 205 | Project: 49
  File: BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
  Path: projects/49/tasks/475/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
  Uploader: HUỲNH BẢO TRÂN (ID: 11570) @ bee
  Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
  Action: Move from bee -> beehcm

Attachment ID: 218 | Project: 49
  File: Báo_cáo_tuần_-_2025.xlsx
  Path: projects/49/tasks/505/Báo_cáo_tuần_-_2025.xlsx
  Uploader: LÊ TRỊNH NHƯ Ý (ID: 11583) @ bee
  Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
  Action: Move from bee -> beehcm

Attachment ID: 270 | Project: 49
  File: 2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx
  Path: projects/49/tasks/581/2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx
  Uploader: NGUYỄN THỊ BÍCH THẢO (ID: 11559) @ bee
  Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
  Action: Move from bee -> beehcm

Attachment ID: 272 | Project: 49
  File: Báo_cáo_tuần_-_2025.xlsx
  Path: projects/49/tasks/583/Báo_cáo_tuần_-_2025.xlsx
  Uploader: LÊ TRỊNH NHƯ Ý (ID: 11583) @ bee
  Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
  Action: Move from bee -> beehcm

Attachment ID: 284 | Project: 49
  File: BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
  Path: projects/49/tasks/611/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
  Uploader: HUỲNH BẢO TRÂN (ID: 11570) @ bee
  Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
  Action: Move from bee -> beehcm
```

**Move commands:**

```bash
mv ./companies/bee/projects/14/tasks/65/WEEKLY_REPORT_W05.OCT._AIREXP.xlsx ./companies/beehph/projects/14/tasks/65/WEEKLY_REPORT_W05.OCT._AIREXP.xlsx
mv ./companies/bee/projects/49/tasks/475/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx ./companies/beehcm/projects/49/tasks/475/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
mv ./companies/bee/projects/49/tasks/505/Báo_cáo_tuần_-_2025.xlsx ./companies/beehcm/projects/49/tasks/505/Báo_cáo_tuần_-_2025.xlsx
mv ./companies/bee/projects/49/tasks/581/2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx ./companies/beehcm/projects/49/tasks/581/2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx
mv ./companies/bee/projects/49/tasks/583/Báo_cáo_tuần_-_2025.xlsx ./companies/beehcm/projects/49/tasks/583/Báo_cáo_tuần_-_2025.xlsx
mv ./companies/bee/projects/49/tasks/611/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx ./companies/beehcm/projects/49/tasks/611/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
```

## Resend Request Partner. Nếu partner đã approved rồi thì ko cho resend/ đổi status nữa [DONE]

Block trên UI, throw error dưới backend. Check từ 2 phía.

## Báo giá Bee INDIA [DONE]

Detach theo company id để fix width của báo giá = A4 paper size

## Fix lỗi type settle edit [DONE]

*(screenshot)*

**Migration scripts:**

```bash
server:migrate:run --script crm/InitTaskTypeDefinitionData.groovy
server:migrate:run --script crm/DeletePartner.groovy
server:migrate:run --script crm/InitUserAppFeatureTemplates.groovy --company bee
server:migrate:run --script crm/MigrateRoleData.groovy --company bee
```

## Check lại quyền cho team IST [DONE]

**Expected:** Chỉ được phép sale lead / agent của VP. Không xem của sales khác.
- Gồm quyền chọn và quyền view
- Chọn ở báo giá, ở tasks, ở request tạo saleman...

**Implementation:** Phân quyền để là **shared**

*(screenshot)*

**Logic notes:**

- BBRefCustomerLead: mặc định show thêm Agent/Leads của sale có type = GENERAL
- Bảng Agent/Leads: nếu Client phân quyền SHARED ⇒ show thêm Agent/Leads của sale có type = GENERAL

**SQL:**

```sql
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permi_agent_potential_approve_scop_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permis_customer_lead_approve_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permiss_agent_potential_edit_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permiss_agent_potential_view_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permissio_customer_lead_edit_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permissio_customer_lead_view_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission__coloader_approve_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission__customer_approve_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_agent_approve_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_coloader_edit_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_coloader_view_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_customer_edit_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_customer_view_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_templa_agent_edit_scope_check;
ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_templa_agent_view_scope_check;
```

## Api Job Tracking [DONE]

*(screenshot)*

Jobs chưa đẩy được vào phần mềm, check để thêm thuộc tính đó vào api, vào response trả về.

## Fix BD Support UI [DONE]

*(screenshot)*

## Convert Lead → Customer [DONE]

Lỗi chưa map Source: form request chọn Freehand → Chuyển qua màn hình request click lên thấy WCA.
- 2 form cũng khác nhau.

*(screenshots)*

## Implement BD Agent Management Task Calendar Plugin [DONE]

### Implement Task Calendar plugin for Agency Agreement Follow Up, Annual Conference, Network Membership Fee in AgentManagementNetworkPlugin [DONE]

### Init Data TaskTypeDefinition [DONE]

### Migrate dữ liệu 3 bảng trên vào Task Calendar ExtendedData theo plugin [DONE]

### Chỉnh lại sắp xếp về thời gian, thêm cột status [DONE]

Status values: Upcoming, Ongoing, Attended, Completed (Not Attended), TBC

**Script:**

```sql
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_address;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_id;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_label;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_onboarding_status;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_shipping_route;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_type;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_volume_details;
ALTER TABLE public.crm_sales_task_calendar DROP COLUMN task_type;

UPDATE crm_sales_task_calendar task
SET task_group_code = (
  SELECT role."type"
  FROM lgc_forwarder_crm_user_roles role
  WHERE task.assignee_account_id = role.account_id
);

UPDATE crm_sales_task_calendar task
SET task_group_code = 'SALE_FREEHAND'
WHERE task_group_code IS NULL;

server:migrate:run --script crm/InitTaskTypeDefinitionData.groovy --company bee
server:migrate:run --script crm/MigrateBDAgentData.groovy --company bee
```

## Customize lại task cho Bee India [DONE]

Task type: Meeting Customer, thêm các trường còn thiếu.

*(screenshot)*
