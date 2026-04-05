# 🔧 Nhật - Enhance / Maintenance Code - Week 2

> Notion ID: `2e2f924d5d7b80808445cc5e6de3736f`
> Parent: Tasks Database → Status: Doing (Current Week)
> Synced: 2026-04-05


### Enhance màn hình Lead/ Agent Potential  [DONE]
*(screenshot)*
Nút bị vỡ, bỏ check tax code nếu là màn hình HD. Bỏ luôn show 2000 records
Nút Request Customer: check để block không cho user click khi ko tích đúng 1 record trên bảng.
Remove nút check tax code ở Lead List

### Phân quyền Reports  [DONE]
```shell
crm-admin-report, crm-report, crm-sale-report, crm-pricing-report, crm-bd-report

Performance Overview: ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
Sales Performance:    ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
Sales Activities:     ['crm-admin-report', 'crm-report']
Sales Dashboard:      ['crm-admin-report', 'crm-sale-report']
Pricing Dashboard:    ['crm-admin-report', 'crm-pricing-report']
Salesman Tracker:     ['crm-admin-report', 'crm-report']
Quotation Summaries:  ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
Quotation Details:    ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
Quotation Partners:   ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
Quotation Markets:    ['crm-admin-report', 'crm-sale-report', 'crm-bd-report']
Pricing Performance:  ['crm-admin-report', 'crm-pricing-report']
Agent Transactions:   ['crm-admin-report', 'crm-bd-report']
Agency Agreements:    ['crm-admin-report', 'crm-bd-report']
Annual Conferences:   ['crm-admin-report', 'crm-bd-report']
N. Membership Fees:   ['crm-admin-report', 'crm-bd-report']
BD Reports:           ['crm-admin-report']
```
*(screenshot)*
Tạo, cập nhật thêm app feature: crm-report (report chung), crm-sale-report (SALE_FREEHAND), crm-bd-report (SALE AGENT,AMN), crm-admin-report, crm-pricing-report (CRM PRICE). 
Viết script, cập nhật phân quyền cho users vào báo cáo đó tương ứng. Review lại code ui báo cáo report manager. 
Account dan, a Quý, a Vinh, a Tuấn, a Henry mặc định vào all báo cáo. 
#### Script
```shell
server:migrate:run --script company/InitAppFeatures.groovy --company bee
server:migrate:run --script crm/MigrateUserAppFeature.groovy --company bee
```

### Tạo Asset cho HPH  [DONE]
*(screenshot)*

### Cập nhật lại phần approve partner.  [DONE]
update để cho phép nhiều người cùng có quyền approve trên 1 request.
Thêm field requestedCompanyBranchCode vào partner_request
Lúc tạo request khoan hãy set approve account id, set sau khi được approve. 
Mail request, gửi cho user được phân quyền COMPANY_ONLY + GROUP_ALL có companyBranchCode giống với người request
Bỏ thông tin người approve trong mail request partner, chỉ để trong mail lúc approve. 
Màn hình PartnerRequest query filter theo companyBranchCode của client(COPMANY_ONLY), hiện hết(GROUP_ALL)
Script:
```shell
ALTER TABLE lgc_forwarder_partner_request 
ADD request_by_company_branch_code varchar(255) DEFAULT '' NOT NULL;

UPDATE lgc_forwarder_partner_request req
SET request_by_company_branch_code = (
	SELECT role.company_branch_code
	FROM lgc_forwarder_crm_user_roles role
	WHERE role.account_id = req.request_by_account_id 
)

```
…

### Export thông tin book xe theo thời gian ra file excel.  [DONE]
review để các thông tin cần thiết.
*(screenshot)*
Để thêm tab các tasks booking xe, lịch họp dạng bảng ở đây, để thêm nút export để xuất dữ liệu, ko sửa bên màn hình booking xe (calendar)

### Export bảng giá   [DONE]
#### Attach vào mail rồi gửi cho user sau khi click Export, nếu gửi mail failed ~~⇒ download thẳng file excel thay vì popup màn hình export options.~~

#### cc mail cho a Vinh, có CRM User role mới export được. Còn không thì ko export được. 

#### Thêm cơ chế cho phép moderator của app export trực tiếp không qua mail. 

### Check lỗi gọi cron, sync cho task đổi status to complete.  [DONE]
*(screenshot)*
- Thêm zalo message cho Đàn để monitor, nhớ note/ comment để sau bỏ đi.

### Check lỗi unit này cho a Minh  [DONE]
filter data unit from bee_legacy
*(screenshot)*

