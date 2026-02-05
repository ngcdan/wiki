# Weekly Plan.




## 2026-01-26

#### Yêu cầu từ CEO (CRM - Bee Group)
- **Mục tiêu:** Check partners toàn hệ thống để chống xung đột sales list.
- **Mục 1 (deadline 2026-02-14):** CRM hiển thị data partners toàn bộ công ty; check chéo 2 chiều.
- **Mục 2:** Triển khai CRM cho toàn bộ công ty thành viên (VN bắt buộc; nước ngoài theo yêu cầu).
  Danh sách chi tiết ở **Bảng tổng hợp**.
  **Deadline mục 2 2026-01-30**

#### Việc cần làm
1) Tạo toàn bộ công ty lên cloud.
1) Rà soát, tạo account cho toàn bộ công ty bắt buộc theo bảng ở dưới.
2) Gửi danh sách account riêng của từng công ty cho anh Vinh.

3) Xác nhận phạm vi dữ liệu partners + cơ chế check toàn hệ thống.
4) Sync dữ liệu về DB `crm`/`bee_legacy_db` và kiểm tra.
5) Cập nhật logic để filter và đồng bộ theo db mới thay vì call về db bf1 để check partner.

**Sheet tổng hợp user & phân quyền:** `https://docs.google.com/spreadsheets/d/1CnGtsaeFHdmeeYQnJRG40n18fMZGBWRMwdCcgG5roxQ/edit?gid=1087768421`

**Bảng tổng hợp**

| Công ty/Sheet | Bắt buộc | Token | DB Server | DB Name | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| Bee HCM (BEEHCM) | Bắt buộc (VN) | Có (chung) | of1.beelogistics.com:34541 | BEE_DB | Chung 1 token |
| Bee Đà Nẵng (BEEDAD) | Bắt buộc (VN) | Có (chung) | of1.beelogistics.com:34541 | BEE_DB | Chung 1 token |
| Bee Hà Nội (BEEHAN) | Bắt buộc (VN) | Có (chung) | of1.beelogistics.com:34541 | BEE_DB | Chung 1 token |
| Bee Hải Phòng (BEEHPH) | Bắt buộc (VN) | Có (chung) | of1.beelogistics.com:34541 | BEE_DB | Chung 1 token |
| Corp (CORP) | Bắt buộc (VN) | Có (chung) | of1.beelogistics.com:34541 | BEE_DB | Chung 1 token |
| EF India (INDIA) | Bắt buộc | Có (riêng) | ind.openfreightone.com:34541 | BEEINDIA | CRM bắt buộc |
| Bee SCS (BEE SCS) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | BEESCS_DB | |
| PAC (PAC) | Bắt buộc | Có (riêng) | of1.beelogistics.com:34541 | PAC_DB | |
| Bee Distribution (BEE DISTRI) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | BEEDIS_DB | |
| Bee Trans (BEE TRNS) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | TRN_DB | |
| Bee Project (BEE PROJ) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | BEEPROJ_DB | |
| Bond (Bond) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | BOND_DB | |
| Hàng Hải (Hàng Hải) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | HANGHAI_DB | |
| HPS (HPS) | Bắt buộc | Có (riêng) | hpsvn.openfreightone.com:34541 | HPS_DB | |
| PROS (PROS) | Bắt buộc | Có (riêng) | pros.openfreightone.com:34541 | PROS_DB | |
| Thủ Đô (Thủ Đô) | Bắt buộc | Có (riêng) | hpsvn.openfreightone.com:34541 | TD_DB | |
| Tiến Đạt (Tiến Đạt) | Bắt buộc | Có (riêng) | hpsvn.openfreightone.com:34541 | TIENDAT_DB | |
| Indonesia (INDO) | Theo yêu cầu | Có (riêng) | hpsvn.openfreightone.com:34541 | INDO_DB | |
| Cambodia (CAM) | Theo yêu cầu | Có (riêng) | pnh.beelogistics.com:34541 | BEECAM_DB | |
| Myanmar/Yangon (MYANMAR) | Theo yêu cầu | Có (riêng) | pnh.beelogistics.com:34541 | BEERGN_DB | Bee RGN |
| Malaysia (MY) | Theo yêu cầu | Có (riêng) | of1.beelogistics.com:34541 | MY_DB | |
| Laos (LAOS) | Theo yêu cầu | Có (riêng) | pros.openfreightone.com:34541 | LAOS_DB | |
| Philippines (PH) | Theo yêu cầu | Không |  |  | |
| Japan (JP) | Theo yêu cầu | Không |  |  | |
| Thailand (TH) | Theo yêu cầu | Không |  |  | |
| Taiwan (TW) | Theo yêu cầu | Không |  |  | |
| Singapore (SIN) | Theo yêu cầu | Không |  |  | |
| China (CNC-CN) | Theo yêu cầu | Có (riêng) | las.openfreightone.com:34541 | BEECN_DB | |
| OCL USA (OCL USA) | Theo yêu cầu | Có (riêng) | las.openfreightone.com:34541 | OCL_US_DB | |
| OCL Korea (OCL KR) | Theo yêu cầu | Không |  |  | |
| OCL Australia (OCL_AU) | Theo yêu cầu | Không |  |  | |
| Germany (DE) | Theo yêu cầu | Không |  |  | |
| TEL (TEL) | Theo yêu cầu | Không |  |  | |
