# Kafka Consumer Group Conflict — Local vs Cluster

**Date:** 2026-04-10
**Project:** of1-fms
**Context:** Debug CDC pipeline — local FMS instance chỉ nhận được một nửa events từ Kafka topic.

---

## Triệu chứng

Trigger CDC với 19 Transactions rows → chỉ 9/19 events được FMS local xử lý. Các events còn lại "biến mất" mặc dù Debezium connector hoạt động bình thường.

## Root cause: Consumer group conflict

### Kafka Consumer Group là gì?

Trong Kafka, mỗi **topic** được chia thành nhiều **partitions** (ví dụ topic `Transactions` có 12 partitions: 0, 1, 2, ..., 11). Messages được phân phối đều vào các partitions theo hash của key.

Một **consumer group** là tập hợp các consumers cùng đọc từ một topic với **group.id giống nhau**. Kafka đảm bảo quy tắc quan trọng:

> **Mỗi partition chỉ được assign cho ĐÚNG MỘT consumer trong cùng một group tại một thời điểm.**

Đây là cách Kafka phân chia công việc và đảm bảo mỗi message chỉ được xử lý 1 lần.

### Cách Kafka phân chia partitions

Ví dụ topic `Transactions` có 12 partitions, consumer group `fms-cdc-consumer-dev`:

**Trường hợp 1 — Chỉ 1 consumer instance:**
```
Consumer A (local) ← partitions [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  ← 12/12
```
Consumer A xử lý TẤT CẢ messages.

**Trường hợp 2 — 2 consumer instances cùng group:**
```
Consumer A (local)            ← partitions [0, 1, 2, 4, 6, 8]         ← 6/12
Consumer B (cluster dev k8s)  ← partitions [3, 5, 7, 9, 10, 11]       ← 6/12
```
Kafka tự động "rebalance" — chia partitions đều cho 2 consumers. Mỗi consumer chỉ thấy **một nửa** messages.

### Vấn đề gặp phải

Config ban đầu trong `addon-fms-config.yaml`:
```yaml
consumer-group: "fms-cdc-consumer-${env.kafka.env}"
```

Khi `env.kafka.env=dev`, group ID = `fms-cdc-consumer-dev`.

**Có 2 instance cùng dùng group này:**
1. **FMS local** trên máy dev (khi chạy để test)
2. **FMS trong cluster `of1-dev-platform` k8s** (luôn chạy để serve dev env)

Cả 2 đều subscribe vào cùng CDC topics với cùng group → Kafka rebalance → mỗi instance chỉ lấy 6/12 partitions.

**Kết quả khi trigger CDC 19 Transactions:**
- Debezium publish 19 messages vào 12 partitions
- Khoảng 9-10 messages rơi vào partitions của local → local xử lý được
- Còn lại 9-10 messages rơi vào partitions của cluster → cluster xử lý, **local không bao giờ thấy**

Log xác nhận điều này — local chỉ nhận partitions 3, 5, 7, 9, 10, 11:
```
fms-cdc-consumer-dev: partitions assigned: [
  Transactions-3, Transactions-5, Transactions-7,
  Transactions-9, Transactions-10, Transactions-11
]
```

## Fix: Unique group ID per instance

### Approach

Tương tự cách config `env.db.host` trong `env.sh`, thêm một env key cho CDC consumer group override:

**env.sh** (local only):
```bash
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.cdc.consumer-group=fms-cdc-consumer-dev-local-$(hostname -s)"
```

**addon-fms-config.yaml**:
```yaml
datatp:
  msa:
    fms:
      queue:
        cdc:
          consumer-group: "${env.cdc.consumer-group:fms-cdc-consumer-${env.kafka.env}}"
```

### Cách hoạt động

- Nếu `env.cdc.consumer-group` được set (local dev) → dùng giá trị override
- Nếu không set (cluster deployment) → fallback về default `fms-cdc-consumer-${env.kafka.env}`

Kết quả: Group ID local = `fms-cdc-consumer-dev-local-<hostname>`

Đây là **group ID hoàn toàn khác** với `fms-cdc-consumer-dev` của cluster. Kafka coi local và cluster là **2 group độc lập**. Mỗi group đều được quyền đọc **toàn bộ** 12 partitions riêng, với offset riêng.

```
Group: fms-cdc-consumer-dev                 → Consumer B (cluster) ← 12/12 partitions
Group: fms-cdc-consumer-dev-local-mac-mini  → Consumer A (local)   ← 12/12 partitions
```

Log sau fix:
```
fms-cdc-consumer-dev-local-mac-mini: partitions assigned:
  [Transactions-0, Transactions-1, ..., Transactions-11]  ← 12 partitions
```

## Điểm cần lưu ý

1. **Mỗi group có offset riêng** — lần đầu local join với group ID mới, Kafka không có committed offset cho group này. `auto.offset.reset` quyết định đọc từ đâu (thường là `latest` hoặc `earliest`). Với CDC dev/test, nên dùng `earliest` để re-process events từ đầu khi trigger.

2. **Cluster không bị ảnh hưởng** — nó vẫn consume bình thường với group cũ.

3. **File `env.sh` không commit vào repo** — nằm trong `working/release-fms/server-env/` directory, được generate từ `env-sample.sh`. Mỗi dev máy tự config.

4. **Alternative approaches đã cân nhắc:**
   - `fms-cdc-local-$USER` — depends on username
   - `fms-cdc-consumer-dev-$(uuidgen)` — mỗi restart tạo group mới, mất offset history
   - Stop cluster dev instance khi test local — không practical
   - Dùng `hostname -s` là balance tốt nhất: ổn định qua restarts, unique per machine

## Debug commands

### Check partitions được assign

Trong server log, tìm:
```bash
grep "partitions assigned" server.log | grep cdc-consumer
```

### Check consumer group lag (nếu có kafka CLI)

```bash
kafka-consumer-groups.sh --bootstrap-server <broker> \
  --group fms-cdc-consumer-dev-local-<hostname> \
  --describe
```

### Count events received per table

```bash
grep "CDC_RECEIVED" server.log | awk -F'table=' '{print $2}' | awk '{print $1}' | sort | uniq -c
```

### Verify unique TransIDs processed

```bash
grep "CDC SAVE fms_transaction" server.log | awk '{print $NF}' | sort -u | wc -l
```

## Related files

- `release/src/app/server/addons/fms/config/addon-fms-config.yaml` — consumer group config
- `working/release-fms/server-env/env.sh` — local JVM override
- `module/core/src/main/java/of1/fms/core/cdc/listener/CDCListener.java` — Kafka listener
- `scripts/cdc-trigger.py` — CDC trigger test script