### Agent Transaction: để thêm các cột revenue/ profit.   [DONE]
check BD report app quyền moderator mới xem được revenue/ profit.

### Ở crm user role export cái api để call lấy thông tin crm user role.  [DONE]
Từ logic lịch họp, call api từ crm user role để lấy thông tin Work Place, show lên trước subject mail [Car Request] - [BEE - Hải Dương] - Người request: ....
dựa vào work place để xác định gửi mail approval

### gọi Api với bee_legacy để update thông tin partner   [DONE]
*(screenshot)*
#### script
```shell
server:migrate:run --script crm/UpdateIntegratedPartner.groovy --company bee
```

- code script để sync toàn bộ data partner từ cloud qua bee legacy.

### Update lại thông tin legacy_db.integrated_partner  [DONE]
bổ sung các field còn thiếu theo CRMPartner
```sql
-- Contact information
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS position VARCHAR(255);

-- VIP Contact information fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS vip_contact VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS vip_position VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS vip_cellphone VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS vip_email VARCHAR(255);

-- Business information fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS investment_origin VARCHAR(255);

-- Location information fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS province_label VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS kcn_code VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS kcn_label VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS work_address TEXT;

-- Bank information fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS bank_accs_no VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS bank_name TEXT;
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS bank_account VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS bank_currency VARCHAR(50);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS bank_address TEXT;
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS swift_code VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS print_custom_confirm_bill_info TEXT;

-- Notes and messages fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS warning_message TEXT;
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS suggestion TEXT;

-- Request information fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS request_by_username VARCHAR(255);
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS request_by_full_name VARCHAR(255);

ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS input_full_name VARCHAR(255);

-- Group information fields
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS bfsone_group_id INTEGER;
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS group_name VARCHAR(255);

-- Partner Reference, Common values: "BEE_VN", "BEE_INDIA", "BEE_SHA", "BEE_GLOBAL"
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS partner_source VARCHAR(255);

-- Other flags
ALTER TABLE integrated_partner ADD COLUMN IF NOT EXISTS is_refund BOOLEAN DEFAULT FALSE;

```

---

- Thêm Pricing Branch (VP Pricing xử lý inquiry này)
- Mặc định sales VP nào gửi cho Pricing văn phòng đó. 
- Thêm message confirm hỏi trước khi gửi, hỏi sales xem có phải muốn gửi cho [Pricing HPH] hay không? 

```sql
ALTER TABLE public.lgc_price_inquiry_request ADD pricing_company_branch_code varchar NULL;
ALTER TABLE public.lgc_price_inquiry_request ADD pricing_company_branch_name varchar NULL;

UPDATE public.lgc_price_inquiry_request req
SET
    pricing_company_branch_code = role.company_branch_code,
    pricing_company_branch_name = role.company_branch_name
FROM lgc_forwarder_crm_user_roles role
WHERE role.account_id = req.pricing_account_id;

UPDATE public.lgc_price_inquiry_request req
SET
    pricing_company_branch_code = role.company_branch_code,
    pricing_company_branch_name = role.company_branch_name
FROM lgc_forwarder_crm_user_roles role
WHERE req.pricing_company_branch_code IS NULL
  AND role.account_id = req.saleman_account_id;

```

*(screenshot)*

*(screenshot)*

---

*(screenshot)*

#### script
```sql
DROP TABLE public.lgc_forwarder_crm_agency_agreement_follow_up;
DROP TABLE public.lgc_forwarder_crm_network_membership_fee;
DROP TABLE public.lgc_forwarder_crm_annual_conference;
```

*(screenshot)*

script: 
```sql
server:migrate:run --script company/DeleteEmployees.groovy --company bee
```

