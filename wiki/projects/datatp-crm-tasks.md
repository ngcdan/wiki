---
title: "CRM Tasks — Bug fixes & Enhancements"
tags:
  - datatp
  - crm
  - bugs
  - tasks
---

## Bugs & Enhancement


> [!note]+ Fix TODO
> ![[Screenshot_2026-01-03_at_11.14.22.png]]

> [!note]+ Implement Identity CRM User Consumer


> [!note]+ Function forgot password


> [!note]+ Nút delete role template ⇒ xoá role type và xoá app feature đi theo role type đó.
> ![[Screenshot_2026-01-22_at_15.16.23.png]]
> 
> - Sắp xếp lại form thông tin bên trái: để full name, email, mobile gần login Id, identity type để chung hàng với login id.

> [!note]+ cập nhật chức năng app feature cho identity
> ![[Screenshot_2026-01-22_at_15.21.07.png]]
> 
> - Thêm nút xoá quyền ở đây

> [!note]+ Mặc định sort theo name (role)
> ![[Screenshot_2026-01-22_at_15.25.05.png]]

Đổi username/ tạo mới account thì việc consume message 

### Sync Role Template

- Trường hợp nếu có thay đổi role template như thêm app feature, xoá app feature cấu hình theo role template đó. 
Cập nhật toàn bộ identity có role template đó, và đồng bộ với app feature mới hoặc xoá app feature cũ tương ứng.


### Sync Identity

- Mục đính: 
    - Đồng bộ thông tin identity như mail, mobile, name, username
    - Đồng bộ thông tin phân quyền theo role template
        - Nếu quyền là none thì không cần thêm bên user.


---

## IT BD Supports


1. Task Calendar cho BD Support. 
    - CRM User Role, tạo thêm user type có tên là **AMN (Agent Management Network)**
    - Update User Type AMN cho user team chị Hằng BĐ.
    - Tạo Task Definition cho type vừa tạo, tạo UI Plugin cho AMN (để giống Sale Agent).

2. Bug phân quyền: phân cho cả team support
![[Screenshot_2025-12-08_at_09.40.24.png]]

3. Agency agreement: Chuyển về Task Calendar - tạo Type tương ứng
Trước nhập ở sheet riêng, giờ chuyển hẳn nhập lên Task Calendar với Type là Agency Agreement.
Vẫn giữ màn hình báo cáo nhưng query từ Task Calendar.
Migrate data từ Report cũ.
![[Screenshot_2025-12-08_at_09.44.41.png]]



---

## Nhật — Fix Bugs Week 1


> [!note]+ Lỗi filter data báo cáo trường hợp user bình thường. **[DONE]**
> Màn hình report ok, nút view all thì chưa được. 
> 
> ![[Screenshot_2025-12-18_at_15.38.08.png]]
> 

> [!note]+ Normalize partner name, lead name **[DONE]**
> override setter, luôn đảm bảo partner name, lead name save xuống db luôn là upper case, loại bỏ ký tự đặc biệt. điều này support cho search, check tax code sau này.
> 
> Viết script để cập nhật các data hiện tại.

> [!note]+ Check account này đang ở HCM, phân lại thành beeHAN - **[DONE]**
> Tài khoản: roxana.vnhan 
> Email: [roxana.vnhan@beelogistics.com](mailto:roxana.vnhan@beelogistics.com)

> [!note]+ Xoá các app feature **[DONE]**
> company-logistics-prices ⇒ Xoá
> 
> company-logistics-sales ⇒ rename thành `name: crm-settings` `module: crm`
> 
> user-logistics-prices ⇒ rename thành `name: crm-pricing` `module: crm`
> 
> user-logistics-sales ⇒ rename thành `name: crm-basic module: crm`
> 
> script:
> 
> ```javascript
> DELETE FROM security_user_app_feature
> WHERE app_id = 81;
> 
> DELETE FROM security_app_feature 
> WHERE id = 81;
> 
> UPDATE security_app_feature
> SET name = 'crm-pricing',
> 	label = 'crm-pricing',
> 	module = 'crm'
> WHERE name = 'user-logistics-prices';
> 
> UPDATE security_app_feature
> SET name = 'crm-settings',
> 	label = 'crm-settings',
> 	module = 'crm'
> WHERE name = 'company-logistics-sales';
> 
> UPDATE security_app_feature
> SET name = 'crm-basic',
> 	label = 'crm-basic',
> 	module = 'crm'
> WHERE name = 'user-logistics-sales';
> ```

> [!note]+ Cập nhật SaleOwnerAccount + InputAccount khi save CRMPartner **[DONE]**
> bổ sung field `saleOwnerAccountId, saleOwnerFullName, requestByAccountId, requestByFullName, approveByAccountId, approveByFullName`
> 
> remove field `saleOwnerUsername, saleOwnerContactCode, inputUsername`
> 
> ```javascript
> 
> DROP INDEX IF EXISTS public.lgc_forwarder_crm_partner_input_account_id_idx;
> ALTER TABLE public.lgc_forwarder_crm_partner DROP COLUMN IF EXISTS input_username;
> ALTER TABLE public.lgc_forwarder_crm_partner DROP COLUMN IF EXISTS sale_owner_username;
> ALTER TABLE public.lgc_forwarder_crm_partner DROP COLUMN IF EXISTS sale_owner_contact_code;
> 
> ALTER TABLE public.lgc_forwarder_crm_partner RENAME COLUMN input_account_id TO approved_by_account_id;
> ALTER TABLE public.lgc_forwarder_crm_partner RENAME COLUMN input_full_name TO approved_by_full_name;
> 
> ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS request_by_account_id BIGINT;
> ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS request_by_full_name VARCHAR(255);
> 
> CREATE INDEX IF NOT EXISTS lgc_forwarder_crm_partner_approved_by_account_id_idx ON public.lgc_forwarder_crm_partner(approved_by_account_id);
> CREATE INDEX IF NOT EXISTS lgc_forwarder_crm_partner_request_by_account_id_idx ON public.lgc_forwarder_crm_partner(request_by_account_id);
> 
> UPDATE lgc_forwarder_crm_partner p
> SET 
>   request_by_account_id = pr.request_by_account_id,
>   request_by_full_name = pr.request_by_label,
>   approved_by_account_id = pr.approved_by_account_id,
>   approved_by_full_name = pr.approved_by_label
> FROM lgc_forwarder_partner_request pr
> WHERE p.id = pr.partner_id
>   AND pr.request_by_account_id IS NOT NULL;
> 
> UPDATE lgc_forwarder_crm_partner p
> SET 
>   request_by_account_id = p.sale_owner_account_id,
>   request_by_full_name = p.sale_owner_full_name
> WHERE p.request_by_account_id IS NULL
>   AND p.sale_owner_account_id IS NOT NULL
>   AND NOT EXISTS (
>     SELECT 1 
>     FROM lgc_forwarder_partner_request pr 
>     WHERE pr.partner_id = p.id
>   );
> 
> ```

