function resolveViewState({ loading, error, hasData }) {
  if (loading) return "loading";
  if (error) return "error";
  if (!hasData) return "empty";
  return "content";
}

function stateLabel(state) {
  return {
    queued: "等待分析",
    analyzing: "正在分析",
    pending_confirmation: "待家长确认",
    failed: "分析失败",
    cancelled: "已取消",
    confirmed: "已确认"
  }[state] || state;
}

module.exports = { resolveViewState, stateLabel };
