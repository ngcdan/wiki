# Keycloak Forgot Password — Custom Reset via API

**Date:** 2026-04-23
**Project:** of1-apps-ext / keycloak-ext
**Theme:** beecorp-theme

## Overview

Override the default "Forgot Password?" link on the Keycloak login page to show an inline modal that calls the OF1 `resetIdentityPassword` API instead of Keycloak's built-in password reset flow.

## Approach

Override `login.ftl` FreeMarker template from parent theme `keycloak.v2`. Replace the default "Forgot Password?" link with a button that opens a PatternFly modal containing a username input form. JavaScript handles the API call and displays results.

## API

```
POST https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call
Content-Type: application/json

{
  "component": "IdentityService",
  "endpoint": "resetIdentityPassword",
  "userParams": {
    "params": {
      "username": "<user-input>",
      "newPassword": "",
      "sendEmail": true
    }
  }
}
```

- `newPassword` is sent as empty string `""` — backend generates a random password and emails it.
- Frontend sends `username`, `newPassword: ""`, and `sendEmail: true`.

## User Flow

1. User clicks "Forgot Password?" on the login page
2. PatternFly modal appears with a username input field
3. User enters username, clicks "Send" (or "Gửi")
4. Frontend calls the API via `fetch()`
5. **Success:** Display message "Email reset password đã được gửi"
6. **Failure:** Display the specific error message returned by the API
7. User can close the modal and return to the login form

## Files to Create/Modify

### 1. `beecorp-theme/login/login.ftl`

- Copy from parent theme `keycloak.v2` login template
- Replace the `<#if realm.resetPasswordAllowed>` link with a button that triggers the modal
- Add modal HTML at the end of the template (PatternFly modal markup)

### 2. `beecorp-theme/login/resources/js/forgot-password.js`

- Handle modal open/close
- Validate username is not empty
- Call the API via `fetch()`
- Display success or error message in the modal
- Loading state while API call is in progress

### 3. `beecorp-theme/login/theme.properties`

- Add `scripts=js/forgot-password.js` to load the JS file

### 4. `beecorp-theme/login/resources/css/custom.css`

- Minor additions if needed for modal alignment (PatternFly should handle most styling)

## UI Details

- Modal uses PatternFly 5 classes (already available in keycloak.v2 theme)
- Single input field: username (text input)
- Two buttons: "Gửi" (primary) and "Hủy" (secondary/link)
- Result area below the form for success/error messages
- Loading spinner or disabled button during API call

## Error Handling

- Empty username: client-side validation, show inline error
- API error: display the specific error message from the API response
- Network error: display a generic connection error message

## Upgrade Considerations

- `login.ftl` is a copy from the parent theme — when upgrading Keycloak, diff the new parent template against the customized version to incorporate upstream changes.
