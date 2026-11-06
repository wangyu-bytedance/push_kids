# UI-001 — DREV-20261105-WORKDAY-02

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261105-WORKDAY-02
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-001-CHINA-WORKDAY-SCHEDULES.md#SPEC-20261105-WORKDAY-02
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261105-WORKDAY-02/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261105-WORKDAY-02/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261105-WORKDAY-02/index.html=b3bde16a5013c1325cdb1f1bb90a2f5bdef1c778985f58f4c948621b24677ee9
- Prototype generated/updated at: 2026-11-05
- Approved by: 产品负责人（用户）
- Approved at: 2026-11-05
- Approval evidence: 当前会话用户明确回复“批准此设计并继续前端实施”，对应具体DREV02审批问题。源文件SHA和60张导出保持不变；Spec02/Architecture02的“完成这个方案的落地”授权独立记录于Task Spec。
- Superseded by: DREV-20261105-WORKDAY-03，仅设置/日程编辑的规则与覆盖备注删除、真实缺覆盖结果的一次短状态范围；其余模式、草稿与权限/恢复合同继续有效。原源、导出及SHA冻结。

Chrome 156.0.8078.80 / macOS系统字体 / font scale100% / DPR1。
20态×3视口=60张HTML导出；不替代原生三视口、真机或可访问性验收。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| settings-weekly-320x568.png | UI-001/settings-weekly | 320×568 | 1x | 0d57266f796b742fbbbc9c3938a5339a9f4604b4b4733ab73f860d5d5108794a | HTML设计导出，非原生验收 |
| settings-perday-320x568.png | UI-001/settings-perday | 320×568 | 1x | 36dd91bcbaeb4530e05b180984a918121dd43a0e75ee33838651ad59952b67df | HTML设计导出，非原生验收 |
| settings-workday-320x568.png | UI-001/settings-workday | 320×568 | 1x | 0118421ac21a2e89d764208d62b66e58e9bac41bf708a16db8881ee1ed9ba953 | HTML设计导出，非原生验收 |
| settings-flexible-320x568.png | UI-001/settings-flexible | 320×568 | 1x | e6d4745ce1114228be1d07a9cb03e89683ae9274b3b3c7e36fffb8f710616538 | HTML设计导出，非原生验收 |
| settings-readonly-320x568.png | UI-001/settings-readonly | 320×568 | 1x | dec99e3afa19e343883e976be9d019a704e026855c9d0aecb818a81fe3f0cef6 | HTML设计导出，非原生验收 |
| settings-saving-320x568.png | UI-001/settings-saving | 320×568 | 1x | 8815973e212411aeb8c8ad204fd41685a69cb99f9dc9b05d2bf2b3d45c55d141 | HTML设计导出，非原生验收 |
| settings-error-320x568.png | UI-001/settings-error | 320×568 | 1x | 5136ed039ec7441e1e00249b14db0e5d11c05a959c27d1b1121bf6b1a9394da3 | HTML设计导出，非原生验收 |
| settings-convert-320x568.png | UI-001/settings-convert | 320×568 | 1x | 129f9eb7ed86105956c1ac56e814e8f65c3de49f509e6b2ee11b9800b785a15e | HTML设计导出，非原生验收 |
| settings-coverage-320x568.png | UI-001/settings-coverage | 320×568 | 1x | 9e2db4bbf10ecf850ac7125ee90e788e2f1b58193f8244ddafb3290a838130b1 | HTML设计导出，非原生验收 |
| calendar-create-320x568.png | UI-001/calendar-create | 320×568 | 1x | 455733d0833ccbeadfdb44b34bc9692f5e3c4589f8fa32d90a311376f69cba19 | HTML设计导出，非原生验收 |
| calendar-edit-320x568.png | UI-001/calendar-edit | 320×568 | 1x | 8f6aa56738e464f23f6e22adb8270e7dd59183a346699869a0d012427eeb7408 | HTML设计导出，非原生验收 |
| calendar-once-320x568.png | UI-001/calendar-once | 320×568 | 1x | 4bd2ec2392e0ccf78cfd61eb70d15f0b1a3b3ec8db65339f1826e0f4060f948c | HTML设计导出，非原生验收 |
| calendar-weekly-320x568.png | UI-001/calendar-weekly | 320×568 | 1x | 402f8dd9972df1c47705d75be2cd0b5bebf5df294bfbf817c3b55e22197ec4f4 | HTML设计导出，非原生验收 |
| calendar-readonly-320x568.png | UI-001/calendar-readonly | 320×568 | 1x | 6b33dee5a28a870755e7fec7cfa0dd1db95539ab36fd3a958043b9e0023763b9 | HTML设计导出，非原生验收 |
| calendar-saving-320x568.png | UI-001/calendar-saving | 320×568 | 1x | 535004dc372bf48172ed9c6cd25e92bcefb7d1c46db36ed846d202eded5af048 | HTML设计导出，非原生验收 |
| calendar-error-320x568.png | UI-001/calendar-error | 320×568 | 1x | ff8d3d771efcee561c27f26e8ffb24f7de62b71f354ca18f467f8dce284100c2 | HTML设计导出，非原生验收 |
| calendar-items-320x568.png | UI-001/calendar-items | 320×568 | 1x | ef8b8565ab7f2a792a9df2283e1943c246c1a3afc0bffd8328dfc12c183c3687 | HTML设计导出，非原生验收 |
| calendar-holiday-320x568.png | UI-001/calendar-holiday | 320×568 | 1x | afb90ca8d5f069390ee41b1f1a9db6f27d478918d877e0d0bf14964dbe1adc01 | HTML设计导出，非原生验收 |
| calendar-adjusted-320x568.png | UI-001/calendar-adjusted | 320×568 | 1x | c69f3becf314413fc9ae7635c343d11d808c4af5b4987d4f2decf82e24dd8e45 | HTML设计导出，非原生验收 |
| calendar-coverage-320x568.png | UI-001/calendar-coverage | 320×568 | 1x | f9d61c89e7511eeb004949879c113719490ae4cca6e7b28acd4a4d5df532fc83 | HTML设计导出，非原生验收 |
| settings-weekly-390x844.png | UI-001/settings-weekly | 390×844 | 1x | 8fc2d862a395146c8808fbbd5169cd424f2fe0f4c1634d94e481de5ce8223f2a | HTML设计导出，非原生验收 |
| settings-perday-390x844.png | UI-001/settings-perday | 390×844 | 1x | 0bd775a677202321e58fd53dbff8a650a915dbf789a4918e872a8f5fb939d474 | HTML设计导出，非原生验收 |
| settings-workday-390x844.png | UI-001/settings-workday | 390×844 | 1x | 39620ffba515e07167e7315afc4b4b8bce82a4455a7ffddbd9ea48c291cc8d2e | HTML设计导出，非原生验收 |
| settings-flexible-390x844.png | UI-001/settings-flexible | 390×844 | 1x | 3aa0a7dd042d101a4498b16ee3030631ab73f62d96638a45f956a0b5a5747722 | HTML设计导出，非原生验收 |
| settings-readonly-390x844.png | UI-001/settings-readonly | 390×844 | 1x | 09be2a7efc40ab6006c8a41d02c71496a1319ec454525d4e476124802c5c47ac | HTML设计导出，非原生验收 |
| settings-saving-390x844.png | UI-001/settings-saving | 390×844 | 1x | e9c1a09bf5913529c7d0095715da7a28ae7e247d3a48ec76771083ad2da9a0df | HTML设计导出，非原生验收 |
| settings-error-390x844.png | UI-001/settings-error | 390×844 | 1x | 4165f804da21cf82db94efb50631915ff5c01ccb2ff830a90b697d360a7228ca | HTML设计导出，非原生验收 |
| settings-convert-390x844.png | UI-001/settings-convert | 390×844 | 1x | cf6e6e6daf8f60d4ae4499e5eb7188d47f4001b9a14485993654ef466da25a81 | HTML设计导出，非原生验收 |
| settings-coverage-390x844.png | UI-001/settings-coverage | 390×844 | 1x | d903fa8ed33f802c167696f250dcdb496cc17ea82830f2f5e4e6cac31a031f14 | HTML设计导出，非原生验收 |
| calendar-create-390x844.png | UI-001/calendar-create | 390×844 | 1x | c76fcaf569ca6f17e79a3b952a29f8dca40897c694fdce1ea4728fb935c3159d | HTML设计导出，非原生验收 |
| calendar-edit-390x844.png | UI-001/calendar-edit | 390×844 | 1x | 8424ab809f5d3a23f242c1b73f402ccade19ea2f1aca8a667efd893446d6b569 | HTML设计导出，非原生验收 |
| calendar-once-390x844.png | UI-001/calendar-once | 390×844 | 1x | 83be32d6fbc64838c96427ecde8b0dbcb9e380e6ba95431e32e7392946600019 | HTML设计导出，非原生验收 |
| calendar-weekly-390x844.png | UI-001/calendar-weekly | 390×844 | 1x | d6fe21266c3f9c1f29549fcad2d06a6525d515927148fcab4e7934878192c4a4 | HTML设计导出，非原生验收 |
| calendar-readonly-390x844.png | UI-001/calendar-readonly | 390×844 | 1x | 5acffc7b26dc1c0341d8ed7447761ce5b413ecb42dcf4a0319500916e593a98f | HTML设计导出，非原生验收 |
| calendar-saving-390x844.png | UI-001/calendar-saving | 390×844 | 1x | 281d04d7524e6ea6fc7d57b7333b2e0b0f9e36bbd2d6ac58ed081236977f9668 | HTML设计导出，非原生验收 |
| calendar-error-390x844.png | UI-001/calendar-error | 390×844 | 1x | f18cdc810564082cac0b32910d995429c5ef54d6dc1be2a04a2d7d05f093a7be | HTML设计导出，非原生验收 |
| calendar-items-390x844.png | UI-001/calendar-items | 390×844 | 1x | 7b12624dfdffbbfb0bb5fb71f5e5ff89e9727aa53ec2ebf64a1a601c0a890b30 | HTML设计导出，非原生验收 |
| calendar-holiday-390x844.png | UI-001/calendar-holiday | 390×844 | 1x | 12b3c2c45e517a6a6e12324025f214db6208599f589b2dc4c49114201b6fc21e | HTML设计导出，非原生验收 |
| calendar-adjusted-390x844.png | UI-001/calendar-adjusted | 390×844 | 1x | faa32d2b75cb407cb94eaff480ba0c55afd7d1c29ad0bd1f4d48d2a5bb06c8f2 | HTML设计导出，非原生验收 |
| calendar-coverage-390x844.png | UI-001/calendar-coverage | 390×844 | 1x | f18bb0204510cfa6c3838d738cc979b7669634ac80098a015530795c176d7c8a | HTML设计导出，非原生验收 |
| settings-weekly-430x932.png | UI-001/settings-weekly | 430×932 | 1x | 765c5efce8ad602c031f8eca8e27e2fec3cdf70cde79d01ade0a928f829407e6 | HTML设计导出，非原生验收 |
| settings-perday-430x932.png | UI-001/settings-perday | 430×932 | 1x | 58ed82ad50bf46b994f5afa01c3492e8ba7a0af4dee8cd81f25567bffc79fef2 | HTML设计导出，非原生验收 |
| settings-workday-430x932.png | UI-001/settings-workday | 430×932 | 1x | 335c27de04349f1bf29df514a85906517360d5213ff72f82c6f796fbe9515965 | HTML设计导出，非原生验收 |
| settings-flexible-430x932.png | UI-001/settings-flexible | 430×932 | 1x | 0ed7aebcc035620b39d518120a67d232e88eb438066a329aa2c35a475501f729 | HTML设计导出，非原生验收 |
| settings-readonly-430x932.png | UI-001/settings-readonly | 430×932 | 1x | bd26089cb7f5f232d146d045c3bcebbb62550506601d523418f96d2a2acfcc5a | HTML设计导出，非原生验收 |
| settings-saving-430x932.png | UI-001/settings-saving | 430×932 | 1x | c95161f9bd2eff540fbc94183fa0130fad278dd7546e1f968dd2e85c13cd8fce | HTML设计导出，非原生验收 |
| settings-error-430x932.png | UI-001/settings-error | 430×932 | 1x | f4e3cdeef7261934ed92420e7c4cb0051da31bc2010a82faff07ffb7ea4482d7 | HTML设计导出，非原生验收 |
| settings-convert-430x932.png | UI-001/settings-convert | 430×932 | 1x | 47d82389062b9c3f9c6e090eddf0609447ed075e649fabafb5f76b9a0c65bf28 | HTML设计导出，非原生验收 |
| settings-coverage-430x932.png | UI-001/settings-coverage | 430×932 | 1x | 1a774ff21fca9c019a07b8eb26efe5b9f63fd284734ec0415f41d744a28b2e36 | HTML设计导出，非原生验收 |
| calendar-create-430x932.png | UI-001/calendar-create | 430×932 | 1x | e884cb7a4a9a5e3f97497ee294c13869c54f9bfd40d44df95cda1675a5b64781 | HTML设计导出，非原生验收 |
| calendar-edit-430x932.png | UI-001/calendar-edit | 430×932 | 1x | b5962a19563ed5f31598178ed8cf224cafaf5ce8a64ca7b413e0c8d15ef658aa | HTML设计导出，非原生验收 |
| calendar-once-430x932.png | UI-001/calendar-once | 430×932 | 1x | c8f615cca8831c69b5f4a7d1f0125e45a2885c9bdd2666a0f0e97fba44573494 | HTML设计导出，非原生验收 |
| calendar-weekly-430x932.png | UI-001/calendar-weekly | 430×932 | 1x | b4f89ebe91d95a9b3df3a193ce3ec622466d8793942e2754f2a563834c787ab9 | HTML设计导出，非原生验收 |
| calendar-readonly-430x932.png | UI-001/calendar-readonly | 430×932 | 1x | c58ac281c13434d4659d33647270b1d96f85846b574355eca823023930101bf8 | HTML设计导出，非原生验收 |
| calendar-saving-430x932.png | UI-001/calendar-saving | 430×932 | 1x | 29d23f6c5caedb720caa55e21d2411b56073a89c09fe39ca92cae9f379cd7b3b | HTML设计导出，非原生验收 |
| calendar-error-430x932.png | UI-001/calendar-error | 430×932 | 1x | 2e33a5695da3e59a02fbe306c5f0e492b888c4f3bd4498622e33bbbb9b786048 | HTML设计导出，非原生验收 |
| calendar-items-430x932.png | UI-001/calendar-items | 430×932 | 1x | 403e7ab4d7a321a9c590b54c6b7b743c01fd95508e3b7bf2111c99ff79f65966 | HTML设计导出，非原生验收 |
| calendar-holiday-430x932.png | UI-001/calendar-holiday | 430×932 | 1x | 74fe2d09a7ab06da0466ca2851f06f04360823f1a38d1fa6dc4b3a6e40dc4038 | HTML设计导出，非原生验收 |
| calendar-adjusted-430x932.png | UI-001/calendar-adjusted | 430×932 | 1x | 4f477af7fe95b681eb1f3782c7b49187a6a0df9fb8cd8b1864c3133cab256b12 | HTML设计导出，非原生验收 |
| calendar-coverage-430x932.png | UI-001/calendar-coverage | 430×932 | 1x | 65608cab74b9a6ed2dbb42ca8e5b3cbc06d5cba7663db734329eabdbd064372d | HTML设计导出，非原生验收 |
