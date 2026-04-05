# 🛹 Mobile

> Notion ID: `2eaf924d5d7b80a3a767dc4b076f02da`
> Parent: Data TP → Status: Technical
> Synced: 2026-04-05

## Android

```bash
flutter clean
flutter pub get
flutter build apk --release
```

```bash
flutter build appbundle --release
```

### Kiểm thử trên android

## IOS

```bash
flutter clean
flutter pub get
flutter build ios --release   # hoặc archive trong Xcode
```

## Mô tả app

**OF1 Mobile – Phiên bản đầu tiên**
- Chat, talk và gọi điện trong ứng dụng
- Tìm kiếm giá cước logistics nhanh chóng
- Hỗ trợ các nghiệp vụ forwarder
- Giao diện đơn giản, dễ sử dụng
- Chào mừng bạn đến với OF1 Mobile by Open Freight One.

**OF1 Mobile – First Release**
- In-app chat, talk, and calling
- Fast logistics rate search
- Forwarder-related features and workflows
- Simple and easy-to-use interface
- Welcome to OF1 Mobile by Open Freight One.

Link: https://apps.apple.com/us/app/bfsone/id1661064497

### Widget conversion

stateful → stateless widget
*(screenshot)*

## Bundle ID Setup (iOS)

1. **Đăng ký Bundle ID**
   - Vào trang Apple Developer Portal (https://developer.apple.com/account/resources/identifiers/list) tạo **Identifiers**.
   - *(screenshot)*
   - Tạo app mới với bundle ID vừa tạo.
   - *(screenshot)*
