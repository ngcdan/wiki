# [platform-federation] Update: audit source cho User App Feature permissions

> Date: 2026-04-10
> PR: https://git.datatp.cloud/of1-platform/of1-core/compare/develop...dan
> Design: [260410-identity-erd.md](./260410-identity-erd.md)
> Migration SQL: [260410-user-app-feature-source-role-type-sql.md](./260410-user-app-feature-source-role-type-sql.md)

---

## Vấn đề đang giải quyết

Trước đây, mỗi row trong bảng permission của user được tạo bằng 2 con đường khác nhau:
1. **Sync từ template** — khi user được gán role, hệ thống tự động tạo permissions từ template của role type đó
2. **Admin gán thủ công** — admin mở UI sửa permission trực tiếp

Nhưng hai loại này **trông giống hệt nhau** trong DB. Hậu quả:
- Không audit được "permission này từ đâu ra"
- Sync logic có thể **lỡ tay xoá** permission mà admin đã cố tình override
- Không biết khi xoá role type thì những permission nào cần cleanup

---

## Concept mới

Mỗi permission row giờ có thêm 1 field "**source role type**" — trỏ tới role type đã sinh ra nó:

- **Rỗng (NULL)** → **CUSTOM** — admin gán tay, được bảo vệ, sync không bao giờ động tới
- **Có giá trị** → **Role-sourced** — materialize từ template của role type đó, sync sẽ refresh/xoá theo template

---

## Các case cần nắm

**Case 1: User được gán role mới**
Hệ thống tự động materialize permissions từ template của role type → tag source là role type đó.

**Case 2: Admin override permission thủ công**
Permission được lưu với source rỗng → được đánh dấu là CUSTOM → từ giờ không bị sync xoá.

**Case 3: Role type bị xoá**
Tất cả permission có source trỏ tới role type đó được cascade xoá tự động. CUSTOM permissions vẫn giữ nguyên.

**Case 4: Template của role thay đổi**
Khi gọi sync, chỉ các role-sourced permissions được refresh theo template mới. CUSTOM permissions không đổi.

**Case 5: User có nhiều role cùng grant 1 app feature**
Ví dụ user có cả ADMIN và AUDITOR, cả 2 template đều có permission cho app X. Do unique constraint chỉ cho phép 1 row → template được iterate cuối sẽ thắng (deterministic). Chưa merge capability — sẽ extend sau nếu có requirement.

**Case 6: Audit — xem permission của user đến từ đâu**
Query bảng permission + join với role type → trả về từng permission kèm label CUSTOM hoặc tên role type. Có thể dùng cho màn hình audit trong admin panel.

---

## Impact lên code team đang viết

- **Hot-path đọc permission** (AppLogic.getAppPermission) — không đổi, vẫn nhanh như cũ
- **Các method save/update permission hiện có** — không cần sửa, giữ nguyên behavior
- **Các nơi gọi syncUserPermissions** — signature không đổi, nhưng behavior mới: CUSTOM rows được bảo vệ. Trước đây nếu gọi sync có thể vô tình xoá row admin đã override; giờ thì không.
- **Admin UI / API gán permission thủ công** — nên để source rỗng (NULL) để flag là CUSTOM. Mặc định Java field = null nên các path hiện tại đã đúng.
- **Khi xoá role type** — không cần xoá permission thủ công nữa, IdentityLogic.deleteRoleTypes đã tự cascade.

---

## Các bước triển khai

1. Review PR
2. Merge → deploy code mới (forward-compatible: cột NULL được treat như CUSTOM nên không break existing data)
3. Chạy migration SQL (xem file migration trong wiki — có sẵn script cho cả PostgreSQL và MSSQL)
4. *(Optional)* chạy backfill script 1-lần để tự động detect các permission cũ thực ra là role-sourced (dựa trên exact-match với template). Không bắt buộc — mặc định tất cả rows cũ sẽ thành CUSTOM.

---

## Câu hỏi team nên hỏi khi review

- Multi-role conflict strategy (last-wins) đã ổn cho use case hiện tại chưa? Có cần merge capability không?
- Có cần thêm endpoint RPC getPermissionsWithSource để UI hiển thị source không?
- Có cần DB-level FK source_role_type_id → identity_role_type.id không, hay giữ application-level cascade như hiện tại?