### Bổ sung api Token cho các văn phòng lên postman  [DONE]
**Server1: pros.openfreightone.com,34541**
- **Bee trans**
DBName: TRN_DB
Token: Cv4XzDuxGD1y4DQhtavGckTeliVRckT3Z1NL4B0WATm13yghaLU1A7pFjc7zMXcb7MdMvGQkwtVekJavtT0zTvdN9gRmGk+TDzcaBV0cMn59wzfzxACLStPvC+dVuLXsAWiH5i1YWLmdWVOQPRY+mU0c0RlrlGL95DYtXrH0QFplnKL71VHiaoeabmFCbCi8Kk0Ya0Y5Cl+ZX+904IoYCgQeJY6NEt9Y5cVG/ucLnL21M8ZV+FTsFj/n1uSqHN/qp6qcUO/xrmXYmSfgCT7I9YhhplRqRC3mzcGQXOGkx1BNOLIFySFCPhfHawI2TEw/iY4xE6ZT1fmqXTS7Wv/tqQ==
- **Bee distr**
DBName: BEEDIS_DB
Token: i57fNyr+fdDSWSXLOWts/JpHPuNMo1BO6WDargulqlhF/yE2ANgdquIPwq1fl+8XM4uPhaBp+4tQCrGI8Gl61l3/52igjmpuJXvuDb8V2bc78U9QhKIb7C4r2a92T/CORhoxslqUY5Fs8UzCBa7BG3VNBqLoQyBGH9y/BytfAr6kvIcZOzFyUB7VTc0XEVNFIt5bdtxcoDhypTvhTVmRDcVYBgOtW6Rm7IESWfyOc5LiPsnRU3NbLD6B7nghxyyTaIU5zWWdr1uu/kerktUi7BfD1s1f/i0xscDC3OsDe8+lQ16AZnSqNB2/o716Ww+rdvPaF20zkqwGsOKCDfJhdQ==
- **Bee proj**
DBName: BEEPROJ_DB
Token: rhpU+V2W2tHmrDcQioN1YW0xkEQl+fC3Vg2Jp0W0yPMQseHyJmxSwCFgq3yU3GMskVd89xhYtJ0E3tIt3W3RBcnDoF3F8TaqG+URr9kFgTlc3wywRN6gs7By/VijFePrR9nLSJDJsELh85qh58A7z1dHFacZf1AgFWJnZK6pdSrhnNWSWaJvQPo2xhtXbTlyVrXs9VHc8DCizf+bItqXo2VM2FJ5SCH7Q8jtB8AAD/Lz0UeJC1p/U/6uOGjItv6rNFvoeXCua9XODxGT7YEsr/QwrXif3JSs33O++Yy3av4DUJ2bRA/iMzmyt4xnchYvXgyqGpa++RNdJ+6ZFA23tg==
- **Beescs**
DBName: BEESCS_DB
Token: ly9VrOFY6NNt9Iq5ZZDdEoqnKy38Nlcwnu3Hfrm6PK4vJEyeC8eKTesyGFeeaKz4HoX1VIfFtZQmVwUbE8nkcPVZm/3y0MlrVLvJxDXz9rcmsTL4n5PUP7VbLomNbKiRrnyJRFAsDbKeHJAenI3x3X4W/p989XnsER755pZeG3pz5D0/UNvznMyOOa8+5FRcj+/Lc+zVtQUUGNQSXzusnx9wF2vFohstX5/1UQrUM7mM16QFoTE3i2FW8g+RAmtpOG1fIVGMXQH0AlMwvC2P2pelLHn5iApkCunbphUJjuGTg+MSGFK1pECZQP47TURPmkLGvofJkZ09c2YLfTrKwA==
- **Bee lào**
DBName: LAOS_DB
Token: I4dS4VVSlIIZrCKkKI+fq2pdvx7PjPp+vzm151SPff4AQaRXug0lRyGyncC06omnHjmQ/zz74mf7aEeSJkdCieI992hWceQzHffYq4aHsI1mVtsb2Td07/CM2VJn3jzaoGIzoYZOgKybLgmLWYjc8W+gvP+U+Bu7rcrH2qZnDcdRTa5Z9hx8+eVlZZUgbByXr2rjEXRryGKU9d89A7tdmmvA5TU7AnMPgyV698UkV+Gup0QFFWShJCQdRMD+K1FsQ0RHvvGCsM823RmH9ZOYGz6kkpaxk60LSKpyh5wE5REjmiyukr1deCCuW6bYJhHCXCpa6ihEwphy4IiY493jzg==
- **Bond**
DBName: BOND_DB
Token: Zvb1jcmEYqIuRg6xQEpiIgc4avGTpyWCOLNPdJJyizGFbLBtb7JvB+gu863pPcRY5ACSRHfIgc5H/mVJngCOjQdTWY5Ax4Cr5NkoDmrFNdyObBr+sc6d2yWY4i2RSzHlpk4+Un1P0V2lso2yMat3C00FuExGI8ZYkwnciiR7XLSfMzROCmSm9+ZE8RqvA2bnOGu0qC/bAKDVxsru7XFhOgNnPoSr32C6MKpbikKmzTwKPN27nkkugZekmyO6zu7JCGWEMt9x00mHKoOtiqkSaX4OZ6hRULRXQi69N4XNCGRN4BfdCaY0QeeMI8QsBoBBZYhl8f5H8yp5sZUbB9rdKQ==
- **Hang hải**
DBName: HANGHAI_DB
Token: NJQG7Z+oFudq89c2/nW3Vo1JjXdWtygOs9FcbzBBY5ALqk2yQSyYocTNy/fMIQNLG6iPOwnbmXx3qyoyP+8eCoWIDpmgh0JgUy122zUciP3jaI2/mG6BJYKow0e5B91GwdWemEhm891QSeYPoAZ1OG024p5pgKjB4ngNG9i01huuZgtUymihiMEgIgSrVe9rkXc9QtehWDX/mQJrkqeQzCOQ/9P/iCzLhQ0ytHOUpQLZY3zJJ5ovo3dQfaITbZ4dNbysl/kdzkT5HxNsNiT8y+yCOndzypKe/eJwqRb3jLnghnup9thUOqyfvaUHkUiOC9a0ctokhqhhc1CE8vGtEg==
- **Pros**
DBName: PROS_DB
Token: a0GBcktpFO2w5lFVWC6pvolUaV1OcALYJKs2aEDnoGAY1LkMoaRwL7PXDDG5f2hzgzzFNbKKxgcJ991cohW4q3oo5JV7EJ8ElZeoHdCfM6Ys1eNIkzQWDaJN1afzmyRIP5QhPbEMzwU/onHtSwVXAVj2aDxJib1iZ/Dnr4XKYv3Q6M9RN3ZGPQnKiGA3EXpkPnm5B9xO2VfxtMx9HmBhvhKCHwpZ6yv9uyXyhQclJXnnUcYLftqMJRsLTO8aQQsNycvdKOcuTtpsPirDxxoAF8vYD7/pOdrsMCh+Fm5B61fu9e1TgA1xRzCaJQAM36QV6Bk27OXlnFqgTnqPdZJHbw==
**Server2: hpsvn.openfreightone.com,34541**
- **HPS**
DBName: HPS_DB
Token: f0J5sVH6mRyxc4obkfEgjFPJe8GAMAAuA0qLrsQWl7jrOF5SYNOQ+SmPX9hxbNrGZzbcYF9twLA96gdY0/vpTSrv3fEwHOH0GTDPf3APa7rz80amEXWvWZS1D0Gmjk2WuE459nN1mXYasW3kWR3C8HgGFu7R8yIIQ8OegN5XwCb40Ur0UU1fGB7Ie2q4ThQ9eP5QCMCAuHwRRlu+UyqEA9k+doknJvaON1N9HRpCuAHYq+cwLhT45Rvci1uJBt8wpRYoFON4bignHIk3o1zAXbyXoHfxSrDs9qR9btbvOlmjGjuM5MX1QXRTk9LGgzlPT/xWT6l+UQRnOcL8mSabxg==
- **BEE INDO**
DBName: INDO_DB
Token: YgT7SNb5A1n4eCYce3AYyhEQW3LaEDQN9pM558oxvUOQVeLZOVmptpDXqUCOxptjtpZNbcXBe2yyrTVt42blUIqGMu0KPDiwSvn8f/ATjidRRH7t2A20/JDSEIwv/rUA5Ggs7XK49QXt+0HEd5pELaJc+ZPdQYDJmSESWmuJabdseQ6o2ZDheiIvmAQywVAqulWXZTvo8H+XsnZRDV9Z40ojuQKWrP9AEHYKgl1TqKdhV+c+gWcdGffDlnLVj8a01ha2o2/TcXlUsD6XMVYc4ekrMtt4NIG0BMdo3uIn4dWPVJquaMZAkljJW2CxGD+FmA2jOcL3RhtiK7ekfSiTbw==
- **THỦ ĐÔ**
DBName: TD_DB
Token: VjKSxUU1UivA4fuPgExAPh5PqG4pldQRd8hdG1oEdVGQfGlxfhpVkszlYDEbeMSWcv39o5UpqCOjHFBxS+04YwN3vMEZ4xn/adzn/P9DiJYNAWuFT20eErzUJevmnB5VaruEmymneK1jW3rCjr8vI+JsgidS2/hJ28iRuA+vTjVDCUuJwpkkyeTyJDaO0VPHcwM59gy691qKcsOyi+AzE6f+XAOY2KMEy4YefBdYmuyWfPBdPbjpg/IL6iwGHHdo4tQTXX5f7K4ZovbrxVDyVJy1Lm/95nu2fJB2c+itHks6uUugsZBTNqG0voRQHbGwIi3EuJx3r+dKpnI0FPP/+Q==
- **TIẾN ĐẠT**
DBName: TIENDAT_DB
Token: qRAoFHN/pMPhyEfzPPN9uYXluQAlogK1hIBkyKtlYLd1AuQ/aSFOPfbRhyVG8IbJVr1c4qrESVSD4N8VuYxtbNfZ9N718dQyQSYZg5wZjhSsUiz2pA/16v2a8Mx3NBK7RsggA1XjsC2LE7SU5vKIPYtulYgD2C6cgxiHdSC70Xd+Hbu/8egF5QVbHYJVDGFw+bhs89+5D5I86FPn2ja06LUQQ05MloMY19TDDFOJEQrfRRD6webUfMF95UJnJW1CKv3Y44nYtUGfP2kttDOfeQmkPZBxMp/SK+HdB70XFhr3EQvE2LaTvdOa/ycdN1v7OToMVlD87Vvxhpo5ouq/eQ==
**Server3: of1.beelogistics.com,34541**
- **PAC**
DBName: PAC_DB
Token: ScU4q73GkYzESueJCAyFKfDIc3GWUP8lrqSuI9e+J63+YTnM9ZNKZjummRA3qsc2EEOLrMpoVlnP8F/6WNVwnqQFkI96SCzLlsy2o/p+zr8QdN0R1XjvzjBVvPkzSb1G0TGm3HG5rB5LMCUrlAIClfDVjg9wMKyKgGnRL887GHJIikyODwfLhl5IOIg3sYeOt9yDXkN7scZJ4P248SIR+3AnWR5oLSTWTXD1smb96kQCYFBx137cdVNy6LvftD9xv2CUKIpjEYN1Un4p54/EN3rpfL8LAaIU8nfP1GXcVdqIgmonZSoYfNcyKNcuDlMJG/KUJyqs6+WY6do0ls4fgw==
- ** BEE MALAYSIA**
DBName: MY_DB
Token: AiJd/v5zKos3a7C7ZlT/ldVgirccxg6Kg/YI0ZCKNqeUJJYTn1PIH/eT3BSbEjG9zzsMcBsnxgdwn9j/LkwqCnMm4GkxOnOOBASwaI/oqSV3t/OqC/RAT0igpLIYveYIvsiXFo7FtyaQg9VciQz5k6m1O6izfw2ZLw3PIf2qtbIrVzcFCo4FtSMYK5dFZ3HVpTG1+vCB9815APFbf7vMoT69qmJeP+cGb94/lc/W0/mmJFdyRp82Ow7MkjENYohnrKwvYQcBaSsHb/lRNH7TiLylGl7j3EQZMRRctmPMfVimJuCnoeRa/SHg0/xbO5ASQaBZPnU34poAHJhEixhNHw==
**Server4: ind.openfreightone.com,34541**
- **BEE INDIA**
DBName: BEEINDIA
Token: QQ7wt4h2OopNs5d9GQjnWYR3z6H+FkIZVPNs2y77O1SQGxyzxwOwrn3UYEpNWWAzNuLWPN7SkrbPSyJe6nDitrUOiMDN+WP5wJLmta77366lf1BBkvCYH7RcfRiXqJ7h3q8b2DzsBuqV62GypL2A9a/93eCPJXU82Q9rQugk7w22EGuFVaTjnyBWyI9nwIImvpOn8/VKPDq94JlLTPQNuTyaSevQFN9iPRze7Op6o9Zk/3KZIpmDHcyBhE2GJVdVzkxCUvQj+hxpdp7KPnQ5ebQSYElcz7b9Y7LUFHAqrVXlZdRrpsuBFNvCn2yLJ/V3ldTaWHRRvEjhzgMFW1AlNg==
**Server5: pnh.beelogistics.com,34541**
- **BEE CAM**
DBName: BEECAM_DB
Token: TLBveOeB6HbJHfA3uSClssVSb5T8CTxt/fKl+Ab1lDj5m0VsK3csC7d3wgnE4w3n606kSfPyLpcvvedSP8hpAqfext7fiwfv3i/hbcMsCFG4xvpxdqd0bpkG2tBDcPO7pGpgxRuiXn+qIlsoPfFG+I+iJpxrfBXMGFH6QJ1aB+As+JQSnkPB2SQVDZuGIIfdZYvc5iz7PURO0x9smkb5MHiZ44FkjKnTAk/fXNyW4rf3qWmE5NVGXd6XwpLJlsvff6ZMCdelvessSlgVZCZ/6Ak8YdeDOl9uIYL2dUZq+3qRic94oaXRXwEGIlHZseRvyhq4R7hMGj49By8D4PX4rA==
- **BEE RGN**
DBName: BEERGN_DB
Token: T9ZBmoHlsxaooXctTDXm+OHYodTUESjcXbXUytFRHqLrR8kv4JcZmuvks1GPfLViS7XxpSUgO8T/V+e743LdfYFyB8d1PS3rvAyLobm7uSPyxN62G0n2Fwy/aPwLMrjdZ6ysHM421403i/YpvTjkNMGFJhZ8kKHxPg93AsdArKeylD+qEMqhOCUhUREZbVAVyKvNU/JCbzGn2sUu7UzPEbDznbdVuTfR9av0/spw8a837d8Yt3vyxq3vAzCQUGJOwxZn0kTmaOQ4WZgnHntuChRSLxzVnbun/HyE8ZnjlGnnOeEv6e41bWiJERKlDHK545sJb8e87jjEvS4+j89WWg==
**Server5: las.openfreightone.com,34541**
- **BEE CNC**
DBName: BEECN_DB
Token: fITcv++OgXVz7bL2PdnrDgqrfftciHJAD1uJYP/aNvrm5LR//1EIN/G8oNqLJwQ+SJ6ge3dSEsNZ6YoyhKaINWPuBAYwsMNh2dAsp2xhI27D6EbQof9WfNuqosUAVjepKAsosrgsX0dvxPb9OkgXL9MTVcfJBycrsVJAuJFv2aICicYXQ73PMstn95aCxbXxqDQlFqhyxjv0hi79ECSWn7yFCfe2QY1fjOYmF6rUqcRl7O7BZJrQG4uUg77ugxqrFaSAo2mt6FvTLvXZ/DMRhSrPbWqzdg6Oq5MLQoumxnG8+4h8AzmB+7V974mzvLSpHnGubWsiygoOQB2ETKDiLg==

