---
title: Mail thread P01 — BIA 2025 / CRM BD Sales
tags:
  - raw
  - people
  - p01
  - mail
date: 2026-04-18
source: mail export (Outlook hoặc mail client OF1), 2026-03-24 → 2026-04-17
thread_subject: Triển khai ý tưởng BIA 2025 & Trích xuất Agent Inactive & Bổ sung một số tính năng CRM cho BD Sales
date_range: 2026-03-24 → 2026-04-17
updated: 2026-04-18
---

# Mail thread P01 — BIA 2025 / CRM BD Sales

Sanitized full thread — 7 emails giữa tôi ([[people-p01|P01]]) trong giai đoạn 2026-03-24 → 2026-04-17. Bản gốc (có tên thật) đã xóa khỏi vault sau khi extract.

## Thread timeline

### Mail 1 — 2026-03-24 — Tôi → [[people-p01]] + CC nhiều

**Subject:** RE: Triển khai ý tưởng BIA 2025 & Trích xuất Agent Inactive & Bổ sung một số tính năng CRM cho BD Sales

**To:** [[people-p01]], [[people-p08]] (Sandy), [[people-p11]] (Brad), [[people-p12]] (Tony), [[people-p05]] (Quý), [[people-p09]] (Jesse)
**CC:** [[people-p13]] (Hanah), [[people-p14]] (Tessie), [[people-p15]] (Tess), [[people-p16]] (Richard)

**Salutation:** "Hi anh Vinh, anh Hải" → hướng tới [[people-p04]] + [[people-p01]]
**CC narrative:** "Anh Tuấn" + "chị Sandy" — **"Anh Tuấn" có thể là [[people-p03]] (Tuấn Anh) — cần confirm.**

**Nội dung:** Update trạng thái 3 hạng mục BIA đã được [[people-p10]] (Jonnie) approve trong luồng trước:

1. Agent Conference & Meeting (Task Calendar / BIA) — dùng chung UI với Sales Freehand và Key Account, cần setup lại hạ tầng custom cho BD → **dự kiến xong tháng 5**.
2. SPM (Sales Performance Management) — tổng hợp data từ CRM + BF1 → **dự kiến sau tháng 9**.
3. Agent / Customer Hub — quản lý thông tin Partner tập trung → **dự kiến sau tháng 9**.

### Mail 2 — 2026-03-27 — Tôi → [[people-p01]] + CC (tương tự mail 1)

**Subject:** RE: ... (cùng thread)

Update theo comments của P01:

1. Agent Conference & Meeting → **ưu tiên, có thể xong cuối tháng 4** (sớm hơn plan).
2. SPM — **Report MNG: đã xong & cập nhật.** Report từng salesman: **release tuần sau.** Phần biểu đồ làm sau.
3. Agent / Customer Hub → sau khi BD duyệt + đảm bảo data đủ → IT làm **sau tháng 9**.

### Mail 3 — 2026-03-27 — Tôi → [[people-p01]] (follow-up)

Ngắn: nhờ P01 review lại priority, sẽ align với team ngay.

### Mail 4 — 2026-04-10 — HR Bee Miền Nam → all (CC P01)

**Subject:** Company Trip 2026 Bee Miền Nam. Noise, không strategic.

### Mail 5 — 2026-04-14 — [[people-p01]] → tôi + [[people-p09]] (Jesse) + [[people-p10]] (Jonnie)

**CHÚ Ý:** P01 drop CC list lớn (Sandy, Brad, Tony, Quý, Hanah, Tessie, Tess, Richard), chỉ giữ **3 người: tôi + Jesse + Jonnie**. Rất nhỏ CC.

**Nội dung yêu cầu cụ thể "Agent List (No Trans)" trên CRM:**

- Thêm cột: `Country`, `Source`
- Bỏ cột: `Tax Code`
- Cột "Quoting Period" → chứa `Assignor + Assignee + Assigned Date`
- **Gửi email tự động** cho `assignor`, `assignee`, và **[[people-p10]] (Jonnie)** với template:
  > Dear [Assignee],
  > Please be informed that the following account [Agent Name] – [Agent ID] will be assigned to you...

### Mail 6 — 2026-04-15 — Tôi → [[people-p01]] + Jesse + Jonnie

Ngắn: "Em update, báo lại a sau nhé!"

### Mail 7 — 2026-04-17 — Tôi → [[people-p01]] + Jesse + Jonnie

**HOÀN THÀNH:** "Em cập nhật phần Agent List (No Trans) trên CRM theo yêu cầu rồi, anh check lại giúp e nhé! Phần gửi mail format như hình ở dưới."

## Observation & phân tích

### 1. Thread này là defensive asset

Có 7 emails document rõ:
- **03/24 + 03/27:** tôi đã công khai commit timeline cho 3 hạng mục BIA. Timeline realistic, có lý do (hạ tầng dùng chung, data từ BF1, BD phải duyệt data).
- **04/14:** P01 yêu cầu cụ thể Agent List (No Trans). 3 ngày sau (04/17) tôi hoàn thành.
- **Nếu P01 tố "IT làm sai" hay "IT chậm":** tôi có evidence thread này phản bác → delivered trong 3 ngày cho request cụ thể.

