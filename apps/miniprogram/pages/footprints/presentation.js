const SOURCES = { exif: "照片信息", gps: "照片信息", parent: "家长填写", unknown: "待补充" };
const missing = (value) => value === null || value === undefined;
function photoView(photo) {
  return { ...photo, dateLabel: photo.local_date || "待补日期",
    placeLabel: photo.place_name || (!missing(photo.latitude) ? "照片拍摄位置" : "待补地点"),
    sourceLabel: [...new Set([SOURCES[photo.time_source] || "待补充", SOURCES[photo.location_source] || "待补充"])].join(" · "),
    expiryLabel: photo.draft_expires_at ? photo.draft_expires_at.replace("T", " ").slice(0, 16) + " UTC" : "上传槽位15分钟后失效",
    statusLabel: (({ uploading: "尚未上传", queued: "正在整理", ready: "待核对", failed: "解析失败，可手动补充", expired: "草稿已到期" })[photo.state] || "已入档") + (photo.duplicate_of ? " · 重复照片" : ""),
    selected: false, previewUrl: "" };
}
function query(values) {
  return Object.entries(values).filter(([, value]) => value !== "" && !missing(value))
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`).join("&");
}
function editValues(photo) {
  return { local_date: photo.local_date || "", local_time: photo.local_time || "",
    offset_minutes: photo.offset_minutes, place_name: photo.place_name || "",
    city: photo.city || "", country: photo.country || "", latitude: photo.latitude,
    longitude: photo.longitude, coordinate_system: photo.coordinate_system,
    precision: photo.precision || "unknown" };
}
function correction(form, batch = false) {
  const values = {};
  ["local_date", "local_time", "place_name", "city", "country"].forEach((field) => {
    if (!batch || form[field]) values[field] = form[field] || null;
  });
  if (!batch || form.place_name || !missing(form.latitude)) {
    Object.assign(values, { latitude: missing(form.latitude) ? null : Number(form.latitude),
      longitude: missing(form.longitude) ? null : Number(form.longitude),
      coordinate_system: form.coordinate_system || null, precision: form.precision || "unknown" });
  }
  if (!batch) values.offset_minutes = missing(form.offset_minutes) ? null : form.offset_minutes;
  if (!batch && form.orderTouched) {
    values.day_order = Number(form.day_order);
    values.order_revision = form.order_revision;
  }
  return values;
}
module.exports = { photoView, query, editValues, correction };
