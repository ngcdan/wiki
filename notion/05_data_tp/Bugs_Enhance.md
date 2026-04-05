# ☄️ Bugs / Enhance

> Notion ID: `2c4f924d5d7b8035bc1bfd5a99aa13af`
> Parent: Tasks Database → Status: Doing (Current Week)
> Synced: 2026-04-05

## Fix TODO
*(screenshot: TODO fix list)*

## Implement Identity CRM User Consumer
Đổi username / tạo mới account thì việc consume message.

## Function Forgot Password

## Delete Role Template
Nút delete role template → xoá role type và xoá app feature đi theo role type đó.

*(screenshot: role template delete UI)*

- Sắp xếp lại form thông tin bên trái: để full name, email, mobile gần login ID, identity type để chung hàng với login ID.

## Cập nhật chức năng App Feature cho Identity

*(screenshot: app feature config)*

- Thêm nút xoá quyền ở đây

## Default Sort theo Name (Role)

*(screenshot: role sort)*

## Sync Role Template
- Trường hợp nếu có thay đổi role template (thêm/xoá app feature theo role template đó):
  - Cập nhật toàn bộ identity có role template đó
  - Đồng bộ với app feature mới hoặc xoá app feature cũ tương ứng

## Sync Identity
- Mục đích:
  - Đồng bộ thông tin identity: mail, mobile, name, username
  - Đồng bộ thông tin phân quyền theo role template
    - Nếu quyền là none thì không cần thêm bên user
