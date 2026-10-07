# 2026-10-07 公平复习修订02 — 本地完成，云端发布通道被占用

- Feature commits: `d536ad5`及最终查询优化`8052419`；工作区保留无关未跟踪`output/`。
- Approved scope: SPEC/ARCH-20261007-FAIR-REVIEW-02；DREV-20261007-FAIR-REVIEW-01不变。
- 用户再次明确允许将无密钥、无儿童数据的包上传到`prod-d2g14rwoycac6b45d / flask-ik19`，创建兼容过渡灰度版本。
- 当前生产schema只读核对为`20260913_0014`；目标新策略`20261007_0018`，本轮未迁移生产。
- 新策略冻结包（包含最终候选字段/预算优化）：`dist/fair-feature-20261007`，103文件、1223520字节；manifest SHA256
  `44c451bdbccbc567fe901af0e9987208256ecc2cdcf915466261a8dc07b4e5b3`。
- 兼容过渡包：`dist/schema-bridge-source/dist/cloud-release`，90文件、1101337字节；manifest SHA256
  `9754fe1d96d79afd6504eba9cf2f94994fe0e4d8a2ac7231934a2c785ed831af`。
  源业务固定`b3db2198a56caa50112b0a2b0e212ce3444b64dc`，唯一补丁是精确允许0014..0018。
  源码不包含环境文件、密钥、儿童内容、测试、文档或本地数据库。生成器`tools/prepare_schema_bridge.py`。
- 本地镜像manifest：过渡版`sha256:5ab840f66dd0e339988414ded83a43270e1dcdf61a32dc6fb10610de19e8bd49`；
  优化前新策略`sha256:f60faff4d35d9010470f1bc47f53a1331341f920f2447c4cf895af61ce08c1a6`。
  两者UID10001、live/ready 200、SIGTERM exit0，OOM=false。
- 最终查询优化镜像`sha256:f8b65e50d17c82da56c2a4d356bd7ec8b16d7f304d81c1aff8a3e0a2f43d5ba6`，
  再次验证UID10001、live/ready 200、SIGTERM exit0、OOM=false；使用上述最终manifest。

## 云端实际执行结果

自动审批首次拒绝dry-run，要求明确载荷与具体目的地。用户随后明确允许，重试dry-run PASS。
随后从冻结过渡目录执行`wxcloud run:deploy`，GRAY、8000、Dockerfile、目标`.`、备注
`push-kids-20261007-fair02-bridge-b3db219`。逐项核对确认表后输入yes，未使用noConfirm。

平台返回`ResourceInUse: 当前已有部署发布任务运行中,请结束后再执行`，本次部署失败，**没有新不可变版本号**。
独立查询仍显示最近版本`flask-ik19-025` normal，服务normal、PUBLIC关闭；没有执行流量切换。
CLI未暴露占用任务ID、流量百分比，不能认定为可自动取消的无效任务。
控制台浏览器访问被站点安全策略阻止，未更换浏览器或绕过；需要管理员直接在控制台核对。

## 本地客户端

微信开发者工具已打开`apps/miniprogram`；preview PASS，包体669664字节，二维码
`dist/local-preview/preview.png`（预览产物忽略，不进入Git/服务端包）。430×932模拟器今日页正常显示。
保留useCloud=true，连接现有线上服务；**公平新策略尚未生效**。未上传开发版/体验版/正式版。
原生三视口节点几何及iOS/Android由后续验证完成，不用HTML证据替代。

## 下一步（必须遵循顺序）

1. 管理员在云托管控制台核实占用的发布任务；正在运行则等待完成，历史未结束任务按平台流程结束，保留当前正常流量。
2. 重试兼容过渡灰度版本，核实normal/ready与实际承载版本；管理员确认兼容版本流量后才允许迁移。
3. 管理员创建生产备份，确认成功及可用隔离恢复路径；不得要求提供凭据到聊天。
4. 0014→0018 additive migration，current/check与投影差异校验；再创建新策略灰度并做业务验收。
5. 用户本地客户端验证新策略；全量切流仍为人工门禁。回滚保留新数据并停止相关新写入口。

后端488通过、MySQL24通过、前端200通过、四组规模/迁移/静态检查结果与限制见
`docs/quality/evidence/FAIR-REVIEW-PROJECTION-20261007.md`。
