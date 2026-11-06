# BUG-037 — 编辑计划页脚与提示本地交付记录

- Date: 2026-11-01
- Release revision: REPORT-FOOTER-TIPS-20261101-PREVIEW-NATIVE-03
- Task: [Spec01](../../../specs/completed/BUG-037-REPORT-FOOTER-TIPS.md)
- Approval: 用户2026-11-01“批准 Spec01 + DREV01”
- Current stage: OFFICIAL_PREVIEW_READY / VERIFICATION_PARTIAL
- Spec lifecycle: VERIFYING，保留`specs/active/`

两个共享WXML/WXSS文件已实现条目/科目Flex分页与专用提示容器；
未改controller、API、后台、数据库或全局五Tab。来源SHA、349项前端回归、
静态/政策、430双宿主48组原生节点和16组方法/状态/尾部检查见
[本轮证据](../../quality/evidence/REPORT-FOOTER-TIPS-20261101.md)。

齐套03已补320/390/430双宿主144组原生PNG/节点，默认字体模拟器矩阵PASS；用户已解锁，手机未扫码。
另从0.1.17冻结源复制并仅替换本Spec两份文件，官方preview成功1,192,127字节；
168份来源与[二维码](../../../output/BUG037-device-preview-20261101.png)绑定本次修复，
另外官方[无线真机调试码](../../../output/BUG037-remote-debug-20261101.png)已生成，等待扫码后设备取证。
[齐套03](../../quality/evidence/REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)保留独立debug本地插件41002失败，不改写原01/02结果。

| 阶段 | 本增量状态 |
|---|---|
| 本地源码实现 | PASS，两份共享文件 |
| 自动化回归与静态 | PASS，349项与必需校验 |
| 原生基线 | PARTIAL，320/390双宿主20组；提示已复现，分页掉行未复现，430缺失 |
| 修复后原生 | PASS，两宿主三视口144组PNG/节点/解码/SHA；默认字体合成模拟器范围 |
| 设备/大字/读屏/实际触摸 | NOT_RUN |
| 本增量CLI preview | PASS，168份冻结生产源＋两份批准替换；1,192,127字节，扫码尚未完成 |
| 本增量开发上传 | NOT_RUN |
| 体验/审核/正式发布 | NOT_RUN |
| 后端或数据库交付 | N/A，无对应变更 |

当前[0.1.17官方上传](20261101-client-0.1.17-upload.md)采用168份冻结源，
明确排除了BUG-037的两份本地增量，其1,191,019字节包体不能作为本任务云端交付证据。
本轮没有Git提交/推送或新增客户端版本。小程序校验的1,234,665字节是工作区源码资源预算。

下一次客户端交付前按[部署入口](../README.md)与前端playbook执行必需检查和人工门禁，
重新绑定本Spec实际源SHA和版本；不能上传隔离合成配置/API。
成功上传覆盖本增量后，按用户批准的云交付开发完成规则设DONE并移至completed，
未验收的设备/可访问性项仍独立保留真实结果。当前未达到该归档条件。

回退仅撤回本Spec两个共享文件的具体增量，不改并行用户工作；无需数据回滚。
Feature/UI/Spec/索引和设计证据已同步，Behavior/Architecture/测试策略核对无合同冲突。
