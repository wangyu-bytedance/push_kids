function appContext() { return getApp().globalData; }

function newIdempotencyKey(prefix = "submission") {
  const random = Math.random().toString(36).slice(2, 12);
  return `${prefix}-${Date.now()}-${random}`;
}

function normalizedError(response) {
  const detail = response && response.data;
  if (detail && detail.error && detail.error.message) return detail.error.message;
  if (detail && detail.detail) {
    if (typeof detail.detail === "string") return detail.detail;
    if (Array.isArray(detail.detail) && detail.detail[0]) return detail.detail[0].msg;
  }
  return "网络有点慢，请稍后再试";
}

function responseError(response) {
  const error = new Error(normalizedError(response));
  error.statusCode = response.statusCode;
  return error;
}

function downloadPreview(capability) {
  const context = appContext();
  const header = {};
  if (capability.download_path) {
    if (context.useCloud || !capability.download_path.startsWith("/submissions/")) return Promise.reject(new Error("照片预览不可用"));
    if (context.localActorId) header["X-Debug-Actor"] = context.localActorId;
    else header["X-Family-ID"] = context.familyId;
  } else if (!/^https:\/\//.test(capability.url || "")) return Promise.reject(new Error("照片预览不可用"));
  return new Promise((resolve, reject) => wx.downloadFile({
    url: capability.download_path ? context.apiBaseUrl + capability.download_path : capability.url,
    header,
    success(result) {
      if (result.statusCode === 200) resolve(result.tempFilePath);
      else { removePreview(result.tempFilePath); reject(new Error("照片暂时无法读取，请重试")); }
    },
    fail: () => reject(new Error("照片下载失败，请检查网络后重试"))
  }));
}

function removePreview(path) {
  if (path && wx.getFileSystemManager) wx.getFileSystemManager().unlink({ filePath: path, fail() {} });
}

function request(path, options = {}) {
  const context = appContext();
  if (context.useCloud) return cloudRequest(path, options, context);
  const header = { "content-type": "application/json" };
  if (context.localActorId) header["X-Debug-Actor"] = context.localActorId;
  else header["X-Family-ID"] = context.familyId;
  if (options.idempotencyKey) header["Idempotency-Key"] = options.idempotencyKey;
  if (options.historyQuery) header["X-History-Query"] = encodeURIComponent(options.historyQuery);
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${context.apiBaseUrl}${path}`,
      method: options.method || "GET",
      data: options.data,
      header,
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) resolve(response.data);
        else reject(responseError(response));
      },
      fail() { reject(new Error("无法连接服务，请检查网络或服务地址")); }
    });
  });
}

function cloudRequest(path, options, context) {
  const header = {
    "content-type": "application/json",
    "X-WX-SERVICE": context.cloudService
  };
  if (options.idempotencyKey) header["Idempotency-Key"] = options.idempotencyKey;
  if (options.historyQuery) header["X-History-Query"] = encodeURIComponent(options.historyQuery);
  return new Promise((resolve, reject) => {
    wx.cloud.callContainer({
      config: { env: context.cloudEnv },
      path: `${context.apiBasePath}${path}`,
      method: options.method || "GET",
      data: options.data,
      header,
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) resolve(response.data);
        else reject(responseError(response));
      },
      fail() { reject(new Error("无法连接云服务，请稍后重试")); }
    });
  });
}

function uploadSubmission(filePath, fields, onProgress, idempotencyKey) {
  const context = appContext();
  if (context.useCloud) return Promise.reject(new Error("云环境图片必须使用对象存储上传"));
  const header = context.localActorId ? { "X-Debug-Actor": context.localActorId } : { "X-Family-ID": context.familyId };
  if (idempotencyKey) header["Idempotency-Key"] = idempotencyKey;
  return new Promise((resolve, reject) => {
    const task = wx.uploadFile({
      url: `${context.apiBaseUrl}/submissions/upload`,
      filePath,
      name: "files",
      formData: fields,
      header,
      success(response) {
        let data;
        try { data = JSON.parse(response.data); } catch { data = {}; }
        if (response.statusCode >= 200 && response.statusCode < 300) resolve(data);
        else reject(new Error(normalizedError({ data })));
      },
      fail() { reject(new Error("图片上传失败，请重试")); }
    });
    if (onProgress) task.onProgressUpdate((event) => onProgress(event.progress));
  });
}

function appendSubmissionMedia(submissionId, filePath, onProgress) {
  const context = appContext();
  if (context.useCloud) return Promise.reject(new Error("云环境图片必须使用对象存储上传"));
  return new Promise((resolve, reject) => {
    const task = wx.uploadFile({
      url: `${context.apiBaseUrl}/submissions/${submissionId}/media`,
      filePath,
      name: "file",
      header: context.localActorId ? { "X-Debug-Actor": context.localActorId } : { "X-Family-ID": context.familyId },
      success(response) {
        let data;
        try { data = JSON.parse(response.data); } catch { data = {}; }
        if (response.statusCode >= 200 && response.statusCode < 300) resolve(data);
        else reject(new Error(normalizedError({ data })));
      },
      fail() { reject(new Error("图片上传失败，请重试")); }
    });
    if (onProgress) task.onProgressUpdate((event) => onProgress(event.progress));
  });
}

module.exports = { request, uploadSubmission, appendSubmissionMedia, normalizedError, newIdempotencyKey, downloadPreview, removePreview };
