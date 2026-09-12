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

/* 保留服务端错误码：界面要区分「冲突」和「需要家长再确认一次」（如新增科目）。 */
function responseError(response) {
  const error = new Error(normalizedError(response));
  error.statusCode = response.statusCode;
  const detail = response && response.data;
  error.code = (detail && detail.error && detail.error.code) || "";
  return error;
}

/*
 * 返回一个可以直接喂给 <image src> / wx.previewImage 的地址。
 * 云环境用服务端签发的短期 https 地址：<image> 与 previewImage 不受 request 合法域名限制，
 * 而 wx.downloadFile 受限，真机上会让所有照片一起加载失败。
 * 本地联调仍走容器内的鉴权下载，落成临时文件。
 */
function downloadPreview(capability) {
  const context = appContext();
  if (context.useCloud) {
    if (/^https:\/\//.test(capability.url || "")) return Promise.resolve(capability.url);
    return Promise.reject(new Error("照片预览不可用，请稍后重试"));
  }
  if (!capability.download_path || !capability.download_path.startsWith("/submissions/")) {
    return Promise.reject(new Error("照片预览不可用"));
  }
  if (!wx.downloadFile) return Promise.reject(new Error("当前微信版本无法读取照片，请更新微信后重试"));
  const header = context.localActorId
    ? { "X-Debug-Actor": context.localActorId }
    : { "X-Family-ID": context.familyId };
  return new Promise((resolve, reject) => wx.downloadFile({
    url: context.apiBaseUrl + capability.download_path,
    header,
    success(result) {
      if (result.statusCode === 200) resolve(result.tempFilePath);
      else { removePreview(result.tempFilePath); reject(new Error("照片暂时无法读取，请重试")); }
    },
    fail: () => reject(new Error("照片下载失败，请检查网络后重试"))
  }));
}

/* 只清理本地落盘的临时文件；云环境拿到的是远端地址，没有本地副本可删。 */
function removePreview(path) {
  if (!path || /^https?:\/\//.test(path)) return;
  if (wx.getFileSystemManager) wx.getFileSystemManager().unlink({ filePath: path, fail() {} });
}

function request(path, options = {}) {
  const context = appContext();
  if (context.useCloud) return cloudRequest(path, options, context);
  const header = { "content-type": "application/json" };
  if (context.localActorId) header["X-Debug-Actor"] = context.localActorId;
  else header["X-Family-ID"] = context.familyId;
  if (options.idempotencyKey) header["Idempotency-Key"] = options.idempotencyKey;
  if (options.historyQuery) header["X-History-Query"] = encodeURIComponent(options.historyQuery);
  if (options.capabilities) header["X-Client-Capabilities"] = options.capabilities;
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
  if (options.capabilities) header["X-Client-Capabilities"] = options.capabilities;
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
