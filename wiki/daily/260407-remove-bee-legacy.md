# Spec: Remove `bee_legacy` module

Date: 2026-04-07
Repo: `of1-platform/datatp-python`
Branch base: `develop`

## Goal

Xoá hoàn toàn package `bee_legacy/` và mọi điểm phụ thuộc nó trong repo `datatp-python`. Sau khi hoàn tất, HTTP server vẫn start được và chỉ phục vụ phần non-legacy (PDF, redis, xlsx, download, các handler còn sống). Schema PostgreSQL được người dùng tự xử lý ngoài repo — spec này không đụng DB.

## Scope

### Hard delete (xoá hẳn)

- `bee_legacy/` — toàn bộ package (config, db, service, tests, requirements, db-tool.py).
- `datatp_server/cron.py` — cron tier ULTRA-HOT/HOT/WARM/COLD cho legacy sync.
- `datatp_server/cron_lcl_addon.py` — verify trước khi xoá; xoá nếu thực sự là cron legacy, giữ nếu không phụ thuộc `bee_legacy`.
- `datatp_server/service/api_integrated_transactions.py`
- `datatp_server/service/api_integrated_partner.py`
- `test_connection.py` (root) — script test kết nối BFS One.
- `dan-tools/read_lcl_data.py`

### Edit

- `datatp_server/httpserver.py`
  - Gỡ 5 import `from bee_legacy.* import ...`.
  - Gỡ khối khởi tạo cron threads + Kafka consumer threads (~11 daemon threads liên quan TransactionConsumer / HouseBillService / HawbProfitService / ExchangeRateService / SettingsUnitService).
  - Giữ HTTP server core + handler registration cho phần non-legacy.
- `datatp_server/handlers/core.py` & `datatp_server/handlers/service.py`
  - Gỡ route đăng ký tới `api_integrated_transactions` và `api_integrated_partner`.
- `datatp_server/requirements.txt` & `datatp_common/requirements.txt`
  - Gỡ MSSQL driver (`pymssql` / `pyodbc`) và Kafka client (`kafka-python` / `confluent-kafka`) **nếu** không còn module non-legacy nào import chúng.
- `datatp_common/kafka/` & `datatp_common/db/`
  - Rà soát từng file. Xoá module chỉ phục vụ BFS One MSSQL engine / Kafka consumer cho legacy. Giữ lại phần shared còn được code non-legacy dùng.
- `README.md`
  - Viết lại: bỏ section Kafka topics, multi-tier sync strategy, 2-tier architecture, monitoring legacy. Giữ phần setup môi trường + mô tả phần còn sống.
- `CLAUDE.md`
  - Đồng bộ với README mới: bỏ phần kiến trúc Kafka/multi-tier, giữ layout repo + commands còn hợp lệ.

### Giữ nguyên

- Schema PostgreSQL (`integrated_transaction`, `integrated_housebill`, `integrated_hawb_profit`, `integrated_exchange_rate`, `integrated_settings_unit`) — user tự xử lý ngoài repo.
- `datatp_server/handlers/`, `service/core.py`, `service/download.py`, `service/pdf.py`, `service/redis.py`, `service/xlsx.py`, `pdf/`, `data/`.
- `datatp_ai/`, `datatp_tool/`, `gui/`, `experiments/`.

## Execution order

Chạy theo thứ tự sau để repo luôn import-clean ở mỗi bước:

1. **Gỡ wiring trước** trong `httpserver.py` và `handlers/*` (bỏ import + route legacy).
2. **Xoá API services**: `api_integrated_transactions.py`, `api_integrated_partner.py`.
3. **Xoá cron**: `cron.py`; verify rồi xoá `cron_lcl_addon.py`.
4. **Xoá scripts ngoài**: `test_connection.py`, `dan-tools/read_lcl_data.py`.
5. **Xoá `bee_legacy/`** — toàn bộ package.
6. **Dọn `datatp_common/`**: grep toàn repo (`datatp_ai`, `datatp_tool`, `gui`, `datatp_server`, `experiments`, `dan-tools`) tìm import của từng module trong `datatp_common/kafka/` và `datatp_common/db/`; xoá module nào không còn ai dùng.
7. **Dọn `requirements.txt`**: gỡ package MSSQL/Kafka nếu grep xác nhận không còn import.
8. **Cập nhật `README.md` + `CLAUDE.md`**.
9. **Verify**:
   - `python -c "import datatp_server.httpserver"` không lỗi.
   - `cd datatp_server && ./service.sh http:run` start được (chạy foreground, Ctrl-C dừng).

## Risks

- **R1 — Shared lib false positive**: `datatp_common/kafka/` hoặc `db/` có thể được dùng bởi `datatp_ai`, `datatp_tool`, `gui`. Mitigation: bước 6 grep toàn repo trước khi xoá từng module, không xoá theo tên thư mục.
- **R2 — `cron_lcl_addon.py` không phải legacy**: có thể là cron độc lập. Mitigation: đọc file trước, chỉ xoá nếu nó import `bee_legacy` hoặc phụ thuộc data flow legacy.
- **R3 — Handlers dynamic registration**: `handlers/core.py` / `service.py` có thể đăng ký endpoint động. Mitigation: đọc cả 2 file trước khi sửa, không grep-edit mù.
- **R4 — Requirements dùng chéo**: gỡ `pymssql`/`kafka-python` có thể vỡ module khác. Mitigation: chỉ gỡ sau khi grep xác nhận zero import non-legacy.

## Verification

- Smoke import: `python -c "import datatp_server.httpserver"`.
- Smoke start: `./service.sh http:run`.
- Grep zero-residual: `grep -r "bee_legacy" .` phải trả về rỗng (trừ chính file spec/plan này nếu nằm trong repo — ở đây spec nằm ngoài repo).
- Không chạy full test suite (repo không có runner thống nhất).

## Out of scope

- DB migration / drop bảng `integrated_*` (user tự làm).
- Refactor handler còn lại.
- Thay thế chức năng sync bằng cơ chế khác.
- Đụng tới `datatp_ai`, `datatp_tool`, `gui`, `experiments` ngoài việc grep kiểm tra.
