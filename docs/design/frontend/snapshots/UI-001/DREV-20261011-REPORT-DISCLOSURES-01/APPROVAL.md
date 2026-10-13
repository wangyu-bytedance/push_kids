# UI-001 — 报表历史记录与编辑计划候选设计证据

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261011-REPORT-DISCLOSURES-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-001-REPORT-DISCLOSURES.md#SPEC-20261011-REPORT-DISCLOSURES-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/both-open-320x568.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/both-open-390x844.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/both-open-430x932.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/collapsed-320x568.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/collapsed-390x844.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/collapsed-430x932.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/history-open-320x568.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/history-open-390x844.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/history-open-430x932.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/review-open-320x568.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/review-open-390x844.svg; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/review-open-430x932.svg
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/both-open-320x568.svg=22dba71e63df5acc88a639a3195f1cef4b5f606fd9d07be328131a1bde5ed8c9; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/both-open-390x844.svg=3b0fc805cd1ec5a7814d138da896959916af2082584b833aeb53e9354171c522; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/both-open-430x932.svg=bc8bde6d652a236e6387b175fc46ce15c25dedf31055d630ed471bf5c08f2f24; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/collapsed-320x568.svg=2aa8223858a094703a7c49b6b5d7a9b626607941b658b3883302cda88532b66c; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/collapsed-390x844.svg=1363f8bbd800834186fc55ae419220906d41434a622250c49ff90ad7f55adf0b; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/collapsed-430x932.svg=f1eb0b21e8017d373a9d1aa5266e9892a47c9d8ea761f60603600068ba74f4d3; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/history-open-320x568.svg=c3d1c335a99e672296578f428c057f7cd62a06f59854269753112344df75e9b1; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/history-open-390x844.svg=e0dc112dc08aead45833e360338c166cc6135ed69d879652060c1131177c499c; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/history-open-430x932.svg=e497a3dedca719996df48825f301cdd2dd909cdf7d8bd27c9e51e0d07e687715; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/review-open-320x568.svg=967b39652977450449e609a4c2accf383f80d99f6a6e0890e28de5fcfdd4895a; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/review-open-390x844.svg=42fde7c44f9c19e6395028002d019bdc0ace3e2cec0695e9c55067ed130bf6dc; docs/design/frontend/prototypes/DREV-20261011-REPORT-DISCLOSURES-01/review-open-430x932.svg=d76e95755d0690b6cdd30dcaffcf3dd565514d1eb27daf52df6b5edc012628bc
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-11
- Approval evidence: 用户在要求区块更名为“编辑计划”并审阅更新方案后回复“然后按照这个方案进行落地”，批准 SPEC-20261011-REPORT-DISCLOSURES-01 与 DREV-20261011-REPORT-DISCLOSURES-01。
- Superseded by: N/A

## Scope

科目学习记录之后、课外活动投入之前，历史记录和编辑计划两块默认收起，彼此独立展开。展开内嵌现有有界内容是待批准的推荐方案。截图采用合成数据，不代表现有小程序已变更。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| both-open-320x568.png | both-open | 320x568 | 1x | 62242f0ef0ca5bb40ce0ad4745f1f7fb71659815f87a19ceb8a223e0c7e8e5bf | 合成数据，静态候选图 |
| both-open-390x844.png | both-open | 390x844 | 1x | 2067f4fee6d02065b5bd9ac68f5402cd99e43a50e4906e6be7e093012f4762cd | 合成数据，静态候选图 |
| both-open-430x932.png | both-open | 430x932 | 1x | 7750fb98e231ec6a698cf48637898f6b5c94fb94f6948ab8354daf98342b2c97 | 合成数据，静态候选图 |
| collapsed-320x568.png | collapsed | 320x568 | 1x | 5fe4882a5b9ac47a46a4c69dedf13397a4f1e1465e33dcb67a2c7a1fb3ac0ac0 | 合成数据，静态候选图 |
| collapsed-390x844.png | collapsed | 390x844 | 1x | 737a41ea73bc910e8d856273c0bd03095d8d551788df07b5bc4679c0f1942161 | 合成数据，静态候选图 |
| collapsed-430x932.png | collapsed | 430x932 | 1x | 37ddf5df12d02ec9d1037a96b258ed6e1fe0055365235f341b92e28e9cf06681 | 合成数据，静态候选图 |
| history-open-320x568.png | history-open | 320x568 | 1x | 62242f0ef0ca5bb40ce0ad4745f1f7fb71659815f87a19ceb8a223e0c7e8e5bf | 合成数据，静态候选图 |
| history-open-390x844.png | history-open | 390x844 | 1x | 5537fc41b867bdea49574d251d0419fb4cf6b18355837753858dcf70b51fe425 | 合成数据，静态候选图 |
| history-open-430x932.png | history-open | 430x932 | 1x | 2b8ad4486b554a74484ba43fa353ccce4d1269e5b322e6f65143b94395808415 | 合成数据，静态候选图 |
| review-open-320x568.png | review-open | 320x568 | 1x | 8f19f95ea4b22f95140a95d4c2fc85dcdb466b37c214533ccd9aa17c77d4d2e3 | 合成数据，静态候选图 |
| review-open-390x844.png | review-open | 390x844 | 1x | 8856f559676d44097766f010d0544a1b2d2631b28e482d8b0756137347478796 | 合成数据，静态候选图 |
| review-open-430x932.png | review-open | 430x932 | 1x | 4f38a07658394f55738896aee66e84d189456fc7f2c205d92a17290a8057ced4 | 合成数据，静态候选图 |

## Verification and gaps

- 12个SVG可编辑设计源和12张精确尺寸PNG均由同目录 render.py 生成；本清单记录当前SHA-256。
- 候选图须由用户审阅并明确批准 Task Spec revision + Design Revision。批准后本清单不可修改，除 Superseded by 指针。
- 原生微信节点几何、长内容/错误/权限状态、iOS/Android真机均 NOT_RUN；生产代码未修改。
- Superseded by: DREV-20261013-REPORT-PANELS-01（仅历史/编辑计划展开区；其余范围保留原批准）