> [!note]+ Review code Partner **[DONE]**
> 1. Submit Tạo Partner
> > [!note]+ Tạo Draft Partner
> > ```json
> > {
> > 		"id" : 79980,
> > 		"created_by" : "huedt",
> > 		"created_time" : "2025-12-23T14:39:33.095Z",
> > 		"modified_by" : "huedt",
> > 		"modified_time" : "2025-12-23T14:39:33.095Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"account_id" : null,
> > 		"address" : "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
> > 		"bank_accs_no" : null,
> > 		"bank_address" : "",
> > 		"bank_name" : "",
> > 		"partner_code" : "CS000536_TEMP",
> > 		"category" : "CUSTOMER",
> > 		"cell" : "test phone",
> > 		"country_label" : "VIETNAM",
> > 		"email" : "testmail@gmail.com",
> > 		"fax" : "",
> > 		"partner_group" : "CUSTOMERS",
> > 		"industry_code" : "I018",
> > 		"industry_label" : "Shipping; ports; fisheries; inland waterways ",
> > 		"input_username" : "HPHUEDT",
> > 		"label" : "test partner",
> > 		"localized_address" : "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
> > 		"localized_label" : "test partner",
> > 		"name" : "TEST PARTNER",
> > 		"note" : "",
> > 		"personal_contact" : "test contact",
> > 		"print_custom_confirm_bill_info" : "TEST PARTNER\nXã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An\ntest contact\nTEL :test phone",
> > 		"sale_owner_contact_code" : null,
> > 		"scope" : "Domestic",
> > 		"shareable" : null,
> > 		"source" : null,
> > 		"swift_code" : "",
> > 		"tax_code" : null,
> > 		"kcn_code" : "41282",
> > 		"kcn_label" : "Khu công nghiệp Bắc Vinh",
> > 		"investment_origin" : "",
> > 		"province_label" : "Tỉnh Nghệ An",
> > 		"lead_code" : null,
> > 		"country_id" : 244,
> > 		"province_id" : 129,
> > 		"routing" : null,
> > 		"date_created" : null,
> > 		"date_modified" : null,
> > 		"home_phone" : "",
> > 		"sale_owner_username" : null,
> > 		"work_phone" : "",
> > 		"partner_code_temp" : "CS000536_TEMP",
> > 		"group_name" : "NORMAL",
> > 		"bfsone_group_id" : null,
> > 		"is_refund" : false,
> > 		"bank_account" : "",
> > 		"status" : "NEW",
> > 		"bank_currency" : null,
> > 		"position" : "test position",
> > 		"suggestion" : "",
> > 		"vip_cellphone" : null,
> > 		"vip_contact" : null,
> > 		"vip_email" : null,
> > 		"vip_position" : null,
> > 		"work_address" : null,
> > 		"sale_owner_account_id" : 62378,
> > 		"sale_owner_full_name" : "BEE HPH",
> > 		"input_account_id" : 10846,
> > 		"input_full_name" : "ĐẶNG THỊ HUẾ - HPHUEDT"
> > 	}
> > ```
> 
> > [!note]+ Tạo new Partner Request
> > ```json
> > 	{
> > 		"id" : 337,
> > 		"created_by" : "huedt",
> > 		"created_time" : "2025-12-23T14:39:33.590Z",
> > 		"modified_by" : "huedt",
> > 		"modified_time" : "2025-12-23T14:39:33.590Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"approved_by_account_id" : 3,
> > 		"approved_by_label" : "LÊ NGỌC ĐÀN - JESSE.VNHPH",
> > 		"approved_date" : null,
> > 		"approved_note" : null,
> > 		"bfsone_partner_code_temp" : "CS000536_TEMP",
> > 		"partner_id" : 79980,
> > 		"partner_label" : "test partner",
> > 		"partner_name" : "TEST PARTNER",
> > 		"request_by_account_id" : 10846,
> > 		"request_by_label" : "ĐẶNG THỊ HUẾ - HPHUEDT",
> > 		"request_date" : "2025-12-23T14:39:33.475Z",
> > 		"status" : "NEW",
> > 		"mail_cc" : null,
> > 		"mail_to" : "jesse.vnhph@openfreightone.com",
> > 		"owner_account_id" : 62378,
> > 		"owner_by_email" : "beehph@beelogistics.com",
> > 		"owner_by_label" : "BEE HPH"
> > 	}
> > ```
> 
> > [!note]+ Send email request
> > ```json
> > 	{
> > 		"id" : 58904,
> > 		"created_by" : "huedt",
> > 		"created_time" : "2025-12-23T14:39:33.626Z",
> > 		"modified_by" : "huedt",
> > 		"modified_time" : "2025-12-23T14:39:33.626Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"content" : "<div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9fafb; padding: 16px;\">\n    <div style=\"background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);\">\n        <h1 style=\"color: #2563eb; font-size: 18px; margin: 0 0 16px 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px;\">\n            🤝 Customer Request - TEST PARTNER\n        <\/h1>\n\n        <div style=\"background-color: #f3f4f6; padding: 12px; border-radius: 6px; margin: 12px 0;\">\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">📅 <strong>Date:<\/strong> 23\/12\/2025<\/p>\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">🏢 <strong>Customer Name:<\/strong> TEST PARTNER<\/p>\n            <p style=\"margin: 0; color: #374151;\">👤 <strong>Requested by:<\/strong> ĐẶNG THỊ HUẾ - HPHUEDT<\/p>\n        <\/div>\n\n        <div style=\"background-color: #fffbeb; padding: 12px; border-radius: 6px; margin: 12px 0; border-left: 3px solid #f59e0b;\">\n            <p style=\"margin: 0; color: #1f2937;\"><strong>⏳ Waiting for approval by:<\/strong> LÊ NGỌC ĐÀN - JESSE.VNHPH<\/p>\n        <\/div>\n\n        <div style=\"margin: 16px 0; text-align: center;\">\n            <a href=\"https:\/\/beelogistics.cloud\" target=\"_blank\"\n               style=\"display: inline-block; background-color: #2563eb; color: #ffffff;\n                      padding: 10px 20px; border-radius: 6px; text-decoration: none;\n                      font-weight: 600; font-size: 14px;\">\n                Review Request →\n            <\/a>\n        <\/div>\n\n        <div style=\"margin-top: 16px; padding-top: 12px; border-top: 1px solid #e5e7eb;\">\n            <p style=\"color: #6b7280; font-size: 12px; margin: 0; font-style: italic;\">\n                Automated notification from CRM Task Management System\n            <\/p>\n        <\/div>\n    <\/div>\n<\/div>\n",
> > 		"error_message" : null,
> > 		"message_type" : "MAIL",
> > 		"metadata" : "{\n  \"fromEmail\" : \"dcenter@beelogistics.com\",\n  \"subject\" : \"CRM - Request Customer for TEST PARTNER\",\n  \"to\" : [ \"jesse.vnhph@openfreightone.com\" ],\n  \"ccList\" : [ \"jesse.vnhph@openfreightone.com\", \"beehph@beelogistics.com\", \"beehph@beelogistics.com\" ]\n}",
> > 		"plugin_name" : "partner-request-notification",
> > 		"purpose_details" : null,
> > 		"recipients" : "[ \"jesse.vnhph@openfreightone.com\" ]",
> > 		"reference_id" : 337,
> > 		"reference_type" : "lgc_forwarder_partner_request",
> > 		"retry_count" : 0,
> > 		"scheduled_at" : "2025-12-23T14:39:33.626Z",
> > 		"sent_at" : null,
> > 		"status" : "PENDING",
> > 		"reminder_count" : 1
> > 	}
> > ```
> 2. Kế toán approve
> > [!note]+ Change Partner Request to APPROVED
> > ```json
> > 	{
> > 		"id" : 337,
> > 		"created_by" : "huedt",
> > 		"created_time" : "2025-12-23T14:39:33.590Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:46:32.738Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 1,
> > 		"approved_by_account_id" : 3,
> > 		"approved_by_label" : "LÊ NGỌC ĐÀN - JESSE.VNHPH",
> > 		"approved_date" : "2025-12-23T14:46:27.000Z",
> > 		"approved_note" : "apprpve",
> > 		"bfsone_partner_code_temp" : "CS000536_TEMP",
> > 		"partner_id" : 79980,
> > 		"partner_label" : "test partner",
> > 		"partner_name" : "TEST PARTNER",
> > 		"request_by_account_id" : 10846,
> > 		"request_by_label" : "ĐẶNG THỊ HUẾ - HPHUEDT",
> > 		"request_date" : "2025-12-23T14:39:33.475Z",
> > 		"status" : "APPROVED",
> > 		"mail_cc" : null,
> > 		"mail_to" : "jesse.vnhph@openfreightone.com",
> > 		"owner_account_id" : 62378,
> > 		"owner_by_email" : "beehph@beelogistics.com",
> > 		"owner_by_label" : "BEE HPH"
> > 	}
> > ```
> 
> > [!note]+ Send email approved
> > ```json
> > 	{
> > 		"id" : 58905,
> > 		"created_by" : "dan",
> > 		"created_time" : "2025-12-23T14:46:32.850Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:46:32.850Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"content" : "<div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9fafb; padding: 16px;\">\n    <div style=\"background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);\">\n        <h1 style=\"color: #2563eb; font-size: 18px; margin: 0 0 16px 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px;\">\n            ✅ Partner Request - Approved\n        <\/h1>\n\n        <div style=\"background-color: #f3f4f6; padding: 12px; border-radius: 6px; margin: 12px 0;\">\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">📅 <strong>Request Date:<\/strong> 23\/12\/2025<\/p>\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">🏢 <strong>Partner Name:<\/strong> TEST PARTNER<\/p>\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">🆔 <strong>Partner ID:<\/strong> CS000536_APPROVED<\/p>\n<p style=\"margin: 0 0 4px 0; color: #374151;\">🆔 <strong>Tax code:<\/strong> N\/A<\/p>\n\n            <p style=\"margin: 0; color: #374151;\">👤 <strong>Requested by:<\/strong> ĐẶNG THỊ HUẾ - HPHUEDT<\/p>\n        <\/div>\n\n        <div style=\"background-color: #f0f9ff; padding: 12px; border-radius: 6px; margin: 12px 0; border-left: 3px solid #0ea5e9;\">\n    <p style=\"margin: 0 0 4px 0; color: #1f2937;\"><strong>✅ Approved by:<\/strong> LÊ NGỌC ĐÀN - JESSE.VNHPH<\/p>\n    <p style=\"margin: 0 0 4px 0; color: #1f2937;\"><strong>📅 Date:<\/strong> 23\/12\/2025<\/p>\n    <p style=\"margin: 0; color: #1f2937;\"><strong>📝 Note:<\/strong> apprpve<\/p>\n\n<\/div>\n\n\n        <div style=\"margin-top: 16px; padding-top: 12px; border-top: 1px solid #e5e7eb;\">\n            <p style=\"color: #6b7280; font-size: 12px; margin: 0; font-style: italic;\">\n                Automated notification from CRM Task Management System\n            <\/p>\n        <\/div>\n    <\/div>\n<\/div>\n",
> > 		"error_message" : null,
> > 		"message_type" : "MAIL",
> > 		"metadata" : "{\n  \"fromEmail\" : \"dcenter@beelogistics.com\",\n  \"subject\" : \"CRM - Approved Request for TEST PARTNER\",\n  \"to\" : [ \"huedt@beelogistics.com\" ],\n  \"ccList\" : [ \"jesse.vnhph@openfreightone.com\", \"jesse.vnhph@openfreightone.com\", \"beehph@beelogistics.com\" ]\n}",
> > 		"plugin_name" : "partner-status-notification",
> > 		"purpose_details" : null,
> > 		"recipients" : "[ \"jesse.vnhph@openfreightone.com\" ]",
> > 		"reference_id" : 337,
> > 		"reference_type" : "lgc_forwarder_partner_request",
> > 		"retry_count" : 0,
> > 		"scheduled_at" : "2025-12-23T14:46:32.850Z",
> > 		"sent_at" : null,
> > 		"status" : "PENDING",
> > 		"reminder_count" : 1
> > 	}
> > ```
> 
> > [!note]+ Partner record có status = APPROVED
> > ```json
> > {
> > 		"id" : 79980,
> > 		"created_by" : "huedt",
> > 		"created_time" : "2025-12-23T14:39:33.000Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:46:32.557Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 3,
> > 		"account_id" : null,
> > 		"address" : "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
> > 		"bank_accs_no" : null,
> > 		"bank_address" : "",
> > 		"bank_name" : "",
> > 		"partner_code" : "CS000536_APPROVED",
> > 		"category" : "CUSTOMER",
> > 		"cell" : "test phone",
> > 		"country_label" : "VIETNAM",
> > 		"email" : "testmail@gmail.com",
> > 		"fax" : "",
> > 		"partner_group" : "CUSTOMERS",
> > 		"industry_code" : "I018",
> > 		"industry_label" : "Shipping; ports; fisheries; inland waterways ",
> > 		"input_username" : "HPHUEDT",
> > 		"label" : "test partner",
> > 		"localized_address" : "Xã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An",
> > 		"localized_label" : "test partner",
> > 		"name" : "TEST PARTNER",
> > 		"note" : "",
> > 		"personal_contact" : "test contact",
> > 		"print_custom_confirm_bill_info" : "TEST PARTNER\nXã Hưng Đông, Thành phố Vinh, Tỉnh Nghệ An\ntest contact\nTEL :test phone",
> > 		"sale_owner_contact_code" : null,
> > 		"scope" : "Domestic",
> > 		"shareable" : null,
> > 		"source" : "",
> > 		"swift_code" : "",
> > 		"tax_code" : null,
> > 		"kcn_code" : "41282",
> > 		"kcn_label" : "Khu công nghiệp Bắc Vinh",
> > 		"investment_origin" : "",
> > 		"province_label" : "Tỉnh Nghệ An",
> > 		"lead_code" : null,
> > 		"country_id" : 244,
> > 		"province_id" : 129,
> > 		"routing" : null,
> > 		"date_created" : "2025-12-23T14:46:32.557Z",
> > 		"date_modified" : "2025-12-23T14:46:32.557Z",
> > 		"home_phone" : "",
> > 		"sale_owner_username" : null,
> > 		"work_phone" : "",
> > 		"partner_code_temp" : "CS000536_TEMP",
> > 		"group_name" : "NORMAL",
> > 		"bfsone_group_id" : null,
> > 		"is_refund" : false,
> > 		"bank_account" : "",
> > 		"status" : "APPROVED",
> > 		"bank_currency" : null,
> > 		"position" : "test position",
> > 		"suggestion" : "",
> > 		"vip_cellphone" : null,
> > 		"vip_contact" : null,
> > 		"vip_email" : null,
> > 		"vip_position" : null,
> > 		"work_address" : null,
> > 		"sale_owner_account_id" : null,
> > 		"sale_owner_full_name" : "BEE HPH",
> > 		"input_account_id" : 10846,
> > 		"input_full_name" : "ĐẶNG THỊ HUẾ - HPHUEDT"
> > 	}
> > ```
> 
> > [!note]+ Tạo partner account
> > ```json
> > 	{
> > 		"id" : 90088,
> > 		"created_by" : "dan",
> > 		"created_time" : "2025-12-23T14:46:33.138Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:46:33.138Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"account_type" : "ORGANIZATION",
> > 		"email" : null,
> > 		"full_name" : "TEST PARTNER",
> > 		"last_login_time" : null,
> > 		"login_id" : "bee_vn.cs000536_approved",
> > 		"mobile" : null,
> > 		"password" : "$2a$10$41NDtdF6Qht9\/jrzP3CinexZ.VmbeZ66SVolJmF4wEI4RtXv8Cuma",
> > 		"legacy_login_id" : "BEE_VN.CS000536_APPROVED",
> > 		"legacy_company_login_id" : null,
> > 		"move_to_login_id" : null
> > 	}
> > ```
> 
> > [!note]+ Tạo partner reference
> > ```json
> > 	{
> > 		"id" : 66653,
> > 		"created_by" : "dan",
> > 		"created_time" : "2025-12-23T14:46:33.356Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:46:33.356Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"account_id" : 90088,
> > 		"lead_code" : null,
> > 		"note" : "",
> > 		"partner_code" : "CS000536_APPROVED",
> > 		"partner_code_temp" : "CS000536_TEMP",
> > 		"partner_group" : "CUSTOMERS",
> > 		"partner_id" : 79980,
> > 		"partner_name" : "TEST PARTNER",
> > 		"partner_source" : "BEE_VN"
> > 	}
> > ```
> 3. Kế toán Reject
> > [!note]+ Change Partner Request to REJECTED
> > ```json
> > 	{
> > 		"id" : 338,
> > 		"created_by" : "huedt",
> > 		"created_time" : "2025-12-23T14:51:58.403Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:52:19.669Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 1,
> > 		"approved_by_account_id" : 3,
> > 		"approved_by_label" : "LÊ NGỌC ĐÀN - JESSE.VNHPH",
> > 		"approved_date" : "2025-12-23T14:52:16.000Z",
> > 		"approved_note" : "reject",
> > 		"bfsone_partner_code_temp" : "CS000541_TEMP",
> > 		"partner_id" : 79981,
> > 		"partner_label" : "TEST PARTNER 2",
> > 		"partner_name" : "TEST PARTNER 2",
> > 		"request_by_account_id" : 10846,
> > 		"request_by_label" : "ĐẶNG THỊ HUẾ - HPHUEDT",
> > 		"request_date" : "2025-12-23T14:51:58.294Z",
> > 		"status" : "REJECTED",
> > 		"mail_cc" : null,
> > 		"mail_to" : "jesse.vnhph@openfreightone.com",
> > 		"owner_account_id" : 62378,
> > 		"owner_by_email" : "beehph@beelogistics.com",
> > 		"owner_by_label" : "BEE HPH"
> > 	}
> > ```
> 
> > [!note]+ Send email rejected.
> > ```json
> > 	{
> > 		"id" : 58907,
> > 		"created_by" : "dan",
> > 		"created_time" : "2025-12-23T14:52:19.586Z",
> > 		"modified_by" : "dan",
> > 		"modified_time" : "2025-12-23T14:52:19.586Z",
> > 		"storage_state" : "ACTIVE",
> > 		"version" : 0,
> > 		"content" : "<div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9fafb; padding: 16px;\">\n    <div style=\"background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);\">\n        <h1 style=\"color: #dc2626; font-size: 18px; margin: 0 0 16px 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px;\">\n            ❌ Partner Request - Rejected\n        <\/h1>\n\n        <div style=\"background-color: #f3f4f6; padding: 12px; border-radius: 6px; margin: 12px 0;\">\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">📅 <strong>Request Date:<\/strong> 23\/12\/2025<\/p>\n            <p style=\"margin: 0 0 4px 0; color: #374151;\">🏢 <strong>Partner Name:<\/strong> TEST PARTNER 2<\/p>\n            \n            <p style=\"margin: 0; color: #374151;\">👤 <strong>Requested by:<\/strong> ĐẶNG THỊ HUẾ - HPHUEDT<\/p>\n        <\/div>\n\n        <div style=\"background-color: #fef2f2; padding: 12px; border-radius: 6px; margin: 12px 0; border-left: 3px solid #ef4444;\">\n    <p style=\"margin: 0 0 4px 0; color: #1f2937;\"><strong>❌ Rejected by:<\/strong> LÊ NGỌC ĐÀN - JESSE.VNHPH<\/p>\n    <p style=\"margin: 0 0 4px 0; color: #1f2937;\"><strong>📅 Date:<\/strong> 23\/12\/2025<\/p>\n    <p style=\"margin: 0; color: #1f2937;\"><strong>📝 Note:<\/strong> reject<\/p>\n\n<\/div>\n\n\n        <div style=\"margin-top: 16px; padding-top: 12px; border-top: 1px solid #e5e7eb;\">\n            <p style=\"color: #6b7280; font-size: 12px; margin: 0; font-style: italic;\">\n                Automated notification from CRM Task Management System\n            <\/p>\n        <\/div>\n    <\/div>\n<\/div>\n",
> > 		"error_message" : null,
> > 		"message_type" : "MAIL",
> > 		"metadata" : "{\n  \"fromEmail\" : \"dcenter@beelogistics.com\",\n  \"subject\" : \"CRM - Approved Request for TEST PARTNER 2\",\n  \"to\" : [ \"huedt@beelogistics.com\" ],\n  \"ccList\" : [ \"jesse.vnhph@openfreightone.com\", \"jesse.vnhph@openfreightone.com\", \"beehph@beelogistics.com\" ]\n}",
> > 		"plugin_name" : "partner-status-notification",
> > 		"purpose_details" : null,
> > 		"recipients" : "[ \"jesse.vnhph@openfreightone.com\" ]",
> > 		"reference_id" : 338,
> > 		"reference_type" : "lgc_forwarder_partner_request",
> > 		"retry_count" : 0,
> > 		"scheduled_at" : "2025-12-23T14:52:19.586Z",
> > 		"sent_at" : null,
> > 		"status" : "PENDING",
> > 		"reminder_count" : 1
> > 	}
> > ```

