# DREV-20260905-AI-01 implementation authorization

- Feature/UI: FEAT-001 / UI-001；Spec: BUG-SPEC-20260905-07，合并BUG-008人工兜底合同。
- 用户授权：2026-09-05 “AI 分析的相关问题都修复掉”，承接此前上下文/重复内容/核心提取建议
  以及“AI不可用前端提示并人工录入”的明确意图。按该授权实施既有页面增量，没有再次询问。
- 基线：FDB-20260830-01 / FEC-20260830-01；暖纸色、墨绿色、既有notice/card/form/button。
- 增量：记录页失败/排队/分析中的人工入口；确认页人工来源、完整原文、关联说明/取消关联、
  learning科目过滤、可输入新科目、重复材料提示和持久错误。
- Figma基线锚点：https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1 。
  沿用FEAT-001 Starter waiver；此记录不是新的Figma节点批准或截图验收证据，不扩展FEAT-002。
- Matrix: 320×568、390×844、430×932；人工/失败/长文本/保存中/保存失败/关联清除。
- 页面VM逻辑测试通过；CUA显示开发者工具未运行、选择bundle ID超时。真实原生视口和触控
  NOT_RUN；不得把本文件当作视觉验收完成。Owner: Codex；公开发布前须补实际设备证据。
