# OF1 Mobile iOS → TestFlight (Fastlane pilot)

## Repo
- Mobile app root: `/Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile`
- iOS dir: `ios/`

## One-time: Create App Store Connect API Key
1. App Store Connect → Users and Access → **Keys**
2. Create a key (role: App Manager/Developer as needed)
3. Download the `.p8` file (only downloadable once)

You will get:
- **Key ID** (e.g. `ABC123DEFG`)
- **Issuer ID** (UUID)
- `.p8` file: `AuthKey_<KEYID>.p8`

## Store secrets (don’t commit)
Recommended location:

```bash
mkdir -p ~/secrets/appstore
mv ~/Downloads/AuthKey_*.p8 ~/secrets/appstore/
chmod 600 ~/secrets/appstore/AuthKey_*.p8
```

## Configure env vars
### Option A (recommended): JSON file
Create `~/secrets/appstore/asc_api_key.json`:

```json
{
  "key_id": "YOUR_KEY_ID",
  "issuer_id": "YOUR_ISSUER_ID",
  "key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----",
  "in_house": false
}
```

Export:

```bash
export ASC_API_KEY_JSON="$HOME/secrets/appstore/asc_api_key.json"
```

### Option B: separate vars (p8 file)

```bash
export ASC_API_KEY_ID="YOUR_KEY_ID"
export ASC_API_ISSUER_ID="YOUR_ISSUER_ID"
export ASC_API_KEY_PATH="$HOME/secrets/appstore/AuthKey_YOUR_KEY_ID.p8"
```

## Run (anywhere)
Shortcut:

```bash
of1m-tf
```

Direct:

```bash
/Users/nqcdan/dev/wiki/automation/of1_mobile_ios_testflight.sh
```

## What it does
- `flutter clean` + `flutter pub get`
- `pod install`
- `flutter build ipa --release`
- `fastlane pilot upload` using ASC API key

## Troubleshooting
- `flutter not found`: ensure Flutter is installed and in PATH
- Signing errors: open `ios/Runner.xcworkspace` in Xcode once, set Team/signing, build once.
- 2FA/session issues: API key should avoid this; re-check env vars + key permissions.
