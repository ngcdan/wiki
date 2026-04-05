---
title: "Keycloak Development"
source: "Notion"
synced_date: "2026-04-05"
---

## Keycloak Configuration

### keycloak.tsx Configuration

Client-side Keycloak configuration for authentication initialization.

### Server Configuration

- **Auth URL**: auth.beelogistics.cloud
- **Realm**: BeeCorp
- **Client**: spring-client

## Dual Authentication System

### Legacy + Keycloak

System supports both legacy authentication and modern Keycloak SSO:
- Maintain backward compatibility with existing user sessions
- Gradual migration to Keycloak authentication
- Dual validation during transition period

## Authentication Flow

### PKCE (Proof Key for Code Exchange)

Modern OAuth 2.0 authentication flow implementation:

1. Generate code_challenge from code_verifier
2. Redirect to Keycloak with code_challenge
3. User logs in and receives authorization code
4. Exchange authorization code + code_verifier for tokens

### Authentication URL Example

```
https://auth.beelogistics.cloud/auth/realms/BeeCorp/protocol/openid-connect/auth?
  client_id=spring-client
  &response_type=code
  &redirect_uri=http://localhost:3000/callback
  &code_challenge=<generated_hash>
  &code_challenge_method=S256
  &scope=openid profile email
```

## Token Management

### Token Storage

Tokens stored in:
- localStorage: for persistence across browser sessions
- sessionStorage: for temporary session tokens

### Token Headers

Tokens sent in Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Refresh Logic

Refresh flow when access token expires:

1. Check if access token near expiration
2. Call refresh token endpoint
3. Receive new access token
4. Update stored tokens
5. Continue with original request

## Session Management

### DATATP_SESSION Singleton

Single session manager instance across application:

```typescript
class DATATP_SESSION {
  private static instance: DATATP_SESSION;
  
  static getInstance(): DATATP_SESSION {
    if (!this.instance) {
      this.instance = new DATATP_SESSION();
    }
    return this.instance;
  }
  
  getCurrentUser() { }
  isAuthenticated() { }
  logout() { }
}
```

### Dual Storage

- Primary: Keycloak token storage
- Fallback: Legacy session storage
- Synchronization: Keep both in sync during migration

## Integration Points

### Frontend Phoenix App with ServiceWorker

ServiceWorker handles:
- Token refresh in background
- Multi-tab authentication synchronization
- Offline request caching
- Push notifications

### ServiceWorker.broadcastMessage

Broadcast authentication state changes across browser tabs:

```typescript
// In ServiceWorker
self.clients.matchAll().then(clients => {
  clients.forEach(client => {
    client.postMessage({
      type: 'AUTH_STATE_CHANGED',
      payload: { user, token }
    });
  });
});

// In app tabs
navigator.serviceWorker.controller.onmessage = (event) => {
  if (event.data.type === 'AUTH_STATE_CHANGED') {
    updateAuthState(event.data.payload);
  }
};
```

### Backend REST API Endpoints

Authentication endpoints for backend services:

```
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET /api/auth/validate
POST /api/auth/change-password
```

## Login and Logout Flows

### Login Flow

1. User clicks login button
2. Generate PKCE code_challenge
3. Redirect to Keycloak login page
4. User enters credentials
5. Keycloak validates and returns authorization code
6. Exchange code for access and refresh tokens
7. Store tokens
8. Redirect to application

### Logout Flow

1. Clear stored tokens
2. Clear session storage
3. Call Keycloak logout endpoint
4. Redirect to login page
5. Notify other browser tabs via ServiceWorker

## Server Run Command

Start Keycloak server:

```bash
./bin/kc.sh start
```

## Keycloak API

### Get User by Username

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users?username=john.doe
```

Response:

```json
[
  {
    "id": "user-id",
    "username": "john.doe",
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "enabled": true
  }
]
```

### Create User

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane.doe",
    "email": "jane.doe@example.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "enabled": true,
    "credentials": [{
      "type": "password",
      "value": "temporary-password",
      "temporary": true
    }]
  }' \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users
```

### Find All Users

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users
```

### Change Password

```bash
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "password",
    "value": "new-password",
    "temporary": false
  }' \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}/reset-password
```

### Update User

```bash
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "firstName": "UpdatedFirstName",
    "lastName": "UpdatedLastName"
  }' \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}
```

### Disable/Enable User

```bash
# Disable user
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}' \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}

# Enable user
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}
```

### Find Groups

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/groups
```

Response:

```json
[
  {
    "id": "group-id",
    "name": "developers",
    "path": "/developers"
  }
]
```

### Join User to Group

```bash
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}/groups/{groupId}
```

### Leave User from Group

```bash
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}/groups/{groupId}
```

### Get User Groups

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}/groups
```

Response:

```json
[
  {
    "id": "group-id",
    "name": "developers",
    "path": "/developers"
  }
]
```

### Delete User

```bash
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  https://auth.beelogistics.cloud/auth/admin/realms/BeeCorp/users/{userId}
```
