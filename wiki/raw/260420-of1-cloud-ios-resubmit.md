# OF1-Cloud — iOS Resubmit Plan (Public Distribution)

**Ngày:** 2026-04-20
**Lý do:** App OF1 Freight (`com.openfreightone.mobile`) đã approved với Distribution Method = Private (lock không đổi được). Cần tạo app record MỚI với Distribution Method = Public.

---

## Quyết định đã chốt

| Item | Giá trị |
|---|---|
| App Store name | **OF1-Cloud** |
| Bundle ID mới | `com.openfreightone.cloud` |
| Bundle ID cũ | `com.openfreightone.mobile` (sẽ delete sau khi mới live) |
| Display name (icon) | `OF1` (giữ nguyên) |
| Version | `1.0.5+19` (sync với Android) |
| Distribution Method | **Public — Discoverable** ⚠️ |
| Pricing | Free (Tier 0) |
| Availability | Vietnam (+ tùy chọn) |
| Metadata/icon/screenshots | Reuse 100% từ app cũ |
| Keycloak redirect URI | Không đổi (`net.datatp.mobile://callback`) |

---

## Phase 1 — Apple Developer Portal

**Login:** <https://developer.apple.com/account>

### Step 1.1 — Tạo App ID mới
- **Link trực tiếp:** <https://developer.apple.com/account/resources/identifiers/list>
- **Help (kèm hình):** <https://developer.apple.com/help/account/manage-identifiers/register-an-app-id/>

Thao tác:
1. Click nút **`+`** bên cạnh "Identifiers"
2. Chọn **App IDs** → Continue
3. Type = **App** → Continue
4. Description: `OF1 Cloud`
5. Bundle ID: **Explicit** = `com.openfreightone.cloud`
6. **Capabilities**: tick các cái app cũ đã dùng (so sánh với App ID `com.openfreightone.mobile` ở cùng list):
   - Push Notifications (nếu có)
   - Sign in with Apple (nếu có)
   - Associated Domains (nếu dùng deep link)
7. Continue → Register

### Step 1.2 — Tạo Distribution Provisioning Profile
- **Link trực tiếp:** <https://developer.apple.com/account/resources/profiles/list>
- **Help (kèm hình):** <https://developer.apple.com/help/account/manage-profiles/create-a-distribution-provisioning-profile/>

Thao tác:
1. Click `+` → **App Store** (Distribution) → Continue
2. App ID: chọn `com.openfreightone.cloud` → Continue
3. Distribution Certificate: chọn cert hiện có → Continue
4. Name: `OF1 Cloud App Store` → Generate → Download

### Step 1.3 — APNs Auth Key (chỉ làm nếu app dùng Push)
- **Link:** <https://developer.apple.com/account/resources/authkeys/list>
- **Help:** <https://developer.apple.com/help/account/manage-keys/create-a-key/>

> Nếu đã có 1 APNs Auth Key dùng chung cho team thì **không cần tạo mới** — Auth Key dùng được cho mọi App ID trong team. Chỉ cần đảm bảo key đó được upload lên backend gửi push.

---

## Phase 2 — App Store Connect

**Login:** <https://appstoreconnect.apple.com>

### Step 2.1 — Tạo app record mới
- **Link My Apps:** <https://appstoreconnect.apple.com/apps>
- **Help (kèm hình):** <https://developer.apple.com/help/app-store-connect/manage-your-app/add-a-new-app>

Thao tác:
1. My Apps → click nút **`+`** ở góc trên trái → **New App**
2. Điền form:
   - **Platforms**: ✅ iOS
   - **Name**: `OF1-Cloud`
   - **Primary Language**: Vietnamese
   - **Bundle ID**: `com.openfreightone.cloud - OF1 Cloud` (chọn từ dropdown — phải xuất hiện sau khi đã tạo App ID ở Phase 1)
   - **SKU**: `of1-cloud-ios-001` (tự đặt, miễn unique trong team)
   - **User Access**: Full Access
