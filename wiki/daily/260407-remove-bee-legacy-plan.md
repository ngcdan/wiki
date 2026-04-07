# Remove `bee_legacy` Module — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xoá hoàn toàn package `bee_legacy/` và mọi điểm phụ thuộc nó trong repo `datatp-python`, giữ HTTP server start được.

**Architecture:** Gỡ wiring trong `httpserver.py` + `cron.py` trước (giữ framework cron + jobs non-legacy), xoá API services + scripts ngoài, cuối cùng xoá `bee_legacy/` và dọn `datatp_common` + `requirements.txt`. Không đụng schema DB.

**Tech Stack:** Python 3, Tornado, `schedule` lib, Kafka, MSSQL/PostgreSQL.

**Spec:** `/Users/nqcdan/dev/wiki/wiki/daily/260407-remove-bee-legacy.md`

**Repo:** `/Users/nqcdan/OF1/forgejo/of1-platform/datatp-python` (branch `develop`)

---

## Pre-flight verification command

Sau mỗi task chỉnh code Python, chạy:
```bash
cd /Users/nqcdan/OF1/forgejo/of1-platform/datatp-python && python -c "import datatp_server.httpserver" 2>&1
```
Expected: không có `ImportError` / `ModuleNotFoundError`.

(Có thể có lỗi runtime config khác — chỉ quan tâm import phải sạch.)

---

## Task 1: Gỡ wiring legacy trong `httpserver.py`

**Files:**
- Modify: `datatp_server/httpserver.py`

- [ ] **Step 1:** Mở `datatp_server/httpserver.py`. Xoá các import legacy (dòng 13, 23–28):
  ```python
  from datatp_server.service.api_integrated_transactions import ApiIntegratedTransactionHttpService
  from bee_legacy.service.exchange_rate_service import getExchangeRateService;
  from bee_legacy.service.settings_unit_service import getSettingsUnitService;
  from bee_legacy.service.hawb.integrated_transaction_service import getTransactionService;
  from bee_legacy.service.hawb.integrated_housebill_service import getHouseBillService;
  from bee_legacy.service.hawb.integrated_hawb_profit_service import getHawbProfitService;
  from datatp_server.service.api_integrated_partner import ApiIntegratedPartnerHttpService
  ```

- [ ] **Step 2:** Trong `HttpServer.__init__`, xoá các dòng register legacy:
  ```python
  PUBLIC_HTTP_SERVICE.register(ApiIntegratedTransactionHttpService());
  ...
  SECURE_HTTP_SERVICE.register(ApiIntegratedPartnerHttpService());
  SECURE_HTTP_SERVICE.register(ApiIntegratedTransactionHttpService());
  ```
  Giữ lại các register non-legacy (Hello, Redis, Xlsx, PDF, TMS, Ecus, Download).

- [ ] **Step 3:** Xoá dòng `self._start_kafka_consumers();` và toàn bộ method `_start_kafka_consumers(self)` (dòng ~64–159).

- [ ] **Step 4:** Giữ `getCronService();` (cron framework vẫn cần cho `TmpStorageCleanJob`).

- [ ] **Step 5:** Verify import:
  ```bash
  python -c "import datatp_server.httpserver" 2>&1
  ```
  Expected: không có lỗi import liên quan `bee_legacy`. (Có thể vẫn lỗi do `cron.py` còn import legacy — sẽ fix ở Task 2.)

- [ ] **Step 6:** Commit:
  ```bash
  git add datatp_server/httpserver.py
  git commit -m "remove: gỡ wiring bee_legacy khỏi httpserver"
  ```

---

## Task 2: Dọn `cron.py` — giữ framework, xoá jobs legacy

**Files:**
- Modify: `datatp_server/cron.py`

