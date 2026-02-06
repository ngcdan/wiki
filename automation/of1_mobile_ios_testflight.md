# OF1 Mobile iOS → TestFlight (Fastlane pilot)

## Repo
- Mobile app root: `/Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile`
- iOS dir: `ios/`

## Auth: fastlane session (chosen)
This avoids needing an App Store Connect API key, but sessions can expire.

### Generate session
```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile/ios
bundle install
bundle exec fastlane spaceauth
```

Fastlane will output a `FASTLANE_SESSION` string.

### Store secrets (don’t commit)
```bash
cat > ~/.fastlane_session <<'EOF'
export FASTLANE_USER="nqcdan1908@gmail.com"
export FASTLANE_SESSION="PASTE_THE_LONG_STRING_HERE"
EOF

chmod 600 ~/.fastlane_session
source ~/.fastlane_session
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
- `fastlane pilot upload` using FASTLANE_SESSION

## Troubleshooting
- `flutter not found`: ensure Flutter is installed and in PATH
- `Missing FASTLANE_SESSION`: run `bundle exec fastlane spaceauth` again
- Signing errors: open `ios/Runner.xcworkspace` in Xcode once, set Team/signing, build once.