> [!note]+ Viết script xoá toàn bộ data rác partner tạo test hôm qua.  **[DONE]**
> Script: run before start server  [nqcdan](mailto:nqcdan1908@gmail.com)  
> 
> ```javascript
> DELETE FROM lgc_forwarder_crm_message_system 
> WHERE reference_type = 'lgc_forwarder_partner_request'
> 	AND reference_id IN (
> 		SELECT r.id FROM lgc_forwarder_partner_request r
> 		LEFT JOIN lgc_forwarder_crm_partner p ON p.id = r.partner_id
> 		WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044)
> 	);
> 
> DELETE FROM lgc_forwarder_partner_request 
> WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);
> 
> DELETE FROM lgc_forwarder_crm_partner_reference 
> WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);
> 
> DELETE FROM lgc_forwarder_crm_partner_source
> WHERE partner_id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);
> 
> DELETE FROM lgc_forwarder_crm_partner 
> WHERE id IN (80047, 80046, 80045, 80043, 80049, 80048, 80044);
> 
> ```
> 
> > [!note]+ Script: run after start server  [nqcdan](mailto:nqcdan1908@gmail.com)  
> 
> 
> > [!note]+ server:migrate:run --script crm/DeletePartner.groovy
> 
> 

> [!note]+ Review lại partner reference, chỉ review data do người dùng tạo.  **[DONE]**
> các thông tin account id, check account có trùng, đúng thông tin với partner hay không? 