- **OCL USA**
DBName: OCL_US_DB
Token: NTummM/6croUwbThl09BelUrUDfyC6nZFL46H4xcv/DeLiq1s/W1d+NIiG3Lr5TxCIxuoZXsY2cWvn05qDvfImvfybLg056v1myDXY9DbWDcnkHxAsfGT8tQZkbe+x+9IbrvNofPB2uXDIX5zONPx+h+/JfHSzzsDXFOHBddfjgyozZ5tHwSM1hN4/6O26FnKOU8gF4i+lJpc6DGsYulzFc+e1hFOk+ckxXAglXr2iRGQJSYbgv5eRBaIcFttUJZOMVkggirQMqaq3BxrXIWZllev+OGt1/ExMT93RdI53+blzuIYYJW5xUwCM5AmP1iEtxOkra7jRI1A1G85IwMXQ==
<file src="file://%7B%22source%22%3A%22attachment%3A970e5172-8be2-42cc-b44e-86419fe7dce0%3AAPI_Connection_Info.docx%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%222f4f924d-5d7b-807e-be82-f9ea667d3182%22%2C%22spaceId%22%3A%22b89c32cd-d948-497f-b7e9-6aeaf9dacf6e%22%7D%7D"></file>

---

### Check báo giá cho a Minh (ưu tiên sau)
<unknown url="https://www.notion.so/2e2f924d5d7b80808445cc5e6de3736f#2f0f924d5d7b8049b9b4d4d8281c5908" alt="embed"/>