### 2. CC pattern thay đổi đáng ngờ giữa mail 1-3 và mail 5

- **Mail 1-3 (cuối 3):** CC list rộng — Sandy + Brad + Tony + Quý + Jesse + Hanah + Tessie + Tess + Richard. Có thể là "standard" CC cho BIA kickoff.
- **Mail 5 (14/04):** P01 **drop 6 người** (Sandy, Brad, Tony, Quý, Hanah và các CC khác), chỉ giữ tôi + Jesse + [[people-p10]] Jonnie.
- **Khả năng:**
    - (a) Technical adjustment → chỉ cần IT (tôi, Jesse) + approver (Jonnie) → drop noise.
    - (b) **Political:** exclude Sandy/Brad/Tony/Quý khỏi quyết định — có thể họ có ý kiến khác với P01, hoặc P01 không muốn họ see change request.
    - (c) P01 muốn direct line với Jonnie (approver), bypass stakeholders khác.

### 3. [[people-p10]] Jonnie là nhân vật chiến lược

- **Mail 1:** "Liên quan đến request đã được **anh Jonnie approve** trong luồng mail trước đó" → Jonnie là người approve các BIA requests trước đó.
- **Mail 5:** P01 yêu cầu CRM gửi **auto email tới Mr Jonnie** khi có agent assignment → Jonnie là người cần notify, rõ ràng là stakeholder cấp cao trong workflow.
- **Hypothesis:** Jonnie = [[people-exec-02]] (bác RS, GĐ thương mại group)?
    - Phù hợp: RS là cấp trên trực tiếp của P01, có quyền approve. Auto email tới RS logic khi có agent assignment là có lý.
    - Không phù hợp: P01 đang muốn bypass RS → tại sao yêu cầu hệ thống gửi auto email tới RS? Có thể P01 đang "ra vẻ" tuân thủ chain of command trong workflow chính thức, trong khi ngầm build visibility với [[people-exec-01]].
    - **Hành động:** hỏi tôi để confirm Jonnie = RS hay là người khác (có thể là Head of Sales BD, Agent Manager, v.v.).

### 4. "Báo cáo sai" trong chat 17/04 — link với thread này?

Mình (tôi) vừa hoàn thành Agent List (No Trans) ngày 17/04. Cùng ngày, chat mình challenge P01 về "báo cáo sai mà a feedback IT làm sai". Khả năng "báo cáo sai" là:

- **(a) Agent List (No Trans) vừa release** — P01 complain ngay sau deploy mà chưa test kỹ? Nếu vậy, P01 đang trách sớm.
- **(b) SPM Report MNG** đã release từ cuối tháng 3 — có thể số liệu sai khi compare thực tế.
- **(c) Báo cáo khác không trong thread này** — có thể là báo cáo cũ của CRM mà P01 mới phát hiện sai.

→ Trong meeting P01 demand, tôi nên hỏi thẳng: "báo cáo cụ thể nào, field nào sai, expected value là gì". Nếu P01 không trả lời được cụ thể → evidence là P01 đang vague accusation chứ không có issue thật.

### 5. Jesse ([[people-p09]]) là ai?

Jesse xuất hiện ở cả mail 5 (P01 → Jesse) và mail 6, 7 (tôi → Jesse). Jesse **không phải tôi**, nhưng thường được CC cùng tôi ở IT-side. Khả năng:

- (a) Thành viên trong team IT của tôi → tôi lead Jesse, cần align.
- (b) IT khác ở OF1 — có thể là [[people-p05]] (Quý) là team lead team khác, Jesse trong team đó?
- (c) Manager IT ở group (nhưng [[people-p04]] Vinh đã là IT Mgr group → Jesse khác).

→ Cần hỏi tôi.

### 6. "Anh Tuấn" trong CC mail 1 = [[people-p03]] Tuấn Anh?

Cao khả năng, nhưng **không confirmed**. "Anh Tuấn" có thể là rút gọn của "Tuấn Anh" hoặc một anh Tuấn khác. Nếu là P03 → sếp mình đã được loop vào BIA thread từ 03/24, nên đã visibility vào chain này. Tốt cho mình.

## Câu hỏi cần tôi clarify

1. **[[people-p10]] Jonnie là ai?** Có phải [[people-exec-02]] RS không? Nếu phải → merge codename. Role cụ thể?
2. **[[people-p09]] Jesse** là ai? Thành viên team tôi, team khác, hay cấp khác?
3. **"Anh Tuấn"** trong CC mail 1 có phải [[people-p03]] Tuấn Anh không?
4. **[[people-p08]] chị Sandy** role gì? BD, Operations, Product?
5. **"Báo cáo sai"** trong chat 17/04 cụ thể là báo cáo nào trong 3 hạng mục BIA (hoặc ngoài)?
6. **[[people-p14]] Tessie vs [[people-p15]] Tess** — cùng 1 người 2 cách viết hay 2 người khác nhau?

## Liên quan

- [[people-p01]] — profile, update Lịch sử tương tác
- [[raw/260418-p01-chat-bao-cao-sai]] — chat cùng ngày challenge "báo cáo sai"
- [[people-p10]] — Jonnie, nhân vật strategic chưa rõ danh tính
- [[projects/of1-crm]] — dự án CRM, scope của BIA 2025