> [!note]+ Clean account entity **[DONE]**
> ![[Screenshot_2025-12-24_at_08.36.26.png]]
> 
> script:  [nqcdan](mailto:nqcdan1908@gmail.com)  
> 
> ```javascript
> ALTER TABLE public.account_account DROP COLUMN password;
> ALTER TABLE public.account_account DROP COLUMN legacy_login_id;
> ALTER TABLE public.account_account DROP COLUMN legacy_company_login_id;
> ALTER TABLE public.account_account DROP COLUMN move_to_login_id;
> ALTER TABLE public.account_account DROP COLUMN last_login_time;
> ```
> 

> [!note]+ Review code Project **[DONE]**
> ![[Screenshot_2025-12-24_at_10.07.37.png]]
> 
> - Tách query searchProject riêng ra/ searchProject chỉ làm đúng search projects, make it simple. 
> - ~~Tách thêm query search project dashboard (list project được phân quyền + list user joined)~~
>     - ~~Dùng CTE filter lấy id của list project phân quyền trước. ~~
>     - ~~join để lấy các thông tin cần thiết của bảng projects (Tên/ Project Type) ~~
>     - ~~join để lấy thêm list permissions ~~
> - Bỏ query trên, sau khi load list project theo phân quyền lên UI, tiếp theo select project nào thì lấy data list permission + list tasks (tạo dto gom chung vào 1 service)
> - Add Permission: thêm 1 nút có chức năng custom permission, edit được chi tiết permission, thêm chức năng edit permission
> - Project Attachment: storage file theo companyId userRole của project host
> 
> ```xml
> 
> Attachment ID: 205 | Project: 49
>   File: BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
>   Path: projects/49/tasks/475/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
>   Uploader: HUỲNH BẢO TRÂN (ID: 11570) @ bee
>   Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
>   Action: Move from bee -> beehcm
> 
> Attachment ID: 218 | Project: 49
>   File: Báo_cáo_tuần_-_2025.xlsx
>   Path: projects/49/tasks/505/Báo_cáo_tuần_-_2025.xlsx
>   Uploader: LÊ TRỊNH NHƯ Ý (ID: 11583) @ bee
>   Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
>   Action: Move from bee -> beehcm
> 
> Attachment ID: 270 | Project: 49
>   File: 2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx
>   Path: projects/49/tasks/581/2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx
>   Uploader: NGUYỄN THỊ BÍCH THẢO (ID: 11559) @ bee
>   Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
>   Action: Move from bee -> beehcm
> 
> Attachment ID: 272 | Project: 49
>   File: Báo_cáo_tuần_-_2025.xlsx
>   Path: projects/49/tasks/583/Báo_cáo_tuần_-_2025.xlsx
>   Uploader: LÊ TRỊNH NHƯ Ý (ID: 11583) @ bee
>   Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
>   Action: Move from bee -> beehcm
> 
> Attachment ID: 284 | Project: 49
>   File: BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
>   Path: projects/49/tasks/611/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
>   Uploader: HUỲNH BẢO TRÂN (ID: 11570) @ bee
>   Host: NGUYỄN THỊ HÀ GIANG (ID: 11512) @ beehcm
>   Action: Move from bee -> beehcm
>   
> mv ./companies/bee/projects/14/tasks/65/WEEKLY_REPORT_W05.OCT._AIREXP.xlsx ./companies/beehph/projects/14/tasks/65/WEEKLY_REPORT_W05.OCT._AIREXP.xlsx
> mv ./companies/bee/projects/49/tasks/475/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx ./companies/beehcm/projects/49/tasks/475/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
> mv ./companies/bee/projects/49/tasks/505/Báo_cáo_tuần_-_2025.xlsx ./companies/beehcm/projects/49/tasks/505/Báo_cáo_tuần_-_2025.xlsx
> mv ./companies/bee/projects/49/tasks/581/2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx ./companies/beehcm/projects/49/tasks/581/2025_BAO_CAO_TUAN_HCMTHAONTB.xlsx
> mv ./companies/bee/projects/49/tasks/583/Báo_cáo_tuần_-_2025.xlsx ./companies/beehcm/projects/49/tasks/583/Báo_cáo_tuần_-_2025.xlsx
> mv ./companies/bee/projects/49/tasks/611/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx ./companies/beehcm/projects/49/tasks/611/BÁOCÁOTUẦN2023HUỲNHBẢOTRÂNACC02.xlsx
> ```

> [!note]+ Resend Request Partner. Nếu partner đã approved rồi thì ko cho resend/ đổi status nữa. **[DONE]**
> Block trên UI, throw error dưới backend. Check từ 2 phía. 

> [!note]+ Báo giá Bee INDIA **[DONE]**
> detach theo company id để fix width của báo giá = A4 paper size

> [!note]+ Fix lỗi type settle edit **[DONE]**
> ![[Screenshot_2025-12-26_at_16.45.58.png]]
> 
> server:migrate:run --script crm/InitTaskTypeDefinitionData.groovy
> 
> server:migrate:run --script crm/DeletePartner.groovy
> 
> server:migrate:run --script crm/InitUserAppFeatureTemplates.groovy --company bee
> 
> server:migrate:run --script crm/MigrateRoleData.groovy --company bee

> [!note]+ Check lại quyền cho team IST. **[DONE]**
> Expect: chỉ được phép sale lead/ agent của VP. không xem của sales khác. 
> 
> Implementation:
> 
> > [!note]+ ⇒ BBRefCustomerLead: mặc định show thêm Agent/Leads của sale có type = GENERAL
> 
> 
> > [!note]+ ⇒ Bảng Agent/Leads: nếu Client phân quyền SHARED ⇒ show thêm Agent/Leads của sale có type = GENERAL
> 
> 
> ```sql
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permi_agent_potential_approve_scop_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permis_customer_lead_approve_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permiss_agent_potential_edit_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permiss_agent_potential_view_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permissio_customer_lead_edit_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permissio_customer_lead_view_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission__coloader_approve_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission__customer_approve_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_agent_approve_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_coloader_edit_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_coloader_view_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_customer_edit_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_tem_customer_view_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_templa_agent_edit_scope_check;
> ALTER TABLE public.lgc_forwarder_crm_user_permission_template DROP CONSTRAINT lgc_forwarder_crm_user_permission_templa_agent_view_scope_check;
> ```

> [!note]+ Api Job Tracking **[DONE]**
> ![[Screenshot_2025-12-30_at_16.32.19.png]]
> 
> jobs chưa đẩy được vào phần mềm, check để thêm thuộc tính đó vào api, vào response trả về.

> [!note]+ Fix BD Support UI **[DONE]**
> ![[image.png]]
> 

> [!note]+ Convert Lead → Customer  **[DONE]**
> Lỗi chưa map Source, form request chọn Freehand → Chuyển qua màn hình request click lên thấy WCA.
> 
> - 2 form cũng khác nhau.
> 
> ![[image 1.png]]
> 
> ![[Screenshot_2026-01-05_at_08.27.11.png]]
> 

