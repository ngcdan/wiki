# Keycloak Forgot Password Modal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Keycloak's default "Forgot Password?" link with a modal that calls the OF1 `resetIdentityPassword` API.

**Architecture:** Override `login.ftl` from keycloak.v2 theme — disable the built-in forgot password link, add a custom link + PatternFly modal + inline JS that calls the API via `fetch()`.

**Tech Stack:** FreeMarker templates, PatternFly 5 CSS (bundled with Keycloak), vanilla JavaScript

**Spec:** `/Users/nqcdan/dev/wiki/wiki/raw/260423-keycloak-forgot-password-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `keycloak-ext/keycloak/themes/beecorp-theme/login/login.ftl` | Override login template — disable built-in forgot link, add custom link + modal HTML |
| Create | `keycloak-ext/keycloak/themes/beecorp-theme/login/resources/js/forgot-password.js` | Modal open/close, API call, success/error display |
| Modify | `keycloak-ext/keycloak/themes/beecorp-theme/login/theme.properties` | Add `scripts=js/forgot-password.js` |
| Modify | `keycloak-ext/keycloak/themes/beecorp-theme/login/resources/css/custom.css` | Minor modal styling if needed |

---

### Task 1: Update theme.properties to load JS

**Files:**
- Modify: `keycloak-ext/keycloak/themes/beecorp-theme/login/theme.properties`

- [ ] **Step 1: Add scripts entry**

Update `theme.properties` to:

```properties
parent=keycloak.v2
import=common/keycloak

# CSS riêng để override logo
styles=css/custom.css

