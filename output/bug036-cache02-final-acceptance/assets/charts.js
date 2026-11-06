(function () {
  "use strict";
  const styles = getComputedStyle(document.documentElement);
  const read = name => styles.getPropertyValue(name).trim();
  const colors = {
    ink: read("--ink"), muted: read("--muted"), rule: read("--rule"),
    accent: read("--accent"), success: read("--success"), fail: read("--fail"),
    warning: read("--accent2"), surface: read("--bg2")
  };
  const chart = echarts.init(document.getElementById("chart-validation"), null, { renderer: "svg" });
  chart.setOption({
    animation: false,
    color: [colors.success, colors.fail, colors.warning],
    backgroundColor: colors.surface,
    textStyle: { color: colors.ink, fontFamily: styles.getPropertyValue("--font").trim() },
    legend: { data: ["通过", "失败（Red为预期）", "条件跳过"], bottom: 0, textStyle: { color: colors.muted } },
    tooltip: {
      trigger: "axis", axisPointer: { type: "shadow" }, appendToBody: true,
      backgroundColor: colors.surface, borderColor: colors.rule, textStyle: { color: colors.ink }
    },
    grid: { top: 8, left: 4, right: 34, bottom: 48, containLabel: true },
    xAxis: { type: "value", axisLabel: { color: colors.muted }, splitLine: { lineStyle: { color: colors.rule } } },
    yAxis: {
      type: "category", inverse: true, data: ["修复前Red", "最终专项", "完整后端", "MySQL 5.7", "发布40例"],
      axisLabel: { color: colors.ink }, axisLine: { show: false }, axisTick: { show: false }
    },
    series: [
      { name: "通过", type: "bar", stack: "counts", barMaxWidth: 26, data: [47, 116, 857, 8, 34] },
      { name: "失败（Red为预期）", type: "bar", stack: "counts", data: [12, 0, 0, 0, 6] },
      { name: "条件跳过", type: "bar", stack: "counts", data: [0, 0, 52, 0, 0] }
    ]
  });
  window.addEventListener("resize", () => chart.resize());
  document.getElementById("print-report").addEventListener("click", () => window.print());
  mermaid.initialize({
    startOnLoad: true, theme: "base", securityLevel: "strict",
    themeVariables: {
      fontFamily: styles.getPropertyValue("--font").trim(),
      primaryColor: read("--blue-bg"), primaryTextColor: colors.ink,
      primaryBorderColor: colors.accent, lineColor: colors.muted,
      secondaryColor: read("--success-bg"), tertiaryColor: read("--warning-bg")
    },
    flowchart: { htmlLabels: false, curve: "linear", useMaxWidth: true }
  });
}());
