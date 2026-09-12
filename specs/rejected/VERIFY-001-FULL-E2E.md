# VERIFY-001 — FEAT-001 完整端到端验证

- Status: REJECTED
- Rejected: 2026-09-12 — 本 revision 绑定 2026-08-30 的 FEAT/UI/Architecture 基线，
  已被后续多孩子、云迁移、通知、PKDS-2.0、有界读取和报表变更整体淘汰；后续完整 E2E
  必须按当前基线重新立 Spec，不能沿用本稿宣称完成。
- Risk: R2
- Revision: `VERIFY-SPEC-20260830-01`
- Approved by: 产品负责人（用户于 2026-08-30 明确要求充分、完整的端到端验证）
- Affected Feature IDs: `FEAT-001`
- Feature current-state documents: `docs/domain/features/FEAT-001-push-kids-mvp.md`
- Feature baseline revision: `FEAT-STATE-20260830-01`
- Feature merge owner: Codex
- Feature current-state impact: 合并真实 E2E 覆盖、运行限制和验证证据，不改变产品行为
- Architecture: no change, `ARCH-20260830-01`
- Frontend design: no visual change, reuse `DREV-20260830-01`
- Frontend engineering: validation-only, `FEC-20260830-01`
- Frontend impact: no
- Frontend impact reason: 本任务只验证既有批准界面，不改变可见合同
- Frontend engineering impact: yes
- Frontend engineering impact reason: 新增小程序真实编译、页面状态、设备与 E2E 质量证据
- Frontend engineering constraint revision: `FEC-20260830-01`
- Affected frontend quality dimensions: state/form, responsive, accessibility, browser/device, security/privacy
- Frontend quality budgets/requirements: 既有包体、视口、隐私和完整状态预算不变
- Frontend quality verification plan: `npm test`、静态检查、微信开发者工具编译与逐页检查
- Approved frontend engineering deviations: none

## Outcome

从真实 HTTP 入口和微信开发者工具验证家长主旅程，而不只依赖模块级测试。测试使用
独立临时 SQLite、媒体目录、后台 Worker 和 Fake Provider，不读取或传输真实儿童数据，
不调用外部 Ark，不修改开发数据。

## Acceptance criteria

1. Given 独立家庭，When 创建孩子、学习科目和活动科目，Then API 与小程序均可读取。
2. Given 文字或照片学习输入，When 后台异步分析完成且家长确认，Then 才生成历史、知识与复习 Todo。
3. Given 重复知识和 Todo 匹配，When 再次确认，Then 复用知识身份并只在确认后处理匹配。
4. Given 历史补录，When 确认，Then 只产生当前检查，不产生历史欠账。
5. Given 今日 Todo，When 分别选择完成、需加强、部分完成、稍后，Then 状态按确定性规则变化。
6. Given 活动计划与练习记录，When 查看首页、日历和报表，Then 展示非强制建议与可追溯计数。
7. Given 缺失 Header、跨家庭 ID、错误媒体和非法状态操作，Then 返回受控错误且无越权副作用。
8. Given 微信开发者工具加载项目，When 浏览四个 Tab 和核心深层页，Then 关键状态、按钮与数据可见，Issues 面板无源码问题。

## Impact map

```text
pytest E2E → 独立 uvicorn 进程 → HTTP API → SQLite/media/worker/Fake Provider
微信开发者工具 → 原生小程序 request/upload → 同一 API → 页面状态
```

异步状态机沿用 `queued → analyzing → pending_confirmation → confirmed`，并覆盖
`queued → cancelled` 与失败重试既有集成测试。架构、Schema、产品行为和 UI 设计均不改变。

## Expected file changes

| File | Change | Reason |
|---|---|---|
| `tests/e2e/test_live_parent_journey.py` | add | 独立进程、真实 HTTP 的主旅程证据 |
| `docs/quality/E2E-VALIDATION-REPORT.md` | add | 命令、环境、结果、截图和残余风险 |
| `docs/quality/TEST-STRATEGY.md` | modify | 固化 E2E 命令与覆盖范围 |
| `docs/domain/features/FEAT-001-push-kids-mvp.md` | modify | 合并已验证最终事实 |

## Required verification

- `uv run pytest tests/e2e -v`
- 全量 Python/Node/static/architecture/mini-program gates
- 微信开发者工具真实编译与逐页检查
- 只读交付审计；发现产品行为缺陷时停止扩大范围，另建 Bug Spec。

## Non-goals and residual gates

- 不使用已暴露密钥，不执行真实 Ark 付费调用。
- 不配置真实微信 AppID、登录、相机权限或公开生产环境。
- Docker 镜像、公网 HTTPS、真机 iOS/Android 仍属于部署环境验证，不伪装为已通过。
