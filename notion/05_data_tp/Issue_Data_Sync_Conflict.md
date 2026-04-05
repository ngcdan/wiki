# ⚠️ Issue: Xung đột dữ liệu khi đồng bộ BFSOne → Cloud

> Notion ID: `2c3f924d5d7b804d8a67d557f394ae43`
> Parent: Tasks → Status: Done
> Synced: 2026-04-05

## 1. Issue: Xung đột dữ liệu giữa BFSOne và Cloud trong quá trình đồng bộ

Hiện tại hệ thống của anh Quý đang tách riêng database cho từng văn phòng (nước ngoài và Việt Nam). Data Partners cũng được lưu tách biệt tương tự.

Khi đồng bộ dữ liệu khách hàng và thông tin nhân sự lên Cloud, việc gộp dữ liệu từ nhiều database vào một nơi dẫn đến nguy cơ **trùng mã (code)** giữa các bản ghi, gây xung đột và khó xác định bản ghi đúng.

## Impact

- Xảy ra trùng mã Partner/Customer khi merge dữ liệu từ nhiều database
- Gây lỗi khi xử lý đồng bộ và ảnh hưởng chất lượng dữ liệu tổng
- Khó tracking nguồn gốc dữ liệu nếu không có cơ chế mapping rõ ràng

## Solutions

### Quản lý Data Partner tập trung

Em đề xuất chuyển sang mô hình quản lý Partner theo hướng tập trung. Nếu anh thấy mô hình này phù hợp, mình sẽ triển khai như sau:

#### Tách thành 2 bảng chính

- **Partner Request:** Lưu thông tin Partner do các văn phòng gửi lên Cloud với trạng thái: **NEW / APPROVED / REJECTED**
- **Partner** (bảng chính): Lưu Partner đã được duyệt và có code chuẩn

#### Quy trình xử lý

1. Gửi yêu cầu tạo Partner → lưu vào **Partner Request**
2. Khi **APPROVE**, hệ thống sẽ:
   - Sinh **code tập trung** theo quy tắc chung
   - Kiểm tra **trùng code** trên toàn hệ thống
   - Sau khi hợp lệ → tạo bản ghi Partner chính thức

Cách này giúp thống nhất quy tắc sinh code và tránh trùng trên toàn bộ Cloud.

### Giải quyết vấn đề dữ liệu cũ

Để xử lý bản ghi Partner cũ đã tồn tại trong nhiều database:

#### Tạo bảng `PartnerReference` / `PartnerDataSource` gồm thông tin:
- Tên database nguồn
- Partner Code gốc
- Partner ID gốc

#### Chạy quy trình validate
- Quét toàn bộ data Partner cũ
- Xác định record bị trùng code và trùng với database nào
- Gắn **flag** đánh dấu bản ghi trùng hoặc cần xử lý

#### Tương thích tìm kiếm & filter, hiển thị cho người dùng
Khi người dùng tìm kiếm Partner:
- Dựa vào flag để quyết định join sang PartnerReference, nếu không trùng dùng code ở partner (primary)
- Đảm bảo hệ thống vẫn tương thích với cả dữ liệu cũ và dữ liệu mới đã chuẩn hóa

## Implementation

Mình tạo thêm bảng PartnerReference, mục đích là Resolver/Mapping cho các nguồn data partner ở hệ thống BFSOne.

- **Partner:** Thông tin chính của partner
- **Partner Reference:** Lưu thông tin identification của partner đó, liên kết 1-1 với partner. Có nhiều loại identification từ các hệ thống khác nhau và entity này như một resolver/mapping để kiếm đúng partner record
- Review, round các query partner qua partner reference: Ví dụ như có code và xác định được nguồn db là ở VN, thì lookup từ reference trước để tìm đúng id của partner trong hệ thống cloud, không dùng code để lookup thẳng partner
- Cân nhắc một số query của partner nặng, data set nhiều cũng có thể chuyển qua query vào bảng reference thay thế (data ít hơn, đánh index tốt hơn)

### Tasks

