# 旅行日记全链路修复验证 — 2026-10-25

本文件保留原执行时点的实施/验证与未交付结论；2026-11-01旅行三Spec已由039/0.1.17交付，DONE/completed，用户照片回看/分页/双账号门禁确认PASS。当前生命周期与平台阶段以[成功上传记录](../../../deploy/releases/20261101-client-0.1.17-upload.md)为准；下方VERIFYING/active/未上传仅代表原时点，设备/内容未验及历史FAIL不改为通过。

- Stage: LOCAL_IMPLEMENTED / VERIFYING / NOT_UPLOADED / NOT_DEPLOYED
- Approval: 用户明确批准“Spec01＋Architecture01＋DREV01，按此实施”；[BUG-035](../../../../specs/completed/BUG-035-TRAVEL-DIARY-END-TO-END.md)记录批准原文。
- Base: `0576ac30464908154c624effed41df6dfa3110cc`；任务开始前其他文档、Spec和发布记录修改均保留。
- Current diff: footprints前端恢复/编辑/确认/回看及后端有界焦点画廊；无DDL、依赖升级、provider或云配置变更。
- Delivery: 本轮没有上传代码包、部署、设体验、提审或正式发布；037/0025与已上传客户端0.1.16是此前版本。三张用户照片已上传真实云端草稿，见下方独立数据验收。

## 已修复并验证

同一家庭/孩子/成员内，系统选图、选点与大图期间hide/show不再废弃操作；真正切身份、孩子或卸载仍拒收迟到回调。上传保留批次幂等键和成功部分，失败继续剩余文件。返回草稿恢复选择、版本、预览和处理轮询；表单不被首页刷新覆盖。

独立只读复核发现CR-001：设置保存未完成时hide→show，onShow因saving提前返回；随后保存结束没有补载已释放的首页缩略图。已退出只读阶段，在原批准生命周期范围修复：同操作上下文且已返回前台、显示代次变化时，保存成功后重载；仍在后台则由下次onShow恢复。两种返回/保存时序回归先红后绿，原生方法流程验证缩略图恢复；最终只读复核另列。

缺日期主动作进入仅补所选缺日期照片的面板，保留已有日期，不默认填今天。单张编辑可看当前照片。批量保存和分批确认记录成功部分，失败保留输入/剩余选择；版本冲突可读取最新版本再继续。点击缩略图携带photo_id，经有界focus窗口打开该照片，前后窗口用服务端游标，不扫描完整历史。

## 自动化与静态检查

