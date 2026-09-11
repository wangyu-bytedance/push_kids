# tools/preview — 小程序设计走查预览

在没有微信开发者工具的环境里，把 WXML/WXSS 近似渲染成 HTML，用来做 320 / 390 / 430
三档视口的设计走查。**它不是验收工具**：原生节点几何、真机字体、`backdrop-filter`
行为必须仍在微信开发者工具或真机上验证（见 `docs/quality/TEST-STRATEGY.md`）。

## 用法

```bash
node tools/preview/render.js                 # 渲染全部页面到 dist/ui-preview/*.html
node tools/preview/render.js today confirm   # 只渲染指定页面
python3 tools/preview/shoot.py               # 用 Playwright 截图（*-vp.png 视口图 / *.png 全页图）
python3 tools/preview/shoot.py today         # 只截指定页面
```

## 组成

| 文件 | 职责 |
|---|---|
| `render.js` | WXML 解析、`wx:if/wx:for`/插值/`template`/`import`/自定义组件近似渲染，rpx→px，`page{}`→`.page-root` |
| `fixtures.js` | 每个页面的假数据，字段与页面 `data` 契约一致，覆盖典型内容长度与边界 |
| `shoot.py` | 截图；全页图会临时隐藏 `.tabbar/.pk-cta-bar/.pk-fab` 等 fixed 层，避免它们出现在长图中间 |

## 已知近似

- 自定义组件只渲染在 `render.js` 的 `COMPONENTS` 里登记过的（当前：`todo-card`、`primary-nav`）。
- `switch/slider/picker` 等原生表单件只渲染为静态近似。
- 页面数据来自 fixture，不发请求；因此不能验证真实数据的空态与异常态。
- fixture 里必须补齐页面/模板引用到的所有字段：缺字段会让整段 `wx:if` 判空而不报错。