- Bỏ unique constraint field partnerCode ở `lgc_forwarder_crm_partner` **[DONE]**
  - lgc_settings_saleman_partner_obligation: remove field partnerCode: viết script xóa field `partner_code`, cập nhật lại value field `code`
  - lgc_forwarder_cs_partner_obligation: thêm field partnerId, migrate dữ liệu từ partner_code sang partnerId, remove field partnerCode
  - partner_document_file_attachment: remove field partnerCode + constraint

- Clean code logic sử dụng partnerCode, nghiên cứu thay thế bằng partnerId **(0.5 day) [DONE]**

- Implement Logic cho PartnerReference + Cập nhật logic sync Partner + Sync lại dữ liệu partner từ các DB source **(0.5 day) [DONE]**

- Thêm field dataSource cho `crm_user_role` để xác định được user sẽ được sử dụng data từ datasource nào, migrate `crm_user_role`, cập nhật lại hàm sync `crm_user_role` **(2 hours) [DONE]**

- Cập nhật các query, logic sử dụng `lgc_forwarder_crm_partner`, link thêm `lgc_forwarder_crm_partner_reference` **(1 day) [DONE]**

### Script

```sql
DELETE FROM lgc_settings_saleman_partner_obligation t
WHERE EXISTS (
    SELECT 1
    FROM lgc_settings_saleman_partner_obligation x
    WHERE x.saleman_account_id = t.saleman_account_id
      AND x.partner_id = t.partner_id
      AND x.created_time > t.created_time
);

UPDATE lgc_settings_saleman_partner_obligation
SET code = CONCAT(partner_id , '-', saleman_company_id , '-', saleman_account_id );

DROP INDEX public.lgc_settings_saleman_partner_obligation_partner_code_idx;

ALTER TABLE lgc_settings_saleman_partner_obligation
DROP COLUMN partner_code;

ALTER TABLE lgc_forwarder_cs_partner_obligation
ADD COLUMN IF NOT EXISTS partner_id int8 NOT NULL DEFAULT 1;

UPDATE lgc_forwarder_cs_partner_obligation ob SET partner_id = (
	SELECT DISTINCT id
	FROM lgc_forwarder_crm_partner partner
	WHERE partner.partner_code = ob.partner_code
);

ALTER TABLE lgc_forwarder_cs_partner_obligation
DROP COLUMN partner_code;

ALTER TABLE partner_document_file_attachment
DROP COLUMN partner_code;

ALTER TABLE public.lgc_forwarder_crm_partner DROP CONSTRAINT lgc_forwarder_crm_partner_account_id;
ALTER TABLE public.lgc_forwarder_crm_partner ALTER COLUMN account_id DROP NOT NULL;

ALTER TABLE lgc_forwarder_crm_user_roles
ADD COLUMN IF NOT EXISTS data_source varchar(50) DEFAULT 'BEE_VN';

UPDATE lgc_forwarder_crm_user_roles
SET data_source = 'BEE_INDIA' WHERE company_branch_code = 'bee-in';

DELETE FROM lgc_forwarder_crm_partner p
WHERE p.partner_code IN ('CS053966', 'CS054074', 'AG003514', 'CS053797', 'CS053759', 'CS053645')
  AND NOT EXISTS (
        SELECT 1
        FROM lgc_settings_saleman_partner_obligation ob
        LEFT JOIN lgc_forwarder_crm_partner partner on partner.id = ob.partner_id
        WHERE ob.partner_id = p.id
          AND partner.partner_code IN ('CS053966', 'CS054074', 'AG003514', 'CS053797', 'CS053759', 'CS053645')
      );

ALTER TABLE public.lgc_forwarder_crm_partner ALTER COLUMN account_id DROP NOT NULL;
```

### Migration Scripts

```bash
server:migrate:run --script crm/UpdatePartnerReference.groovy --company bee
server:migrate:run --script crm/SyncBFSOnePartner.groovy --company bee
server:migrate:run --script crm/SyncBFSOnePartner.groovy --company bee-in
```

## Additional Tasks