> [!note]+ Implement BD Agent Management Task Calendar Plugin **[DONE]**
> > [!note]+ Implement Task Calendar plugin for `**Agency Agreement Follow Up, Annual Conference, Network Membership Fee**` in `AgentManagementNetworkPlugin`  **[DONE]**
> 
> 
> > [!note]+ Init Data TaskTypeDefinition  **[DONE]**
> 
> 
> > [!note]+ Migrate dữ liệu 3 bảng trên vào Task Calendar ExtendedData theo plugin  **[DONE]**
> 
> 
> > [!note]+ Chỉnh lại sắp xếp về thời gian, thêm cột status: Upcoming, Ongoing, Attended, Completed (Not Attended), TBC  **[DONE]**
> 
> 
> > [!note]+ script:
> > ```shell
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_address;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_id;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_label;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_onboarding_status;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_shipping_route;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_type;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN partner_volume_details;
> > ALTER TABLE public.crm_sales_task_calendar DROP COLUMN task_type;
> > 
> > UPDATE crm_sales_task_calendar task
> > SET task_group_code = (
> > 	SELECT role."type" 
> > 	FROM lgc_forwarder_crm_user_roles role
> > 	WHERE task.assignee_account_id = role.account_id 
> > );
> > 
> > UPDATE crm_sales_task_calendar task
> > SET task_group_code = 'SALE_FREEHAND'
> > WHERE task_group_code IS NULL;
> > 
> > 
> > 
> > 
> > server:migrate:run --script crm/InitTaskTypeDefinitionData.groovy --company bee
> > server:migrate:run --script crm/MigrateBDAgentData.groovy --company bee
> > ```
> 

> [!note]+ Customize lại task cho Bee India, task type là Meeting Customer, thêm các trường còn thiếu như dưới nhé **[DONE]**
> ![[image 2.png]]




---

## Nhật — Maintenance Week 2


> [!note]+ Enhance màn hình Lead/ Agent Potential **[DONE]**
> ![[image 3.png]]
> 
> Nút bị vỡ, bỏ check tax code nếu là màn hình HD. Bỏ luôn show 2000 records
> 
> Nút Request Customer: check để block không cho user click khi ko tích đúng 1 record trên bảng.
> 
> Remove nút check tax code ở Lead List

> [!note]+ Phân quyền Reports **[DONE]**
> ```shell
> crm-admin-report, crm-report, crm-sale-report, crm-pricing-report, crm-bd-report
> 
> Performance Overview: ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
> Sales Performance:    ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
> Sales Activities:     ['crm-admin-report', 'crm-report']
> Sales Dashboard:      ['crm-admin-report', 'crm-sale-report']
> Pricing Dashboard:    ['crm-admin-report', 'crm-pricing-report']
> Salesman Tracker:     ['crm-admin-report', 'crm-report']
> Quotation Summaries:  ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
> Quotation Details:    ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
> Quotation Partners:   ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
> Quotation Markets:    ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
> Pricing Performance:  ['crm-admin-report', 'crm-pricing-report']
> Agent Transactions:   ['crm-admin-report', 'crm-bd-report']
> Agency Agreements:    ['crm-admin-report', 'crm-bd-report']
> Annual Conferences:   ['crm-admin-report', 'crm-bd-report']
> N. Membership Fees:   ['crm-admin-report', 'crm-bd-report']
> BD Reports:           ['crm-admin-report']
> ```
> 
> ![[image 4.png]]
> 
> Tạo, cập nhật thêm app feature: crm-report (report chung), crm-sale-report (SALE_FREEHAND), crm-bd-report (SALE AGENT,AMN), crm-admin-report, crm-pricing-report (CRM PRICE). 
> Viết script, cập nhật phân quyền cho users vào báo cáo đó tương ứng. Review lại code ui báo cáo report manager. 
> Account dan, a Quý, a Vinh, a Tuấn, a Henry mặc định vào all báo cáo. 
> 
> > [!note]+ Script
> > ```shell
> > server:migrate:run --script company/InitAppFeatures.groovy --company bee
> > server:migrate:run --script crm/MigrateUserAppFeature.groovy --company bee
> > ```
> > 

> [!note]+ Tạo Asset cho HPH **[DONE]**
> ![[Screenshot_2026-01-14_at_10.45.02.png]]

> [!note]+ Cập nhật lại phần approve partner. [DONE]
> update để cho phép nhiều người cùng có quyền approve trên 1 request.
> 
> Thêm field requestedCompanyBranchCode vào partner_request
> 
> Lúc tạo request khoan hãy set approve account id, set sau khi được approve. 
> 
> Mail request, gửi cho user được phân quyền COMPANY_ONLY + GROUP_ALL có companyBranchCode giống với người request
> 
> Bỏ thông tin người approve trong mail request partner, chỉ để trong mail lúc approve. 
> 
> Màn hình PartnerRequest query filter theo companyBranchCode của client(COPMANY_ONLY), hiện hết(GROUP_ALL)
> 
> Script:
> 
> …
> 

> [!note]+ Export thông tin book xe theo thời gian ra file excel. **[DONE]**
> review để các thông tin cần thiết.
> 
> ![[Screenshot_2026-01-16_at_08.36.33.png]]
> 
> Để thêm tab các tasks booking xe, lịch họp dạng bảng ở đây, để thêm nút export để xuất dữ liệu, ko sửa bên màn hình booking xe (calendar)

> [!note]+ Export bảng giá  **[DONE]**
> > [!note]+ Attach vào mail rồi gửi cho user sau khi click Export, nếu gửi mail failed ~~⇒ download thẳng file excel thay vì popup màn hình export options.~~
> 
> 
> > [!note]+ cc mail cho a Vinh, có CRM User role mới export được. Còn không thì ko export được. 
> 
> 
> > [!note]+ Thêm cơ chế cho phép moderator của app export trực tiếp không qua mail. 
> 

> [!note]+ Check lỗi gọi cron, sync cho task đổi status to complete. **[DONE]**
> ![[Screenshot_2026-01-20_at_09.06.17.png]]
> 
> - Thêm zalo message cho Đàn để monitor, nhớ note/ comment để sau bỏ đi.

> [!note]+ Check lỗi unit này cho a Minh **[DONE]**
> filter data unit from bee_legacy
> 
> ![[Screenshot_2026-01-20_at_09.52.48.png]]
> 

> [!note]+ Agent Transaction: để thêm các cột revenue/ profit.  **[DONE]**
> check BD report app quyền moderator mới xem được revenue/ profit.

> [!note]+ Ở crm user role export cái api để call lấy thông tin crm user role. **[DONE]**
> Từ logic lịch họp, call api từ crm user role để lấy thông tin Work Place, show lên trước subject mail [Car Request] - [BEE - Hải Dương] - Người request: ....
> 
> dựa vào work place để xác định gửi mail approval

> [!note]+ gọi Api với bee_legacy để update thông tin partner  **[DONE]**
> ![[Screenshot_2026-01-20_at_13.44.06.png]]
> 
> > [!note]+ script
> > ```shell
> > server:migrate:run --script crm/UpdateIntegratedPartner.groovy --company bee
> > ```
> 
> - code script để sync toàn bộ data partner từ cloud qua bee legacy.

> [!note]+ Update lại thông tin legacy_db.integrated_partner **[DONE]**
> bổ sung các field còn thiếu theo CRMPartner
> 

---

> [!note]+ Cập nhật Form request Pricing [DONE]
> - Thêm Pricing Branch (VP Pricing xử lý inquiry này)
> - Mặc định sales VP nào gửi cho Pricing văn phòng đó. 
> - Thêm message confirm hỏi trước khi gửi, hỏi sales xem có phải muốn gửi cho [Pricing HPH] hay không? 
> > [!note]+ script:
> > ```sql
> > ALTER TABLE public.lgc_price_inquiry_request ADD pricing_company_branch_code varchar NULL;
> > ALTER TABLE public.lgc_price_inquiry_request ADD pricing_company_branch_name varchar NULL;
> > 
> > UPDATE public.lgc_price_inquiry_request req
> > SET
> >     pricing_company_branch_code = role.company_branch_code,
> >     pricing_company_branch_name = role.company_branch_name
> > FROM lgc_forwarder_crm_user_roles role
> > WHERE role.account_id = req.pricing_account_id;
> > 
> > UPDATE public.lgc_price_inquiry_request req
> > SET
> >     pricing_company_branch_code = role.company_branch_code,
> >     pricing_company_branch_name = role.company_branch_name
> > FROM lgc_forwarder_crm_user_roles role
> > WHERE req.pricing_company_branch_code IS NULL
> >   AND role.account_id = req.saleman_account_id;
> > 
> > ```

> [!note]+ CronJob cập nhật lại status SaleTask không save được [DONE]
> ![[image 5.png]]

> [!note]+ Kiểm tra lỗi Partner được approve nhưng request không cập nhật lại code mới từ BFS [DONE]
> ![[image 6.png]]

---

> [!note]+ Inquiry Request: set mail to mặc định theo văn phòng HP + HN + DAD  [DONE]
> ![[image 7.png]]

> [!note]+ Move code FE Utility về platform. (ưu tiên sau)  [DONE]


> [!note]+ Clean Code BD Report  [DONE]
> > [!note]+ script
> > ```sql
> > DROP TABLE public.lgc_forwarder_crm_agency_agreement_follow_up;
> > DROP TABLE public.lgc_forwarder_crm_network_membership_fee;
> > DROP TABLE public.lgc_forwarder_crm_annual_conference;
> > ```
> 
> ![[image 8.png]]

