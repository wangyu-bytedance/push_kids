# Push Kids 发布手册

本目录是 Push Kids 后续发布的执行入口。详细架构和平台约束仍以
[`docs/operations/WECHAT-CLOUD-HOSTING.md`](../operations/WECHAT-CLOUD-HOSTING.md) 为准；这里仅保留
每次发布都需要执行的顺序、门禁、人工操作和直达入口。

## 固定发布模式

1. 先冻结发布范围，记录 Git commit、未提交差异、目标环境和发布版本。
2. 先执行自动检查；任何必需检查失败都停止发布，不得以“先上线再修复”替代。
3. 有数据库变更时，先完成兼容性审查、备份和 Alembic migration，再发布兼容的新后端。
4. 后端先灰度并完成健康检查和业务 smoke；公网入口保持关闭。
5. 后端稳定后再上传小程序前端，先体验版真机验收，再提交微信审核。
6. 微信审核通过后由管理员人工发布正式版。
7. 保留上一不可变后端版本和数据库备份，直至观察窗口结束。

具体流程：

- [前端发布](FRONTEND-RELEASE.md)
- [后端与数据库发布](BACKEND-RELEASE.md)

## 人工操作输出约定

自动化执行到必须由管理员完成的页面操作、扫码、验证码、隐私/法律声明、密钥配置或最终发布时，
立即停止在该门禁之前，并按下面格式直接输出：

```text
【需要人工操作】<操作标题>
原因：<为什么不能或不应自动完成>
操作入口：<可点击 URL>
导航路径：<控制台菜单路径>
需要填写/选择：
- <字段和值或判断标准>
完成标志：<页面上应出现的状态>
完成后回复：已完成 <操作标题>
```

约束：

- 不要求用户把密码、OpenID、数据库连接串、Ark Key、HMAC Key 或 COS 凭证发到聊天中。
- 表单涉及服务类目、隐私声明、备案、资质、发布范围等真实对外陈述时，只给建议和核对要求，
  由账号管理员确认并提交。
- “已上传”“体验版”“审核通过”“已发布”是不同状态，发布报告必须明确写出实际到达的状态。
- 不能操作某个受保护站点时，给出直达入口、菜单路径、字段建议和完成标志，不尝试绕过平台保护。

## 固定环境

| 项目 | 当前值 |
|---|---|
| 小程序 AppID | `wx5d2e0014690bf285` |
| 小程序源码 | `apps/miniprogram` |
| 云托管环境 | `prod-d2g14rwoycac6b45d` |
| 云托管服务 | `flask-ik19` |
| 容器端口 | `8000` |
| 云托管入口 | 仅 `MINIAPP`；公网关闭 |
| 数据库 | 微信云托管 MySQL / `push_kids` |

固定入口：

- [微信公众平台](https://mp.weixin.qq.com/)
- [微信云托管控制台](https://cloud.weixin.qq.com/)
- [微信开发者工具下载](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- [微信云托管部署文档](https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html)
- [火山方舟控制台](https://console.volcengine.com/ark)