3. Create

### Step 2.2 — Pricing and Availability ⚠️ QUAN TRỌNG NHẤT
- **Link** (sau khi tạo app, từ trang app):
  `https://appstoreconnect.apple.com/apps/{APP_ID}/distribution/pricing`
- **Help — Distribution Methods (kèm hình):** <https://developer.apple.com/help/app-store-connect/manage-app-distribution/distribution-methods-overview>
- **Help — Set price:** <https://developer.apple.com/help/app-store-connect/manage-pricing/set-a-price>
- **Help — Set availability:** <https://developer.apple.com/help/app-store-connect/manage-availability/set-app-availability-by-country-or-region>

Trong sidebar trái: **Pricing and Availability**

a) **App Distribution Methods** ⚠️
   - Chọn: **Public — Discoverable by anyone on the App Store (default)**
   - **KHÔNG CHỌN** Private/Custom App for Business
   - Save

b) **Pricing**:
   - Click **Add Pricing**
   - Price: **Free (USD 0 — Tier 0)**
   - Save

c) **Availability**:
   - Click **Manage Availability** (hoặc Edit Countries/Regions)
   - Chọn **Vietnam** (+ countries khác nếu muốn — có thể tick **Make available in all countries/regions**)
   - Save

### Step 2.3 — App Information
- **Link:** `https://appstoreconnect.apple.com/apps/{APP_ID}/distribution/info`

Copy y nguyên từ app cũ:
- Subtitle (30 ký tự)
- Category: Primary + Secondary (vd: Business / Productivity)
- Content Rights: tick nếu có third-party content
- Age Rating: làm questionnaire — nên trùng với app cũ

### Step 2.4 — Version 1.0.5 metadata
- **Link:** `https://appstoreconnect.apple.com/apps/{APP_ID}/distribution/ios/version/inflight`
- **Help:** <https://developer.apple.com/help/app-store-connect/manage-your-app/about-app-information>

Mục **iOS App Version 1.0.5** trong sidebar:
- **Promotional Text** (170 ký tự) — copy từ app cũ
- **Description** — copy nguyên từ app cũ
- **Keywords** (100 ký tự, comma-separated) — copy
- **Support URL** — copy
- **Marketing URL** (optional) — copy
- **Version**: `1.0.5`
- **Copyright**: `© 2026 OF1`
- **Screenshots**: upload lại từ asset cũ
  - **iPhone 6.9" Display** (iPhone 16 Pro Max): bắt buộc — `1320 × 2868` hoặc `2868 × 1320`
  - **iPhone 6.7" Display** (iPhone 14 Pro Max): bắt buộc nếu chưa có 6.9 — `1290 × 2796`
  - **iPad Pro 13" Display**: nếu support iPad
- **App Preview** (video, optional)
- **App Icon**: upload `1024 × 1024 PNG, no alpha, no rounded corners`
- **What's New in This Version**: `First public release`

Help — Screenshot specs (kèm bảng kích thước): <https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications>

### Step 2.5 — App Privacy
- **Link:** `https://appstoreconnect.apple.com/apps/{APP_ID}/distribution/privacy`
- **Help (kèm hình):** <https://developer.apple.com/help/app-store-connect/manage-app-privacy/manage-data-collection>

Copy data collection disclosure từ app cũ. Các loại thường có:
- Contact Info (email, name)
- Identifiers (User ID, Device ID)
- Usage Data
- Diagnostics

→ Đánh dấu **Linked to user** + mục đích sử dụng (App Functionality, Analytics).

### Step 2.6 — App Review Information
- Trong **Version 1.0.5** page, scroll xuống **App Review Information**:
  - **Sign-in required**: ✅
  - **User Name**: tài khoản demo Keycloak (vd: `apple-review@example.com`)
  - **Password**: password tài khoản demo
  - **Notes**:
    ```
    This app is being resubmitted as a NEW app record because the
    previous app (com.openfreightone.mobile) was published with
    Private distribution method, which Apple does not allow to
    be changed after approval. We are now releasing the same
    application under Public distribution.

    Demo credentials above grant access to a sandbox tenant with
    sample logistics data. After login, you can browse CRM and
    TMS modules.
    ```
  - **Contact Information**: email + phone của bạn