| Check | Actual result / boundary |
|---|---|
| `node --test tests/frontend/footprints.test.js` | PASS 41/41；新增12项动作回归，含相册生命周期、补日期保选、部分成功重试、冲突、选点返回、精确回看和CR-001两种设置保存恢复时序 |
| `npm test` | PASS 347/347，0 fail/skip/cancel；records真正卸载测试改用onUnload，普通hide允许恢复 |
| `.venv/bin/python -m pytest tests/unit tests/integration tests/contract -q` | PASS 781，46条件skip，108既有警告；在最终MySQL索引hint前执行，最终reads改动后补跑下两行专项 |
| footprints integration / performance / MySQL未配环境专项 | PASS 21，3条件skip；最终源码，含深层focus、双向/旧cursor、归属、删除/归档及SQLite五万规模 |
| 真实MySQL5.7.44＋SQLite规模/确认并发专项 | PASS 5，0 skip；独占Docker临时库/临时凭据，结束销毁，见[摘要](mysql57.json) |
| `.venv/bin/ruff check .` / `format --check .` | PASS；最终753 files already formatted |
| `.venv/bin/mypy apps/api/src` | PASS；150 source files |
| `npm run lint:miniapp` | PASS |
| `.venv/bin/python tools/check_architecture.py` | PASS；150模块依赖图无环 |
| `.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | PASS；批准源/导出SHA未改 |
| `.venv/bin/python tools/validate_miniprogram.py` | PASS；17页，最终源码1235050字节（不是上传包大小） |
| `git diff --check` | PASS |

MySQL五万照片含单大到访和1000到访分布，focus在第40000条并前后分页；每页≤20、领域查询≤6、JSON<64KiB、单次<500ms、内存增量<16MiB。实际计划检查gallery索引且无filesort。首次实库选PRIMARY/index_merge不合预算，已在既有Photo查询及反向边界探测使用MySQL专用`FORCE INDEX (ix_footprint_photo_gallery)`，复跑通过；SQLite不受hint影响，无新增索引。MySQL确认并发夹具对DATETIME秒级舍入采用最多3秒有界worker轮询，生产worker未改。

`uv run`未成功（用户cache沙箱不可读），直接使用既有.venv，未安装/升级依赖。原始安全输出保留本机`/private/tmp/bug035-{front-full-cr001,front-cr001,backend-full,backend-focused-final}.txt`。CR-001修改后前端重跑；后端未再改，不重复全量。独立只读review在实施和文档收尾后执行，结论见本会话最终回复。

## 三张真实照片的隔离API验收

三张用户JPEG为130531/240796/241000字节，1080×1440/1080×1920/1080×1920，均无EXIF日期/GPS。复查Pillow主/嵌套EXIF均为空，JPEG仅APP0、无APP1 EXIF/XMP或APP13 IPTC，不能从当前字节取回拍摄日期。代码读取DateTimeOriginal及offset，不以文件名、下载/上传时间代填。用户仅提供城市“大连”，未提供日期。原件、派生图、私有URL、身份和原始模型数据不进入仓库或普通日志。

最终源码使用生产FastAPI、内存SQLite、临时私有媒体和test provider：3/3上传及worker成功，3/3有展示图，日期/地点保持空；缺日期确认409。仅在隔离库填合成日期/地点后确认200，统计3照片/1到访日、时间线/地图/回放各1条，第三张focus准确；跨家庭预览404。临时媒体退出销毁，无外部AI、真实档案确认或云写入。

content路径两张展示图触发既有JSON预算告警（仅route/size/status），HTTP仍200；本轮不扩展预算政策。脚本`/private/tmp/push-kids-travel-realphotos-20261025.py`从Downloads外部注入真实照片，未复制到仓库。

## 原生三尺寸与实际操作

[源SHA与42份节点/PNG清单](source-native-manifest.json)绑定7份当前前端文件、2份后端文件及每张原生截图SHA。320×568、390×844、430×932各14态，42份无几何错误：横向边界、44px目标、14px正文、48px/16px主CTA、标题/关闭间距、独立滚动及面板边界通过。状态为consent/uploading/review-missing/batch-date/edit/review-ready/upload-error/processing-error/conflict/confirm/saved/gallery-focused/readonly/edit-keyboard。

重放：`.venv/bin/python tools/prepare_travel_diary_native.py`建立禁云副本，官方CLI在9586启动；开发者工具选精确机型后执行`node tools/travel_diary_geometry.js 320 9586`（390/430同理）。基础库3.16.2，DPR2/3。副本移除语音插件、使用合成transport，增加测试setter/滚动取证绑定；生产模板/样式/controller不替换。键盘态为原生面板配210px占位，不是真实软键盘或真机验收。

430尺寸实际原生点击：记录→旅行→授权→系统文件选择器选用户三张照片；生产getFileInfo/getImageInfo执行，上传走隔离transport；全选→补日期→原生日期picker→保存，3项选择保留；确认后统计/时间线更新；第三缩略图打开第三张；正式编辑输入“大连”后放弃保护出现；回放开始/暂停可操作。测试日期只在隔离副本使用，截图仅合成插画，不保存用户照片。

首次点亮点击时，测试transport误返字符串marker id（真实API本就返回数字），该次地图不通过。修复测试夹具并重编译后，官方原生自动化调用生产方法重走上传→补日期→保选→确认→第三张/前一张→数字marker地图→回放，并在CR-001修复后补验设置保存中hide/show→保存结束缩略图恢复，[结果PASS](native-method-flow.json)。42组节点/PNG也在CR-001最终源码上重采。这是方法级原生结果，不写成修复后CUA地图点击或真实底图通过。初次副本基础库3.17.4本机未安装，改用已安装3.16.2后才取证；生产配置未改。

## 真实完整云客户端与剩余门禁

解锁后，完整AppID/插件、useCloud=true客户端加载本轮前端，原六六照片0/草稿0、AI开关true。实际点击同意与系统文件选择器，仅选用户指定三张JPEG；真实upload-ticket→上传→claim→worker→展示图/草稿已执行。上传曾出现“无法连接云服务，请稍后重试”；实际点击重试两次后同一稳定批次三张全部收讫，无重复草稿，成功项未重传。错误根因未定位，不写成已证明的网络或数据库故障。

真实AI终态为两张failed/location_unavailable、一张succeeded但候选为空；三张均ready、有展示图、日期null，不能宣称AI地点质量通过。人工路径仍可用。原生全选→批量编辑；CUA输入没有触发input，改用官方自动化调用生产editField填用户提供的“大连”，随后实际点击保存。首次遇worker版本更新产生409；实际点击读取最新版本后输入/三项选择保留，再保存成功。原生缺日期CTA进入空日期面板，空值保存显示字段错误，未代填或确认正式到访。

最终只读核验：3草稿、0正式照片/到访日/地点/城市统计；三张city“大连”、local_date=null，选择3。真实缩略图三张和单张编辑预览在原生画面可见，未保存到仓库。另行wx.getImageInfo远程URL探针3次均失败，开发者工具提示下载域名不在合法列表；生产downloadPreview云路径直接给image/previewImage短期HTTPS地址，不走该探针的downloadFile路径。不能宣称解码API通过，也不据此推翻组件实际显示；未修改域名配置或安全校验。生产onHide/onShow方法调用后选择/表单保留，预览异步恢复；这不是物理真机后台验收。[脱敏摘要](cloud-drafts.json)不含照片、ID、URL或原始模型输出。

真实草稿链路已验，真实日期和正式确认仍待家长；旧037未包含新focus实现，完整新前后端云端精确回看须未来另授权后端优先发布。iOS/Android相册、选点、大图/后台、真实键盘、大字体、读屏、全球底图及家长产品验收NOT_RUN；AI真实调用已执行但质量未通过。Spec保持active/VERIFYING，不再以锁屏作为当前阻塞。本轮发布不在授权范围，未触发发布人工操作门禁。

## 设计与文档闭合

[DREV01源](../../../design/frontend/prototypes/DREV-20261025-TRAVEL-DIARY-E2E-01/index.html)和[批准42张导出清单](../../../design/frontend/snapshots/UI-018/DREV-20261025-TRAVEL-DIARY-E2E-01/APPROVAL.md)保持冻结；HTML仅作批准证据，不替代原生42组。最初29前端/20后端是历史基线，当前结论使用本报告修复后结果。

已同步FEAT-012、BHV-038/040/041、Architecture、UI-018/UI-001、Frontend Design、Test Strategy、Spec/索引和[本地交付](../../../deploy/releases/20261025-travel-diary-e2e-local.md)。按当前diff替换“尚未实施/待批准”“当前源码全部上传/匹配037”及“锁屏未上传真实草稿”等冲突正文；其他发布记录和批准快照保留历史范围。[闭合检查](closure-check.json)记录12份文档的本地链接、7前端/2后端源SHA及42原生PNG/节点一致性，批准设计源SHA未改。独立只读review在此后执行，结论见本会话最终回复。
