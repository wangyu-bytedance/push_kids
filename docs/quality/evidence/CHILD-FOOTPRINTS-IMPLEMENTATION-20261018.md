# 孩子照片足迹 — 2026-10-18本地实现与验证

- Feature/UI: FEAT-012 / UI-018，集成FEAT-002/005/006与UI-001入口。
- Spec: [SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04](../../../specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)，`VERIFYING`。
- Approval: 用户2026-10-18“落地编写代码”，承接唯一Spec04/Architecture03；DREV01已在Q19批准。仅本地开发/合成验证，不包含部署或真实儿童素材外发。
- Checkout baseline: `8f3c5b04e61c96d4c19cf9eefd26514a8a095e1a`；本轮未提交/推送。原有通知未提交修改保留，不混作足迹改动证据。
- Architecture: `ARCH-20261017-CHILD-PHOTO-FOOTPRINTS-03`；FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02沿用。
- Release: [本地状态及后续门禁](../../deploy/releases/20261018-child-footprints-local.md)。

## 已实现的范围

`apps/api/src/push_kids/footprints/`独立拥有导入、照片、到访日、scope revision与成员AI偏好五表。路由只处理传输；imports/service/reads/media_service分别负责导入、命令、有界查询与私有媒体授权。纯策略无框架依赖，地图固定适配器与AI专用合同分离。bootstrap注册领域模型、worker和readiness，迁移0021接本地已有0020，无历史回填。

一批一孩子、最多20张，待整理200张；JPEG/PNG/WebP、10MiB、4000万像素单帧，HEIC明确转换提示。EXIF日期、偏移与GPS独立读取；无日期不使用上传时间。解码在独立进程运行，10秒硬超时；展示2048/缩略320且去元数据，不上采样。首次显式AI同意按成员保存，worker在派发前重验成员、偏好、版本及地点，只传已去元数据展示图；最多三个候选，允许拒答，不写正式事实。

家长明确确认产生place+local-date到访日，正式照片逐张纠正/删除同步更新统计及视图。拍摄日内先parent day_order，再已知时刻、确认时间与ID稳定排序；只知日期不造UTC时刻。已上传照片168h固定到期，读取立即拒绝，到期物理清理独立于读取；元数据/派生成功后原件24h清理，正式展示图不随草稿TTL删除。持久任务有5分钟租约、最多3次尝试，清理耗尽可由manager查询/重试，不把冻结家庭排在队首而饿死其他家庭。

所有读取/写入经家庭孩子边界，viewer只读；上传者拥有票据/claim，云对象走既有精确路径/owner验证，预览签名60秒或鉴权本地内容，均no-store，不提供原件下载。归档允许既有槽位和草稿继续，不能新增；删除冻结与worker串行。data_management先清媒体，再调用足迹owner在原事务purge，孩子删除保留兄弟档案与家庭偏好，家庭删除清偏好。

小程序记录页入口通向`pages/footprints/`。孩子/日期贯穿时间线、回放和点亮；有导入说明/按需AI、批量核对、未知字段、失败恢复、归档草稿、单图编辑/删除、2048预览及20张画廊分页。播放跟随当前地点、可暂停/拖动，离开停止；连线只示意顺序。切孩子/离开后忽略迟到回调、释放临时预览。翻草稿下一页停止首屏轮询，保留后续页选择。

## 最新实际检查

全部命令均于本次实现后运行；使用仓库`.venv/bin/`执行器，未借用历史通知或HTML证据。