### Step 2.7 — Export Compliance (đã có sẵn trong code)
- Trong Version page, mục **Build** (sẽ chọn ở Phase 5).
- App đã có `ITSAppUsesNonExemptEncryption = false` trong `Info.plist` → không cần khai báo lại trên ASC.

---

## Phase 3 — Code/config changes ✅ ĐÃ DONE

Branch hiện tại (`develop`) đã được update:

| File | Thay đổi |
|---|---|
| `apps/mobile/pubspec.yaml` | `version: 1.0.4+18` → `1.0.5+19` |
| `apps/mobile/ios/Runner.xcodeproj/project.pbxproj` | Bundle ID Runner: `com.openfreightone.mobile` → `com.openfreightone.cloud` (3 build configs) |
| `apps/mobile/ios/Runner.xcodeproj/project.pbxproj` | Bundle ID RunnerTests: `…mobile.RunnerTests` → `…cloud.RunnerTests` (3 build configs) |

Chưa commit. Khi sẵn sàng:
```bash
git add apps/mobile/pubspec.yaml apps/mobile/ios/Runner.xcodeproj/project.pbxproj
git commit -m "chore(ios): bump to 1.0.5+19 and switch bundle id to com.openfreightone.cloud for public release"
```

---

## Phase 4 — Build & Upload

### Step 4.1 — Clean & install
```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile
flutter clean
flutter pub get
cd ios
pod install --repo-update
cd ..
```

### Step 4.2 — Cấu hình Signing trong Xcode
- Mở: `apps/mobile/ios/Runner.xcworkspace`
- Chọn target **Runner** → Tab **Signing & Capabilities**
- **Team**: chọn team của bạn
- **Bundle Identifier**: `com.openfreightone.cloud` (đã tự đọc từ pbxproj)
- **Provisioning Profile**: chọn profile vừa tạo ở Step 1.2 (`OF1 Cloud App Store`) — hoặc tick "Automatically manage signing" nếu thích
- Lặp lại cho target **RunnerTests** với bundle id `com.openfreightone.cloud.RunnerTests`

### Step 4.3 — Build IPA
```bash
flutter build ipa --release --export-options-plist=ios/ExportOptions.plist
```

> Nếu chưa có `ExportOptions.plist`, dùng cách dưới (build trong Xcode UI):

### Step 4.4 — Archive & Upload qua Xcode
- **Help (kèm hình):** <https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds>

Thao tác:
1. Trong Xcode, chọn destination = **Any iOS Device (arm64)**
2. Menu **Product → Archive**
3. Khi xong, **Organizer** mở ra → chọn archive vừa tạo
4. Click **Distribute App** → **App Store Connect** → **Upload** → Next
5. Tick các tùy chọn (Strip Swift symbols, Upload symbols) → Next
6. Chọn signing (Automatic hoặc profile vừa tạo) → Next → Upload
7. Đợi upload xong → check email Apple ~15-30 phút sau (có/không có warning)

### Step 4.5 — Verify build trong App Store Connect
- **Link:** `https://appstoreconnect.apple.com/apps/{APP_ID}/testflight/ios`
- Vào **TestFlight** tab → đảm bảo build `1.0.5 (19)` xuất hiện ở status "Ready to Submit" (sau khi Apple xử lý xong)

---

## Phase 5 — Submit for Review

### Step 5.1 — Gắn build vào version
- **Link:** `https://appstoreconnect.apple.com/apps/{APP_ID}/distribution/ios/version/inflight`
- **Help:** <https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-for-review>

