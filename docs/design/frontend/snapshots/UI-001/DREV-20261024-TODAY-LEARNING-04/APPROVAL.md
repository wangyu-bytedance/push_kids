# UI-001 — 学习建议标题约束候选

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261024-TODAY-LEARNING-04
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md#SPEC-20261024-SUGGESTION-TITLE-LIMIT-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/index.html=6ebbac1c69481fc5d5d09376f6bde689e6be2a5e678b0e61a0a9dfcf3008a754
- Prototype generated/updated at: 2026-10-24
- Approved by: 用户
- Approved at: 2026-10-24
- Approval evidence: call_39aaa3dd3cdf4a52b2bfc9c4d862ee58，用户回复「批准，按此实现」，明确批准Spec01（含Architecture01）和DREV04。源/33张PNG及SHA冻结。
- Superseded by: N/A

## Proposed scope

新生成/重新编辑的标题最多20个Unicode码点、无内部换行；详细步骤放已有正文。编辑增加字数和字段错误，超限保留输入且不提交。旧标题不批量改写，读取/审批/任务保持兼容，旧标题重新编辑须精简后保存。颜色、字体及既有操作层级沿用DREV02/03；批准时尚未应用生产代码，实施证据独立记录。

320×568、390×844、430×932各11态，共33张，DPR1。全部合成HTML设计，不代验微信原生、实际键盘或真机。33张布局及21条本地交互检查通过；报告位于原型目录render-report.json。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| proposal-320x568.png | UI-001/proposal | 320×568 | 1x | 4a7e83adb3b91264c5e2d89465841370acfec738f20d9b610185e8185013a88e | 合成设计，非原生验收 |
| proposal-max-320x568.png | UI-001/proposal-max | 320×568 | 1x | e1c0e1f25eab5c04e8e2bebd270354b905775c4796dc077faca30ea6e4222ee6 | 合成设计，非原生验收 |
| card-max-320x568.png | UI-001/card-max | 320×568 | 1x | 8920c038dc9167de590c1a732937ec8849a78b8c4edac881af4201a29bde7b2a | 合成设计，非原生验收 |
| edit-320x568.png | UI-001/edit | 320×568 | 1x | 262975442e498a13d4efc3142fa5ecdf6f7fa737bd0e73072881c88a5f35b399 | 合成设计，非原生验收 |
| edit-max-320x568.png | UI-001/edit-max | 320×568 | 1x | 4045c30d0daa8149fec6e76f752a34ddb66c1b65336a216e3106fea486d9c765 | 合成设计，非原生验收 |
| edit-over-320x568.png | UI-001/edit-over | 320×568 | 1x | 45b488dcc2061ed8976d8af9f0e1123b8acbbe5d279436d1e34bd363baecd7aa | 合成设计，非原生验收 |
| edit-empty-320x568.png | UI-001/edit-empty | 320×568 | 1x | a661a4b8c994bb7cc846bceb24eac2f09bff5bd659df8bb882d5850e8d06be65 | 合成设计，非原生验收 |
| edit-legacy-320x568.png | UI-001/edit-legacy | 320×568 | 1x | 6428a74102aadfa7539279a0eebd1c29453242f3d1866d9c95cd4ff318986364 | 合成设计，非原生验收 |
| edit-error-320x568.png | UI-001/edit-error | 320×568 | 1x | d89f63a25b78fbaf648e2e2f3993f79c54a1095a23d86fa5b7c501183a380ea8 | 合成设计，非原生验收 |
| edit-saving-320x568.png | UI-001/edit-saving | 320×568 | 1x | a4d9d3259c55d900df375254186b48562f7c8b9f32763a588887655c038f54c0 | 合成设计，非原生验收 |
| legacy-320x568.png | UI-001/legacy | 320×568 | 1x | eeb31f956612cc486db3d1caef376ce35464ca766c5e74d9a5e4a850d7085570 | 合成设计，非原生验收 |
| proposal-390x844.png | UI-001/proposal | 390×844 | 1x | edc352ba0e07626f20d4d906ce690e43ac27d2b40354645b41c6f056ce076282 | 合成设计，非原生验收 |
| proposal-max-390x844.png | UI-001/proposal-max | 390×844 | 1x | d8b7f1fab0b394af4b0b36de64d80ff9bde34e4af0c53fe070e93c402878031a | 合成设计，非原生验收 |
| card-max-390x844.png | UI-001/card-max | 390×844 | 1x | 07e8cb97485a7932d1b810625bb8772de8a2db9c36173852153a687fe3640554 | 合成设计，非原生验收 |
| edit-390x844.png | UI-001/edit | 390×844 | 1x | 57b16acde099dc194cb67082d9699023bbc94bff0cf5ee7fcc3f47bc9d85f206 | 合成设计，非原生验收 |
| edit-max-390x844.png | UI-001/edit-max | 390×844 | 1x | 2bcecc7a56cfd0dc848d741fd01b6e7ff4b934aa4d4f65c6f36822bd7bd97759 | 合成设计，非原生验收 |
| edit-over-390x844.png | UI-001/edit-over | 390×844 | 1x | 7a60ac3e7166054763551c0a66493bb4490a2d13b463a0f537d12cd2ca96b7b4 | 合成设计，非原生验收 |
| edit-empty-390x844.png | UI-001/edit-empty | 390×844 | 1x | 17ee6aeffbc5f2ced0b48212c92b86f67258028536b1df185b77f9151db053ca | 合成设计，非原生验收 |
| edit-legacy-390x844.png | UI-001/edit-legacy | 390×844 | 1x | 8707bd24f6aee1a92e0b97b6aadcbd5b4b08eae9a06f873f118ea2fba2f5aaf6 | 合成设计，非原生验收 |
| edit-error-390x844.png | UI-001/edit-error | 390×844 | 1x | 9c6a7f2ab52edb378b3a428dfc9afa9a32500977cbb64667eb2acef3ef43a4ec | 合成设计，非原生验收 |
| edit-saving-390x844.png | UI-001/edit-saving | 390×844 | 1x | c7a9ac2997774e5b2dbcf757de6efd8832a5115345f29b3cdbc580bb6df51c7f | 合成设计，非原生验收 |
| legacy-390x844.png | UI-001/legacy | 390×844 | 1x | c295b31c4c24e0bebdcef6e67ec2e3d40091477b144aa0d32bc98d78477e303c | 合成设计，非原生验收 |
| proposal-430x932.png | UI-001/proposal | 430×932 | 1x | 5e0d08cd0cd13c9466a9a9a5ab7c3055483bd398d9331a49996dc67b5a4d5977 | 合成设计，非原生验收 |
| proposal-max-430x932.png | UI-001/proposal-max | 430×932 | 1x | e6481d879f51fee2f0b8b8b5091fa27858066b403c76757fcb4ba07b24387051 | 合成设计，非原生验收 |
| card-max-430x932.png | UI-001/card-max | 430×932 | 1x | 9867c7b7bb4ff6fb61fe84a07fecaaab363c71bd0f425ad21a95852d4e7d9c88 | 合成设计，非原生验收 |
| edit-430x932.png | UI-001/edit | 430×932 | 1x | eed24b98429d2ebdd0e7ee9435de8b9f9b52159adada04598ab05c2eaa162606 | 合成设计，非原生验收 |
| edit-max-430x932.png | UI-001/edit-max | 430×932 | 1x | 4582e2b6dad6c8cc2cd33eb32bdf32375f4d651c74092bdb772e4a554683d33b | 合成设计，非原生验收 |
| edit-over-430x932.png | UI-001/edit-over | 430×932 | 1x | 1d97492060e39265c9faf1777ff360fffcd8dd7a7431218cf6fd2a48d5d313bb | 合成设计，非原生验收 |
| edit-empty-430x932.png | UI-001/edit-empty | 430×932 | 1x | 5d605320a05a482ebe7f7cac738efea238c460e1b5647b65b955ba3a7fe1fdca | 合成设计，非原生验收 |
| edit-legacy-430x932.png | UI-001/edit-legacy | 430×932 | 1x | d93cade8317cdd717cef784061101c0512fe4e7d6e6cda289ee20ce08e83a277 | 合成设计，非原生验收 |
| edit-error-430x932.png | UI-001/edit-error | 430×932 | 1x | 1b5a6870eec5988acfcb6a41a7b753e86082b566897e4f936b272d88c2b8a567 | 合成设计，非原生验收 |
| edit-saving-430x932.png | UI-001/edit-saving | 430×932 | 1x | dd4d8b5376ee64ff0207b116c919442b9ec2979d09f3217473025c613091b251 | 合成设计，非原生验收 |
| legacy-430x932.png | UI-001/legacy | 430×932 | 1x | 724ebedf79c8772413bca9ae7a3fe2d40fd5dda99b4e606da7df0e132ef90f3d | 合成设计，非原生验收 |