- [ ] **Step 1:** Mở `datatp_server/cron.py`. Xoá các import legacy ở đầu file:
  ```python
  from bee_legacy.service.hawb.integrated_transaction_service import getTransactionService
  from bee_legacy.service.exchange_rate_service import getExchangeRateService
  from bee_legacy.service.settings_unit_service import getSettingsUnitService
  from bee_legacy.service.integrated_partner_service import getIntegratedPartnerService
  ```
  Giữ: `schedule`, `time`, `threading`, `logging`, `datetime`, `timedelta`, `from .service.download import getTmpStorageService`.

- [ ] **Step 2:** Xoá các class job legacy:
  - `SyncBFSOneExchangeRateJob`
  - `SyncBFSOneUnitContentJob`
  - `SyncBFSOneTransactionUltraHotJob`
  - `SyncBFSOneTransactionHotJob`
  - `SyncBFSOneTransactionWarmJob`
  - `SyncBFSOneTransactionColdJob`
  - `SyncLCLDataJob` (phụ thuộc `dan-tools/read_lcl_data.py` sẽ bị xoá ở Task 5)

  Giữ: `CronJob`, `CronJobContainer`, `CronService`, `HelloJob`, `TmpStorageCleanJob`.

- [ ] **Step 3:** Trong hàm `getCronService()`, xoá các registration tương ứng:
  ```python
  CRON_SERVICE.add_every_1_min('sync-bfsone-exchange-rate', ...);
  CRON_SERVICE.add_every_1_min('sync-bfsone-unit-content', ...);
  CRON_SERVICE.add_every_30_min('sync-bfsone-transaction-ultra-hot', ...);
  CRON_SERVICE.add_every_3_hour('sync-bfsone-transaction-hot', ...);
  CRON_SERVICE.add_every_12_hour('sync-bfsone-transaction-warm', ...);
  CRON_SERVICE.add_every_24_hour('sync-bfsone-transaction-cold', ...);
  CRON_SERVICE.add_every_30_min('sync-lcl-data', ...);
  ```
  Cùng với các comment "Multi-tier transaction sync strategy" và "LCL data sync".

  Giữ:
  ```python
  CRON_SERVICE.add_every_1_min('hello', HelloJob());
  CRON_SERVICE.add_every_3_hour('tmp-storage-clean', TmpStorageCleanJob());
  ```

- [ ] **Step 4:** Verify import:
  ```bash
  python -c "import datatp_server.cron" 2>&1
  python -c "import datatp_server.httpserver" 2>&1
  ```
  Expected: không có `ImportError`. Nếu vẫn lỗi → còn import bee_legacy ở đâu đó, fix trước khi tiếp.

- [ ] **Step 5:** Commit:
  ```bash
  git add datatp_server/cron.py
  git commit -m "remove: gỡ legacy cron jobs, giữ framework + non-legacy jobs"
  ```

---

## Task 3: Xoá `cron_lcl_addon.py`

**Files:**
- Delete: `datatp_server/cron_lcl_addon.py`

- [ ] **Step 1:** Verify file không được import:
  ```bash
  cd /Users/nqcdan/OF1/forgejo/of1-platform/datatp-python && grep -r "cron_lcl_addon" . --exclude-dir=.git
  ```
  Expected: không có kết quả (file là snippet helper, không được import).

- [ ] **Step 2:** Xoá file:
  ```bash
  git rm datatp_server/cron_lcl_addon.py
  ```

- [ ] **Step 3:** Commit:
  ```bash
  git commit -m "remove: xoá cron_lcl_addon.py (snippet không dùng)"
  ```

---

## Task 4: Xoá API service legacy

**Files:**
- Delete: `datatp_server/service/api_integrated_transactions.py`
- Delete: `datatp_server/service/api_integrated_partner.py`

- [ ] **Step 1:** Verify không còn import từ chỗ khác (httpserver đã gỡ ở Task 1):
  ```bash
  grep -rn "api_integrated_transactions\|api_integrated_partner\|ApiIntegratedTransactionHttpService\|ApiIntegratedPartnerHttpService" datatp_server datatp_common dan-tools datatp_ai datatp_tool gui experiments 2>/dev/null
  ```
  Expected: không kết quả ngoài chính 2 file sắp xoá.

