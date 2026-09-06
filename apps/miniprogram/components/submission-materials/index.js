const api = require("../../utils/api");

/* 展示层只做「可核对的原始材料」：不判断内容、不生成结论，缩略图按后端 sort_order 顺序渲染。 */
Component({
  options: { addGlobalClass: true },
  properties: { childId: String, submissionId: String, submissionState: String, defaultOpen: Boolean },
  data: { open: false, loading: false, error: "", text: "", media: [], previewBusy: false, countLabel: "" },
  lifetimes: { detached() { this.clear(); } },
  pageLifetimes: {
    hide() { this.visible = false; this.generation = (this.generation || 0) + 1; },
    show() { this.visible = true; if (this.data.open) { this.clear(); this.load(); } }
  },
  observers: {
    "submissionId, defaultOpen, submissionState": function(sid, open) {
      this.visible = true;
      this.clear();
      this.setData({ open: !!open });
      if (sid && open) this.load();
    }
  },
  methods: {
    clear() {
      this.generation = (this.generation || 0) + 1;
      (this.paths || []).forEach(api.removePreview);
      this.paths = [];
      this.setData({ media: [], text: "", error: "", loading: false, previewBusy: false, countLabel: "" });
    },
    toggle() {
      this.setData({ open: !this.data.open });
      if (this.data.open) this.load(); else this.clear();
    },
    async load() {
      const generation = (this.generation || 0) + 1;
      this.generation = generation;
      this.setData({ loading: true, error: "" });
      try {
        const result = await api.request(`/children/${this.data.childId}/history/${this.data.submissionId}`);
        if (generation !== this.generation || this.visible === false) return;
        const media = result.media || [];
        this.setData({ text: result.input_text || "", media, loading: false,
          countLabel: media.length ? `${media.length} 张照片` : (result.input_text ? "仅文字" : "") });
        await this.loadThumbnails(generation);
      } catch (error) {
        if (generation === this.generation) {
          if ([401, 403, 404].includes(error.statusCode)) this.clear();
          this.setData({ loading: false, error: error.message });
        }
      }
    },
    async loadThumbnails(generation) {
      let next = 0;
      const worker = async () => {
        while (generation === this.generation && this.visible !== false && next < this.data.media.length) {
          const index = next++;
          const item = this.data.media[index];
          if (!item.available) continue;
          try {
            const capability = await api.request(`/submissions/${this.data.submissionId}/media/${item.id}/preview?child_id=${encodeURIComponent(this.data.childId)}`);
            if (generation !== this.generation) return;
            const path = await api.downloadPreview(capability);
            if (generation !== this.generation || this.visible === false) { api.removePreview(path); return; }
            const previous = this.data.media[index].thumbnail;
            if (previous) api.removePreview(previous);
            this.paths = (this.paths || []).filter((p) => p !== previous).concat(path);
            this.setData({ [`media[${index}].thumbnail`]: path });
          } catch (error) {
            if (generation !== this.generation) return;
            if ([401, 403, 404].includes(error.statusCode)) { this.clear(); this.setData({ error: error.message }); return; }
            this.setData({ [`media[${index}].unavailable`]: error.statusCode === 410,
              [`media[${index}].hint`]: error.statusCode === 410 ? "原图已删除或不可用" : "暂时无法读取，点此重试" });
            this.setData({ error: error.message });
          }
        }
      };
      await Promise.all([worker(), worker()]);
    },
    /* 地址过期或网络抖动会让 <image> 直接渲染失败，此时给出可重试的提示而不是留一个空格子。 */
    thumbnailFailed(event) {
      const index = this.data.media.findIndex((m) => m.id === event.currentTarget.dataset.id);
      if (index < 0) return;
      this.setData({ [`media[${index}].thumbnail`]: "", [`media[${index}].hint`]: "暂时无法读取，点此重试" });
    },
    thumbnailLoaded(event) {
      const index = this.data.media.findIndex((m) => m.id === event.currentTarget.dataset.id);
      if (index < 0 || !this.data.media[index].hint) return;
      this.setData({ [`media[${index}].hint`]: "" });
    },
    async preview(event) {
      if (this.data.previewBusy) return;
      if (!wx.previewImage) { this.setData({ error: "当前微信版本无法预览图片，请更新微信后重试" }); return; }
      const id = event.currentTarget.dataset.id;
      const index = this.data.media.findIndex((m) => m.id === id);
      if (index < 0 || !this.data.media[index].available) return;
      if (!this.data.media[index].thumbnail && !this.data.media[index].hint) { this.setData({ error: "照片正在读取，请稍后点开" }); return; }
      const generation = this.generation;
      this.setData({ previewBusy: true, error: "" });
      try {
        let path;
        for (let attempt = 0; attempt < 2; attempt += 1) {
          const capability = await api.request(`/submissions/${this.data.submissionId}/media/${id}/preview?child_id=${encodeURIComponent(this.data.childId)}`);
          if (generation !== this.generation) return;
          try { path = await api.downloadPreview(capability); break; }
          catch (error) { if (attempt === 1) throw error; }
        }
        if (generation !== this.generation || this.visible === false) { api.removePreview(path); return; }
        const previous = this.data.media[index].thumbnail;
        if (previous) api.removePreview(previous);
        this.paths = (this.paths || []).filter((saved) => saved !== previous).concat(path);
        this.setData({ [`media[${index}].thumbnail`]: path });
        wx.previewImage({ current: path, urls: [path], fail: () => this.setData({ error: "当前设备无法预览图片，请重试" }) });
      } catch (error) {
        if (generation !== this.generation) return;
        if ([401, 403, 404].includes(error.statusCode)) this.clear();
        if (error.statusCode === 410) this.setData({ [`media[${index}].available`]: false });
        this.setData({ error: error.message });
      } finally { if (generation === this.generation) this.setData({ previewBusy: false }); }
    }
  }
});