> [!note]+ Kiểm tra trường hợp 1 user access được nhiều hơn 1 Company (trừ account của dev)  (ưu tiên sau) [DONE]
> script: 

> [!note]+ Bổ sung api Token cho các văn phòng lên postman **[DONE]**
> **Server1: pros.openfreightone.com,34541**
> 
> - **Bee trans**
> 
> DBName: TRN_DB
> 
> Token: Cv4XzDuxGD1y4DQhtavGckTeliVRckT3Z1NL4B0WATm13yghaLU1A7pFjc7zMXcb7MdMvGQkwtVekJavtT0zTvdN9gRmGk+TDzcaBV0cMn59wzfzxACLStPvC+dVuLXsAWiH5i1YWLmdWVOQPRY+mU0c0RlrlGL95DYtXrH0QFplnKL71VHiaoeabmFCbCi8Kk0Ya0Y5Cl+ZX+904IoYCgQeJY6NEt9Y5cVG/ucLnL21M8ZV+FTsFj/n1uSqHN/qp6qcUO/xrmXYmSfgCT7I9YhhplRqRC3mzcGQXOGkx1BNOLIFySFCPhfHawI2TEw/iY4xE6ZT1fmqXTS7Wv/tqQ==
> 
> - **Bee distr**
> 
> DBName: BEEDIS_DB
> 
> Token: i57fNyr+fdDSWSXLOWts/JpHPuNMo1BO6WDargulqlhF/yE2ANgdquIPwq1fl+8XM4uPhaBp+4tQCrGI8Gl61l3/52igjmpuJXvuDb8V2bc78U9QhKIb7C4r2a92T/CORhoxslqUY5Fs8UzCBa7BG3VNBqLoQyBGH9y/BytfAr6kvIcZOzFyUB7VTc0XEVNFIt5bdtxcoDhypTvhTVmRDcVYBgOtW6Rm7IESWfyOc5LiPsnRU3NbLD6B7nghxyyTaIU5zWWdr1uu/kerktUi7BfD1s1f/i0xscDC3OsDe8+lQ16AZnSqNB2/o716Ww+rdvPaF20zkqwGsOKCDfJhdQ==
> 
> - **Bee proj**
> 
> DBName: BEEPROJ_DB
> 
> Token: rhpU+V2W2tHmrDcQioN1YW0xkEQl+fC3Vg2Jp0W0yPMQseHyJmxSwCFgq3yU3GMskVd89xhYtJ0E3tIt3W3RBcnDoF3F8TaqG+URr9kFgTlc3wywRN6gs7By/VijFePrR9nLSJDJsELh85qh58A7z1dHFacZf1AgFWJnZK6pdSrhnNWSWaJvQPo2xhtXbTlyVrXs9VHc8DCizf+bItqXo2VM2FJ5SCH7Q8jtB8AAD/Lz0UeJC1p/U/6uOGjItv6rNFvoeXCua9XODxGT7YEsr/QwrXif3JSs33O++Yy3av4DUJ2bRA/iMzmyt4xnchYvXgyqGpa++RNdJ+6ZFA23tg==
> 
> - **Beescs**
> 
> DBName: BEESCS_DB
> 
> Token: ly9VrOFY6NNt9Iq5ZZDdEoqnKy38Nlcwnu3Hfrm6PK4vJEyeC8eKTesyGFeeaKz4HoX1VIfFtZQmVwUbE8nkcPVZm/3y0MlrVLvJxDXz9rcmsTL4n5PUP7VbLomNbKiRrnyJRFAsDbKeHJAenI3x3X4W/p989XnsER755pZeG3pz5D0/UNvznMyOOa8+5FRcj+/Lc+zVtQUUGNQSXzusnx9wF2vFohstX5/1UQrUM7mM16QFoTE3i2FW8g+RAmtpOG1fIVGMXQH0AlMwvC2P2pelLHn5iApkCunbphUJjuGTg+MSGFK1pECZQP47TURPmkLGvofJkZ09c2YLfTrKwA==
> 
> - **Bee lào**
> 
> DBName: LAOS_DB
> 
> Token: I4dS4VVSlIIZrCKkKI+fq2pdvx7PjPp+vzm151SPff4AQaRXug0lRyGyncC06omnHjmQ/zz74mf7aEeSJkdCieI992hWceQzHffYq4aHsI1mVtsb2Td07/CM2VJn3jzaoGIzoYZOgKybLgmLWYjc8W+gvP+U+Bu7rcrH2qZnDcdRTa5Z9hx8+eVlZZUgbByXr2rjEXRryGKU9d89A7tdmmvA5TU7AnMPgyV698UkV+Gup0QFFWShJCQdRMD+K1FsQ0RHvvGCsM823RmH9ZOYGz6kkpaxk60LSKpyh5wE5REjmiyukr1deCCuW6bYJhHCXCpa6ihEwphy4IiY493jzg==
> 
> - **Bond**
> 
> DBName: BOND_DB
> 
> Token: Zvb1jcmEYqIuRg6xQEpiIgc4avGTpyWCOLNPdJJyizGFbLBtb7JvB+gu863pPcRY5ACSRHfIgc5H/mVJngCOjQdTWY5Ax4Cr5NkoDmrFNdyObBr+sc6d2yWY4i2RSzHlpk4+Un1P0V2lso2yMat3C00FuExGI8ZYkwnciiR7XLSfMzROCmSm9+ZE8RqvA2bnOGu0qC/bAKDVxsru7XFhOgNnPoSr32C6MKpbikKmzTwKPN27nkkugZekmyO6zu7JCGWEMt9x00mHKoOtiqkSaX4OZ6hRULRXQi69N4XNCGRN4BfdCaY0QeeMI8QsBoBBZYhl8f5H8yp5sZUbB9rdKQ==
> 
> - **Hang hải**
> 
> DBName: HANGHAI_DB
> 
> Token: NJQG7Z+oFudq89c2/nW3Vo1JjXdWtygOs9FcbzBBY5ALqk2yQSyYocTNy/fMIQNLG6iPOwnbmXx3qyoyP+8eCoWIDpmgh0JgUy122zUciP3jaI2/mG6BJYKow0e5B91GwdWemEhm891QSeYPoAZ1OG024p5pgKjB4ngNG9i01huuZgtUymihiMEgIgSrVe9rkXc9QtehWDX/mQJrkqeQzCOQ/9P/iCzLhQ0ytHOUpQLZY3zJJ5ovo3dQfaITbZ4dNbysl/kdzkT5HxNsNiT8y+yCOndzypKe/eJwqRb3jLnghnup9thUOqyfvaUHkUiOC9a0ctokhqhhc1CE8vGtEg==
> 
> - **Pros**
> 
> DBName: PROS_DB
> 
> Token: a0GBcktpFO2w5lFVWC6pvolUaV1OcALYJKs2aEDnoGAY1LkMoaRwL7PXDDG5f2hzgzzFNbKKxgcJ991cohW4q3oo5JV7EJ8ElZeoHdCfM6Ys1eNIkzQWDaJN1afzmyRIP5QhPbEMzwU/onHtSwVXAVj2aDxJib1iZ/Dnr4XKYv3Q6M9RN3ZGPQnKiGA3EXpkPnm5B9xO2VfxtMx9HmBhvhKCHwpZ6yv9uyXyhQclJXnnUcYLftqMJRsLTO8aQQsNycvdKOcuTtpsPirDxxoAF8vYD7/pOdrsMCh+Fm5B61fu9e1TgA1xRzCaJQAM36QV6Bk27OXlnFqgTnqPdZJHbw==
> 
> **Server2: hpsvn.openfreightone.com,34541**
> 
> - **HPS**
> 
> DBName: HPS_DB
> 
> Token: f0J5sVH6mRyxc4obkfEgjFPJe8GAMAAuA0qLrsQWl7jrOF5SYNOQ+SmPX9hxbNrGZzbcYF9twLA96gdY0/vpTSrv3fEwHOH0GTDPf3APa7rz80amEXWvWZS1D0Gmjk2WuE459nN1mXYasW3kWR3C8HgGFu7R8yIIQ8OegN5XwCb40Ur0UU1fGB7Ie2q4ThQ9eP5QCMCAuHwRRlu+UyqEA9k+doknJvaON1N9HRpCuAHYq+cwLhT45Rvci1uJBt8wpRYoFON4bignHIk3o1zAXbyXoHfxSrDs9qR9btbvOlmjGjuM5MX1QXRTk9LGgzlPT/xWT6l+UQRnOcL8mSabxg==
> 
> - **BEE INDO**
> 
> DBName: INDO_DB
> 
> Token: YgT7SNb5A1n4eCYce3AYyhEQW3LaEDQN9pM558oxvUOQVeLZOVmptpDXqUCOxptjtpZNbcXBe2yyrTVt42blUIqGMu0KPDiwSvn8f/ATjidRRH7t2A20/JDSEIwv/rUA5Ggs7XK49QXt+0HEd5pELaJc+ZPdQYDJmSESWmuJabdseQ6o2ZDheiIvmAQywVAqulWXZTvo8H+XsnZRDV9Z40ojuQKWrP9AEHYKgl1TqKdhV+c+gWcdGffDlnLVj8a01ha2o2/TcXlUsD6XMVYc4ekrMtt4NIG0BMdo3uIn4dWPVJquaMZAkljJW2CxGD+FmA2jOcL3RhtiK7ekfSiTbw==
> 
> - **THỦ ĐÔ**
> 
> DBName: TD_DB
> 
> Token: VjKSxUU1UivA4fuPgExAPh5PqG4pldQRd8hdG1oEdVGQfGlxfhpVkszlYDEbeMSWcv39o5UpqCOjHFBxS+04YwN3vMEZ4xn/adzn/P9DiJYNAWuFT20eErzUJevmnB5VaruEmymneK1jW3rCjr8vI+JsgidS2/hJ28iRuA+vTjVDCUuJwpkkyeTyJDaO0VPHcwM59gy691qKcsOyi+AzE6f+XAOY2KMEy4YefBdYmuyWfPBdPbjpg/IL6iwGHHdo4tQTXX5f7K4ZovbrxVDyVJy1Lm/95nu2fJB2c+itHks6uUugsZBTNqG0voRQHbGwIi3EuJx3r+dKpnI0FPP/+Q==
> 
> - **TIẾN ĐẠT**
> 
> DBName: TIENDAT_DB
> 
> Token: qRAoFHN/pMPhyEfzPPN9uYXluQAlogK1hIBkyKtlYLd1AuQ/aSFOPfbRhyVG8IbJVr1c4qrESVSD4N8VuYxtbNfZ9N718dQyQSYZg5wZjhSsUiz2pA/16v2a8Mx3NBK7RsggA1XjsC2LE7SU5vKIPYtulYgD2C6cgxiHdSC70Xd+Hbu/8egF5QVbHYJVDGFw+bhs89+5D5I86FPn2ja06LUQQ05MloMY19TDDFOJEQrfRRD6webUfMF95UJnJW1CKv3Y44nYtUGfP2kttDOfeQmkPZBxMp/SK+HdB70XFhr3EQvE2LaTvdOa/ycdN1v7OToMVlD87Vvxhpo5ouq/eQ==
> 
> **Server3: of1.beelogistics.com,34541**
> 
> - **PAC**
> 
> DBName: PAC_DB
> 
> Token: ScU4q73GkYzESueJCAyFKfDIc3GWUP8lrqSuI9e+J63+YTnM9ZNKZjummRA3qsc2EEOLrMpoVlnP8F/6WNVwnqQFkI96SCzLlsy2o/p+zr8QdN0R1XjvzjBVvPkzSb1G0TGm3HG5rB5LMCUrlAIClfDVjg9wMKyKgGnRL887GHJIikyODwfLhl5IOIg3sYeOt9yDXkN7scZJ4P248SIR+3AnWR5oLSTWTXD1smb96kQCYFBx137cdVNy6LvftD9xv2CUKIpjEYN1Un4p54/EN3rpfL8LAaIU8nfP1GXcVdqIgmonZSoYfNcyKNcuDlMJG/KUJyqs6+WY6do0ls4fgw==
> 
> - ** BEE MALAYSIA**
> 
> DBName: MY_DB
> 
> Token: AiJd/v5zKos3a7C7ZlT/ldVgirccxg6Kg/YI0ZCKNqeUJJYTn1PIH/eT3BSbEjG9zzsMcBsnxgdwn9j/LkwqCnMm4GkxOnOOBASwaI/oqSV3t/OqC/RAT0igpLIYveYIvsiXFo7FtyaQg9VciQz5k6m1O6izfw2ZLw3PIf2qtbIrVzcFCo4FtSMYK5dFZ3HVpTG1+vCB9815APFbf7vMoT69qmJeP+cGb94/lc/W0/mmJFdyRp82Ow7MkjENYohnrKwvYQcBaSsHb/lRNH7TiLylGl7j3EQZMRRctmPMfVimJuCnoeRa/SHg0/xbO5ASQaBZPnU34poAHJhEixhNHw==
> 
> **Server4: ind.openfreightone.com,34541**
> 
> - **BEE INDIA**
> 
> DBName: BEEINDIA
> 
> Token: QQ7wt4h2OopNs5d9GQjnWYR3z6H+FkIZVPNs2y77O1SQGxyzxwOwrn3UYEpNWWAzNuLWPN7SkrbPSyJe6nDitrUOiMDN+WP5wJLmta77366lf1BBkvCYH7RcfRiXqJ7h3q8b2DzsBuqV62GypL2A9a/93eCPJXU82Q9rQugk7w22EGuFVaTjnyBWyI9nwIImvpOn8/VKPDq94JlLTPQNuTyaSevQFN9iPRze7Op6o9Zk/3KZIpmDHcyBhE2GJVdVzkxCUvQj+hxpdp7KPnQ5ebQSYElcz7b9Y7LUFHAqrVXlZdRrpsuBFNvCn2yLJ/V3ldTaWHRRvEjhzgMFW1AlNg==
> 
> **Server5: pnh.beelogistics.com,34541**
> 
> - **BEE CAM**
> 
> DBName: BEECAM_DB
> 
> Token: TLBveOeB6HbJHfA3uSClssVSb5T8CTxt/fKl+Ab1lDj5m0VsK3csC7d3wgnE4w3n606kSfPyLpcvvedSP8hpAqfext7fiwfv3i/hbcMsCFG4xvpxdqd0bpkG2tBDcPO7pGpgxRuiXn+qIlsoPfFG+I+iJpxrfBXMGFH6QJ1aB+As+JQSnkPB2SQVDZuGIIfdZYvc5iz7PURO0x9smkb5MHiZ44FkjKnTAk/fXNyW4rf3qWmE5NVGXd6XwpLJlsvff6ZMCdelvessSlgVZCZ/6Ak8YdeDOl9uIYL2dUZq+3qRic94oaXRXwEGIlHZseRvyhq4R7hMGj49By8D4PX4rA==
> 
> - **BEE RGN**
> 
> DBName: BEERGN_DB
> 
> Token: T9ZBmoHlsxaooXctTDXm+OHYodTUESjcXbXUytFRHqLrR8kv4JcZmuvks1GPfLViS7XxpSUgO8T/V+e743LdfYFyB8d1PS3rvAyLobm7uSPyxN62G0n2Fwy/aPwLMrjdZ6ysHM421403i/YpvTjkNMGFJhZ8kKHxPg93AsdArKeylD+qEMqhOCUhUREZbVAVyKvNU/JCbzGn2sUu7UzPEbDznbdVuTfR9av0/spw8a837d8Yt3vyxq3vAzCQUGJOwxZn0kTmaOQ4WZgnHntuChRSLxzVnbun/HyE8ZnjlGnnOeEv6e41bWiJERKlDHK545sJb8e87jjEvS4+j89WWg==
> 
> **Server5: las.openfreightone.com,34541**
> 
> - **BEE CNC**
> 
> DBName: BEECN_DB
> 
> Token: fITcv++OgXVz7bL2PdnrDgqrfftciHJAD1uJYP/aNvrm5LR//1EIN/G8oNqLJwQ+SJ6ge3dSEsNZ6YoyhKaINWPuBAYwsMNh2dAsp2xhI27D6EbQof9WfNuqosUAVjepKAsosrgsX0dvxPb9OkgXL9MTVcfJBycrsVJAuJFv2aICicYXQ73PMstn95aCxbXxqDQlFqhyxjv0hi79ECSWn7yFCfe2QY1fjOYmF6rUqcRl7O7BZJrQG4uUg77ugxqrFaSAo2mt6FvTLvXZ/DMRhSrPbWqzdg6Oq5MLQoumxnG8+4h8AzmB+7V974mzvLSpHnGubWsiygoOQB2ETKDiLg==
> 
> - **OCL USA**
> 
> DBName: OCL_US_DB
> 
> Token: NTummM/6croUwbThl09BelUrUDfyC6nZFL46H4xcv/DeLiq1s/W1d+NIiG3Lr5TxCIxuoZXsY2cWvn05qDvfImvfybLg056v1myDXY9DbWDcnkHxAsfGT8tQZkbe+x+9IbrvNofPB2uXDIX5zONPx+h+/JfHSzzsDXFOHBddfjgyozZ5tHwSM1hN4/6O26FnKOU8gF4i+lJpc6DGsYulzFc+e1hFOk+ckxXAglXr2iRGQJSYbgv5eRBaIcFttUJZOMVkggirQMqaq3BxrXIWZllev+OGt1/ExMT93RdI53+blzuIYYJW5xUwCM5AmP1iEtxOkra7jRI1A1G85IwMXQ==
> 
> [[API_Connection_Info.docx]]

