---
title: "OF1 Identity Service"
tags: [of1, identity, api, service]
---

# Identity API - Platform Federation Module

> Module: `platform-federation`
> Base URL: `https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call`
> All APIs use `AccessPath.Internal` (internal service-to-service calls)
> `ClientContext` is auto-injected by the framework — do not include in `userParams`

---

## Table of Contents

- [IdentityService](#identityservice)
  - [1. Get Identity By Login Id](#1-get-identity-by-login-id)
  - [2. Create Employee Identity](#2-create-employee-identity)
  - [3. Get Role By Identity Id](#3-get-role-by-identity-id)
  - [4. Get Role Type By Id](#4-get-role-type-by-id)
  - [5. Reset Identity Password](#5-reset-identity-password)
- [IdentityEventService](#identityeventservice)
  - [6. Sync Roles](#6-sync-roles)
- [IdentityEventAckProducer](#identityeventackproducer)
  - [7. Send Identity Event ACK to Kafka](#7-send-identity-event-ack-to-kafka)
- [AppService](#appservice)
  - [8. Get App Feature](#8-get-app-feature)
  - [9. Get App Permission](#9-get-app-permission)
  - [10. Save App Permission](#10-save-app-permission)
- [Enums Reference](#enums-reference)

---

## IdentityService

Component: `IdentityService`
Source: `datatp.platform.identity.IdentityService`

### 1. Get Identity By Login Id

| Field | Value |
|-------|-------|
| **Endpoint** | `getIdentityByLoginId` |
| **Label** | Get Identity By Login Id |
| **Access** | Internal, Private |
| **Tags** | platform, identity |
| **Return Type** | `Identity` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `loginId` | String | Yes | Login ID of the identity (lowercase) |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityService",
  "endpoint": "getIdentityByLoginId",
  "userParams": {
    "loginId": "it.test"
  }
}'
```

**Response (Identity object):**

```json
{
  "id": 1,
  "loginId": "it.test",
  "accountId": 100,
  "identityType": "USER",
  "email": "it.test@beelogistics.com",
  "mobile": "1234567",
  "fullName": "IT TEST",
  "enabled": true,
  "changeRequest": {
    "requestAt": "2024-01-01T00:00:00",
    "note": "",
    "ackAt": "2024-01-01T00:00:00",
    "ackStatus": "PROCESSED",
    "ackNote": ""
  }
}
```

---

### 2. Create Employee Identity

| Field | Value |
|-------|-------|
| **Endpoint** | `createEmployeeIdentity` |
| **Label** | Create Employee Identity |
| **Access** | Private, Internal |
| **Tags** | platform, identity |
| **Return Type** | `EmployeeCreator` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `employeeCreator.username` | String | Yes | Username for login |
| `employeeCreator.fullName` | String | Yes | Full name |
| `employeeCreator.email` | String | Yes | Email address |
| `employeeCreator.phone` | String | No | Contact phone |
| `employeeCreator.position` | String | No | Job position/title (e.g. "LOG", "ACC") |
| `employeeCreator.departmentLabel` | String | No | Department name (e.g. "LOGISTICS/BEEHP") |
| `employeeCreator.companyId` | Long | No | Company ID |
| `employeeCreator.companyCode` | String | No | Company code (e.g. "beehph") |
| `employeeCreator.workPlace` | String | No | Work place (e.g. "BEE - Hai Phong") |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityService",
  "endpoint": "createEmployeeIdentity",
  "userParams": {
    "employeeCreator": {
      "username": "it.test",
      "fullName": "IT TEST",
      "email": "it.test@beelogistics.com",
      "phone": "1234567",
      "departmentLabel": "LOGISTICS/BEEHP",
      "position": "LOG",
      "workPlace": "BEE - Hai Phong",
      "companyCode": "beehph"
    }
  }
}'
```

**Response (EmployeeCreator object):**

```json
{
  "username": "it.test",
  "fullName": "IT TEST",
  "email": "it.test@beelogistics.com",
  "phone": "1234567",
  "departmentLabel": "LOGISTICS/BEEHP",
  "position": "LOG",
  "workPlace": "BEE - Hai Phong",
  "companyCode": "beehph",
  "companyId": 1
}
```

---

### 3. Get Role By Identity Id

| Field | Value |
|-------|-------|
| **Endpoint** | `getRoleByIdentityId` |
| **Label** | Get Role By Identity Id |
| **Access** | Private, Internal |
| **Tags** | platform, identity |
| **Return Type** | `List<IdentityRole>` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identityId` | Long | Yes | Identity ID |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityService",
  "endpoint": "getRoleByIdentityId",
  "userParams": {
    "identityId": 123
  }
}'
```

**Response (List of IdentityRole):**

```json
[
  {
    "id": 1,
    "identityId": 123,
    "roleTypeId": 10,
    "roleTypeName": "ADMIN",
    "companyId": 1,
    "changeRequest": {
      "requestAt": "2024-01-01T00:00:00",
      "ackStatus": "PROCESSED"
    }
  }
]
```

---

### 4. Get Role Type By Id

| Field | Value |
|-------|-------|
| **Endpoint** | `getRoleTypeById` |
| **Label** | Get Role Type By Id |
| **Access** | Internal, Private |
| **Tags** | platform, identity |
| **Return Type** | `IdentityRoleType` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Long | Yes | Role type ID |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityService",
  "endpoint": "getRoleTypeById",
  "userParams": {
    "id": 1
  }
}'
```

**Response (IdentityRoleType object):**

```json
{
  "id": 1,
  "role": "ADMIN",
  "label": "Administrator",
  "description": "System administrator role"
}
```

---

### 5. Reset Identity Password

| Field | Value |
|-------|-------|
| **Endpoint** | `resetIdentityPassword` |
| **Label** | Reset Identity Password |
| **Access** | Private, Internal |
| **Tags** | platform, identity |
| **Return Type** | `void` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | String | Yes | Login username |
| `newPassword` | String | Yes | New password to set |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityService",
  "endpoint": "resetIdentityPassword",
  "userParams": {
    "username": "it.test",
    "newPassword": "NewPassword@123"
  }
}'
```

> Note: This method integrates with Keycloak to reset the user's password.

---

## IdentityEventService

Component: `IdentityEventService`
Source: `datatp.platform.identity.queue.IdentityEventService`

### 6. Sync Roles

| Field | Value |
|-------|-------|
| **Endpoint** | `syncRoles` |
| **Label** | Sync Roles |
| **Access** | Private, Internal |
| **Tags** | platform, identity |
| **Return Type** | `void` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identityId` | Long | Yes | Identity ID to sync roles for |
| `rolesIds` | List\<Long\> | Yes | List of role IDs to sync |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityEventService",
  "endpoint": "syncRoles",
  "userParams": {
    "identityId": 123,
    "rolesIds": [1, 2, 3]
  }
}'
```

> Note: Updates ChangeRequest ackStatus to `PROCESSED` for the specified roles.

---

## IdentityEventAckProducer

Component: `IdentityEventAckProducer`
Source: `datatp.platform.identity.queue.IdentityEventAckProducer`

### 7. Send Identity Event ACK to Kafka

| Field | Value |
|-------|-------|
| **Endpoint** | `sendApi` |
| **Label** | Send Message Kafka |
| **Access** | Internal |
| **Tags** | platform, identity |
| **Return Type** | `void` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `event.type` | IdentityEventType | Yes | Event type: `Create`, `Update`, `Delete`, `Sync` |
| `event.identity` | Identity | No | Identity data |
| `event.roles` | List\<IdentityRole\> | No | List of roles |
| `event.attributes` | Map | No | Additional attributes |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "IdentityEventAckProducer",
  "endpoint": "sendApi",
  "userParams": {
    "event": {
      "type": "Sync",
      "identity": {
        "loginId": "it.test",
        "fullName": "IT TEST",
        "email": "it.test@beelogistics.com",
        "identityType": "USER",
        "enabled": true
      },
      "roles": [],
      "attributes": {}
    }
  }
}'
```

> Note: Publishes an acknowledgment event to the Kafka topic configured in `datatp.msa.identity.queue.topic.event-acks`.

---

## AppService

Component: `AppService`
Source: `datatp.platform.resource.logic.AppService`

### 8. Get App Feature

| Field | Value |
|-------|-------|
| **Endpoint** | `getApp` |
| **Label** | Get App Feature |
| **Access** | Internal, Private |
| **Tags** | module, app |
| **Return Type** | `AppFeature` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `module` | String | Yes | Module name |
| `name` | String | Yes | App feature name |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "AppService",
  "endpoint": "getApp",
  "userParams": {
    "module": "platform",
    "name": "identity"
  }
}'
```

**Response (AppFeature object):**

```json
{
  "id": 1,
  "module": "platform",
  "name": "identity"
}
```

---

### 9. Get App Permission

| Field | Value |
|-------|-------|
| **Endpoint** | `getAppPermission` |
| **Label** | Get App Permission |
| **Access** | Internal, Private |
| **Tags** | module, app |
| **Return Type** | `UserAppFeature` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `appId` | Long | Yes | App feature ID |
| `companyId` | Long | Yes | Company ID |
| `accountId` | Long | Yes | Account ID |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "AppService",
  "endpoint": "getAppPermission",
  "userParams": {
    "appId": 1,
    "companyId": 1,
    "accountId": 100
  }
}'
```

**Response (UserAppFeature object):**

```json
{
  "id": 1,
  "companyId": 1,
  "appId": 1,
  "accountId": 100,
  "accessType": "Employee",
  "capability": "ReadWrite",
  "dataScope": "Owner"
}
```

---

### 10. Save App Permission

| Field | Value |
|-------|-------|
| **Endpoint** | `saveAppPermission` |
| **Label** | Save App Permission |
| **Access** | Internal, Private |
| **Tags** | module, app |
| **Return Type** | `UserAppFeature` |

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `permission.companyId` | Long | Yes | Company ID |
| `permission.appId` | Long | Yes | App feature ID |
| `permission.accountId` | Long | Yes | Account ID |
| `permission.accessType` | AccessType | Yes | `Employee` |
| `permission.capability` | Capability | Yes | `ReadWrite`, `Read`, `Write` |
| `permission.dataScope` | DataScope | No | `Owner`, `Group`, `Company`, `All` (default: `Owner`) |

**Request:**

```bash
curl --location 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
--header 'Content-Type: application/json' \
--data-raw '{
  "version": "1.0.0",
  "component": "AppService",
  "endpoint": "saveAppPermission",
  "userParams": {
    "permission": {
      "companyId": 1,
      "appId": 1,
      "accountId": 100,
      "accessType": "Employee",
      "capability": "ReadWrite",
      "dataScope": "Owner"
    }
  }
}'
```

**Response (UserAppFeature object):**

```json
{
  "id": 1,
  "companyId": 1,
  "appId": 1,
  "accountId": 100,
  "accessType": "Employee",
  "capability": "ReadWrite",
  "dataScope": "Owner"
}
```

---

## Enums Reference

### IdentityEventType
| Value | Description |
|-------|-------------|
| `Create` | New identity created |
| `Update` | Identity updated |
| `Delete` | Identity deleted |
| `Sync` | Identity sync event |

### AccessType
| Value | Description |
|-------|-------------|
| `Employee` | Employee access |

### Capability
| Value | Description |
|-------|-------------|
| `Read` | Read only |
| `Write` | Write only |
| `ReadWrite` | Read and write |

### DataScope
| Value | Description |
|-------|-------------|
| `Owner` | Own data only |
| `Group` | Group-level data |
| `Company` | Company-level data |
| `All` | All data |

### ChangeRequest.ackStatus
| Value | Description |
|-------|-------------|
| `WAITING` | Pending acknowledgment |
| `PROCESSED` | Already processed |

## Liên quan

- [[datatp-index|DataTP - Tổng quan]]
- [[bf1-index|BF1 — Index]]
- [[namespace-ip-cloud|Namespace & IP Cloud]]