- [ ] **Step 2:** Xoá:
  ```bash
  git rm datatp_server/service/api_integrated_transactions.py datatp_server/service/api_integrated_partner.py
  ```

- [ ] **Step 3:** Verify import server:
  ```bash
  python -c "import datatp_server.httpserver" 2>&1
  ```
  Expected: clean.

- [ ] **Step 4:** Commit:
  ```bash
  git commit -m "remove: xoá API service legacy (transactions, partner)"
  ```

---

## Task 5: Xoá scripts ngoài phụ thuộc legacy

**Files:**
- Delete: `test_connection.py`
- Delete: `dan-tools/read_lcl_data.py`

- [ ] **Step 1:** Verify `read_lcl_data.py` không còn import (Task 2 đã xoá `SyncLCLDataJob`):
  ```bash
  grep -rn "read_lcl_data" . --exclude-dir=.git
  ```
  Expected: không kết quả.

- [ ] **Step 2:** Xoá:
  ```bash
  git rm test_connection.py dan-tools/read_lcl_data.py
  ```

- [ ] **Step 3:** Commit:
  ```bash
  git commit -m "remove: xoá test_connection.py và dan-tools/read_lcl_data.py"
  ```

---

## Task 6: Xoá package `bee_legacy/`

**Files:**
- Delete: `bee_legacy/` (toàn bộ thư mục)

- [ ] **Step 1:** Final check không còn import:
  ```bash
  grep -rn "bee_legacy" . --exclude-dir=.git --exclude=CLAUDE.md --exclude=README.md
  ```
  Expected: không kết quả (CLAUDE.md/README.md sẽ dọn ở Task 9).

- [ ] **Step 2:** Xoá package:
  ```bash
  git rm -r bee_legacy
  ```

- [ ] **Step 3:** Verify server import:
  ```bash
  python -c "import datatp_server.httpserver" 2>&1
  ```
  Expected: clean.

- [ ] **Step 4:** Commit:
  ```bash
  git commit -m "remove: xoá package bee_legacy"
  ```

---

## Task 7: Dọn `datatp_common` (kafka + db dead code)

**Files:**
- Modify/Delete: các file trong `datatp_common/kafka/` và `datatp_common/db/` không còn được dùng.

- [ ] **Step 1:** Liệt kê các module trong 2 thư mục:
  ```bash
  ls datatp_common/kafka datatp_common/db
  ```

- [ ] **Step 2:** Với MỖI file trong `datatp_common/kafka/` và `datatp_common/db/`, grep tìm import non-legacy:
  ```bash
  for f in datatp_common/kafka/*.py datatp_common/db/*.py; do
    name=$(basename "$f" .py)
    echo "=== $f ==="
    grep -rn "from datatp_common.kafka.$name\|from datatp_common.db.$name\|import datatp_common.kafka.$name\|import datatp_common.db.$name" . --exclude-dir=.git --exclude-dir=bee_legacy 2>/dev/null
  done
  ```

- [ ] **Step 3:** Với mỗi file zero-result (không ai import) → xoá. Với file vẫn được import → giữ. Đặc biệt chú ý: BFS One MSSQL engine (likely zero ref sau khi xoá `bee_legacy`) → xoá.

  Ghi rõ trong commit message file nào bị xoá và lý do.

- [ ] **Step 4:** Verify import server:
  ```bash
  python -c "import datatp_server.httpserver" 2>&1
  ```

- [ ] **Step 5:** Commit:
  ```bash
  git add -A datatp_common
  git commit -m "remove: dọn dead code datatp_common kafka/db sau khi xoá bee_legacy"
  ```

---

## Task 8: Dọn `requirements.txt`

**Files:**
- Modify: `datatp_server/requirements.txt`
- Modify: `datatp_common/requirements.txt`

- [ ] **Step 1:** Đọc cả 2 file requirements.