---

> [!note]+ Check báo giá cho a Minh (ưu tiên sau)
> []()

> [!note]+ [Đức] Bổ sung field Pricing Branch vào List Inquiry Request [DONE]
> ![[image 9.png]]

> [!note]+ Đọc chat, break vấn đề, lên giải pháp, note lại review với trước khi làm. (ưu tiên sau)
> ![[Screenshot_2026-01-20_at_09.09.49.png]]
> 
> - Đặt vấn đề:
>     - **Sales** nhận yêu cầu từ khách: "Check giá 1 lô hàng từ HPH đến **3 destinations**: SHA, BIJ, NGB"
>     - **Hiện tại:** Sales phải tạo **3 inquiry riêng** → mất thời gian
>     - **Nếu gộp 1 inquiry:** Pricing không tính được KPI (1 inquiry nhưng phải làm 3 đầu việc)
> ⇒ Vấn đề:
>     - **Sales: Tốn công tạo nhiều inquiry cho cùng 1 request của khách**
>     - **Pricing: Không đếm đủ số lượng công việc thực tế → KPI sai**
>     - **System**: Không có cơ chế link các inquiry cùng nguồn gốc
>     - **Report: Đếm trùng khi tính theo khách hàng/lead**
> - Giải pháp triển khai:
>     - 