1. Check tax partner exists: chỗ code để thêm event on detail vào **[DONE]**
   - Nhớ check quyền trước, check quyền theo user role quyền view
   - *(screenshot)*
   - *(screenshot)*
   - Để thêm check tax code ở 2 màn hình request/approve này **[DONE]**

2. Phần Request/Approve đưa về màn hình User, không để ở màn hình company nữa. Áp dụng cho người được phân quyền từ tạo/approve, view **[DONE]**
   - *(screenshot)*
   - Làm luôn cho toàn bộ màn hình ở PartnerWindow
   - Check theo user role template, không check theo app permission, không chia theo company/user **[DONE]**
   - *(screenshot)*
   - companyId phải lấy từ permission **[DONE]**
   - *(screenshot)*
   - 'AGENT' = c.partner_group **[DONE]**
   - *(screenshot)*
   - Để thêm thông tin tax code vào mail này **[DONE]**

## Details

### Tạo request partner, có partner những không có request
Check theo mã ở dưới. Lấy thông tin account ở created_by của partner.
- CS000407_TEMP, CS000407_TEMP
- Không phải mọi request đều lỗi, nhưng một số account bị

### Trùng Ref code
*(screenshot)*

## Unrelease

### Script: `server:migrate:run --script crm/SyncBFSOnePartner.groovy --company bee`

CRMPartner bổ sung fields + migrate dữ liệu ⇒ sau đó cập nhật lại WCheckPartnerExists **[DONE]**
- salemanAccountId
- salemanFullName
- inputAccountId
- inputFullName

```sql
ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS sale_owner_account_id BIGINT;
ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS sale_owner_full_name VARCHAR(255);
ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS input_account_id BIGINT;
ALTER TABLE public.lgc_forwarder_crm_partner ADD COLUMN IF NOT EXISTS input_full_name VARCHAR(255);

CREATE INDEX IF NOT EXISTS lgc_forwarder_crm_partner_sale_owner_account_id_idx ON public.lgc_forwarder_crm_partner(sale_owner_account_id);
CREATE INDEX IF NOT EXISTS lgc_forwarder_crm_partner_input_account_id_idx ON public.lgc_forwarder_crm_partner(input_account_id);

UPDATE lgc_forwarder_crm_partner p
SET
	sale_owner_account_id = u.account_id,
	sale_owner_full_name = u.full_name
FROM (
	SELECT DISTINCT ON (bfsone_username)
		account_id, full_name, bfsone_username
	FROM lgc_forwarder_crm_user_roles
	WHERE bfsone_username IS NOT NULL
	ORDER BY bfsone_username, id DESC
) u
WHERE p.sale_owner_username IS NOT NULL
	AND p.sale_owner_username != ''
	AND UPPER(p.sale_owner_username) = UPPER(u.bfsone_username);

UPDATE lgc_forwarder_crm_partner p
SET
	input_account_id = u.account_id,
	input_full_name = u.full_name
FROM (
	SELECT DISTINCT ON (bfsone_username)
		account_id, full_name, bfsone_username
	FROM lgc_forwarder_crm_user_roles
	WHERE bfsone_username IS NOT NULL
	ORDER BY bfsone_username, id DESC
) u
WHERE p.input_username IS NOT NULL
	AND p.input_username != ''
	AND UPPER(p.input_username) = UPPER(u.bfsone_username);
```

### Additional Updates

- Sync lại dữ liệu Leads từ db đã dump trước đó, lọc theo tên người tạo (ignore dev) **[DONE]**

- Debug lỗi không tạo request khi tạo partner request

- Show thông tin saleman, người tạo lên màn hình danh sách lead **[DONE]**
  - *(screenshot)*

### Cleanup Tasks

- Remove code gọi BFSOne API liên quan tới Customer Leads **[DONE]**

- WCheckPartnerExists search Partners trong db cloud, không search bfsone nữa ⇒ Cập nhật lại hàm show Detail Exists Partner **[DONE]**

- Ẩn partner refund, chỉ hiển thị ở BBRef và PartnerRequest **[DONE]**

- Check chéo với bảng partners bên bfsone có trường isRefund, xem thông tin refund có đồng bộ với bảng partners bên mình ko **[DONE]**
