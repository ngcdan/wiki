---
title: "Server / Config / Release"
source: "Notion"
synced_date: "2026-04-05"
---

## Download DB

- beelogistics.cloud

## SSH Key Info

Details of SSH key configuration for server access.

## Win VMware Config

- Host: win-server-vm.of1-dev-crm.svc.cluster.local

## Server Cloud k8s Commands

Using k-ctl.sh for admin operations:
- admin
- undeploy
- sync-pv
- deploy

## Grafana Monitoring

Grafana monitoring configuration and access information.

## Pod Exec Commands

Using kns-ctl for pod access and execution.

## Copy to/from Commands

Commands for copying files to and from pods/containers.

## DataTP Docs SSH Info

SSH configuration for DataTP documentation servers.

## Debezium + Kafka URLs

Debezium and Kafka service endpoints and configuration.

## Keycloak Start Command

Start command for Keycloak authentication service.

## Mobile Apple ID

Apple ID configuration for mobile development.

## Cách Clone Database Trên Cloud

### Step 1: Backup Database

Using psql to create database backup from source database.

### Step 2: Restore Database

Restore from backup with appropriate permissions and schema configuration.

### Step 3: HikariDataSource Configuration

YAML configuration for HikariDataSource connection pool:

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

## Tailscale Setup

### Mac Mini Setup

Tailscale installation and configuration on Mac mini.

### SSH Commands

SSH access through Tailscale network.

### Screen Sharing (VNC) Commands

VNC remote desktop access configuration.

## Setup Discussion

Notes on cloud infrastructure setup discussions with:
- anh Tuấn
- anh Quý

## Setup Hiếu PC Credentials

Credentials and configuration for Hiếu's PC setup.