> [!note]+ New task from CEO
> ### Yêu cầu từ CEO (CRM - Bee Group)
> 
> - **Mục tiêu:** Check partners toàn hệ thống để chống xung đột sales list.
> - **Mục 1 (deadline 2026-02-14):** CRM hiển thị data partners toàn bộ công ty; check chéo 2 chiều.
> - **Mục 2:** Triển khai CRM cho toàn bộ công ty thành viên (VN bắt buộc; nước ngoài theo yêu cầu).
> Danh sách chi tiết ở **Bảng tổng hợp**.
> **Deadline mục 2 2026-01-30**
> 
> ### Việc cần làm
> 
> 1. Tạo toàn bộ công ty lên cloud.
> 2. Rà soát, tạo account cho toàn bộ công ty bắt buộc theo bảng ở dưới.
> 3. Gửi danh sách account riêng của từng công ty cho anh Vinh.
> 4. Xác nhận phạm vi dữ liệu partners + cơ chế check toàn hệ thống.
> 5. Sync dữ liệu về DB `crm`/`bee_legacy_db` và kiểm tra.
> 6. Cập nhật logic để filter và đồng bộ theo db mới thay vì call về db bf1 để check partner.
> 
> **Sheet tổng hợp user & phân quyền:** `https://docs.google.com/spreadsheets/d/1CnGtsaeFHdmeeYQnJRG40n18fMZGBWRMwdCcgG5roxQ/edit?gid=1087768421`
> 
> > [!note]+ **Bảng tổng hợp**
> > | Công ty/Sheet | Bắt buộc | Token | DB Server | DB Name | Ghi chú |
> > | --- | --- | --- | --- | --- | --- |
> > | Bee HCM (BEEHCM) | Bắt buộc (VN) | Có (chung) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | BEE_DB | Chung 1 token |
> > | Bee Đà Nẵng (BEEDAD) | Bắt buộc (VN) | Có (chung) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | BEE_DB | Chung 1 token |
> > | Bee Hà Nội (BEEHAN) | Bắt buộc (VN) | Có (chung) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | BEE_DB | Chung 1 token |
> > | Bee Hải Phòng (BEEHPH) | Bắt buộc (VN) | Có (chung) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | BEE_DB | Chung 1 token |
> > | Corp (CORP) | Bắt buộc (VN) | Có (chung) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | BEE_DB | Chung 1 token |
> > | EF India (INDIA) | Bắt buộc | Có (riêng) | [ind.openfreightone.com:34541](http://ind.openfreightone.com:34541/) | BEEINDIA | CRM bắt buộc |
> > | Bee SCS (BEE SCS) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | BEESCS_DB |   |
> > | PAC (PAC) | Bắt buộc | Có (riêng) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | PAC_DB |   |
> > | Bee Distribution (BEE DISTRI) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | BEEDIS_DB |   |
> > | Bee Trans (BEE TRNS) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | TRN_DB |   |
> > | Bee Project (BEE PROJ) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | BEEPROJ_DB |   |
> > | Bond (Bond) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | BOND_DB |   |
> > | Hàng Hải (Hàng Hải) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | HANGHAI_DB |   |
> > | HPS (HPS) | Bắt buộc | Có (riêng) | [hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/) | HPS_DB |   |
> > | PROS (PROS) | Bắt buộc | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | PROS_DB |   |
> > | Thủ Đô (Thủ Đô) | Bắt buộc | Có (riêng) | [hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/) | TD_DB |   |
> > | Tiến Đạt (Tiến Đạt) | Bắt buộc | Có (riêng) | [hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/) | TIENDAT_DB |   |
> > | Indonesia (INDO) | Theo yêu cầu | Có (riêng) | [hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/) | INDO_DB |   |
> > | Cambodia (CAM) | Theo yêu cầu | Có (riêng) | [pnh.beelogistics.com:34541](http://pnh.beelogistics.com:34541/) | BEECAM_DB |   |
> > | Myanmar/Yangon (MYANMAR) | Theo yêu cầu | Có (riêng) | [pnh.beelogistics.com:34541](http://pnh.beelogistics.com:34541/) | BEERGN_DB | Bee RGN |
> > | Malaysia (MY) | Theo yêu cầu | Có (riêng) | [of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/) | MY_DB |   |
> > | Laos (LAOS) | Theo yêu cầu | Có (riêng) | [pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/) | LAOS_DB |   |
> > | Philippines (PH) | Theo yêu cầu | Không |   |   |   |
> > | Japan (JP) | Theo yêu cầu | Không |   |   |   |
> > | Thailand (TH) | Theo yêu cầu | Không |   |   |   |
> > | Taiwan (TW) | Theo yêu cầu | Không |   |   |   |
> > | Singapore (SIN) | Theo yêu cầu | Không |   |   |   |
> > | China (CNC-CN) | Theo yêu cầu | Có (riêng) | [las.openfreightone.com:34541](http://las.openfreightone.com:34541/) | BEECN_DB |   |
> > | OCL USA (OCL USA) | Theo yêu cầu | Có (riêng) | [las.openfreightone.com:34541](http://las.openfreightone.com:34541/) | OCL_US_DB |   |
> > | OCL Korea (OCL KR) | Theo yêu cầu | Không |   |   |   |
> > | OCL Australia (OCL_AU) | Theo yêu cầu | Không |   |   |   |
> > | Germany (DE) | Theo yêu cầu | Không |   |   |   |
> > | TEL (TEL) | Theo yêu cầu | Không |   |   |   |
> 
> **Hiện trạng:**
> 
> - Dữ liệu Partner BFS1 lưu tại **database riêng của từng công ty**
> - Database Cloud chỉ có dữ liệu Partner của **VN và India**
> - Database `crm/bee_legacy_db` chỉ có dữ liệu Partner **VN**
> - Data Partner đang được đồng bộ hàng ngày từ BFS1 → Cloud → `crm/bee_legacy_db`
> 
> **Vấn đề:**
> 
> - Dữ liệu Partner **chưa tập trung**, khó quản lý
> - Logic kiểm tra Partner **truy vấn trực tiếp vào BFS1**, chỉ hoạt động với công ty VN
> - Dữ liệu **hiển thị** (từ Cloud) và dữ liệu **kiểm tra** (từ BFS1) **không đồng nhất**
> - Thiếu cơ chế phân biệt Partner thuộc công ty nào trong `bee_legacy_db`
> 
> **Việc cần làm:**
> 
> - Đồng bộ dữ liệu toàn hệ thống
>     - Sync data Partner từ BFS1 → Cloud cho **tất cả công ty**
>     - Thiết lập sync Cloud → `bee_legacy_db` cho **tất cả công ty**
> - Bổ sung cơ chế phân biệt công ty cho `bee_legacy_db` : thêm cột `partner_source` vào bảng partner để xác định công ty
> - Cập nhật logic Check Partner Exist: query `bee_legacy_db` thay vì bfs1

> [!note]+ Clean data, code [DONE]
> > [!note]+ Bảng thừa → drop 
> > ![[Screenshot_2026-02-03_at_08.47.41.png]]
> 
> > [!note]+ script `datatp_crm_db`:
> > ```powershell
> > DROP TABLE public.forwarder_sales_daily_task;
> > ALTER TABLE public.crm_user_task_access_control RENAME COLUMN notes TO note;
> > 
> > ```

> [!note]+ Bổ sung field continent cho CRMPartner, enhance code sync integrated_partner [DONE]
> migrate lại continent cho CRMPartner, khi tạo partner set continent theo country

> [!note]+ Review lại báo cáo Pricing Dashboard, số liệu giữa view quản lý và cá nhân lệch nhau [DONE]
> > [!note]+ Số liệu bị lệch do pricing_company_branch_code chưa đúng lúc sale chọn target pricing company khi gửi request ⇒ migrate dữ liệu
> 
> 
> > [!note]+ Thêm target pricing company branch vào subject khi gửi mail để pricing reject khi sale gửi nhầm company
> 

> [!note]+ Review lại Partner request, đảm bảo logic async vs sync đều chạy đúng [DONE]


---

---

## Performance Report KA


![[Screenshot_2025-12-08_at_11.02.25.png]]

Chỉnh báo cáo cho team Key Account dựa theo form của Sale Freehand và Sale Agent.

Tạo thêm type nữa cho KeyAccount

![[Screenshot_2025-12-09_at_08.52.41.png]]





### Báo cáo cho Quản lý

![[Screenshot_2026-03-04_at_09.03.33.png]]



Highlight: 












---

Xem thêm: [[datatp-index]]