- [ ] **Step 2:** Với mỗi candidate package có khả năng chỉ dùng cho legacy (`pymssql`, `pyodbc`, `kafka-python`, `confluent-kafka`, `aiokafka`...), grep xác nhận không còn import:
  ```bash
  for pkg in pymssql pyodbc kafka confluent_kafka aiokafka; do
    echo "=== $pkg ==="
    grep -rn "import $pkg\|from $pkg" . --exclude-dir=.git 2>/dev/null
  done
  ```

- [ ] **Step 3:** Gỡ các package có grep zero-result khỏi requirements.txt tương ứng.

- [ ] **Step 4:** Verify import server:
  ```bash
  python -c "import datatp_server.httpserver" 2>&1
  ```

- [ ] **Step 5:** Commit:
  ```bash
  git add datatp_server/requirements.txt datatp_common/requirements.txt
  git commit -m "remove: gỡ MSSQL/Kafka deps không còn dùng"
  ```

---

## Task 9: Cập nhật `README.md` và `CLAUDE.md`

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1:** Viết lại `README.md`:
  - Giữ section "Set Up Environment" (cập nhật `pip3 install -r` thành 2 file requirements).
  - Xoá toàn bộ section "Architecture Overview", "Kafka Topics", "Data Sync Flow", "Multi-Tier Sync", "2-Tier Kafka Architecture", "Kafka Configuration", "Key Design Patterns", "Log Levels", "Multi-Tier Sync Monitoring", "Database Schema".
  - Thay bằng mô tả ngắn về layout repo (datatp_server, datatp_common, datatp_ai, datatp_tool, gui) và cách chạy server (`./service.sh http:run`).

- [ ] **Step 2:** Viết lại `CLAUDE.md` để đồng bộ:
  - Xoá section "Architecture (big picture)" và "Conventions" (phần Kafka/multi-tier).
  - Giữ "Repository Layout" (xoá dòng `bee_legacy`), "Common Commands".

- [ ] **Step 3:** Verify zero residual:
  ```bash
  grep -rn "bee_legacy\|BFS One\|bee-legacy\|ULTRA-HOT\|multi-tier" . --exclude-dir=.git
  ```
  Expected: không kết quả.

- [ ] **Step 4:** Commit:
  ```bash
  git add README.md CLAUDE.md
  git commit -m "docs: cập nhật README và CLAUDE.md sau khi xoá bee_legacy"
  ```

---

## Task 10: Final verification

- [ ] **Step 1:** Smoke import:
  ```bash
  python -c "import datatp_server.httpserver; print('OK')"
  ```
  Expected: `OK`.

- [ ] **Step 2:** Smoke start (foreground, Ctrl-C để dừng sau ~5s):
  ```bash
  cd datatp_server && timeout 5 python httpserver.py; echo "exit=$?"
  ```
  Expected: server start được, không có ImportError. Exit code có thể là 124 (timeout) — chấp nhận được.

- [ ] **Step 3:** Zero-residual check:
  ```bash
  cd /Users/nqcdan/OF1/forgejo/of1-platform/datatp-python && grep -rn "bee_legacy" . --exclude-dir=.git
  ```
  Expected: không kết quả.

- [ ] **Step 4:** Git log review:
  ```bash
  git log --oneline develop..HEAD
  ```
  Expected: ~9 commit từ Task 1–9, ngắn gọn, mô tả rõ.

- [ ] **Step 5:** Báo user hoàn tất, sẵn sàng cho code review hoặc merge.

---

## Notes / Risks

- **Không có test runner thống nhất** → chỉ verify bằng smoke import + smoke start.
- **Schema DB không bị đụng** — user tự xử lý các bảng `integrated_*` ngoài repo.
- **Task 7 & 8 nhạy cảm**: chỉ xoá khi grep cho zero-result. Nếu có doubt → giữ lại file/package, ghi note trong commit message.
- **Không commit hàng loạt**: mỗi task = 1 commit để dễ revert nếu cần.
