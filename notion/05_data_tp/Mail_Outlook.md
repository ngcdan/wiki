# ⛅ Mail Outlook

> Notion ID: `2a1f924d5d7b80a0befce17fd4167e7e`
> Parent: Data TP Database → Status: Technical
> Synced: 2026-04-05

Hướng dẫn cấu hình Exchange Online cho CRM integration (Teams meeting access).

## Cài đặt PowerShell trên macOS

```bash
brew install --cask powershell
pwsh
```

## Cài module Exchange Online

```powershell
Install-Module -Name ExchangeOnlineManagement -Force
Connect-ExchangeOnline -UserPrincipalName admin@beelogistics.com
```

## Tạo Application Access Policy

```powershell
New-ApplicationAccessPolicy `
    -AppId "YOUR-CLIENT-ID" `
    -PolicyScopeGroupId "GraphAPI-TeamsAccess@beelogistics.com" `
    -AccessRight RestrictAccess `
    -Description "Teams meeting access for CRM"
```

## Test Policy

```powershell
Test-ApplicationAccessPolicy `
    -Identity "dcenter@beelogistics.com" `
    -AppId "YOUR-CLIENT-ID"
```

## Production Config

```powershell
Connect-ExchangeOnline
New-ApplicationAccessPolicy -AppId "4fd9400d-b576-4884-880b-670a3b0c7f0a" -PolicyScopeGroupId "dcenter@beelogistics.com" -AccessRight RestrictAccess -Description "Teams access"
```