# JS cho forgot password modal
scripts=js/forgot-password.js
```

---

### Task 2: Create the forgot-password.js

**Files:**
- Create: `keycloak-ext/keycloak/themes/beecorp-theme/login/resources/js/forgot-password.js`

- [ ] **Step 1: Create the JS file**

```javascript
(function () {
  'use strict';

  var API_URL = 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call';

  var modal = document.getElementById('forgot-password-modal');
  var openBtn = document.getElementById('forgot-password-open');
  var closeBtn = document.getElementById('forgot-password-close');
  var cancelBtn = document.getElementById('forgot-password-cancel');
  var form = document.getElementById('forgot-password-form');
  var usernameInput = document.getElementById('forgot-password-username');
  var submitBtn = document.getElementById('forgot-password-submit');
  var resultArea = document.getElementById('forgot-password-result');
  var errorArea = document.getElementById('forgot-password-error');

  if (!modal || !openBtn) return;

  function openModal() {
    modal.classList.add('pf-m-open');
    modal.style.display = '';
    usernameInput.value = '';
    resultArea.style.display = 'none';
    errorArea.style.display = 'none';
    submitBtn.disabled = false;
    usernameInput.focus();
  }

  function closeModal() {
    modal.classList.remove('pf-m-open');
    modal.style.display = 'none';
  }

  openBtn.addEventListener('click', function (e) {
    e.preventDefault();
    openModal();
  });

  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);

  // Close on backdrop click
  modal.addEventListener('click', function (e) {
    if (e.target === modal) closeModal();
  });

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.classList.contains('pf-m-open')) {
      closeModal();
    }
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var username = usernameInput.value.trim();
    if (!username) {
      errorArea.textContent = 'Vui lòng nhập tên đăng nhập';
      errorArea.style.display = '';
      resultArea.style.display = 'none';
      return;
    }

    submitBtn.disabled = true;
    errorArea.style.display = 'none';
    resultArea.style.display = 'none';

    fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        component: 'IdentityService',
        endpoint: 'resetIdentityPassword',
        userParams: {
          params: {
            username: username,
            newPassword: '',
            sendEmail: true
          }
        }
      })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        if (result.ok && !result.data.error) {
          resultArea.textContent = 'Email reset password đã được gửi cho tài khoản "' + username + '"';
          resultArea.style.display = '';
          errorArea.style.display = 'none';
        } else {
          var msg = (result.data && (result.data.error || result.data.message)) || 'Có lỗi xảy ra, vui lòng thử lại';
          errorArea.textContent = msg;
          errorArea.style.display = '';
          resultArea.style.display = 'none';
        }
      })
      .catch(function () {
        errorArea.textContent = 'Không thể kết nối đến server, vui lòng thử lại';
        errorArea.style.display = '';
        resultArea.style.display = 'none';
      })
      .finally(function () {
        submitBtn.disabled = false;
      });
  });
})();
```

---

### Task 3: Create the login.ftl template override

**Files:**
- Create: `keycloak-ext/keycloak/themes/beecorp-theme/login/login.ftl`

- [ ] **Step 1: Create login.ftl**

This is a copy of the keycloak.v2 `login.ftl` with two changes:
1. `forgotPassword` param changed to `false` on `@field.password` to disable the built-in link
2. A custom "Forgot Password?" link and PatternFly modal added after the form

```freemarker
<#import "template.ftl" as layout>
<#import "field.ftl" as field>
<#import "buttons.ftl" as buttons>
<#import "social-providers.ftl" as identityProviders>
<@layout.registrationLayout displayMessage=!messagesPerField.existsError('username','password') displayInfo=realm.password && realm.registrationAllowed && !registrationDisabled??; section>
<!-- template: login.ftl (beecorp-theme override) -->

    <#if section = "header">
        ${msg("loginAccountTitle")}
    <#elseif section = "form">
        <div id="kc-form">
          <div id="kc-form-wrapper">
            <#if realm.password>
                <form id="kc-form-login" class="${properties.kcFormClass!}" onsubmit="login.disabled = true; return true;" action="${url.loginAction}" method="post" novalidate="novalidate">
                    <#if !usernameHidden??>
                        <#assign label>
                            <#if !realm.loginWithEmailAllowed>${msg("username")}<#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}<#else>${msg("email")}</#if>
                        </#assign>
                        <@field.input name="username" label=label error=kcSanitize(messagesPerField.getFirstError('username','password'))?no_esc autofocus=true autocomplete="username" value=login.username!'' />
                        <#-- forgotPassword=false to disable built-in link, custom modal below -->
                        <@field.password name="password" label=msg("password") error="" forgotPassword=false autofocus=usernameHidden?? autocomplete="current-password">
                            <#if realm.rememberMe && !usernameHidden??>
                                <@field.checkbox name="rememberMe" label=msg("rememberMe") value=login.rememberMe?? />
                            </#if>
                        </@field.password>
                    <#else>
                        <@field.password name="password" label=msg("password") forgotPassword=false autofocus=usernameHidden?? autocomplete="current-password">
                            <#if realm.rememberMe && !usernameHidden??>
                                <@field.checkbox name="rememberMe" label=msg("rememberMe") value=login.rememberMe?? />
                            </#if>
                        </@field.password>
                    </#if>

                    <#-- Custom forgot password link -->
                    <div class="pf-v5-c-form__group" style="margin-top: -0.5rem; margin-bottom: 0.5rem; text-align: right;">
                        <a href="#" id="forgot-password-open" class="pf-v5-c-button pf-m-link pf-m-small">${msg("doForgotPassword")}</a>
                    </div>

                    <input type="hidden" id="id-hidden-input" name="credentialId" <#if auth.selectedCredential?has_content>value="${auth.selectedCredential}"</#if>/>
                    <@buttons.loginButton />
                </form>
            </#if>
            </div>
        </div>

        <#-- Forgot Password Modal (PatternFly 5) -->
        <div id="forgot-password-modal" class="pf-v5-c-modal-box__overlay" style="display: none;">
          <div class="pf-v5-c-modal-box pf-m-sm" role="dialog" aria-modal="true" aria-labelledby="forgot-password-title">
            <div class="pf-v5-c-modal-box__close">
              <button id="forgot-password-close" class="pf-v5-c-button pf-m-plain" type="button" aria-label="Close">
                <span class="pf-v5-c-button__icon">✕</span>
              </button>
            </div>
            <header class="pf-v5-c-modal-box__header">
              <h1 id="forgot-password-title" class="pf-v5-c-modal-box__title">Quên mật khẩu</h1>
            </header>
            <div class="pf-v5-c-modal-box__body">
              <p style="margin-bottom: 1rem;">Nhập tên đăng nhập, hệ thống sẽ gửi mật khẩu mới qua email.</p>
              <form id="forgot-password-form">
                <div class="pf-v5-c-form__group">
                  <label class="pf-v5-c-form__label" for="forgot-password-username">
                    <span class="pf-v5-c-form__label-text">Tên đăng nhập</span>
                  </label>
                  <input id="forgot-password-username" class="pf-v5-c-form-control" type="text" required />
                </div>
                <div id="forgot-password-result" class="pf-v5-c-alert pf-m-success pf-m-inline" style="display: none; margin-top: 1rem;"></div>
                <div id="forgot-password-error" class="pf-v5-c-alert pf-m-danger pf-m-inline" style="display: none; margin-top: 1rem;"></div>
              </form>
            </div>
            <footer class="pf-v5-c-modal-box__footer">
              <button id="forgot-password-submit" class="pf-v5-c-button pf-m-primary" type="button">Gửi</button>
              <button id="forgot-password-cancel" class="pf-v5-c-button pf-m-link" type="button">Hủy</button>
            </footer>
          </div>
        </div>

    <#elseif section = "socialProviders" >
        <#if realm.password && social.providers?? && social.providers?has_content>
            <@identityProviders.show social=social/>
        </#if>
    <#elseif section = "info" >
        <#if realm.password && realm.registrationAllowed && !registrationDisabled??>
            <div id="kc-registration-container">
                <div id="kc-registration">
                    <span>${msg("noAccount")} <a href="${url.registrationUrl}">${msg("doRegister")}</a></span>
                </div>
            </div>
        </#if>
    </#if>

</@layout.registrationLayout>
```

---

### Task 4: Add modal overlay CSS

**Files:**
- Modify: `keycloak-ext/keycloak/themes/beecorp-theme/login/resources/css/custom.css`

- [ ] **Step 1: Add modal overlay styles**

Append to existing `custom.css`:

```css
/* Forgot password modal overlay */
#forgot-password-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

#forgot-password-modal .pf-v5-c-modal-box {
  max-width: 28rem;
  width: 90%;
}
```

---

### Task 5: Manual testing

- [ ] **Step 1: Run Keycloak in dev mode** (`start-dev`)
- [ ] **Step 2: Ensure `dev-tool.sh` is running** (or manually copy theme files to Keycloak themes dir)
- [ ] **Step 3: Navigate to the login page and verify:**
  - "Forgot Password?" link is visible
  - Clicking it opens the modal
  - Submitting with empty username shows validation error
  - Submitting with a valid username calls the API and shows success message
  - Submitting with an invalid username shows the API error
  - Close button, Cancel button, Escape key, and backdrop click all close the modal
- [ ] **Step 4: Commit**

```bash
git add keycloak-ext/keycloak/themes/beecorp-theme/login/
git commit -m "feat: custom forgot password modal calling OF1 resetIdentityPassword API"
```
