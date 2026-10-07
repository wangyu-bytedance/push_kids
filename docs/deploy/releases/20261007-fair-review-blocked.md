# 2026-10-07 公平复习服务端发布准备 — BLOCKED

- Code commit: `207f59b` (`feat: balance review subjects and waiting priority`)
- Approved scope: `SPEC-20261007-FAIR-REVIEW-01 / ARCH-20261007-FAIR-REVIEW-01`
- Target: `prod-d2g14rwoycac6b45d / flask-ik19 / port 8000`；未连接或修改云端控制面。
- Expected schema: `20261007_0017`；本轮只迁移本机隔离MySQL，无生产迁移。
- Final code verification package: `dist/fair-review-verification`，101文件、1215968字节。
- Manifest SHA-256: `1acd1fdc778325e6eccd68af2092fdf5a2f0a9c4c47167a1f862053ec2ca04e4`
- Package whitelist: Dockerfile、pyproject.toml、uv.lock、wxcloud.config.json及API Python源码；
  不含测试、文档、前端、儿童内容、环境文件或本地数据库。该目录只用于本地验证，未执行上传。

功能验证：后端487 passed/16可选环境skipped，隔离MySQL专项19 passed，前端200 passed；
Ruff、Mypy97文件、前端lint、架构/设计/小程序验证通过。SQLite迁移及全新MySQL5.7
base→0014→0017/current/check通过。本地Docker UID10001，live/ready200，SIGTERM exit0、无OOM。

**发布阻断，不能称为测试全部通过：**

1. 新候选规模门禁FAIL：SQLite1万最大550ms、5万1323ms；MySQL5.7 5万3558ms，超过500ms预算。
2. 独立审查确认旧镜像严格校验schema revision，迁移后不能健康共存/直接回滚；兼容过渡方案尚未实施。

新增索引投影与schema过渡方案`SPEC-20261007-FAIR-REVIEW-02`为READY_FOR_REVIEW，等待用户批准。
当前代码不得用于云端发布。先完成技术门禁，再按BACKEND-RELEASE.md获取管理员备份确认并推进灰度；
此时尚未达到请求生产备份操作的阶段。未知生产版本/流量/数据库当前revision不以历史文档代替实时核验。
冻结代码包含既有0015分析暂存、0016复习管理基线；实际发布前还须核对它们各自剩余发布验收。

NOT_RUN：云dry-run、生产备份/迁移、灰度版本创建、真实业务smoke、全量切流、小程序上传及原生设备验收。
生产保持原状。详细证据：[FAIR-REVIEW-20261007](../../quality/evidence/FAIR-REVIEW-20261007.md)。
