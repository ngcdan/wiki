---
title: "ECUS Batch Sync"
tags: [egov, ecus, sync, batch]
---

# ECUS Sync Runner

## Setup (Windows)

```bash
cd of1-egov/scripts
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

## Usage

```bash
# Interactive mode
python sync_runner.py

# Run specific ECUS
python sync_runner.py --ecus ECUS5VNACCS

# Run specific endpoints (1=core, 2=company, 3=declaration...)
python sync_runner.py --ecus ECUS5VNACCS --endpoints 1,2

# Run all ECUS
python sync_runner.py --all

# List config
python sync_runner.py --list
```

## Configuration

Edit `sync_runner.py` top section:

```python
SERVER_URL = "http://localhost:7082"

ECUS_DATABASES = {
    "ECUS5VNACCS": "Bee Logistics",
    "ECUS5THAISON": "Thai Son",
}
```

## Logs

Saved to `scripts/logs/`:
- `{ECUS}_{date}.log` - daily summary
- `{ECUS}_{endpoint}_{timestamp}.json` - detailed result