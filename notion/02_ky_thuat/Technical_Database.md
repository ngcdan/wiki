---
title: "Technical: Database"
source: "Notion"
synced_date: "2026-04-05"
---

## Docker SQL Server on Mac M1

### Azure SQL Edge Setup

Running SQL Server container on Apple Silicon Mac:

```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123!" \
  -p 1433:1433 --name sql-server \
  mcr.microsoft.com/azure-sql-edge
```

### Connecting with DBeaver

1. Install DBeaver database client
2. Create new SQL Server connection
3. Host: localhost
4. Port: 1433
5. Username: sa
6. Password: (your SA password)

## MSSQL Backup/Restore Commands

### List Backup Contents

View files in backup before restoring:

```sql
RESTORE FILELISTONLY FROM DISK = '/path/to/backup.bak'
```

### Restore Database

Restore database from backup with file relocation:

```sql
RESTORE DATABASE [TargetDatabase]
FROM DISK = '/path/to/backup.bak'
WITH
  MOVE 'LogicalDataName' TO '/var/opt/mssql/data/data.mdf',
  MOVE 'LogicalLogName' TO '/var/opt/mssql/data/log.ldf',
  REPLACE
```

## PostgreSQL Schema Owner Commands

### Change Schema Owner

Alter schema ownership:

```sql
ALTER SCHEMA schema_name OWNER TO new_owner;
```

### Change Database Owner

Transfer database ownership:

```sql
ALTER DATABASE database_name OWNER TO new_owner;
```

## PostgreSQL Dump and Restore

### pg_dump for Tables

Export table structure and data:

```bash
pg_dump -U username -d database_name -t table_name > table_dump.sql
```

### pg_restore from Spreadsheet

Restore data from exported format:

```bash
pg_restore -U username -d database_name -t table_name table_backup.dump
```

## Setup PostgreSQL with Homebrew

### Install PostgreSQL

```bash
brew install postgresql
```

### Start PostgreSQL Service

```bash
brew services start postgresql
```

### Check Configuration

```bash
brew services list
```

### Connect with psql

```bash
psql -U postgres
```

### Create Database

```bash
createdb my_database
```

### Create Role with Permissions

```sql
CREATE ROLE my_user WITH LOGIN PASSWORD 'password';
ALTER ROLE my_user SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE my_database TO my_user;
```

## Docker PostgreSQL Container

### Run PostgreSQL in Docker

```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  -d postgres:latest
```

## References

### Common Commands

- **cp command**: File copying and backup
- **log file paths**: System and application logs
- **server-env config**: Server environment variables
- **server-instances**: Multiple server instances
- **TransactionRequiredException note**: Transaction handling in JPA
- **Java enum methods**: Enum utility methods

### Concepts

#### @Polymorphism Annotation

Inheritance strategy annotation for JPA:

```java
@Entity
@Polymorphism(type = PolymorphismType.SINGLE_TABLE)
public class BaseEntity { }
```

#### @JsonProperty

JSON serialization field mapping:

```java
@JsonProperty("custom_name")
private String fieldName;
```

#### Unix Path Separator

Cross-platform path handling:

```java
String path = "dir" + File.separator + "file.txt";
```

#### Web Concepts

**Browser Caching**: Store static assets locally
- Cache headers (ETag, Last-Modified)
- Cache duration control
- Cache invalidation strategies

**DOM (Document Object Model)**: Tree structure of HTML elements
- Element selection
- Event handling
- Dynamic manipulation

**API (Application Programming Interface)**: Contract between systems
- REST principles
- HTTP methods
- Response formats

**Polyfill**: Compatibility code for older browsers
- Feature detection
- Fallback implementations
- Library polyfills

**Web Storage**: Client-side data persistence
- localStorage: Permanent storage
- sessionStorage: Session-only storage
- IndexedDB: Large data storage
- Cookies: Server-side storage

#### Spaced Repetition System

Learning technique for long-term retention:

**Schedule**:
- Review after 1 day
- Review after 3 days
- Review after 7 days
- Review after 14 days
- Review after 30 days

**Storage**: Database of flashcards and review history

**Metrics**:
- Recall rate
- Average review interval
- Difficulty factor

#### Logistics Terms

**Bill Surrendered**: Bill of lading returned to shipper

**Báo Có Payment**: Payment notification in accounting

### Clean Data Notes

Data cleaning and validation procedures:
- Null value handling
- Duplicate removal
- Format standardization
- Integrity checks

### PostgreSQL Replication

Master-slave replication setup:
- Streaming replication
- Replication slots
- WAL archiving