*(screenshot)*

### Đọc chat, break vấn đề, lên giải pháp, note lại review với trước khi làm. (ưu tiên sau)
*(screenshot)*
- Đặt vấn đề:
- **Sales** nhận yêu cầu từ khách: "Check giá 1 lô hàng từ HPH đến **3 destinations**: SHA, BIJ, NGB"
- **Hiện tại:** Sales phải tạo **3 inquiry riêng** → mất thời gian
- **Nếu gộp 1 inquiry:** Pricing không tính được KPI (1 inquiry nhưng phải làm 3 đầu việc)
⇒ Vấn đề:
- **Sales: Tốn công tạo nhiều inquiry cho cùng 1 request của khách**
- **Pricing: Không đếm đủ số lượng công việc thực tế → KPI sai**
- **System**: Không có cơ chế link các inquiry cùng nguồn gốc
- **Report: Đếm trùng khi tính theo khách hàng/lead**
- Giải pháp triển khai:
-

### New task from CEO
### Yêu cầu từ CEO (CRM - Bee Group)
- **Mục tiêu:** Check partners toàn hệ thống để chống xung đột sales list.
- **Mục 1 (deadline 2026-02-14):** CRM hiển thị data partners toàn bộ công ty; check chéo 2 chiều.
- **Mục 2:** Triển khai CRM cho toàn bộ công ty thành viên (VN bắt buộc; nước ngoài theo yêu cầu).
Danh sách chi tiết ở **Bảng tổng hợp**.
**Deadline mục 2 2026-01-30**
### Việc cần làm
1. Tạo toàn bộ công ty lên cloud.
2. Rà soát, tạo account cho toàn bộ công ty bắt buộc theo bảng ở dưới.
3. Gửi danh sách account riêng của từng công ty cho anh Vinh.
4. Xác nhận phạm vi dữ liệu partners + cơ chế check toàn hệ thống.
5. Sync dữ liệu về DB `crm`/`bee_legacy_db` và kiểm tra.
6. Cập nhật logic để filter và đồng bộ theo db mới thay vì call về db bf1 để check partner.
**Sheet tổng hợp user & phân quyền:** `https://docs.google.com/spreadsheets/d/1CnGtsaeFHdmeeYQnJRG40n18fMZGBWRMwdCcgG5roxQ/edit?gid=1087768421`
#### **Bảng tổng hợp**
<table header-row="true">
<colgroup>
<col>
<col>
<col>
<col width="236.9296875">
<col>
<col>
</colgroup>
<tr>
<td>Công ty/Sheet</td>
<td>Bắt buộc</td>
<td>Token</td>
<td>DB Server</td>
<td>DB Name</td>
<td>Ghi chú</td>
</tr>
<tr>
<td>Bee HCM (BEEHCM)</td>
<td>Bắt buộc (VN)</td>
<td>Có (chung)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>BEE_DB</td>
<td>Chung 1 token</td>
</tr>
<tr>
<td>Bee Đà Nẵng (BEEDAD)</td>
<td>Bắt buộc (VN)</td>
<td>Có (chung)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>BEE_DB</td>
<td>Chung 1 token</td>
</tr>
<tr>
<td>Bee Hà Nội (BEEHAN)</td>
<td>Bắt buộc (VN)</td>
<td>Có (chung)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>BEE_DB</td>
<td>Chung 1 token</td>
</tr>
<tr>
<td>Bee Hải Phòng (BEEHPH)</td>
<td>Bắt buộc (VN)</td>
<td>Có (chung)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>BEE_DB</td>
<td>Chung 1 token</td>
</tr>
<tr>
<td>Corp (CORP)</td>
<td>Bắt buộc (VN)</td>
<td>Có (chung)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>BEE_DB</td>
<td>Chung 1 token</td>
</tr>
<tr>
<td>EF India (INDIA)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[ind.openfreightone.com:34541](http://ind.openfreightone.com:34541/)</td>
<td>BEEINDIA</td>
<td>CRM bắt buộc</td>
</tr>
<tr>
<td>Bee SCS (BEE SCS)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>BEESCS_DB</td>
<td></td>
</tr>
<tr>
<td>PAC (PAC)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>PAC_DB</td>
<td></td>
</tr>
<tr>
<td>Bee Distribution (BEE DISTRI)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>BEEDIS_DB</td>
<td></td>
</tr>
<tr>
<td>Bee Trans (BEE TRNS)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>TRN_DB</td>
<td></td>
</tr>
<tr>
<td>Bee Project (BEE PROJ)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>BEEPROJ_DB</td>
<td></td>
</tr>
<tr>
<td>Bond (Bond)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>BOND_DB</td>
<td></td>
</tr>
<tr>
<td>Hàng Hải (Hàng Hải)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>HANGHAI_DB</td>
<td></td>
</tr>
<tr>
<td>HPS (HPS)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/)</td>
<td>HPS_DB</td>
<td></td>
</tr>
<tr>
<td>PROS (PROS)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>PROS_DB</td>
<td></td>
</tr>
<tr>
<td>Thủ Đô (Thủ Đô)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/)</td>
<td>TD_DB</td>
<td></td>
</tr>
<tr>
<td>Tiến Đạt (Tiến Đạt)</td>
<td>Bắt buộc</td>
<td>Có (riêng)</td>
<td>[hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/)</td>
<td>TIENDAT_DB</td>
<td></td>
</tr>
<tr>
<td>Indonesia (INDO)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[hpsvn.openfreightone.com:34541](http://hpsvn.openfreightone.com:34541/)</td>
<td>INDO_DB</td>
<td></td>
</tr>
<tr>
<td>Cambodia (CAM)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[pnh.beelogistics.com:34541](http://pnh.beelogistics.com:34541/)</td>
<td>BEECAM_DB</td>
<td></td>
</tr>
<tr>
<td>Myanmar/Yangon (MYANMAR)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[pnh.beelogistics.com:34541](http://pnh.beelogistics.com:34541/)</td>
<td>BEERGN_DB</td>
<td>Bee RGN</td>
</tr>
<tr>
<td>Malaysia (MY)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[of1.beelogistics.com:34541](http://of1.beelogistics.com:34541/)</td>
<td>MY_DB</td>
<td></td>
</tr>
<tr>
<td>Laos (LAOS)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[pros.openfreightone.com:34541](http://pros.openfreightone.com:34541/)</td>
<td>LAOS_DB</td>
<td></td>
</tr>
<tr>
<td>Philippines (PH)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Japan (JP)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Thailand (TH)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Taiwan (TW)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Singapore (SIN)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>China (CNC-CN)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[las.openfreightone.com:34541](http://las.openfreightone.com:34541/)</td>
<td>BEECN_DB</td>
<td></td>
</tr>
<tr>
<td>OCL USA (OCL USA)</td>
<td>Theo yêu cầu</td>
<td>Có (riêng)</td>
<td>[las.openfreightone.com:34541](http://las.openfreightone.com:34541/)</td>
<td>OCL_US_DB</td>
<td></td>
</tr>
<tr>
<td>OCL Korea (OCL KR)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>OCL Australia (OCL_AU)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Germany (DE)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>TEL (TEL)</td>
<td>Theo yêu cầu</td>
<td>Không</td>
<td></td>
<td></td>
<td></td>
</tr>
</table>

**Hiện trạng:**
- Dữ liệu Partner BFS1 lưu tại **database riêng của từng công ty**
- Database Cloud chỉ có dữ liệu Partner của **VN và India**
- Database `crm/bee_legacy_db` chỉ có dữ liệu Partner **VN**
- Data Partner đang được đồng bộ hàng ngày từ BFS1 → Cloud → `crm/bee_legacy_db`
**Vấn đề:**
- Dữ liệu Partner **chưa tập trung**, khó quản lý
- Logic kiểm tra Partner **truy vấn trực tiếp vào BFS1**, chỉ hoạt động với công ty VN
- Dữ liệu **hiển thị** (từ Cloud) và dữ liệu **kiểm tra** (từ BFS1) **không đồng nhất**
- Thiếu cơ chế phân biệt Partner thuộc công ty nào trong `bee_legacy_db`
**Việc cần làm:**
- Đồng bộ dữ liệu toàn hệ thống
- Sync data Partner từ BFS1 → Cloud cho **tất cả công ty**
- Thiết lập sync Cloud → `bee_legacy_db` cho **tất cả công ty**
- Bổ sung cơ chế phân biệt công ty cho `bee_legacy_db` : thêm cột `partner_source` vào bảng partner để xác định công ty
- Cập nhật logic Check Partner Exist: query `bee_legacy_db` thay vì bfs1

### Clean data, code  [DONE]
#### Bảng thừa → drop 
*(screenshot)*

#### script `datatp_crm_db`:
```powershell
DROP TABLE public.forwarder_sales_daily_task;
ALTER TABLE public.crm_user_task_access_control RENAME COLUMN notes TO note;

```

### Bổ sung field continent cho CRMPartner, enhance code sync integrated_partner  [DONE]
migrate lại continent cho CRMPartner, khi tạo partner set continent theo country

### Review lại báo cáo Pricing Dashboard, số liệu giữa view quản lý và cá nhân lệch nhau  [DONE]
#### Số liệu bị lệch do pricing_company_branch_code chưa đúng lúc sale chọn target pricing company khi gửi request ⇒ migrate dữ liệu

#### Thêm target pricing company branch vào subject khi gửi mail để pricing reject khi sale gửi nhầm company

### Review lại Partner request, đảm bảo logic async vs sync đều chạy đúng  [DONE]

---