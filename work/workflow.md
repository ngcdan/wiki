# Workflow: Dan (Dev Lead) — Quy trình làm việc hằng ngày (VN)

Updated: 2026-02-06

## 0) Mục tiêu
- **Tối ưu thời gian**: giảm context switching, giảm bị kéo bởi inbox.
- **Làm việc có hệ thống**: mọi request đi qua một pipeline thống nhất.
- **Tối ưu chất lượng**: task rõ ràng → dev làm nhanh → review nhanh → release ổn.
- **Tự động hoá tối đa**: ghi chép/đúc kết/điều phối được chuẩn hoá để AI + tooling hỗ trợ.

---

## 1) Vai trò & phạm vi công việc
Anh Đàn là **leader của một team dev**. Công việc chính gồm:

1) **Nhận yêu cầu & bug từ người dùng**
- Nguồn vào thường gặp: **Zalo** và **Outlook email**.

2) **Phân tích & chuẩn hoá yêu cầu**
- Làm rõ nhu cầu, bối cảnh, tác động.
- Đưa ra hướng giải quyết/đề xuất kỹ thuật ở mức phù hợp.

3) **Breakdown & giao việc cho team**
- Chia nhỏ thành task có thể thực thi.
- Gán ưu tiên, owner, deadline (nếu có).

4) **Hướng dẫn team, review code, và đôi khi trực tiếp code**
- Review PR, đảm bảo convention/quality.
- Code các phần khung (scaffold/framework) để team bám theo.

5) **Theo dõi tiến độ & cập nhật tài liệu**
- Update tiến độ, docs, todo, wiki dự án.

6) **Báo cáo và sync kỹ thuật với sếp (anh Tuấn)**
- Trong ngày có thể nhận cuộc gọi để:
  - báo cáo công việc
  - cập nhật thay đổi hệ thống
  - trao đổi kỹ thuật/định hướng

7) **Kế hoạch nhân sự gần hạn**
- Có thể onboard **anh Hiếu** (freelancer) làm phụ ~**15h/tuần**.

8) **Mục tiêu phát triển cá nhân**
- Luyện gõ phím, học tiếng Anh, tìm hiểu thị trường/đầu tư.

---

## 2) Nguyên tắc vận hành (để giữ focus)
### 2.1. Batch inbox theo khung giờ cố định
Để giảm context switching:
- **Block toàn bộ chat của người dùng** (chỉ mở các chat của dev để support).
- Chỉ mở lại user chat theo 2 khung giờ:
  - **gần cuối giờ 11h**
  - **gần 16h**

Ngoài 2 khung này: hạn chế “đập vào inbox” liên tục.

### 2.2. One-pipeline rule
Dù request đến từ đâu (Zalo/Outlook/call), **kết quả cuối phải đổ về 1 chỗ**:
- Issue / Backlog / file tracking trong `work/`.

### 2.3. Rõ ràng trước khi giao việc
- Task mơ hồ → tạo task “làm rõ yêu cầu” trước.
- Ưu tiên task độc lập, có acceptance criteria.

---

## 3) Quy trình xử lý request/bug (2 lần mỗi ngày)
> Thực hiện theo 2 batch: **~11:00** và **~16:00**

### Bước A — Intake (gom yêu cầu/lỗi)
Lướt Zalo/Outlook 1 lượt, với mỗi request ghi nhanh:
- **What**: lỗi/yêu cầu gì?
- **Impact**: ảnh hưởng ai? mức độ?
- **Evidence**: ảnh/log/link/case cụ thể.

### Bước B — Triage (xếp ưu tiên)
Gán ưu tiên theo mức độ:
- **P0**: ảnh hưởng vận hành/tiền/khách hàng ngay, cần phản ứng nhanh
- **P1**: ảnh hưởng đáng kể nhưng có workaround / chưa cháy
- **P2**: cải tiến/tiện ích/đẹp/không gấp

Quyết định trạng thái:
- làm ngay
- lên lịch
- cần hỏi thêm (thiếu dữ liệu)

### Bước C — Normalize (chuẩn hoá thành Issue/Backlog item)
Mỗi item tối thiểu nên có:
- **Context** (bối cảnh)
- **Expected / Acceptance criteria** (kỳ vọng/tiêu chí nghiệm thu)
- **Priority** (P0/P1/P2) + **Deadline** (nếu có)
- **Owner** + **Reviewer**
- **Links** (chat/email/screenshot/log)

### Bước D — Breakdown & Delegation
- Chia nhỏ để dev có thể làm 2–6 giờ/nhát.
- Nếu cần quyết định kỹ thuật: nêu rõ option + trade-off.

### Bước E — Tracking (cập nhật tiến độ)
Update file tracking/backlog trong `work/`:
- Top 3 ưu tiên
- In progress
- Blocked (vì sao, cần ai quyết)

### Bước F — Report cho anh Tuấn
Sau mỗi batch, gửi report ngắn gọn dựa trên backlog:
- Top priorities
- Done / In progress
- Incoming requests (P0/P1/P2)
- Risks/Blockers/Decisions needed
- Next 24h

---

## 4) Quy trình review & chất lượng (nhẹ nhưng hiệu quả)
### 4.1. PR convention tối thiểu
- Title có prefix theo issue:
  - `Fixes #...` / `Closes #...` / `Refs #...`
- PR description có:
  - tóm tắt what/why
  - test steps
  - note rủi ro/breaking change (nếu có)

### 4.2. Definition of Done (DoD) ngắn
- Có link issue
- Có test steps
- Không phá flow hiện tại (hoặc ghi rõ breaking change)
- Update docs/runbook nếu có thay đổi vận hành

---

## 5) Onboard anh Hiếu (15h/tuần) — nguyên tắc để không “ăn thời gian lead”
- Giao task rõ, độc lập, có acceptance criteria.
- Yêu cầu update tiến độ kiểu 3 dòng: Done / Next / Blockers.
- Chuẩn hoá PR/DoD như mục 4.

---

## 6) Thói quen duy trì năng suất (gợi ý)
- Mỗi ngày 30p: Anki + 30p: luyện gõ phím.
- Giữ nhịp “2 batch inbox” để đầu óc rảnh cho việc quan trọng.
- Ưu tiên ghi chép nhanh (raw) rồi dùng AI/tool clean-up thành note chuẩn.
