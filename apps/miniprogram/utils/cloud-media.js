const api = require("./api");

function appContext() { return getApp().globalData; }

function imageMetadata(filePath) {
  return Promise.all([
    new Promise((resolve, reject) => wx.getFileInfo({
      filePath,
      success: ({ size }) => resolve(size),
      fail: () => reject(new Error("无法读取图片大小，请重新选择"))
    })),
    new Promise((resolve, reject) => wx.getImageInfo({
      src: filePath,
      success: ({ type }) => resolve(type),
      fail: () => reject(new Error("无法识别图片格式，请重新选择"))
    }))
  ]).then(([byteSize, type]) => {
    const contentTypes = { jpg: "image/jpeg", jpeg: "image/jpeg", png: "image/png", webp: "image/webp" };
    const contentType = contentTypes[String(type).toLowerCase()];
    if (!contentType) throw new Error("仅支持 JPG、PNG 或 WebP 图片");
    return { byteSize, contentType };
  });
}

function uploadObject(filePath, cloudPath, onProgress) {
  const context = appContext();
  return new Promise((resolve, reject) => {
    const task = wx.cloud.uploadFile({
      cloudPath,
      filePath,
      config: { env: context.cloudEnv },
      success: ({ fileID }) => resolve(fileID),
      fail: () => reject(new Error("图片上传失败，请重试"))
    });
    if (onProgress) task.onProgressUpdate(({ progress }) => onProgress(progress));
  });
}

async function submitCloudPhotoBatch(photos, fields, onProgress, batchKey) {
  const draft = await api.request("/submissions/photo-drafts", {
    method: "POST",
    idempotencyKey: batchKey,
    data: {
      child_id: fields.child_id,
      occurred_at: fields.occurred_at,
      input_text: fields.input_text || null
    }
  });
  const total = photos.length;
  for (let index = draft.media_count; index < total; index += 1) {
    const metadata = await imageMetadata(photos[index]);
    const ticket = await api.request("/media/upload-tickets", {
      method: "POST",
      idempotencyKey: `${batchKey}-media-${index}`,
      data: {
        submission_id: draft.id,
        content_type: metadata.contentType,
        byte_size: metadata.byteSize
      }
    });
    const fileID = await uploadObject(photos[index], ticket.cloud_path, (progress) => {
      if (onProgress) onProgress(Math.round((index + progress / 100) / total * 100));
    });
    await api.request("/media/claims", {
      method: "POST",
      data: { ticket_id: ticket.ticket_id, file_id: fileID }
    });
    if (onProgress) onProgress(Math.round((index + 1) / total * 100));
  }
  return api.request(`/submissions/${draft.id}/finalize`, { method: "POST" });
}

module.exports = { imageMetadata, uploadObject, submitCloudPhotoBatch };
