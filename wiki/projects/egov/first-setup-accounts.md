# First-Time Account Setup

## Setup (Windows)

```bash
cd of1-egov/scripts/first-setup-accounts
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

## Usage

```bash
# Interactive mode
python setup_accounts.py

# Setup all accounts
python setup_accounts.py --all

# Setup specific user
python setup_accounts.py --user hieu.ht

# Auto-yes delete existing records
python setup_accounts.py --all --yes

# Override DB host (e.g. for local dev)
python setup_accounts.py --db-host localhost
```

## Configuration

Edit `setup_accounts.py` top section:

```python
DB_HOST = "egov-server.of1-prod-platform.svc.cluster.local"
DB_PORT = 5432
DB_NAME = "egov"

ACCOUNTS = [
    {
        "login_id": "hieu.ht",
        "company_id": 8,
        "sync_source_config_value": "2",
        "sync_source_config_display": "BEEOLD",
        "partner_company_id": 62268,
        "partner_company_display": "COMPANY NAME",
        "partner_assign_company_id": 62298,
    },
]
```

## What it does

For each account in the list:

1. Checks if `account_configuration` and `account_partner_company` records exist
2. If existing records found, asks to delete first (yes/no)
3. If yes → deletes and re-creates; if no → skips
4. Inserts:
   - `account_configuration` with key `account.selected_sync_source`
   - `account_configuration` with key `account.selected_partner_company_id`
   - `account_partner_company` partner assignment
