---
title: "Mobile App - Setup"
tags:
  - datatp
  - mobile
  - flutter
---

### Android

```bash
flutter clean
flutter pub get
flutter build apk --release
flutter build appbundle --release
```

### IOS

```bash
flutter clean
flutter pub get
flutter build ios --release   # hoặc archive trong Xcode
```

Mô tả app

[App Store — BFSOne](https://apps.apple.com/us/app/bfsone/id1661064497)

stful → stateful widget

![[Screenshot_2026-03-05_at_10.57.26.png]]

1. **Đăng ký Bundle ID**
    - Vào trang Apple Develop Portal ([https://developer.apple.com/account/resources/identifiers/list](https://developer.apple.com/account/resources/identifiers/list)) tạo **Identifiers**.
![[Screenshot_2026-03-05_at_11.12.37.png]]
    - Tạo app mới với bundle ID vừa tạo.
![[Screenshot_2026-03-05_at_11.14.49.png]]
