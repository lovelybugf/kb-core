---
title: {{title}}
tags: [{{tags}}]
product: {{product}}
source: {{source}}
reliability: unverified
updated: {{date}}
owner: {{owner}}
---
**TL;DR:** {{Runbook này làm gì, mất bao lâu, có gián đoạn dịch vụ không.}}

## Phạm vi và điều kiện

- Áp dụng cho: {{sản phẩm, phiên bản, môi trường}}
- Quyền cần có: {{root / tài khoản Satellite có role ...}}
- Thời gian dự kiến: {{...}} · Gián đoạn: {{có/không}}
- Điều kiện trước: {{backup/snapshot đã có, cửa sổ bảo trì đã duyệt, ...}}

## Kiểm tra trước

```bash
{{lệnh kiểm tra hiện trạng}}
```

Kết quả mong đợi: {{...}}

## Các bước

### Bước 1 — {{tên bước}}

```bash
{{lệnh}}
```

Kiểm tra: {{lệnh/điều kiện xác nhận bước đã xong}}

### Bước 2 — {{tên bước}}

```bash
{{lệnh}}
```

Kiểm tra: {{...}}

## Kiểm tra sau

```bash
{{lệnh xác nhận hệ thống hoạt động bình thường}}
```

## Rollback

{{Khi nào rollback, các bước đảo ngược, dữ liệu nào không khôi phục được.}}

```bash
{{lệnh rollback}}
```

## Liên quan

- [{{Tiêu đề}}]({{duong-dan.md}})

## Nguồn

- {{Tên tài liệu, phiên bản, chương/mục}} — {{URL}}
