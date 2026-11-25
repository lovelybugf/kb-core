---
title: Danh mục tag dùng chung
tags: [standard, kb-meta, reference]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Đây là danh mục tag duy nhất được phép dùng trong mọi kho kb-*, mỗi tag định nghĩa trên một dòng gạch đầu dòng bắt đầu bằng tag trong dấu backtick. Công cụ `kb_lint.py` đọc trực tiếp file này, tag không có ở đây bị báo lỗi.

## Quy tắc

- Mỗi trang 1–6 tag: nên có đúng 1 tag loại trang + 1–5 tag chủ đề.
- Thêm tag: thêm một dòng vào đúng nhóm (giữ thứ tự chữ cái), commit kb-core trước rồi mới dùng ở kho khác.
- Không tạo tag đồng nghĩa với tag đã có; không tạo tag cho một trang duy nhất.
- Dòng định nghĩa tag có dạng: gạch đầu dòng, tag trong backtick, gạch ngang dài, mô tả. Dòng khác trong file không được bắt đầu theo dạng đó.

## Loại trang

- `concept` — giải thích khái niệm, nguyên lý hoạt động.
- `decision` — ghi nhận quyết định (decision record).
- `howto` — hướng dẫn làm một việc cụ thể.
- `reference` — tra cứu: bảng tham số, lệnh, schema dữ liệu.
- `runbook` — quy trình vận hành từng bước, có kiểm tra và rollback.
- `standard` — chuẩn, quy ước bắt buộc.
- `troubleshooting` — triệu chứng → nguyên nhân → cách xử lý.

## Vận hành kho tri thức

- `claude` — dùng kho với Claude (Projects, Claude Code, API).
- `kb-meta` — cách tổ chức và quy ước của hệ thống kho.
- `kb-tooling` — script hỗ trợ kho (lint, index, tạo trang).
- `process` — quy trình làm việc (ingest, review).

## Nền tảng DevOps

- `argocd` — Argo CD.
- `cicd` — pipeline build/test/deploy.
- `cloud` — điện toán đám mây nói chung.
- `container` — container nói chung (runtime, vòng đời).
- `container-image` — image: build, tag, digest, layer.
- `docker` — Docker Engine/CLI.
- `flux` — Flux CD.
- `git` — Git và quy trình làm việc với Git.
- `gitops` — mô hình GitOps.
- `iam` — định danh và phân quyền.
- `kubernetes` — Kubernetes upstream.
- `linux` — hệ điều hành Linux nói chung.
- `lvm` — Logical Volume Manager.
- `networking` — mạng: subnet, routing, DNS, firewall.
- `podman` — Podman, Buildah, Skopeo.
- `registry` — container registry.
- `security` — bảo mật, hardening.
- `storage` — lưu trữ: disk, filesystem, volume.
- `systemd` — systemd, unit, journal.
- `windows` — Windows: PowerShell, Office COM, Task Scheduler.

## Red Hat

- `aap` — Red Hat Ansible Automation Platform.
- `activation-key` — Activation Key của Satellite.
- `ansible` — Ansible (playbook, role, collection).
- `authentication` — xác thực người dùng: LDAP, AD, IdM, SSO.
- `backup` — sao lưu, khôi phục, khắc phục thảm hoạ.
- `capsule` — Capsule Server.
- `certificate` — chứng chỉ SSL/TLS, CA.
- `compliance` — tuân thủ bảo mật, OpenSCAP.
- `content-view` — Content View, Lifecycle Environment, promote/publish.
- `download-policy` — download policy của repository (immediate, on_demand, ...).
- `errata` — errata, vá lỗi bảo mật (RHSA/RHBA/RHEA).
- `hammer` — Hammer CLI.
- `idm` — Red Hat Identity Management (IdM/FreeIPA).
- `installation` — cài đặt sản phẩm.
- `lightspeed` — Red Hat Lightspeed (tên mới của Red Hat Insights).
- `monitoring` — giám sát, health check, log, thông báo.
- `ocp` — Red Hat OpenShift Container Platform.
- `performance` — sizing, tuning hiệu năng.
- `provisioning` — cấp phát máy: PXE, boot disk, kickstart, compute resource.
- `pulp` — Pulp, lưu trữ nội dung trong `/var/lib/pulp`.
- `registration` — đăng ký host, subscription-manager.
- `remote-execution` — chạy job từ xa (REX, SSH, pull mode).
- `rhel` — Red Hat Enterprise Linux.
- `satellite` — Red Hat Satellite.
- `upgrade` — nâng cấp phiên bản sản phẩm hoặc hệ điều hành.
- `virt-who` — virt-who, subscription cho máy ảo.

## Thị trường Việt Nam

- `data-schema` — mô tả cột, đơn vị, múi giờ của file dữ liệu.
- `data-source` — nguồn dữ liệu, điều khoản sử dụng.
- `gold` — giá vàng (SJC, thế giới).
- `market-event` — sự kiện thị trường.
- `market-vn` — thị trường tài chính Việt Nam nói chung.
- `stock` — cổ phiếu, mã chứng khoán.
- `stock-index` — chỉ số thị trường (VN-Index, HNX-Index).

## Liên quan

- [Quy tắc đặt tên](naming.md) · [Frontmatter](frontmatter.md)
