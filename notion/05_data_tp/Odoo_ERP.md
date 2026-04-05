# 👨🏽‍💻 Odoo ERP

> Notion ID: `160efb9db8574e7b912a4c291db9e1db`
> Parent: Data TP → Status: Technical
> Synced: 2026-04-05

## Develop

- **Activate ENV:** `source odoo14-venv/bin/activate`

## Cập nhật dữ liệu lên web server

**SSH:**
```bash
ssh -p 30221 datatp@beescs-1.dev.datatp.net
# password: Datatp!@#

ssh -p 30222 datatp@beescs-2.dev.datatp.net
# password: Datatp!@#
```

Account: tuan08@gmail.com / DataTP@123 ⇒ acc beescs.com

**Command depends:**
- Connect qua ssh lên server → chạy run:clean → init data từ giao diện

## Ask

*(screenshot)*

- Hạch toán lương, hạch toán chi phí bảo hiểm trừ lương

## Docker & Container Architecture

Khái niệm là có 1 cái máy chủ ở bên ngoài, và có nhiều cái máy ảo ở bên trong. Thực sự máy ảo của docker không phải là máy ảo thật. Chiến lược là nhiều phần mềm (program) nhóm chung lại với nhau, và coi như nhóm chung đó là một cái máy ảo.

```bash
cd namespaces/generic-server/production
vi k8s-config/

ssh -p 30231 datatp@datatp.cloud
```

Máy ảo giống virtual box hay parallel thì nó simulate một cái máy ảo thật, như vậy có thể cái window trên linux, và linux trên window được. Còn container là máy ảo và máy chủ là phải cùng nhân kernel là linux.

*(screenshot)*

### Kubernetes (K8s) Commands

In **projects/k8s:**
```bash
source env.sh => activate scripts
k8s sys:status => Kiem tra
```

Nhóm các programs đang chạy thành một nhóm ⇒ Máy ảo docker.

In **namespace/generic-server/productions:**
- `vi k8s-config/datatp/pod.yaml` ⇒ file config cho từng máy ảo.
- `k8s ns:status`

**Địa chỉ mount trên máy thật:** `/mnt/data/cloud/pv/generic-server/production/servers`
```bash
echo "hello dan" > test.txt
```

In **namespace/it/prod:** (location của nginx container)
- `k8s ns:status`
- `vi /mnt/data/cloud/pv/it/nginx/config/datatp.config` ⇒ File config của nginx

### Container Root Access

Trong trường hợp cần vào root của máy ảo để cài:

In **projects/k8s:**
- `source env.sh`
- `cd namespace/generic-server/production`

Cần quyền root:
- `k8s ns:pod:shell tên máy` ⇒ `k8s ns:pod:shell datatp-odoo`
- `df -h` ? lệnh gì?

Nhiều lúc máy bị chết, và mình redeploy lại, hoặc trong tương lai mình sẽ dịch chuyển từ máy này sang máy khác. Trong hệ thống cloud, nó có thể chạy 3 4 con máy physical thật, trong trường hợp 1 con chết thì nó sẽ dịch chuyển sang 1 con máy khác. Dẫn đến chỉ có những dữ liệu được mount thì nó không bị mất, còn không khi nó dịch chuyển sang chỗ khác thì nó sẽ chạy các script nó cài lại các thứ, thành ra dữ liệu có thể bị mất. Nên phải hiểu rõ hệ thống và tính toán.

```bash
chown datatp odoo
chgrp datatp odoo
ls -lh
```

⇒ Đổi quyền cho thư mục `odoo`

```bash
k8s ns:redeploy datatp-odoo
```

⇒ Deploy lại máy datatp odoo

Khi cài 1 cái máy, thường thường nó có 1 file iso đóng gọi lại. Vì vậy nếu muốn cài thêm các command, program trong máy ảo thì mình phải build lại image của máy đó.

*(screenshot)*
*(screenshot)*

Trong image, khi cài một command gì, nó gọi là cái layer, để lên trên một cái đã có sẵn.

```bash
kubectl get pods --all-namespaces
```

⇒ View tất cả các con pod đang chạy ở các namespace khác nhau

```bash
kubectl get pods --n prod
```

In **projects/k8s/namespaces/it/prod:**
- `vi k8s-config-gen/nginx/nginx.yaml`
- `sudo vi /mnt/data/cloud/pv/it/nginx/config/datatp.conf`
- `k8s ng:redeploy nginx`

## Setup Odoo

```bash
brew install libpq --build-from-source
brew install openssl

export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/libpq/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/libpq/include"

pip3 install psycopg2
```

Bên em đang triển khai phần mềm cho một số công ty khác. Nhưng dùng chung một hệ thống. Nên những khi muốn cập nhật em đều phải tắt máy đi để tiến hành cập nhật. Thường thì em sẽ cập nhật vào cuối tuần. Lúc tối thứ 7 hoặc chủ nhật.

---

Thùng thanh long xuất khẩu