| 命令/范围 | 实际结果 | 限制 |
|---|---|---|
| `.venv/bin/pytest tests/unit tests/integration tests/contract -q --tb=short` | **639 passed, 22 skipped, 84 warnings**，74.55s | skipped为环境/秘密门禁，含新增MySQL足迹竞争；不是通过。警告主要为既有httpx/SQLite日期适配弃用 |
| `npm test` | **258 passed**，0 failed/skip；WXSS修正后再次运行，1245.55ms | JavaScript状态/事件mock；原生显示另有隔离布局证据 |
| `.venv/bin/pytest tests/performance/test_footprints_reads.py -q --tb=short` | **2 passed** | SQLite，50k照片分别集中1个到访与分布1000到访；非MySQL性能证据 |
| `.venv/bin/ruff check .` / `ruff format --check .` | **PASS**；578文件格式检查 | 全工作区含原有通知修改 |
| `.venv/bin/mypy apps/api/src` | **PASS**，121文件 | untyped body保留工具提示，未宣称严格全类型覆盖 |
| `npm run lint:miniapp` | **PASS** | 不替代微信编译 |
| `.venv/bin/python tools/check_architecture.py` | **PASS**，4个纯策略/121模块runtime及lazy import DAG | 不覆盖动态反射或完整test-only依赖图 |
| `.venv/bin/python tools/validate_miniprogram.py` | **PASS**，17页，源码1152541字节 | 原生按钮WXSS修正后重跑；静态校验，不是完整原生验收 |
| `node tools/footprints_geometry.js` 三视口及 `audit` | **72份节点JSON+72张PNG，24态×3，断言/截图SHA通过** | 320×568、390×844、430×932，隔离合成布局；见[原生证据及限制](child-footprints-20261018/native/README.md)，TP09仍PARTIAL |
| `.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | **PASS** | 冻结证据完整性，不是实现视觉一致性批准 |
| `uv lock --offline` | **PASS**，Pillow已成为运行依赖 | 没有外部供应商调用 |
| 文档相对链接/尾随空白审计、`git diff --check` | **PASS**，16份当前文档、83个相对链接目标存在，无已跟踪diff空白错误 | 历史部署事实不在本次重验范围 |

足迹专用测试：integration18项、迁移2项、元数据unit2项、frontend11项、50k性能2项。`test_footprints_mysql.py`提供真实MySQL双session确认门禁，但本机未配置隔离DB故skip。HTTP请求/响应和错误通过integration验证。

迁移测试覆盖空库与0020升级、模型/DDL五表一致、已有数据保留、非空拒绝破坏性downgrade与清空后回退。查询测试证明timeline最多5条、map最多7条、playback最多5条SQL；top4由每访问复合索引LIMIT4子查询合并为一次查询，避免大到访的平方扫描；响应分别小于512/256KiB。SQLite计划使用tenant-leading visit索引。追加tracemalloc后专用2项重跑通过：1个到访峰值682236字节，1000到访峰值2244390字节，均低于16MiB测试阈值；这是Python有界读取分配峰值，不是进程RSS、解码器或原生内存，真实MySQL EXPLAIN仍未采集。

合成图片只含纯色像素，无真实儿童。覆盖未知日期、去EXIF、云/本地响应不泄露原件、固定168h、24h仅删原件、正式保留、清理失败3次/manager重试、归档续接、冻结队列公平、跨家庭/角色、成员同意隔离、逐张纠正/删除、兄弟档案媒体保留和parent-vs-worker交错。迟到解码不覆盖家长字段；候选查询后抢先确认也不被后台退回草稿。

中间失败已修复后重跑：首次类型/格式/lint问题；预览top4二次扫描；新解码进程初用`-m`时pytest路径不能被子进程继承，改为固定本地脚本入口，之后18项integration通过。中间失败不计为当前PASS。

## Spec测试点逐项收口

PARTIAL只表示列出的本地子集通过，不代表整个验收点通过。

| 测试点 | 当前状态 | 已有/缺少证据 |
|---|---|---|
| TP01 | PARTIAL | 合成EXIF/坏日期不吞GPS/未知日期/去元数据/10s超时通过；DST/日期线和完整格式方向真值矩阵待补 |
| TP02 | NOT_RUN | 40来源真机选图/EXIF保留率及HEIC转换验证待授权素材/设备 |
| TP03 | NOT_RUN | 100张分层AI真值、错误/拒答/费用评估未进行 |
| TP04 | PARTIAL | 本地导入/确认幂等、指纹冲突、版本/迟到和部分批次恢复通过；云认领真实端到端及MySQL竞争待验 |
| TP05 | PARTIAL | 本地跨家庭/角色/成员偏好/归档/冻结和鉴权预览通过；双账号staging及移除/退出全路由云媒体矩阵待补 |
| TP06 | PARTIAL | scoped owned-data真实删除编排、清理失败3次恢复、其他孩子资源保留通过；真实云对象/缓存及目标MySQL回滚待验 |
| TP07 | PARTIAL | 同地同日、时间/parent顺序、未知/无点、修改/删除重算、跟随/暂停/过期回调通过；跨境真实坐标/日期线待验 |
| TP08 | PARTIAL | SQLite50k两分布、查询/响应/分配峰值及索引计划通过；真实MySQL5.7与设备资源证据缺失 |
| TP09 | PARTIAL | 用户解锁后24态×3原生节点/截图/SHA通过，修正按钮尺寸/间距；27态基线还缺7态，完整插件包、设计一致性、iOS/Android及地图相册授权/真实交互矩阵未通过 |
| TP10 | PARTIAL | 全量本地学习/规划/活动/删除回归通过；供应商/隐私声明、日志人工审计及真机回归待补 |
| TP11 | PARTIAL | 固定168h、24h原件资格、正式保留、归档入口、偏好隔离与worker确认竞态通过；真实MySQL边界竞争/撤回同意并发待验 |

## 独立只读代码复审

Reviewer `footprints_readonly_review`按code-review流程只读审查当前领域/媒体/清理接线/小程序，排除通知改动。最初CR001–007涉及top4性能、同日排序、清理恢复、首文件重试、画廊返回、清回未知、路由职责，均修复并回归。

最终CR008复现ORM identity-map竞态：worker选中候选后等待家庭锁，家长已确认，但旧ORM值可能让worker把正式记录置ready。当前只选作用域标量，加锁查询`populate_existing=True`，领取/派发/成功/失败落地均拒绝confirmed业务终态。新增真实confirm插入candidate与guard之间的测试；Reviewer独立执行两次内存诊断，确认正式version保持且旧ORM对象刷新正确。

最终disposition：**代码review PASS；CR008 CLOSED，已审范围内没有剩余有证据的P0/P1**。Reviewer没有独立重跑全量pytest，以上数字由实施者运行。此结论不是生产、隐私、设计或真机验收批准。

解锁后新增WXSS/几何工具只读复审：修正规则与原生矩形相符，没有发现P0/P1回归。CR009为候选位于滚动区外、截图不能目检的P2覆盖缺口；已增加副本原生scroll-top夹具和候选垂直边界断言，补采可视候选。最终独立复核**PASS，CR009 CLOSED**；72份audit、72张PNG及外部manifest的144个节点/图片哈希、14个源码哈希、两副本12个文件哈希均通过。详见[原生证据](child-footprints-20261018/native/README.md)，不扩大到完整包/真机/设计批准。

## 未完成的验收与已知差异

1. **全球底图未验收。** 当前自动范围取最密集30°空间网格的包围盒，空态中国、显示范围外到访；世界总览为经纬度点位图与列表，可下钻原生map。它不满足“真实全球底图已验收”的结论；首版全球合同仍开放，不把世界改为后置。Tencent固定接口的海外覆盖、配额/商用条款/费用与实际坐标转换均未核验；缺密钥时不伪造地点或转换，原WGS84点单独计待处理。
2. **原生验收部分完成。** 用户回复“已解锁，可以继续原生验证”后，隔离足迹页面成功启动；24态在320×568、390×844、430×932导出72份有效节点/PNG并通过断言。真实原生默认按钮宽度问题已修复；长姓名、插画缩略图、长候选可视换行已补验。副本关闭云、替换load、移除报41002的语音插件并增加测试滚动绑定，不能代表完整包编译/真实业务成功。批准27态中records/import/saved/denied/photo-delete/expired/draft-delete的原生矩阵、iOS/Android、权限/键盘/字体放大、前后台及真实播放手势仍待补；完整范围仍未通过。详见[逐项原生范围](child-footprints-20261018/native/README.md)。
3. **设计一致性待核对。** DREV01源SHA仍为`58982a8241094d1fbc6da97b6eb7d16a7f4bb046a7538b76c6c67eba893c896e`，81手机图/桌面清单不改。实现中的清空日期/时刻、同日排序控件、字符图标/圆角及全球呈现需纳入后续设计差异评审；如可见差异，另立DREV并批准，无工程豁免。
4. **真实MySQL5.7未运行。** 隔离测试URL未配置；新迁移、锁竞争、50k计划/内存和删除事务必须在目标版本验证。SQLite的时序钩子不替代真实锁竞争。
5. **真实素材/供应商未运行。** TP02至少40路径真机EXIF保留率、TP03至少100张分层地点真值、iOS/Android相册与展示清晰度、跨时区/日期线真值、双账号云对象owner/撤销、全量隐私日志/条款核查待补。当前没有发送真实儿童照片到AI、地图或其他外部服务。

## 文档与生命周期核对

按实际diff核对并同步Feature012及关联002/005/006、Behavior038–040、Architecture03、UI001/018、设计索引、测试策略、Spec与目录索引、发布状态；“未批准/无实现”当前措辞已更新，历史研究/Q19仍保留原语境。原有通知变更未替代或撤销。新增代码实现不冒充生产事实；全球底图与原生设计差异明确保留。

解锁续验的生产diff仅足迹WXSS，工具/原生证据单列。逐项核对：Feature012、UI018、设计/Feature/Spec索引、测试策略、实现证据及本地发布记录同步；Behavior038–040、Architecture03、UI001及关联002/005/006合同无新的语义/边界变化，核对后无需改写。冻结DREV01不变，当前文档无“仍锁屏/没有有效原生导出”的冲突正文。72对节点/PNG、当前工具/样式源码及隔离副本外部manifest哈希由实施者复核通过。后端本次续验没有代码改动，未重复运行639项服务端回归，表内保留本轮实现后的实际结果。

Spec最终为**VERIFYING / specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md**，尚不能DONE/迁移completed。恢复条件是上述验收/设计门禁完成；真实全球合同若需变更，先明确新Spec revision并批准。未部署、未迁移云DB、未上传、未设体验、未提审、未正式发布。
