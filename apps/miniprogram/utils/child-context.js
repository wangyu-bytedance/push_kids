/* 孩子档案选择的唯一口径：装饰切换列表、回落失效的选择、给出档案数量上限提示。
   页面只负责取数据和渲染，选中哪个孩子的判断都走这里，避免每个 Tab 各写一份回落规则。 */

/* 与后端 MAX_ACTIVE_CHILDREN 对齐，只用于提前给出说明，真正的拒绝仍在服务端。 */
const MAX_ACTIVE_CHILDREN = 5;
const FALLBACK_AVATAR = "芽";
const GRADE_OPTIONS = [
  "学前",
  "小学一年级",
  "小学二年级",
  "小学三年级",
  "小学四年级",
  "小学五年级",
  "小学六年级",
  "初中一年级",
  "其他"
];

function decorate(child) {
  const name = child && child.name ? child.name : "";
  return {
    ...child,
    avatar: name ? name.charAt(0) : FALLBACK_AVATAR,
    label: child && child.grade ? `${name} · ${child.grade}` : name
  };
}

function decorateAll(children) {
  return (children || []).map(decorate);
}

/* 返回切换所需的全部视图字段。selectedChildId 指向已归档或已不存在的档案时回落到第一个，
   并用 changed 告诉调用方需要把新的选择写回全局态。 */
function resolveSelection(children, selectedChildId) {
  const list = decorateAll(children);
  if (!list.length) {
    return {
      children: list,
      childIndex: 0,
      childId: "",
      multiChild: false,
      changed: Boolean(selectedChildId)
    };
  }
  let childIndex = list.findIndex((item) => item.id === selectedChildId);
  const missing = childIndex < 0;
  if (missing) childIndex = 0;
  return {
    children: list,
    childIndex,
    childId: list[childIndex].id,
    multiChild: list.length > 1,
    changed: missing
  };
}

/* 解析并把结果落回全局态与本地存储，让所有页面下一次进入时口径一致。 */
function syncSelection(app, children) {
  const current = app && app.globalData ? app.globalData.selectedChildId || "" : "";
  const resolved = resolveSelection(children, current);
  if (app && app.selectChild && resolved.childId !== current) app.selectChild(resolved.childId);
  return resolved;
}

function activeCount(children) {
  return (children || []).filter((item) => item.active !== false).length;
}

function canAddChild(children) {
  return activeCount(children) < MAX_ACTIVE_CHILDREN;
}

function limitHint() {
  return `最多同时保留 ${MAX_ACTIVE_CHILDREN} 个学习档案，可以先归档不再使用的档案。`;
}

module.exports = {
  MAX_ACTIVE_CHILDREN,
  GRADE_OPTIONS,
  decorate,
  decorateAll,
  resolveSelection,
  syncSelection,
  activeCount,
  canAddChild,
  limitHint
};