Thao tác:
1. Vào page **iOS App 1.0.5** trong sidebar
2. Mục **Build** → click **`+ Add Build`** → chọn `1.0.5 (19)` → Done
3. Kéo xuống **Version Release**:
   - Chọn **Manually release this version** (an toàn hơn — bạn quyết định lúc release sau khi approve)
4. **Verify lần cuối**:
   - ✅ Distribution Method = **Public**
   - ✅ Pricing = Free
   - ✅ Availability có Vietnam
   - ✅ Tất cả screenshots/description đầy đủ
   - ✅ App Review Information có demo credentials
5. Click **Add for Review** → **Submit to App Review**

### Step 5.2 — Theo dõi review
- **Link:** `https://appstoreconnect.apple.com/apps/{APP_ID}/distribution/ios/version/inflight`
- Status: `Waiting for Review` → `In Review` → `Pending Developer Release` (vì chọn Manual)
- Thời gian: thường 24-48h
- Email từ Apple sẽ báo khi có thay đổi status

### Step 5.3 — Release manual
- Khi status = **Pending Developer Release**: click **Release This Version**
- Sau ~2-24h, app sẽ live trên App Store toàn cầu (theo Availability đã set)

---

## Phase 6 — Post-Approval & Migration

### Step 6.1 — Thông báo user nội bộ
Sau khi app live:
- Gửi thông báo qua kênh nội bộ (Slack/Email/Teams):
  > "OF1-Cloud" mới đã có trên App Store: <link App Store sau khi live>
  > Vui lòng:
  > 1. Logout app cũ "OF1 Freight"
  > 2. Cài app mới "OF1-Cloud" từ App Store
  > 3. Login lại bằng tài khoản cũ
  > Hai app có Bundle ID khác nhau nên có thể tồn tại song song trên cùng iPhone.

### Step 6.2 — Sau 1-2 tuần ổn định: Remove from Sale app cũ
- **Link:** `https://appstoreconnect.apple.com/apps/{OLD_APP_ID}/distribution/pricing`
- Vào app cũ `OF1 Freight` → **Pricing and Availability** → **Remove from Sale**
  - User đã cài vẫn dùng được, chỉ ẩn khỏi store, không tải mới được nữa

### Step 6.3 — Sau 2-4 tuần: Delete app cũ
- **Link:** trong app cũ → **App Information** → scroll xuống cuối → **Delete App**
- **Help:** <https://developer.apple.com/help/app-store-connect/manage-your-app/remove-an-app>
- ⚠️ Lưu ý: Apple yêu cầu app phải đã Removed from Sale trước khi Delete

---

## Risks & Open Questions

| ID | Risk | Mitigation |
|---|---|---|
| R1 | Chưa rõ ai có Admin role trên Apple Developer Account | Confirm với Charles trước khi bắt đầu Phase 1 |
| R2 | App có dùng Push Notification không? | Check code: nếu có, đảm bảo APNs key/cert hoạt động cho Bundle ID `com.openfreightone.cloud` |
| R3 | Backend có whitelist Bundle ID không? | Grep backend cho `com.openfreightone.mobile`, nếu có → thêm `com.openfreightone.cloud` vào whitelist |
| R4 | Apple Review có thể hỏi vì sao tạo app gần giống app cũ | Đã chuẩn bị note trong App Review Information ở Step 2.6 |
| R5 | Screenshot có thể outdated nếu UI đã đổi từ lần submit cũ | Verify screenshot trước khi submit, chụp lại nếu cần |

---

## Helpful References

- **App Store Connect Help (full)**: <https://developer.apple.com/help/app-store-connect/>
- **App Review Guidelines**: <https://developer.apple.com/app-store/review/guidelines/>
- **Distribution Methods overview**: <https://developer.apple.com/help/app-store-connect/manage-app-distribution/distribution-methods-overview>
- **Manage builds**: <https://developer.apple.com/help/app-store-connect/manage-builds/about-builds>
- **Screenshot specifications**: <https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications>
- **Flutter iOS deployment docs**: <https://docs.flutter.dev/deployment/ios>
