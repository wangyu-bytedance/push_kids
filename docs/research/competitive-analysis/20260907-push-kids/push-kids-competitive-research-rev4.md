# push_kids 功能与体验深度调研：竞品格局、能力缺口与后续优先级

<callout emoji="🎯">
**核心判断**
1. **「AI 只碰录入」这条边界是这个产品最稀缺的资产，不是保守的妥协**：仓库契约里的三条硬规则（AI 输出仅为可编辑草稿、AI 不评分不判定掌握度、复习日期由确定性策略产生）同时挡住了合规风险与产品定位漂移；本轮核实的国内外产品中，没有任何一家在家长面板输出「建议明天复习什么」的处方 [[27]](https://support.khanacademy.org/hc/en-us/articles/360040168512-Khan-Academy-for-Parents-Quick-Start-Guide)，Prodigy 甚至主动声明答题量不等于进度 [[28]](https://prodigygame.zendesk.com/hc/es/articles/115001744726-Parent-Dashboard)。
2. **主链路已经闭环，剩下的短板集中在两个底座，而非功能数量**：录入到确认到排期到每日 Todo 的链路在仓库当前实现里已经跑通，近三个 PR（#1/#2/#5）都在还体验债；同期没有动过的两处是固定阶梯排期与自由文本知识点。
3. **竞品格局里的中间带确实空着，但空着有其原因**：国内 16 款、海外十余款检索范围内，有排期机制的产品操作者都是学生本人 [[23]](https://zyctb.com/)，以家长为操作者的产品记录对象都是错题或任务完成度、官方描述对「间隔重复／遗忘曲线／复习到期」零命中 [[15]](https://apps.apple.com/cn/app/id1325419855)；空白的直接原因是「家长代替孩子判断回忆结果」这件事在行业里没有成熟做法。
4. **排期升级的方向是可配置、可分材料的策略层，不是照搬 FSRS**：FSRS 至今不是 Anki 的默认调度器，作者本人于 2026-02-12 关闭了「默认启用」的 PR，理由是默认参数下 FSRS-6 在排程上并不优于 SM-2 [[4]](https://github.com/ankitects/anki/pull/4391)；真实课堂环境的复现研究也未发现长间隔重复的收益 [[13]](https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.3245)。
5. **后续三个月的优先级是「排期策略参数化 → 知识点身份层 → 提醒闭环收口」**：前两项是新增底座，第三项是把已有 Spec（FEAT-003／PR #6）收口到可上线；同时有三件事明确不建议做——积分排行式激励、自建题库与讲解出题、全量采购知识点树。
6. **上线前的硬约束不在功能侧，而在儿童数据与微信类目两处**：14 周岁以下个人信息属敏感个人信息、须单独同意 [[51]](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)，导出与永久删除是法定义务而非可选功能 [[52]](https://www.cac.gov.cn/2023-10/24/c_1699806932316206.htm)；微信长期性订阅消息目前不向商业服务类目开放 [[55]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html)，提醒能力必须有站内兜底。
</callout>

## 一、产品定位：AI 只碰录入，是最该守住的边界

### 1.1 定位与代码里已固化的三条边界

<html5-block alt="push_kids 产品身份卡：家长端「已学内容 + 复习计划 + 课外活动」微信小程序；字段含项目主体与仓库、技术栈与部署形态、AI 能力边界（高亮：AI 只出可编辑草稿，不评分、不判掌握、不排复习日）、复习排期策略（固定阶梯 1/3/7/14/30/60 天）、反馈信号（家长手工三态）、数据与隔离边界（家庭级隔离、多孩子上限 5、知识点为自由文本无教材锚点）、前端与设计体系、当前发布阶段（FEAT-001 MVP CURRENT、FEAT-002 IMPLEMENTING、1 个 open PR）。" data-ref="html5_1"></html5-block>

*图 1：push_kids 产品身份卡——定位、技术栈与代码中已固化的三条 AI 边界（来源：仓库当前实现，2026-09-07 main 分支快照）*

把这三条边界写进仓库契约、而不是写进宣传语，改变了产品的性质：它不是一个「用 AI 帮孩子学习」的工具，而是一个「用 AI 降低家长录入成本」的工具。AI 承担的是把一张作业照片变成结构化草稿这一段，确认权、排期权、判断权都留在家长和确定性策略手里。

这条边界之所以值得守，有两层理由。合规层面，处理 14 周岁以下未成年人信息属于敏感个人信息，须有特定目的与充分必要性 [[51]](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)，而《儿童个人信息网络保护规定》第十四条明确要求使用超出约定目的与范围时须再次征得监护人同意 [[50]](https://www.gov.cn/gongbao/content/2019/content_5456808.htm)——「让模型判断孩子该学什么」正是最容易滑出原始告知范围的一步。产品层面，本轮核实的家长面板全部止步于呈现事实：Khan Academy 的下一步由家长手动布置 [[27]](https://support.khanacademy.org/hc/en-us/articles/360040168512-Khan-Academy-for-Parents-Quick-Start-Guide)，Google Classroom 的家长摘要明确不含成绩 [[24]](https://support.google.com/edu/classroom/answer/6386354?hl=en)，Prodigy 在家长面板里专门解释「回答更多题目并不必然意味着课程进度提升」[[28]](https://prodigygame.zendesk.com/hc/es/articles/115001744726-Parent-Dashboard)。行业在这条线上的一致克制，说明它不是能力不足，而是有意选择。

### 1.2 题库刷题与家校通知之间的空位

需求侧的强度是确定的，小学阶段正是家长深度介入的峰值学段。苏州市教育质量监测中心的研究显示，家长在「作业检查与批改」环节的参与率小学为 72.3%，显著高于初中 51.1% 与高中 23.2% [[64]](http://jyzljc.suzhou.edu.cn/jyyj/lwfx/1229.html)；基于北京大学中国家庭追踪调查的测算显示，小学生家长每周辅导作业时长从 2010 年的 3.67 小时增至 2018 年的 5.88 小时，折算日均约从 31.5 分钟增至 50.4 分钟（日均为本文换算，非原报道口径）[[62]](https://m.thepaper.cn/wifiKey_detail.jsp?contid=11504352)；中国青年报社会调查中心对 1980 名家长的问卷显示 84.0% 会因陪写作业头疼 [[63]](http://www.edu.cn/edu/ji_chu/ji_jiao_news/201711/t20171121_1568052.shtml)。教育部门户刊载的地方案例中，68% 的家长自评「缺少正确方法技巧」，而学生最不满意的一项是「晚上闲暇时间，家长布置过多过难的家庭书面作业」，占比约 60% [[66]](https://hudong.moe.gov.cn/jyb_xwfb/moe_2082/2021/2021_zl53/dddxal/202307/t20230711_1068364.html)。

这组数据同时给出机会与红线。机会是家长有管理意愿却缺方法；红线是「双减」意见把「家长相应精力负担」列为需要减轻的对象，并严禁学校要求家长检查批改作业（该条针对学校，不禁止家长自主行为）[[61]](https://www.gov.cn/zhengce/2021-07/24/content_5627132.htm)。因此这个产品的成败判据不是「功能是否丰富」，而是「有没有把家长的时间占用压到低于它替代掉的那部分」。

供给侧确实存在空位。在本轮 16 款国内产品的检索范围内，有明确排期机制的两款——记忆卡片（pro，基于遗忘曲线的十个可编辑复习节点）[[22]](https://jiyikapian.cn/) 与智因错题本（闪卡采用 SM-2 调度）[[23]](https://zyctb.com/)——操作者都是学习者本人，智因甚至在官网写明只给家长周报、「不看具体题目」。而以家长为操作者的五款（小猿AI、爱作业、作业帮家长版、一起学、小盒AI学）记录对象都是错题、批改结果或任务完成度，官方描述中对「间隔重复／遗忘曲线／复习日／到期」关键词零命中 [[15]](https://apps.apple.com/cn/app/id1325419855)[[17]](https://apps.apple.com/cn/app/id1246135464)[[19]](https://apps.apple.com/cn/app/id913817574)。家校类产品的记录发起权在老师，家长是回收方 [[21]](https://banjixiaoguanjia.com/)。海外一侧的结论方向相同：homeschool 记录类产品（Homeschooly、Homeschool Manager）的家长录入与照片留痕已经很成熟，但产出物是 portfolio 与合规报表，记录之后没有下一步动作 [[31]](https://www.homeschooly.app/homeschool-tracker-app)[[32]](https://homeschoolmanager.com/)。

需要同时承认一个减分项：单纯「排一张复习计划表」这件事已被免费轻量工具覆盖，输入开始日期与学习组数即可生成逐日计划并导出到手机日历 [[68]](https://kachika.app/zh-CN/blog/ebbinghaus-forgetting-curve/)。所以真正的差异化不落在「会排期」，而落在三件事的组合：录入成本接近于零、排期对象来自真实发生过的学习内容、排期结果与家长当天的时间预算耦合。这三件里，第一件已经做到，第三件做了一半（`daily_budget_minutes` 分必做与可选），第二件的质量取决于知识点结构——正是第二章要谈的薄弱处。

---

## 二、能力现状：主链路已闭环，两处底座仍薄

> **本节要点**：仓库当前实现已经能完成一次完整的「录入—确认—排期—回流」，家长确认是唯一的正式记录生成门禁；但排期只有一套全局固定阶梯，知识点只有自由文本，这两处决定了产品目前只能沉淀记录、还沉淀不出学情资产。

### 2.1 从拍照到复习的主链路

<html5-block alt="push_kids 主链路机制闭环：1 家长拍照或文字录入（支持多图与历史补录）→ 2 AI 异步分析产出可编辑草稿（豆包/Ark 经 AnalysisProvider，上下文含年级、科目表、最近历史与当前到期待复习项）→ 3 家长确认门禁（高亮，唯一写入闸门，未确认不生成任何正式记录与复习项）→ 4 确定性排期（planning/domain.py 纯策略，固定阶梯 1/3/7/14/30/60 天，首个复习日＝学习日+1，模型不参与）→ 5 每日 Todo（按 daily_budget_minutes 分必做与可选，并解释为什么今天出现）→ 6 家长三态反馈回流（complete 前进一级、reinforce 降级强化、partial 取下一档间隔的一半），反馈只改变走到阶梯哪一级，不重算记忆稳定度。" data-ref="html5_2"></html5-block>

*图 2：主链路闭环中，「家长确认」是唯一生成正式学习记录与复习项的门禁（来源：仓库当前实现）*

这条链路上有两处设计值得单独指出，因为它们是外部同类产品没有的。第一处是 AI 的输入上下文里包含了「当前到期待复习项」，模型据此判断本次素材是学新还是温故——这让录入这一步同时承担了去重与归并的职责，而不是简单地新增条目。第二处是历史补录不制造过去的 Todo 债务，只安排一次当前检查；这条规则决定了家长补录上周内容时不会被一堆逾期任务淹没，是把「漏记」变成低成本动作的前提。

从 PR 历史看，迭代重心已经从「能不能用」转向「家长动线是否顺、视觉是否可长期维护」：#1 补齐界面解释性字段（Todo 为什么今天出现、来自哪次学习）、#2 修的是用户提出的六条真实反馈、#5 把小程序视觉与交互升级为 PKDS-2.0，动机写得很直接——家长通常在晚上、疲惫状态下打开这个小程序。体验债在被主动偿还，这是好信号，也说明接下来的边际收益更可能来自底座而不是再一轮界面打磨。

### 2.2 固定阶梯排期与无锚点的知识点

第一处薄弱在排期。仓库当前实现的 `REVIEW_INTERVALS = (1, 3, 7, 14, 30, 60)` 是一套全局固定阶梯，不区分科目、不区分难度、不区分孩子；首个复习日为学习日加一天；反馈三态里 `complete` 推进一步、`reinforce` 降级强化、`partial` 取下一档间隔的一半（`REVIEW_INTERVALS[next_step] // 2`，最小 1 天）。这套策略的优点是可解释、可预测、纯策略模块不依赖任何外部依赖；缺点是它只有一条轨道，任何材料、任何孩子、任何科目走的都是同一条曲线。

更关键的是反馈信号的信息量。当前只有三态、且由家长手工给出，没有任何题目层面的作答证据。这意味着即使换上更强的算法，它能吃到的输入也依然只有「间隔长度 + 一个三档评分」。第四章会说明，这个输入下界在形式上其实已经够用，但语义主体不同——家长评的是「看起来会不会」，不是孩子「有没有想起来」。

第二处薄弱在内容结构。`KnowledgeItem` 加 `Occurrence` 的设计已经把「知识点身份」与「每次出现的痕迹」分开，这个建模方向是对的；但知识点本身是自由文本，没有挂接任何教材或课标体系。有意思的是，仓库里已经存在一套 `subject_routing.py` 做科目清洗——拆分隔符、过滤「其他／未知」停用词、把「英文」归一为「英语」，目的正是保证科目目录干净。作者显然已经感受到结构缺失带来的麻烦，只是这套规则治理只做到了「科目」这一层，「知识点」这一层还完全裸露。

还有一处半薄弱需要提前记账：数据主权。当前只有孩子档案的归档与恢复（归档边界是「拦新增、放收尾」），没有永久删除孩子或家庭的接口与界面，FEAT-006 仍是 `PLANNED / NOT_IMPLEMENTED`。这一条在第七章会看到，它在法规上属于硬义务，不是可以排到很后面的功能。

---

## 三、竞品格局：四类玩家各解一段，中间带空着

> **本节要点**：把参照对象按「谁录入、记录什么、谁判定回忆结果」三条切成四类，可以看清 push_kids 的位置——它取了家长录入（家校类与家庭协作类的做法）与间隔排期（记忆软件类的做法）的组合，而这个组合在本轮检索范围内没有对手，也没有先例。

### 3.1 纳入的四类参照对象

<grid>
<column width-ratio="0.250000">
<callout emoji="📝">
**题库刷题类**
小猿AI、爱作业、作业帮家长版、一起学、小盒AI学。纳入理由：它们是家长晚间时间的真实占用方，也是「以错题为中心」这条路线的完整样本。
</callout>
</column>
<column width-ratio="0.250000">
<callout emoji="📝">
**记忆软件类**
Anki、Quizlet、Brainscape、墨墨背单词、RemNote。纳入理由：排期机制的技术上界在这里，能回答「自适应算法到底能带来什么」。
</callout>
</column>
<column width-ratio="0.250000">
<callout emoji="📝">
**家校通知类**
班级小管家、Google Classroom 家长摘要、ClassDojo、Seesaw。纳入理由：家长侧信息触达的成熟形态，直接给周报与提醒的设计参照。
</callout>
</column>
<column width-ratio="0.250000">
<callout emoji="📝">
**家庭协作记录类**
Cozi、S'moresUp、Greenlight、Homeschooly、Homeschool Manager。纳入理由：家长作为唯一操作者时的动线、权限与审批设计参照。
</callout>
</column>
</grid>

两类看似相关但被排除：一是学科类培训与课程销售产品，它们与本产品的类目资质路径完全不同（见 7.2），对功能决策没有可迁移性；二是学生自主刷题类工具，操作主体不是家长，其动线假设与「晚上三分钟」相反。需要说明检索边界：国内一侧覆盖 16 款产品，渠道为官网加 App Store 中国区官方描述加中文检索，未覆盖安卓独占长尾、未上架 App Store 的纯小程序与企业微信家校产品；海外一侧为一轮检索，非穷尽。

### 3.2 六个维度上的横向对比

| 维度 | push_kids（仓库当前实现） | 题库刷题类 | 记忆软件类 | 家校通知类 | 家庭协作记录类 |
|-|-|-|-|-|-|
| 目标用户 | 小学生家长，家长是唯一操作者 | 学生做题、家长检查，家长为监督者 [[15]](https://apps.apple.com/cn/app/id1325419855) | 自主学习者本人，多为中学以上及成人 [[1]](https://faqs.ankiweb.net/what-spaced-repetition-algorithm.html) | 学校或学区采购，家长为附属只读角色 [[24]](https://support.google.com/edu/classroom/answer/6386354?hl=en) | 有学龄孩子的家庭，家长主导 [[33]](https://smoresup.com/pricing/) |
| 谁录入 | 家长拍照或文字，AI 出草稿、家长确认 | 系统从批改结果自动生成错题 [[17]](https://apps.apple.com/cn/app/id1246135464) | 学习者本人手动建卡 [[22]](https://jiyikapian.cn/) | 教师发布，家长零录入 [[24]](https://support.google.com/edu/classroom/answer/6386354?hl=en) | 家长派任务，孩子交完成凭证 [[33]](https://smoresup.com/pricing/) |
| 内容结构 | 知识点身份加每次出现痕迹；知识点为自由文本，无教材锚点 | 题目级，附错因标签与知识点归类 [[16]](http://www.xiaoyuankousuan.com/baike) | 卡片级，牌组与标签自管理 [[3]](https://docs.ankiweb.net/deck-options.html) | 通知、作业与作品集条目，无知识结构 [[21]](https://banjixiaoguanjia.com/) | 任务与日志条目，可附照片，无知识结构 [[31]](https://www.homeschooly.app/homeschool-tracker-app) |
| 排期机制 | 确定性固定阶梯 1/3/7/14/30/60，全局同一套 | 未见间隔排期，只有同类题重练与打卡式计划 [[20]](https://apps.apple.com/cn/app/id1475739886) | SM-2 或 FSRS 自适应，FSRS 非默认、需手动全局开启 [[4]](https://github.com/ankitects/anki/pull/4391) | 无排期，事件驱动或按日／周摘要 [[25]](https://www.classdojo.com/) | 无排期，按周计划与循环任务 [[35]](https://www.cozi.com/cozi-gold/) |
| 家长角色 | 录入者、确认者与回忆结果判定者 | 拍照检查者与报告查看者 [[18]](https://apps.apple.com/cn/app/id1569820044) | 不适用，无家长端 [[7]](https://help.quizlet.com/hc/en-us/articles/48324742264077-Studying-with-Spaced-Repetition) | 接收者，可回私信 [[25]](https://www.classdojo.com/) | 派单者与审批者，审批为付费功能 [[33]](https://smoresup.com/pricing/) |
| 定价 | 未定价，当前为自用与内测阶段 | 免费加订阅，19–69 元／月区间 [[19]](https://apps.apple.com/cn/app/id913817574) | 免费到一次性买断，参数功能不额外收费 [[3]](https://docs.ankiweb.net/deck-options.html) | 国内免费；Seesaw 仅机构询价、无 C 端入口 [[26]](https://seesaw.com/pricing/) | 家庭订阅制，不按孩子数计价 [[34]](https://greenlight.com/plans) |

*表 1：六个维度上的横向对比，口径为各产品官方文档与 App Store 中国区描述，2026-09-07 取数*

矩阵读下来只有一条共性最值得注意：**录入自动化与排期科学性在市场上是互斥的**。凡是录入不需要家长动手的（题库刷题类、家校通知类），排期一律退化为打卡或同类题重练；凡是排期讲究的（记忆软件类），录入成本全部压在使用者自己身上，且没有家长端。push_kids 选的是「家长承担少量录入 + 系统承担排期」这个中间态，它的合理性建立在一个假设上：AI 把录入成本压得足够低，低到家长愿意每天付出两三分钟。这个假设成立与否，第六章会用时间预算再检验一次。

### 3.3 两轴定位坐标里的空白象限

<html5-block alt="竞品定位散点图：横轴为家长录入负担与参与深度（越右家长越接近唯一操作者），纵轴为复习排期的科学性与自适应程度（越上越接近按个体与材料难度动态定间隔）。记忆软件与错题类（Anki FSRS、墨墨背单词、Quizlet、智因错题本 SM-2、记忆卡片 pro）聚在左上：排期自适应但家长零参与；K12 题库批改类（小猿AI、爱作业、作业帮家长版、一起学与小盒、Khan Academy 家长面板）与家校通知类（班级小管家、ClassDojo/Seesaw、Google Classroom 家长摘要）聚在左下：家长参与浅且无间隔复习；家庭协作与记录类（Cozi、S&#39;moresUp、It&#39;s a Family Thing、Homeschool Moment）在右下：家长深度参与但记录之后没有排期。push_kids 位于右侧中低位——家长深度参与、有确定性排期但不自适应；右上角为本轮检索无人占据的空白区。" data-ref="html5_3"></html5-block>

*图 3：在家长参与深度与排期自适应程度两轴上，右上象限至今空着（来源：各产品官方文档，2026-09 口径，参见* [*[15]*](https://apps.apple.com/cn/app/id1325419855)[*[22]*](https://jiyikapian.cn/)[*[23]*](https://zyctb.com/)[*[24]*](https://support.google.com/edu/classroom/answer/6386354?hl=en)[*[33]*](https://smoresup.com/pricing/)*）*

空白象限不等于无人发现的机会，更可能是有难点没被解决。本轮核实的自适应排期产品全部要求学习者本人逐条自评：Anki 的 Again／Hard／Good／Easy [[1]](https://faqs.ankiweb.net/what-spaced-repetition-algorithm.html)、Quizlet 的 Repeat／Hard／Okay／Easy [[7]](https://help.quizlet.com/hc/en-us/articles/48324742264077-Studying-with-Spaced-Repetition)、Brainscape 的 1–5 信心自评 [[8]](https://www.brainscape.com/spaced-repetition)、墨墨的认识／模糊／忘记／熟知 [[9]](https://memodocs.maimemo.com/docs/2022_KDD)——没有一款由第三方代评。换句话说，push_kids 要占的这个位置，需要自己解决「家长代评」这个行业没有先例的问题。这既是壁垒，也是风险，它决定了第四章的判断方向：先把评分语义做实，再谈算法升级。

---

## 四、差距归因：短板在排期策略与内容锚点

> **本节要点**：固定阶梯的问题不是算得不准，而是只有一条轨道、对材料难度与个体差异都不敏感；知识点无锚点的问题不是不好看，而是让四条下游能力同时失效。两处都属于底座，功能数量补不上。

### 4.1 固定阶梯与自适应算法的实际差别

<html5-block alt="折线对比图：同一份材料前 6 次复习的间隔天数。push_kids 固定阶梯为 1/3/7/14/30/60 天，不论材料难易走同一条曲线；FSRS-6 默认参数、目标留存 90% 下，难材料（每次评 Hard）前 6 次间隔为 1/3/7/12/18/25 天，易材料（每次评 Easy）为 8/66/397/1875/7265/23933 天，第 6 次相差约 957 倍。前 3 次固定阶梯与难材料曲线重合，第 4 次起分叉，说明固定阶梯近似「平均难度、全部答对」的特例，对材料难度不敏感。纵轴为对数刻度。" data-ref="html5_4"></html5-block>

*图 4：固定阶梯对材料难度不敏感，自适应算法在同一材料上分叉出两条差距极大的轨道（来源：py-fsrs 6.3.2 默认参数实测、关闭 fuzz；SM-2 序列为按公开默认参数的近似实现，非移植 Anki 源码；参数口径见* [*[3]*](https://docs.ankiweb.net/deck-options.html)*）*

先把差别量化。仓库当前的固定阶梯累计到第 6 次复习为 1/4/11/25/55/115 天；按公开默认参数近似实现的 SM-2 在「全部答对」序列下为 1/3/8/20.5/51.7/129.8 天，前四次几乎重合。也就是说，固定阶梯近似于「平均难度、全部答对」这一种特例，它并不算错。真正的差别出现在材料分叉上：FSRS 默认参数、目标留存 90% 时，难材料（每次都评 Hard）前六次间隔为 1/3/7/12/18/25 天，易材料（每次都评 Easy）为 8/66/397/1875/7265/23933 天，第六次相差约 957 倍。同一套阶梯服务这两类材料，对难材料是复习不足，对易材料是把家长的时间浪费在已经牢固的内容上。留存目标同理：同为「全部答对」，目标留存 0.85／0.90／0.95 三档下的前六次间隔分别是 4/31/173/773/2859/9071、2/11/46/163/497/1346、1/3/8/19/43/89 天，而固定阶梯没有任何对应旋钮。

第三处差别是遗忘之后的回退。在「第三次遗忘」序列下，FSRS 的间隔为 2/11/2/5/12/28 天——失败后回落再重建稳定度；仓库当前的 `reinforce` 只降一级、`partial` 取半步推进，没有稳定度重算，连续两次困难与一次困难对后续曲线的影响几乎相同。

但方向不能因此写成「应该换成 FSRS」，有三条反向证据必须同时摆出来。其一是最直接的反证：FSRS 至今不是 Anki 的默认调度器，作者 L-M-Sherlock 于 2025-10-14 提出「Enable FSRS by default」的 PR，2026-02-12 自行关闭，理由原文是默认参数下的 FSRS-6 在排程上并不优于 SM-2 [[4]](https://github.com/ankitects/anki/pull/4391)；维护者另外给出两条反对意见，一是存量用户未跑过 FSRS 所需的参数优化即被按 FSRS 处理有风险，二是 Hard 按钮的语义至今仍令部分用户困惑 [[4]](https://github.com/ankitects/anki/pull/4391)。成年自主学习者尚且困惑于评分语义，家长代评的语义风险只会更高。其二是效果证据的口径问题：FSRS 官方 benchmark 的指标是记忆状态预测精度（Log Loss、RMSE、AUC），不是复习量减少多少 [[5]](https://github.com/open-spaced-repetition/srs-benchmark)；「同等留存下少 20–30% 复习量」一说仅见于 RemNote 的厂商文档且页面自标 beta [[6]](https://help.remnote.com/en/articles/9124137-the-fsrs-spaced-repetition-algorithm)。其三是场景外推的限制：实验室层面自适应排程确实在即时与延迟测验上优于固定排程 [[12]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6028005/)，但那是成人被试与卡片式材料；覆盖 2/3/4/6 年级真实课堂词汇教学的复现研究并未发现长间隔重复与检索练习的收益 [[13]](https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.3245)。间隔与检索练习整体证据充分，但学习者因元认知错觉而系统性低估、少用这两种策略 [[14]](https://www.nature.com/articles/s44159-022-00089-1)——这提示产品的真实价值在「替家长做了排期决策」这一点上，而不在算法精度上多领先几个百分点。

因此判断是：**固定阶梯要升级成可配置、可分材料的策略层，而不是替换为某个具体的自适应算法**。可以借的有三样东西。第一样是一个旋钮而非一套模型：仿照 desired retention 的思路给出松／中／紧三档，各档映射一张不同的间隔表，家庭级默认、科目级可覆盖 [[3]](https://docs.ankiweb.net/deck-options.html)。第二样是主题级排期范式：Incremental RemNote 对不逐题作答的条目采用 `interval = ⌈1.5^N⌉`，beta 的 Saturating Curve 从默认首间隔 5 天渐近到默认上限 30 天，并用 0–100 的优先级而非回忆评分做排序，积压时收敛到高优先级子集 [[11]](https://github.com/bjsi/incremental-everything)——这套「不判分也能排序」的范式与本产品的家长代评处境高度契合。第三样是积压兜底必须自己做：行业至今仍是人工兜底，墨墨系产品面对 1500 张卡逾期给出的官方建议是「提前签到、逐步消化」，压力分摊能力被列为后续低优先级 [[10]](https://memodocs.maimemo.com/docs/markji-help-260529)；家长场景下没有这种耐心，逾期收敛策略要和排期表一起设计。

还有一个前置条件容易被跳过。FSRS 的最低输入只有间隔长度与评分等级两项，不需要答题耗时、不需要客观判分 [[2]](https://faqs.ankiweb.net/frequently-asked-questions-about-fsrs.html)——仓库当前的三态反馈在形式上已经达到这个下界。真正欠缺的是语义可靠性：家长给出的 `reinforce` 到底表示「孩子想不起来」还是「我觉得他还不熟」，目前无从区分。所以升级次序应当是先把评分语义做实（见 5.2 的弱信号），再谈换不换曲线。

### 4.2 知识点无锚点的连锁后果

<html5-block alt="归因图：知识点为自由文本、未挂教材与课标锚点这一件事，并列导致五类后果——复习粒度失控（同一知识点的不同写法各自成条、各自排期，无归并键）、家长报表不可聚合（课标以学段×主题×内容要求给维度，自由文本挂不上任一层级，覆盖度与超纲判断都算不出）、跨孩子跨学期不可比（无稳定标识符则无法累积学情资产、做不了薄弱点归因）、AI 增量去重只能靠字面相似（识别重复材料没有概念级键）、外部题库与资源取不到（菁优、学科网 API 均以章节与知识点为检索入参）。五者共同汇聚到结论：内容锚点是比功能数量更靠前的底座。" data-ref="html5_5"></html5-block>

*图 5：知识点为自由文本这一件事，四条后果并列汇聚到「内容锚点比功能数量更靠前」（来源：仓库当前实现，外部对照见* [*[37]*](http://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html)[*[43]*](https://open.xkw.com/exam/chapters/)[*[45]*](https://github.com/haolpku/K12-KGraph)*）*

图里四条后果中，最容易被低估的是第四条：外部资源接不进来。学科网的「章节知识点推题」与菁优的题库 API 都以章节与知识点标识作为检索入参 [[43]](https://open.xkw.com/exam/chapters/)[[44]](https://www.jyeoo.com/open/quesapi)。这意味着锚点不只是报表的聚合键，它同时是将来任何「给一道同类题」「给一段微课」能力的钥匙；没有锚点，这条路根本走不通，与预算无关。

但下一步不能是「挂上课标或买一棵知识点树」，四条路线都有硬约束。课标路线的问题在粒度与形态：2022 年版义务教育课程方案与 16 个课程标准均可公开引用 [[37]](http://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html)，但其最细可用层级是「学段 × 主题 × 一条内容要求」，一条要求覆盖两个学年，无法当作单次作业的标签；且官方数学课标 PDF 为扫描图片版，实测 189 页可提取文本字符数为 0，任何自建都要先过一遍 OCR 与人工校对 [[38]](http://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220510531636118932.pdf)。国家中小学智慧教育平台路线的问题在授权：平台介绍页明示资源免费但「任何单位及个人不得用于商业行为」，网站声明进一步写明未经许可任何互联网站、App 应用、商业机构、个人不得转载或改编 [[39]](https://basic.smartedu.cn/introduce)[[40]](https://basic.smartedu.cn/copyright)；社区侧的取数工具也自述与平台无隶属关系并要求勿用于商业用途 [[41]](https://github.com/happycola233/tchMaterial-parser)。开源图谱路线质量不错却不可商用：K12-KGraph 有 10,685 节点／23,278 边、48 册教材、6,579 个概念，标注一致性 Fleiss κ=0.84，但数据许可为 CC BY-NC-SA 4.0（禁商用且相同方式共享），且只有数理化生、没有语文与英语 [[45]](https://github.com/haolpku/K12-KGraph)[[46]](https://github.com/haolpku/K12-KGraph/blob/main/LICENSE)。商用题库路线则没有自助定价，必须走商务洽谈 [[42]](https://open.xkw.com/docs/)。

识别侧也不存在捷径。「拍照直接定位到教材某个单元」没有现成通用能力，可得的最近路径是先把题目匹配到题库、再取其章节与知识点标签，依赖题库命中 [[42]](https://open.xkw.com/docs/)。识别精度本身也要打折：手写数学表达式的第三方学术对比中，Mathpix 平均准确率为 76.83%（2021 年、非小学作业本场景）[[48]](https://www.cin.ufpe.br/~damorim/publications/Costa_ETAL_DocEng21.pdf)；腾讯云自报手写体 90% 以上但未披露测试集与判定口径 [[49]](https://cloud.tencent.com/product/generalocr)。若确实要引入外部 OCR，成本与隐私两项要一起算：Mathpix 图片接口 0.002 美元／张、首个 API key 有一次性 19.99 美元开通费，默认图片保留 30 天用于质量保证，可开启 Opt-Out 在 24 小时内删除且不落盘——涉及儿童作业照片外发时，这个开关是必须配置项 [[47]](https://mathpix.com/pricing/api)。

综合看，正确的锚点做法是自建一层轻量骨架并把力气花在归并上，而不是引入一棵完整的知识点树。K12-KGraph 的 schema 提供了可借的形状：用 `Concept` 节点承载概念身份、用 `aliases` 属性收纳同一概念的不同写法 [[45]](https://github.com/haolpku/K12-KGraph)。这与仓库里 `subject_routing.py` 已经在做的事同构，只是要把它从科目一层下移到知识点一层。

---

## 五、功能建议：先补底座，再收口触达

> **本节要点**：P0 只放三项，两项是新增底座、一项是把已有 Spec 收口到能上线；P1 集中在弱信号、周报、导出与孩子端；另有三件事建议明确不做，理由都不是「暂时没资源」，而是会破坏定位或触发平台与合规约束。

### 5.1 P0：三项底座级改动

| 建议 | 解决什么 | 实现成本 | 主要风险 |
|-|-|-|-|
| P0-1 排期策略参数化与积压收敛 | 把单条固定阶梯改为「策略表 + 选择器」：内置松／中／紧三档间隔表，家庭级默认、科目级可覆盖；`partial` 与 `reinforce` 改为在所选策略表内取步，而非全局硬编码半步；新增逾期积压的显式收敛（按优先级收敛到当日必做子集）。参照目标留存旋钮 [[3]](https://docs.ankiweb.net/deck-options.html) 与主题级优先级排序 [[11]](https://github.com/bjsi/incremental-everything) | 中。`planning/domain.py` 是纯策略模块，改造不触碰传输层与存储层；主要工作量在迁移已有复习项到新策略表、以及策略变更时的到期日重算 | 策略变更会改动全部在途复习项的到期日，Anki 官方对同类 reschedule 行为专门给出谨慎提示 [[3]](https://docs.ankiweb.net/deck-options.html)；需要「只对新学内容生效／全量重排」的显式选择，否则家长会突然看到一批任务集体前移 |
| P0-2 知识点身份层与别名归并 | 给 `KnowledgeItem` 补稳定标识与别名集合，支持手工合并与拆分；在科目之下自建「领域」一层（如数学的数与运算、图形与几何），领域取自课标主题名 [[37]](http://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html)，条目仍由家长与 AI 生成。目标是让报表可聚合、复习粒度可控、增量去重不再只靠字面相似 | 中偏高。数据迁移与既有自由文本的回填是主要成本；可复用 `subject_routing.py` 的清洗与别名归一思路，AI 侧只需在草稿里多产出一个「建议归入的领域」字段 | 领域划分若做细就会退化成知识点树、做粗则聚合价值有限；不可直接复制受限授权的外部体系（智慧教育平台禁转载改编 [[40]](https://basic.smartedu.cn/copyright)、K12-KGraph 数据禁商用 [[46]](https://github.com/haolpku/K12-KGraph/blob/main/LICENSE)） |
| P0-3 提醒闭环收口（FEAT-003／PR #6） | 已有 Spec 与 open PR，需要收口的是可靠性表达：维护每个家长的订阅额度账本（一次性订阅一次仅可下发一条 [[55]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html)，订阅与取消均有事件推送可用于对账 [[56]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html)），并在站内保留红点与今日页兜底 | 低到中。服务端通道与前端授权入口已在 PR #6 中实现，剩余工作集中在额度账本、文案与站内兜底 | 长期性订阅目前只向政务民生、医疗、交通、金融、教育等线下公共服务开放，商业服务类目暂不支持 [[57]](https://developers.weixin.qq.com/community/develop/doc/000ac87bd640e02abb146c28263c00)；限频消息暂向金融等指定行业开放 [[55]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html)；用户勾选「不再询问」后无法再弹窗 [[56]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html)；强制订阅属运营规范 5.21 违规 [[54]](https://developers.weixin.qq.com/miniprogram/product/) |

*表 2：P0 三项的价值、成本与风险，成本为相对量级判断而非工时估算*

P0-3 需要额外说一句它在 Spec 里最容易出问题的地方。Spec 本身已经写明「必须家长明确点击触发订阅授权，不能静默订阅，也不能把『已开启设置』误报成『保证收到微信通知』」——这条约束方向正确，真正的落地风险在实现层：一次性订阅的额度是可累计但会被消耗的，若界面只显示开关状态而不显示剩余可下发条数，那句「不保证收到」就只是免责声明，家长仍会按「已开启即会收到」来理解，等到某天没收到提醒时，损失的是对整个产品的信任。因此收口的判据应当是三条同时成立：额度可见、每次下发有站内同源记录、提醒缺失时今日页仍能自证有几项到期。上线前还要先验证订阅消息模板与定时执行器可用性，这一点 Spec 已列，属必须真跑而非勾选的项。

### 5.2 P1：弱信号、周报、导出与孩子端

- **掌握度弱信号**：在不评分、不判定掌握的前提下，把可观测计数补齐——同一知识点连续 `reinforce` 的次数、从首次学习到首次通过的天数、是否需要家长提示。这些是事实计数而非评价，可用于策略选择与当日排序，参照 Brainscape 用信心自评而非对错判定驱动排期 [[8]](https://www.brainscape.com/spaced-repetition)、以及优先级替代回忆评分的做法 [[11]](https://github.com/bjsi/incremental-everything)。
- **家长周报（低频摘要）**：形态直接照 Google Classroom 的三段式——缺什么、接下来什么到期、近期发生了什么，家长自选日报或周报，无内容则不发 [[24]](https://support.google.com/edu/classroom/answer/6386354?hl=en)；ClassDojo 的周末未登录召回可作为沉默用户召回参照 [[25]](https://www.classdojo.com/)。周报明确不含成绩、不含同龄人对比。
- **导出与数据主权**：提供家庭数据导出（按孩子、按学期、按科目筛选的可读文件）与真正的永久删除，形态可参考 homeschool 记录类的 portfolio 导出 [[31]](https://www.homeschooly.app/homeschool-tracker-app)[[32]](https://homeschoolmanager.com/)。这一项在第七章会看到属于法定义务。
- **录入通道扩展**：在拍照之外补「一句话文字录入」与「补齐上周漏记」两个入口，两者都不需要新模型能力，只需要把已有的历史补录路径提到更浅的位置。
- **孩子端的最小参与**：只做两件事——看今天要复习什么、打一个完成标记。作品集式的自我表达（Seesaw 与 ClassDojo 的做法 [[26]](https://seesaw.com/pricing/)[[25]](https://www.classdojo.com/)）诱人但要克制：一旦孩子端承载信息发布或即时通讯，就触发《未成年人网络保护条例》第三十一条的真实身份信息要求 [[52]](https://www.cac.gov.cn/2023-10/24/c_1699806932316206.htm)，产品性质随之改变。

另有两项已有 Spec，此处只谈如何收口。FEAT-004「每日学习建议」的风险在于它天然贴着「AI 不预测孩子下一步该学什么」这条红线：一旦「建议」里出现了任何家长没录入过的新内容，边界就破了。建议把它严格限定为在已到期项集合内做排序与预算裁剪，排序输入用 5.2 的弱信号与家长填写的「学习要求」，全过程为确定性计算；模型只用于把家长填的自然语言要求映射到已有科目与领域，不生成新条目。FEAT-006「资料清理与重新开始」的风险相反，在于范围太小：当前只有归档与恢复，而法规要求的是可删除、可导出、停运可清空，因此这项应当与上面的导出一起做，一次覆盖「查阅、复制、更正、删除、转移」五个动作，而不是只补一个删除按钮。

### 5.3 明确不建议做的三件事

<grid>
<column width-ratio="0.333333">
<callout emoji="🚫">
**积分、勋章与排行式激励**
唯一可用的一手实证中，游戏化组的外在动机显著低于传统教学组，作者归因为产生了内化程度差的外在动机（被试为大学英语学习者，不可直接外推小学）[[36]](https://link.springer.com/article/10.1007/s10639-022-11130-4)；Prodigy 把同龄人对比放进付费档是反面样本 [[29]](https://prodigygame.zendesk.com/hc/en-us/articles/360045401352-Parent-Membership-Perks)，ClassDojo 的处理是把积分挂在社会情感目标而非学科分数上 [[25]](https://www.classdojo.com/)。
</callout>
</column>
<column width-ratio="0.333333">
<callout emoji="🚫">
**自建题库、讲解与出题**
一旦出现讲解、授课或课程销售形态，微信类目立刻升级为需资质档位；个人主体在教育服务下仅开放「教育信息展示」，且官方注明该类目不支持视频播放与课程销售 [[53]](https://developers.weixin.qq.com/miniprogram/product/material/)。「双减」意见亦对惰化思维能力的学习方法有禁止性表述 [[61]](https://www.gov.cn/zhengce/2021-07/24/content_5627132.htm)。
</callout>
</column>
<column width-ratio="0.333333">
<callout emoji="🚫">
**照搬自适应算法或采购全量知识点树**
默认参数下的 FSRS-6 未被其作者认为优于 SM-2 [[4]](https://github.com/ankitects/anki/pull/4391)，且家长代评的语义可靠性尚未建立；知识点树一侧，可得的高质量数据带禁商用条款 [[46]](https://github.com/haolpku/K12-KGraph/blob/main/LICENSE)，商用授权无公开定价 [[42]](https://open.xkw.com/docs/)。
</callout>
</column>
</grid>

---

## 六、体验优化：三分钟预算决定动线取舍

> **本节要点**：这个产品的体验目标不是「好用」，而是「在晚上疲惫状态下三分钟内完成」。按这个预算重看动线，卡点集中在异步等待、确认粒度与反馈选择三处；对应的改动大多成本很低。

### 6.1 晚间三分钟动线的关键卡点

先把时间预算的边界立住。家长现状在辅导上的投入日均约 30 至 50 分钟 [[62]](https://m.thepaper.cn/wifiKey_detail.jsp?contid=11504352)，但政策方向是压缩家长精力负担 [[61]](https://www.gov.cn/zhengce/2021-07/24/content_5627132.htm)，学生侧最大的不满恰恰是晚上被家长加作业 [[66]](https://hudong.moe.gov.cn/jyb_xwfb/moe_2082/2021/2021_zl53/dddxal/202307/t20230711_1068364.html)；在线教育类使用时长集中在 19 至 22 点 [[65]](https://www.questmobile.com.cn/blog/blog_149.html)，而线上培训不得晚于 21 点的规定可作为晚间时段的硬边界参照 [[61]](https://www.gov.cn/zhengce/2021-07/24/content_5627132.htm)。三者叠加得到的设计前提是：目标动线必须在 19 至 21 点之间、疲惫状态下、三分钟内跑完，并且不能给孩子新增任务。PR #5 的动机已经承认了这个前提，接下来是把它落到具体卡点上。

- **卡点一：拍照与草稿之间的异步等待**。AI 分析是异步任务，家长提交后必须再回来一次。三分钟预算里最贵的就是这次「回来」。方向是让提交即结束：草稿就绪后走站内红点与提醒通道，家长在同一次会话里不必等待。
- **卡点二：多知识点草稿的逐条确认**。PR #2 已经把「待确认就地确认」做出来，下一步是默认动作的粒度——整条草稿一键接受、事后再单条修正，比逐条勾选更符合疲惫状态下的操作能力。
- **卡点三：三态反馈需要家长做判断**。`complete`／`reinforce`／`partial` 三选一要求家长先理解语义再选择，这正是 Anki 维护者担心的那类困惑 [[4]](https://github.com/ankitects/anki/pull/4391)。方向是把最常用的动作前置为单击「做完了」，另两态收进次级操作，并在文案里说清它们影响的是下次出现时间。
- **卡点四：逾期积压没有出口**。每日预算已按 `daily_budget_minutes` 分必做与可选，但连续几天未打开后的积压没有收敛机制，家长回来看到的是一屏欠账。这一项与 P0-1 是同一件事的两面。
- **卡点五：提醒不可靠导致的主动回访依赖**。在长期性订阅不可得的前提下，站内兜底不是降级方案而是主路径，今日页需要能自证「今天有几项到期、其中几项必做」。
- **卡点六：漏记补齐的入口深度**。历史补录不制造过去的 Todo 债务，这个策略是对的，但它的价值取决于家长能否在两步之内找到入口；补录入口越浅，「漏记一周」的挫败感越小。

### 6.2 低成本高感知的改动清单

| 改动 | 针对的卡点 | 成本 | 家长可感知的变化 |
|-|-|-|-|
| 提交即结束，草稿就绪后红点召回 | 卡点一 | 低 | 录入动作从「拍照—等待—确认」缩为「拍照—走开」，晚间单次占用时间下降最明显的一项 |
| 整条草稿一键接受，保留单条修正 | 卡点二 | 低 | 正常情况下确认从多次点击变为一次，出错时仍可回改，不牺牲家长确认这道门禁的语义 |
| Todo 主操作单击完成，另两态收入次级菜单 | 卡点三 | 低 | 不必每次在三个语义之间做选择；配合文案说明「这会让它下次更早／更晚出现」 |
| 今日页顶部显示到期总数与必做数 | 卡点五 | 低 | 提醒没到也能一眼确认今天有没有事，把可靠性从平台手里收回一部分 |
| 逾期项按优先级折叠为「今天先做这几项」 | 卡点四 | 中 | 断更几天后回来不再面对一屏欠账，避免直接放弃 |
| 补录入口提到今日页可见位置 | 卡点六 | 低 | 漏记从「需要找路径」变成顺手补齐，减少记录链断裂 |
| 提醒设置页显示剩余可下发条数与最近一次下发 | 卡点五 | 低 | 把「已开启」与「一定收到」区分开，避免一次失约损伤整体信任 |
| 完成三视口与真机几何验收 | 全部 | 中 | 仓库当前 320／390／430 三视口与 iOS／Android 真机几何证据为未执行，属体验风险的兜底项 |

*表 3：低成本高感知的改动清单，成本为相对量级判断*

---

## 七、风险边界：儿童数据与类目限制是上线前提

> **本节要点**：这两节列的不是「未来要注意的事」，而是从自用转向任何形式公开发布之前必须先落地的条件；其中导出与永久删除、专门的儿童信息处理规则、类目与订阅能力三项，直接影响第五章的排期。

### 7.1 儿童个人信息与监护人同意

小学生全部落入「儿童」定义（不满十四周岁），且其个人信息在《个人信息保护法》下属敏感个人信息，只有在具有特定目的和充分必要性、并采取严格保护措施时方可处理，处理时须取得单独同意 [[51]](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)。《儿童个人信息网络保护规定》给出的是可逐条对照的清单：第八条要求设置专门的儿童个人信息保护规则与用户协议并指定专人负责；第九、十条要求以显著清晰方式告知监护人并征得同意、同时提供拒绝选项，并明确告知七项内容（含存储地点与期限、到期处理方式、更正与删除的途径），告知事项发生实质性变化须再次征得同意；第十一条不得收集与服务无关的信息；第十二条存储不超过必需期限；第十三条须加密存储；第十四条超出约定目的与范围使用须再次征得同意；第十六、十七条对委托第三方处理与向第三方转移都要求安全评估、明确不得转委托、委托关系解除时及时删除；第二十条列明监护人撤回同意、超出目的范围或注销等四类必删情形；第二十三条要求停止运营时立即停止收集并删除已持有信息、同时告知监护人 [[50]](https://www.gov.cn/gongbao/content/2019/content_5456808.htm)。

《未成年人网络保护条例》再叠加三层。第三十二条禁止强制要求同意非必要的个人信息处理，且不得因不同意或撤回同意而拒绝提供基本功能服务——这条直接否定「不上传照片就不能记录学习内容」这类设计。第三十四条要求提供便捷的查阅、复制、更正、补充、删除功能，不得设置不合理条件，拒绝须书面说明理由，符合条件的转移请求应提供转移途径。第三十六至三十八条要求最小授权、访问审批与记录、每年合规审计并向网信等部门报告，以及对私密信息的及时提示与保护措施 [[52]](https://www.cac.gov.cn/2023-10/24/c_1699806932316206.htm)。罚则不轻：违反最小授权等条款可责令改正、警告、没收违法所得，违法所得不足一百万元的并处十万至一百万元罚款，对直接负责人员处一万至十万元罚款，情节严重可责令停业整顿或关闭网站 [[52]](https://www.cac.gov.cn/2023-10/24/c_1699806932316206.htm)。检察机关的指导性与典型案例也已明确把「未取得监护人同意」「超出约定目的范围使用」认定为违法违规处理儿童个人信息 [[59]](https://www.spp.gov.cn/spp/jczdal/202203/t20220307_547759.shtml)[[60]](https://www.spp.gov.cn/spp/xwfbh/dxal/202601/t20260122_716668.shtml)。

落到这个产品上，有五项动作应当排在任何公开发布之前：一是单独成文的儿童信息处理规则，同意页同时给出拒绝选项与拒绝后果说明；二是照片最小化，默认只保留 AI 产出的结构化结果、原图可选不留存或短期留存，并剥离位置等元数据——作业本照片可能包含姓名、学校、班级与笔迹，属条例第三十八条关注的私密信息范畴；三是模型调用侧的委托处理条款与安全评估记录，若引入外部 OCR 须同时关闭其默认留存 [[47]](https://mathpix.com/pricing/api)；四是导出与永久删除（即 5.2 与 FEAT-006），这是第三十四条与第二十条的直接要求；五是停运预案，含删除与告知监护人的路径。需要如实说明一处口径缺口：法规只设「不超过必需期限」的上限，本轮未查到任何法定或行业标准给出具体保留天数，「30 天自动清理」这类做法无权威来源可引。

### 7.2 微信平台能力与类目限制

类目是第一道门。非个人主体在教育服务下的全部二级类目都需要资质，学历教育需办学许可证、非学科类培训需四选一的许可或备案、课程销售与教育平台需增值电信业务经营许可证；个人主体在教育服务下仅开放「教育信息展示」一个三级类目，无资质要求，但官方注明该类目不支持教育视频播放、直播与课程产品销售 [[53]](https://developers.weixin.qq.com/miniprogram/product/material/)。因此这个产品的现实落点在「工具」类目下的备忘录、日历、信息查询、健康管理等无资质项；但要注意备忘录一项官方注明「不涉及用户原创内容的传播及公开访问」，图片处理一项注明「本地制作剪辑，不适用于传播分享、公开访问」[[53]](https://developers.weixin.qq.com/miniprogram/product/material/)——家庭多成员共享一旦被认定为传播或公开访问，就会与所选类目不符，而运营规范 5.7「类目不符行为」是独立违规项，代码审核环节会核实运营内容与所选类目是否相符 [[54]](https://developers.weixin.qq.com/miniprogram/product/)。备案变更亦有独立违规项（5.35）与专门指引 [[58]](https://developers.weixin.qq.com/miniprogram/product/record/guidelines)。

能力是第二道门，集中在订阅消息。长期性订阅消息目前仅向政务民生、医疗、交通、金融、教育等线下公共服务开放，社区答复进一步说明商业服务类目暂不支持申请；长期订阅中的限频消息（正是「每日一次」这种形态）当前暂向金融等指定行业开放 [[55]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html)[[57]](https://developers.weixin.qq.com/community/develop/doc/000ac87bd640e02abb146c28263c00)。免弹窗的新版一次性订阅只有两种取得凭据的方式——微信支付订单号，或将按钮的 open-type 设为 liveActivity 后由用户点击，且模板由平台定义 [[55]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html)；两者本产品都不天然具备。可用的路径只剩「一次性订阅 + 在关键节点分别触发」，配合订阅与取消的事件推送维护额度账本 [[56]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html)。这里有两条容易踩的红线：运营规范 5.21 把「订阅后才能继续下一步」明确列为诱导订阅，处理方式最重可永久封禁订阅消息接口能力；5.12 对收集用户隐私的要求包括用户要求即删除、终止使用即删除，以及不得通过用户上传照片进行恶意收集隐私，处理方式最重为封号 [[54]](https://developers.weixin.qq.com/miniprogram/product/)。另需注意日下发上限（未开通支付为一千万条／日）是小程序整体总量口径，不是单用户配额，不能据此推断单个家长能收到多少条 [[56]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html)。

---

## 八、综合判断：底座先行，功能其次

<callout emoji="📌">
**综合判断**：这个产品占的位置是真实且稀缺的，接下来三个月的收益主要来自把两处底座补上，而不是继续增加功能面。
方向成立——它建立在三段论据的叠加上：第三章的矩阵显示「录入自动化」与「排期科学性」在市场上互斥，而本产品是唯一同时取了两者的组合；第四章的实测显示当前排期只有一条轨道，同一材料在自适应算法下会分叉出近千倍的间隔差异，同时 FSRS 未被其作者认为在默认参数下优于 SM-2，说明要补的是策略的可配置性而非算法的先进性；第二章与第四章共同显示知识点缺锚点会让报表聚合、复习粒度、跨期比较与外部资源接入四条能力同时失效，这一层的缺失比任何单个功能都更靠前。
残余风险与反向信号：
1. 家长代评这件事在行业里没有先例，所有已核实的自适应排期产品都要求学习者本人自评；如果家长的三态反馈在实际使用中噪声过大，排期参数化的收益会被噪声吃掉，届时更保守的做法是回到固定阶梯加人工调节。
2. 间隔重复在真实课堂环境的复现研究并未得到正向结果，因此产品价值主张应落在「替家长做了排期与记录这件事」，不宜承诺学习效果的提升幅度。
3. 提醒能力的可靠性由微信平台决定且当前不利，如果站内兜底做不实，整条「每日复习」的产品逻辑会因为触达断裂而失效。
</callout>

把上面的判断翻译成执行顺序，是「先做可回滚的底座、再做需要平台配合的触达」。第一步是 P0-1 的排期策略参数化，它改动范围收在纯策略模块内、可用现有测试覆盖，且能立刻让不同科目走不同节奏；同期把逾期收敛一起做掉，因为二者共用同一张策略表。第二步是 P0-2 的知识点身份层，先上稳定标识与别名归并（能马上改善增量去重与报表聚合），领域一层可以只做数学与语文两科试点，验证「家长与 AI 产出的条目能否稳定归入自建领域」之后再铺开。第三步才是 P0-3 的提醒收口，因为它的上限由平台决定，投入产出比取决于额度账本与站内兜底是否做实。

最吃紧的假设有两个，值得在动手前先用最小成本验证。一个是家长三态反馈的噪声水平：可以只用现有数据做一次回看，统计同一知识点连续 `reinforce` 的分布，如果这类序列极少出现，说明家长倾向于一律给「完成」，那么先要做的是评分语义而不是策略表。另一个是自建领域的覆盖率：抽一批已有的自由文本知识点，人工归入课标主题名，看能否稳定落位；若归不进去的比例很高，则领域层应当先只服务报表聚合，不参与排期决策。这两次验证都在一天量级，却能决定后面两个月的工作是否白做。

---

## 待验证事项与本轮未展开的方向

<callout emoji="🔍">
**待验证与口径说明**（仅供量级参考，不作精确结论）：
- 「自适应算法能减少多少复习量」没有一手数字：官方 benchmark 的指标是记忆状态预测精度而非复习量 [[5]](https://github.com/open-spaced-repetition/srs-benchmark)，「少 20–30%」仅见于 RemNote 厂商文档且自标 beta [[6]](https://help.remnote.com/en/articles/9124137-the-fsrs-spaced-repetition-algorithm)。第四章的量化对比只用于说明「有无分叉」，不可当作收益预估。
- FSRS 作者关闭默认启用 PR 时所依据的模拟结果原始图表未取到（在社交平台推文中，PR 页内嵌图为需签名链接），本文只引用其结论性表述与关闭时间 [[4]](https://github.com/ankitects/anki/pull/4391)。FSRS-7 的官方发布状态与后续社区 benchmark 中的胜率数字为单源、未经核实，未进正文。
- 「无同定位产品」是本轮检索范围内的否定性结论，非穷尽：国内覆盖 16 款、渠道为官网与 App Store 中国区官方描述，未覆盖安卓独占长尾与未上架 App Store 的纯小程序；海外为一轮检索。残余风险点包括名称高度相近但未核实的「知渴」（App Store id1202829936），以及晓黑板、钉钉家校两款未取到一手功能清单的产品。
- 各竞品「错题本是否含复习到期提醒」为文档级证据（官方描述关键词零命中），未做实机验证；SM-2 对照序列为按公开默认参数的近似实现，非移植 Anki 源码。
- 学科网与菁优的实际报价、最低合作门槛、是否接受个人开发者或小程序主体：均需商务洽谈，公开页无价目 [[42]](https://open.xkw.com/docs/)[[44]](https://www.jyeoo.com/open/quesapi)；P0-2 的成本判断因此只到「不采购、自建轻骨架」这一层。
- 儿童照片的具体保留期数值与去标识化技术标准：法规仅设「不超过必需期限」上限 [[50]](https://www.gov.cn/gongbao/content/2019/content_5456808.htm)，未查到给出具体天数的法定或行业标准；《网络产品和服务必要个人信息范围》清单中是否列入学习记录类工具亦未查到，条例第三十二条的适用边界无法精确锚定。
- 长期性订阅消息「教育」类目对个人主体的实际准入门槛：官方文档只写「线下公共服务」，无准入清单，本文判断为不可得系推断 [[55]](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html)；微信客服消息与服务通知作为替代路径的规则原文本轮未取到。
- 教育类小程序的留存基准：可溯源的官方数据仅到 2016–2018 年 [[65]](https://www.questmobile.com.cn/blog/blog_149.html)，近两年公开数字互相矛盾且无法溯源，本文对留存与打开成本只作定性表述。同理，「遗忘曲线／复习计划」的搜索指数未取得量化数据，仅有内容存在性证据。
- 本轮为控制交付时长未展开的方向：其一，push_kids 自身 14 个页面的逐页实操截图与三视口真机几何验收（仓库当前状态为未执行），这会直接影响第六章卡点判断的精度；其二，Ark 严格 JSON Schema 的线上冒烟（本机无密钥）；其三，各竞品家长端的实机走查与同一批测试用例横比。这三项均可按需追加一轮采集。
</callout>

---

## 参考文献

- [1] Anki, What spaced repetition algorithm does Anki use?（官方 FAQ）. https://faqs.ankiweb.net/what-spaced-repetition-algorithm.html
- [2] Anki, Frequently Asked Questions about FSRS（官方 FAQ）. https://faqs.ankiweb.net/frequently-asked-questions-about-fsrs.html
- [3] Anki, Deck Options（官方手册）. https://docs.ankiweb.net/deck-options.html
- [4] ankitects/anki, PR #4391「Enable FSRS by default」（2025-10-14 提出，2026-02-12 由作者关闭）. https://github.com/ankitects/anki/pull/4391
- [5] open-spaced-repetition, srs-benchmark. https://github.com/open-spaced-repetition/srs-benchmark
- [6] RemNote, The FSRS Spaced Repetition Algorithm（厂商文档）. https://help.remnote.com/en/articles/9124137-the-fsrs-spaced-repetition-algorithm
- [7] Quizlet, Studying with Spaced Repetition（官方帮助中心）. https://help.quizlet.com/hc/en-us/articles/48324742264077-Studying-with-Spaced-Repetition
- [8] Brainscape, Spaced Repetition（官方产品页）. https://www.brainscape.com/spaced-repetition
- [9] 墨墨, KDD 2022 论文页（DHP 记忆模型与 SSP-MMC 调度）, 2022. https://memodocs.maimemo.com/docs/2022_KDD
- [10] 墨墨／Markji 帮助文档（逾期复习处理建议）. https://memodocs.maimemo.com/docs/markji-help-260529
- [11] bjsi/incremental-everything（Incremental RemNote，主题级排期实现）. https://github.com/bjsi/incremental-everything
- [12] Adaptive vs. fixed retrieval practice scheduling（同行评议论文，PMC6028005）, 2016. https://pmc.ncbi.nlm.nih.gov/articles/PMC6028005/
- [13] Goossens et al., Applied Cognitive Psychology（真实课堂中未发现长间隔重复收益）, 2016. https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.3245
- [14] Nature Reviews Psychology, 间隔与检索练习综述, 2022. https://www.nature.com/articles/s44159-022-00089-1
- [15] 小猿AI, App Store 中国区官方描述（ver 3.141.2）, 2026-08-31. https://apps.apple.com/cn/app/id1325419855
- [16] 小猿口算／小猿AI 官方百科页, 2026-09-07 访问. http://www.xiaoyuankousuan.com/baike
- [17] 爱作业, App Store 中国区官方描述（ver 5.2.6）, 2026-02-24. https://apps.apple.com/cn/app/id1246135464
- [18] 作业帮家长版, App Store 中国区官方描述（ver 14.42.0）, 2026-08-28. https://apps.apple.com/cn/app/id1569820044
- [19] 一起学, App Store 中国区官方描述（ver 3.9.28）, 2026-09-03. https://apps.apple.com/cn/app/id913817574
- [20] 小盒AI学, App Store 中国区官方描述（ver 5.3.12）, 2026-06-18. https://apps.apple.com/cn/app/id1475739886
- [21] 班级小管家官网, 2026-09-07 访问. https://banjixiaoguanjia.com/
- [22] 记忆卡片（pro）官网, 2026-09-07 访问. https://jiyikapian.cn/
- [23] 智因错题本官网, 2026-09-07 访问. https://zyctb.com/
- [24] Google Classroom, Guardian email summaries（官方帮助文档）. https://support.google.com/edu/classroom/answer/6386354?hl=en
- [25] ClassDojo 官网, 2026-09-07 访问. https://www.classdojo.com/
- [26] Seesaw, Pricing, 2026-09-07 访问. https://seesaw.com/pricing/
- [27] Khan Academy for Parents Quick Start Guide（官方帮助文档）. https://support.khanacademy.org/hc/en-us/articles/360040168512-Khan-Academy-for-Parents-Quick-Start-Guide
- [28] Prodigy, Parent Dashboard（官方帮助中心）, 2026-03-19. https://prodigygame.zendesk.com/hc/es/articles/115001744726-Parent-Dashboard
- [29] Prodigy, Parent Membership Perks（官方帮助中心）, 2026-07-23. https://prodigygame.zendesk.com/hc/en-us/articles/360045401352-Parent-Membership-Perks
- [30] IXL, Family Reports Quick Start（官方 PDF）. https://ca.ixl.com/userguides/ca/IXLQuickStart_FamilyReports.pdf
- [31] Homeschooly, Homeschool Tracker App, 2026-09-07 访问. https://www.homeschooly.app/homeschool-tracker-app
- [32] Homeschool Manager 官网, 2026-09-07 访问. https://homeschoolmanager.com/
- [33] S'moresUp, Pricing, 2026-09-07 访问. https://smoresup.com/pricing/
- [34] Greenlight, Plans, 2026-09-07 访问. https://greenlight.com/plans
- [35] Cozi Gold, 2026-09-07 访问. https://www.cozi.com/cozi-gold/
- [36] Education and Information Technologies, 游戏化（ludicization）反效果实证研究, 2022-05-30. https://link.springer.com/article/10.1007/s10639-022-11130-4
- [37] 教育部, 关于印发义务教育课程方案和课程标准（2022年版）的通知, 2022-04-21. http://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html
- [38] 义务教育数学课程标准（2022年版）PDF, 2022-05-09 版. http://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220510531636118932.pdf
- [39] 国家中小学智慧教育平台, 平台介绍, 2026-09-07 访问. https://basic.smartedu.cn/introduce
- [40] 国家中小学智慧教育平台, 网站声明, 2026-09-07 访问. https://basic.smartedu.cn/copyright
- [41] happycola233/tchMaterial-parser（第三方教材解析工具）. https://github.com/happycola233/tchMaterial-parser
- [42] 学科网开放平台文档, 2026-09-07 访问. https://open.xkw.com/docs/
- [43] 学科网, 章节知识点推题服务页, 2026-09-07 访问. https://open.xkw.com/exam/chapters/
- [44] 菁优网, 题库 API 开放平台, 2026-09-07 访问. https://www.jyeoo.com/open/quesapi
- [45] haolpku/K12-KGraph（开源 K12 知识图谱）, 2026-08-09 最近提交. https://github.com/haolpku/K12-KGraph
- [46] K12-KGraph LICENSE（数据 CC BY-NC-SA 4.0，代码 MIT）, 2026-05-06. https://github.com/haolpku/K12-KGraph/blob/main/LICENSE
- [47] Mathpix, API Pricing, 2026-09-07 访问. https://mathpix.com/pricing/api
- [48] Costa et al., DocEng'21, 手写数学表达式识别方法对比, 2021. https://www.cin.ufpe.br/\~damorim/publications/Costa_ETAL_DocEng21.pdf
- [49] 腾讯云, 通用文字识别产品页（厂商宣传口径）, 2026-09-07 访问. https://cloud.tencent.com/product/generalocr
- [50] 国家互联网信息办公室令第4号, 儿童个人信息网络保护规定（国务院公报原文）, 2019-10-01 施行. https://www.gov.cn/gongbao/content/2019/content_5456808.htm
- [51] 中华人民共和国个人信息保护法（网信办发布全文）, 2021-11-01 施行. https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm
- [52] 未成年人网络保护条例（国务院令第766号）, 2024-01-01 施行. https://www.cac.gov.cn/2023-10/24/c_1699806932316206.htm
- [53] 微信开放文档, 小程序服务类目与所需资质, 2026-09-07 访问. https://developers.weixin.qq.com/miniprogram/product/material/
- [54] 微信开放文档, 微信小程序运营规范, 2026-09-07 访问. https://developers.weixin.qq.com/miniprogram/product/
- [55] 微信开放文档, 订阅消息功能介绍, 2026-09-07 访问. https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message-overview.html
- [56] 微信开放文档, 订阅消息开发指南, 2026-09-07 访问. https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html
- [57] 微信开放社区, 长期性订阅消息类目限制答复, 2025-10-22. https://developers.weixin.qq.com/community/develop/doc/000ac87bd640e02abb146c28263c00
- [58] 微信开放文档, 小程序备案指引, 2026-09-07 访问. https://developers.weixin.qq.com/miniprogram/product/record/guidelines
- [59] 最高人民检察院, 第三十五批指导性案例, 2022-03-07. https://www.spp.gov.cn/spp/jczdal/202203/t20220307_547759.shtml
- [60] 最高人民检察院, 个人信息保护检察公益诉讼典型案例, 2026-01-22. https://www.spp.gov.cn/spp/xwfbh/dxal/202601/t20260122_716668.shtml
- [61] 中共中央办公厅、国务院办公厅, 关于进一步减轻义务教育阶段学生作业负担和校外培训负担的意见, 2021-07-24. https://www.gov.cn/zhengce/2021-07/24/content_5627132.htm
- [62] 澎湃新闻美数课（数据源为北京大学中国家庭追踪调查 CFPS）, 家长辅导作业时长变化. https://m.thepaper.cn/wifiKey_detail.jsp?contid=11504352
- [63] 中国教育和科研计算机网转载中国青年报社社会调查中心陪写作业调查（样本 1980 名家长）, 2017-11-21. http://www.edu.cn/edu/ji_chu/ji_jiao_news/201711/t20171121_1568052.shtml
- [64] 苏州市教育质量监测中心, 居家学习期间家长参与情况研究. http://jyzljc.suzhou.edu.cn/jyyj/lwfx/1229.html
- [65] QuestMobile, 在线教育行业洞察报告, 2018-06-12. https://www.questmobile.com.cn/blog/blog_149.html
- [66] 教育部门户网站, 家庭教育典型案例（含 2300 名学生与家长调查数据）, 2023-07-11. https://hudong.moe.gov.cn/jyb_xwfb/moe_2082/2021/2021_zl53/dddxal/202307/t20230711_1068364.html
- [67] 教育部, 家庭教育促进法相关报道, 2022-03-08. http://www.moe.gov.cn/jyb_xwfb/xw_zt/moe_357/jjyzt_2022/2022_zt01/baodao/202203/t20220308_605384.html
- [68] 卡吃卡, 艾宾浩斯复习计划表生成器（产品自述）, 2026-09 访问. https://kachika.app/zh-CN/blog/ebbinghaus-forgetting-curve/
- [69] 界面新闻 JMedia, 2026年中国GenAI+教育行业发展报告（转载）, 2026-03-03. https://www.jiemian.com/article/14060378.html