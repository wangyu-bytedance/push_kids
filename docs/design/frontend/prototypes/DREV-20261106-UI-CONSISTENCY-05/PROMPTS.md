# DREV05 — 指定六主题设置页生成提示词

用户确认：已有预置图标直接用；无预置时使用本主题的统一默认图标，不做运行时AI生成，也不增加逐课程图标制作流程。

本轮image_gen仅用于制作评审效果图，不代表产品内提供图标生成功能。每个方向一次调用；引用图仅用于保留既有视觉方向。A为现有视觉复绘，不冒充原生截图。

## A 原始风格

- 默认图标：线性书本
- 视觉：暖纸松绿 · 现有视觉复绘
- 参考：/var/folders/hq/l74_1q417nbdffshwhtw79640000gn/T/codex-clipboard-628517e7-caa6-41ab-a0fc-32dd18ec9517.png

```text
Use case: ui-mockup.
Generate ONE refined Chinese mobile WeChat Mini Program Settings-page mockup for “知芽”, a parent-facing primary-school learning organizer. Output one full-screen flat front-facing portrait screenshot, approximately 9:19.5, no device frame, no outer presentation or labels. Crisp high-resolution simplified Chinese typography. This is a design preview only.
SAME SHARED PAGE STRUCTURE ACROSS ALL THEMES: compact status bar and WeChat nav in top 7%; page header/scene from 7–25%; subject section at 25–40%; extracurricular section at 42–66%; daily-task section at 68–91%; fixed five-tab bar at 92–100%. All functional text, FOUR activity/task rows and both add buttons must be fully visible. Theme artwork stays mainly in the header and outer margins; content has calm solid backgrounds and clean readable typography. Keep common button sizes, single-column lists and semantic hierarchy. Visual differentiation comes from scene artwork, materials, icons, background and surfaces, not different product behavior.
Exact screen content:
top status “9:41”, top centered sprout brand “知芽”, WeChat menu capsule at upper right;
header title “设置”, subtitle “小禾的学习与日常”, child selector “小禾”.
Section “在学科目”: three well-spaced subject tiles, “语文”, “数学”, “思维拓展”, followed by a small + add control. The third tile “思维拓展” has a small secondary label “自定义”. It MUST use the theme's GENERIC DEFAULT ICON specified below, NOT a custom thinking/puzzle/brain icon. The first two subjects can use a preset book and ruler icon. The purpose is to show that an unknown custom subject always uses the theme default.
Section “课外活动”: row “围棋” with “每周日 14:00–16:00”; row “游泳” with “每周日 17:00–18:00”; button “＋ 添加课外活动”.
Section “每日任务”: row “阅读” with “每天 20 分钟”; row “围棋” with “每天 30 分钟”; button “＋ 添加每日任务”.
Each row has relevant preset icon and a small right disclosure arrow.
The two add buttons must be EXACTLY the same visual style and surface in this theme. No arbitrary default gray native-button background.
Bottom navigation labels in order: “今日” “日程” “记录” “报表” “设置”, with the settings tab selected; home indicator below.
Important behavior constraints for the design: custom subjects get a generic theme fallback; there is NO runtime AI icon generation, no sparkle generation button, no waiting, no icon-generation flow, no request to draw custom icons. Do not put implementation explanations such as “默认图标” inside the product interface. Do not invent scores, streaks, rewards, learning grades or extra business features. All data synthetic; no real children photos.
The six images must feel like themed versions of this SAME page. Keep artwork polished and education-appropriate, with plenty of readable text space.
Specific theme and fallback:
Reference image is the EXISTING PRODUCT VISUAL BASELINE only, not a crop or pixel-edit target. Recreate its warm paper cream background (#FAF7F0), deep pine green (#1F5B45), pale sage round icon backgrounds, soft cream cards with large round corners and restrained low shadows, dark neutral Chinese text, delicate gray dividers. Preserve the familiar mature quiet original look; do NOT turn it into a new playful theme, no full-screen garden, no large mascots. Use small tasteful existing-style book/clock stationery illustrations only in the header corners. Reconstruct the complete shared settings page content above, since the reference screenshot is scrolled and has different crop/content. Show simple preset line icons, not all new 3D graphics. The generic fallback for “思维拓展” is a PINE-GREEN OUTLINED OPEN BOOK inside a PALE SAGE CIRCLE, identical to the theme's standard learning fallback. Subject titles are plain native-like Chinese text. Both add buttons use matching cream/light-sage surface and pine text. Keep the original familiar raised round green camera “记录” entry in the bottom navigation while the other four tabs stay subtle. Remove the reference iPhone dynamic island and unrelated Starbucks logo, use a small conventional 9:41 status area. The result is a faithful visual restaging of the original style using the comparison content.
```

## B 成长花园

- 默认图标：嫩芽
- 视觉：纸雕花园 · 嫩芽与种子袋
- 参考：/Users/bytedance/Documents/push_kids/docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-04/style-a.png

```text
Use case: ui-mockup.
Generate ONE refined Chinese mobile WeChat Mini Program Settings-page mockup for “知芽”, a parent-facing primary-school learning organizer. Output one full-screen flat front-facing portrait screenshot, approximately 9:19.5, no device frame, no outer presentation or labels. Crisp high-resolution simplified Chinese typography. This is a design preview only.
SAME SHARED PAGE STRUCTURE ACROSS ALL THEMES: compact status bar and WeChat nav in top 7%; page header/scene from 7–25%; subject section at 25–40%; extracurricular section at 42–66%; daily-task section at 68–91%; fixed five-tab bar at 92–100%. All functional text, FOUR activity/task rows and both add buttons must be fully visible. Theme artwork stays mainly in the header and outer margins; content has calm solid backgrounds and clean readable typography. Keep common button sizes, single-column lists and semantic hierarchy. Visual differentiation comes from scene artwork, materials, icons, background and surfaces, not different product behavior.
Exact screen content:
top status “9:41”, top centered sprout brand “知芽”, WeChat menu capsule at upper right;
header title “设置”, subtitle “小禾的学习与日常”, child selector “小禾”.
Section “在学科目”: three well-spaced subject tiles, “语文”, “数学”, “思维拓展”, followed by a small + add control. The third tile “思维拓展” has a small secondary label “自定义”. It MUST use the theme's GENERIC DEFAULT ICON specified below, NOT a custom thinking/puzzle/brain icon. The first two subjects can use a preset book and ruler icon. The purpose is to show that an unknown custom subject always uses the theme default.
Section “课外活动”: row “围棋” with “每周日 14:00–16:00”; row “游泳” with “每周日 17:00–18:00”; button “＋ 添加课外活动”.
Section “每日任务”: row “阅读” with “每天 20 分钟”; row “围棋” with “每天 30 分钟”; button “＋ 添加每日任务”.
Each row has relevant preset icon and a small right disclosure arrow.
The two add buttons must be EXACTLY the same visual style and surface in this theme. No arbitrary default gray native-button background.
Bottom navigation labels in order: “今日” “日程” “记录” “报表” “设置”, with the settings tab selected; home indicator below.
Important behavior constraints for the design: custom subjects get a generic theme fallback; there is NO runtime AI icon generation, no sparkle generation button, no waiting, no icon-generation flow, no request to draw custom icons. Do not put implementation explanations such as “默认图标” inside the product interface. Do not invent scores, streaks, rewards, learning grades or extra business features. All data synthetic; no real children photos.
The six images must feel like themed versions of this SAME page. Keep artwork polished and education-appropriate, with plenty of readable text space.
Specific theme and fallback:
The reference supplies the approved-for-exploration GROWING GARDEN art direction: finely layered paper-cut leaves, a small original smiling sprout reading a book, warm sunlight, seed packets, cream scalloped surfaces and fresh green broad buttons. Retain its distinctive paper relief, charming plant world and polished craft; do not flatten it into a bland green UI. Recompose to the shared page structure above and replace the third preset subject with “思维拓展” and small “自定义”. Its generic fallback is ONE SIMPLE TWO-LEAF GREEN SPROUT in a small paper seed-packet/round pale-green badge, not a brain or unique course image. Use exactly that same sprout motif for any unknown subject. Decorative foliage around outer edges should be slightly restrained so content and controls stay clean. Preset Go/swim/book icons may be soft paper miniatures. Keep consistent matching green add buttons and original garden theme tab icons.
```

## C 星际探索

- 默认图标：小星球
- 视觉：观测站 · 星球与轨道
- 参考：/Users/bytedance/Documents/push_kids/docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-04/style-b.png

```text
Use case: ui-mockup.
Generate ONE refined Chinese mobile WeChat Mini Program Settings-page mockup for “知芽”, a parent-facing primary-school learning organizer. Output one full-screen flat front-facing portrait screenshot, approximately 9:19.5, no device frame, no outer presentation or labels. Crisp high-resolution simplified Chinese typography. This is a design preview only.
SAME SHARED PAGE STRUCTURE ACROSS ALL THEMES: compact status bar and WeChat nav in top 7%; page header/scene from 7–25%; subject section at 25–40%; extracurricular section at 42–66%; daily-task section at 68–91%; fixed five-tab bar at 92–100%. All functional text, FOUR activity/task rows and both add buttons must be fully visible. Theme artwork stays mainly in the header and outer margins; content has calm solid backgrounds and clean readable typography. Keep common button sizes, single-column lists and semantic hierarchy. Visual differentiation comes from scene artwork, materials, icons, background and surfaces, not different product behavior.
Exact screen content:
top status “9:41”, top centered sprout brand “知芽”, WeChat menu capsule at upper right;
header title “设置”, subtitle “小禾的学习与日常”, child selector “小禾”.
Section “在学科目”: three well-spaced subject tiles, “语文”, “数学”, “思维拓展”, followed by a small + add control. The third tile “思维拓展” has a small secondary label “自定义”. It MUST use the theme's GENERIC DEFAULT ICON specified below, NOT a custom thinking/puzzle/brain icon. The first two subjects can use a preset book and ruler icon. The purpose is to show that an unknown custom subject always uses the theme default.
Section “课外活动”: row “围棋” with “每周日 14:00–16:00”; row “游泳” with “每周日 17:00–18:00”; button “＋ 添加课外活动”.
Section “每日任务”: row “阅读” with “每天 20 分钟”; row “围棋” with “每天 30 分钟”; button “＋ 添加每日任务”.
Each row has relevant preset icon and a small right disclosure arrow.
The two add buttons must be EXACTLY the same visual style and surface in this theme. No arbitrary default gray native-button background.
Bottom navigation labels in order: “今日” “日程” “记录” “报表” “设置”, with the settings tab selected; home indicator below.
Important behavior constraints for the design: custom subjects get a generic theme fallback; there is NO runtime AI icon generation, no sparkle generation button, no waiting, no icon-generation flow, no request to draw custom icons. Do not put implementation explanations such as “默认图标” inside the product interface. Do not invent scores, streaks, rewards, learning grades or extra business features. All data synthetic; no real children photos.
The six images must feel like themed versions of this SAME page. Keep artwork polished and education-appropriate, with plenty of readable text space.
Specific theme and fallback:
The reference supplies the SPACE OBSERVATORY theme: navy cosmos header, small original friendly robot looking through a telescope, books, restrained stars and planets, pale icy station panels and periwinkle buttons. Retain the imaginative soft-clay 3D observatory atmosphere and calm body panels. Recompose to the exact shared page structure and subject content above, with “思维拓展” tagged “自定义”. Its generic fallback is a SIMPLE SMALL LAVENDER PLANET WITH ONE RING on a round light-blue badge, the same generic planet for any unknown subject, not a brain/puzzle icon. Keep orbital lines confined to margins, good dark text on pale content surfaces, small porthole presets for Go/swimming/reading. Two matching periwinkle add buttons, fixed consistent five-tab order. This is discovery and education, no game levels or reward systems.
```

## D 深海夜色

- 默认图标：罗盘星
- 视觉：深蓝灰 · 香槟色 · 安静细线
- 参考：/Users/bytedance/Documents/push_kids/docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-03/style-f-390x844.png

```text
Use case: ui-mockup.
Generate ONE refined Chinese mobile WeChat Mini Program Settings-page mockup for “知芽”, a parent-facing primary-school learning organizer. Output one full-screen flat front-facing portrait screenshot, approximately 9:19.5, no device frame, no outer presentation or labels. Crisp high-resolution simplified Chinese typography. This is a design preview only.
SAME SHARED PAGE STRUCTURE ACROSS ALL THEMES: compact status bar and WeChat nav in top 7%; page header/scene from 7–25%; subject section at 25–40%; extracurricular section at 42–66%; daily-task section at 68–91%; fixed five-tab bar at 92–100%. All functional text, FOUR activity/task rows and both add buttons must be fully visible. Theme artwork stays mainly in the header and outer margins; content has calm solid backgrounds and clean readable typography. Keep common button sizes, single-column lists and semantic hierarchy. Visual differentiation comes from scene artwork, materials, icons, background and surfaces, not different product behavior.
Exact screen content:
top status “9:41”, top centered sprout brand “知芽”, WeChat menu capsule at upper right;
header title “设置”, subtitle “小禾的学习与日常”, child selector “小禾”.
Section “在学科目”: three well-spaced subject tiles, “语文”, “数学”, “思维拓展”, followed by a small + add control. The third tile “思维拓展” has a small secondary label “自定义”. It MUST use the theme's GENERIC DEFAULT ICON specified below, NOT a custom thinking/puzzle/brain icon. The first two subjects can use a preset book and ruler icon. The purpose is to show that an unknown custom subject always uses the theme default.
Section “课外活动”: row “围棋” with “每周日 14:00–16:00”; row “游泳” with “每周日 17:00–18:00”; button “＋ 添加课外活动”.
Section “每日任务”: row “阅读” with “每天 20 分钟”; row “围棋” with “每天 30 分钟”; button “＋ 添加每日任务”.
Each row has relevant preset icon and a small right disclosure arrow.
The two add buttons must be EXACTLY the same visual style and surface in this theme. No arbitrary default gray native-button background.
Bottom navigation labels in order: “今日” “日程” “记录” “报表” “设置”, with the settings tab selected; home indicator below.
Important behavior constraints for the design: custom subjects get a generic theme fallback; there is NO runtime AI icon generation, no sparkle generation button, no waiting, no icon-generation flow, no request to draw custom icons. Do not put implementation explanations such as “默认图标” inside the product interface. Do not invent scores, streaks, rewards, learning grades or extra business features. All data synthetic; no real children photos.
The six images must feel like themed versions of this SAME page. Keep artwork polished and education-appropriate, with plenty of readable text space.
Specific theme and fallback:
Reference is the prior QUIET PREMIUM MIDNIGHT visual theme. Preserve its dark slate/navy background (#17252b), slightly lighter slate cards, champagne-gold accent (#e8c69a), fine outline icons and pale readable text. This is an understated dark-mode theme, NOT a cartoon underwater scene and NOT outer space. At most a subtle abstract midnight ocean horizon or a faint curved wave texture in the header, no fish, no whales, no robot, no planets. Use refined system-like sans-serif Chinese text, quiet rounded panels and light separators. Expand the header breathing room only to align with the shared comparison structure, keep attractive negative space. The custom “思维拓展” tile tagged “自定义” uses ONE SMALL CHAMPAGNE-GOLD FOUR-POINT COMPASS STAR inside a dark rounded badge; this is the generic fallback for all unknown courses. Both add buttons matching solid muted-champagne surface, dark text. Semantic line icons for the known rows. Calm premium atmosphere suitable for evening parental use. No glossy neon effects.
```

## E 海洋风格

- 默认图标：贝壳
- 视觉：浅海蓝 · 小鲸鱼 · 波浪与珊瑚
- 参考：无，新增主题

```text
Use case: ui-mockup.
Generate ONE refined Chinese mobile WeChat Mini Program Settings-page mockup for “知芽”, a parent-facing primary-school learning organizer. Output one full-screen flat front-facing portrait screenshot, approximately 9:19.5, no device frame, no outer presentation or labels. Crisp high-resolution simplified Chinese typography. This is a design preview only.
SAME SHARED PAGE STRUCTURE ACROSS ALL THEMES: compact status bar and WeChat nav in top 7%; page header/scene from 7–25%; subject section at 25–40%; extracurricular section at 42–66%; daily-task section at 68–91%; fixed five-tab bar at 92–100%. All functional text, FOUR activity/task rows and both add buttons must be fully visible. Theme artwork stays mainly in the header and outer margins; content has calm solid backgrounds and clean readable typography. Keep common button sizes, single-column lists and semantic hierarchy. Visual differentiation comes from scene artwork, materials, icons, background and surfaces, not different product behavior.
Exact screen content:
top status “9:41”, top centered sprout brand “知芽”, WeChat menu capsule at upper right;
header title “设置”, subtitle “小禾的学习与日常”, child selector “小禾”.
Section “在学科目”: three well-spaced subject tiles, “语文”, “数学”, “思维拓展”, followed by a small + add control. The third tile “思维拓展” has a small secondary label “自定义”. It MUST use the theme's GENERIC DEFAULT ICON specified below, NOT a custom thinking/puzzle/brain icon. The first two subjects can use a preset book and ruler icon. The purpose is to show that an unknown custom subject always uses the theme default.
Section “课外活动”: row “围棋” with “每周日 14:00–16:00”; row “游泳” with “每周日 17:00–18:00”; button “＋ 添加课外活动”.
Section “每日任务”: row “阅读” with “每天 20 分钟”; row “围棋” with “每天 30 分钟”; button “＋ 添加每日任务”.
Each row has relevant preset icon and a small right disclosure arrow.
The two add buttons must be EXACTLY the same visual style and surface in this theme. No arbitrary default gray native-button background.
Bottom navigation labels in order: “今日” “日程” “记录” “报表” “设置”, with the settings tab selected; home indicator below.
Important behavior constraints for the design: custom subjects get a generic theme fallback; there is NO runtime AI icon generation, no sparkle generation button, no waiting, no icon-generation flow, no request to draw custom icons. Do not put implementation explanations such as “默认图标” inside the product interface. Do not invent scores, streaks, rewards, learning grades or extra business features. All data synthetic; no real children photos.
The six images must feel like themed versions of this SAME page. Keep artwork polished and education-appropriate, with plenty of readable text space.
Specific theme and fallback:
Create a NEW SUNLIT OCEAN EXPLORATION education theme, visually unlike the dark midnight and space themes. Bright crystal-clear shallow-water aqua, azure, warm white and small coral-pink accents. Header is a beautifully crafted miniature underwater picture-book / soft paper relief scene: a small friendly original blue whale carrying a little book, shafts of gentle daylight through rippling water, a few bubbles, seaweed and restrained coral at the extreme corners. A tiny surface sailboat is acceptable but no huge full-screen animal. The functional panels are clean white or very pale aqua with soft wave-scalloped lower edges; subtle water ripple background only at outer margins. Subject tiles look like little clean floating study plaques. The “思维拓展” tile tagged “自定义” has ONE SIMPLE PEACH-AND-CREAM SCALLOP SHELL as the generic fallback for any unknown course, not a brain or bespoke subject illustration. Known icons stay readable: Go board, swim ring, book. Both add buttons use the same medium ocean-blue surface and white text, with one subtle wave accent. Charming coordinated ocean tab icons, selected settings clearly marked. Contemporary sophisticated child-friendly illustration, good contrast, no aquarium-game UI and no clutter behind text. Keep exact shared content and placement.
```

## F 科技风格

- 默认图标：芯片
- 视觉：白银青蓝 · 机器人 · 电路模块
- 参考：无，新增主题

```text
Use case: ui-mockup.
Generate ONE refined Chinese mobile WeChat Mini Program Settings-page mockup for “知芽”, a parent-facing primary-school learning organizer. Output one full-screen flat front-facing portrait screenshot, approximately 9:19.5, no device frame, no outer presentation or labels. Crisp high-resolution simplified Chinese typography. This is a design preview only.
SAME SHARED PAGE STRUCTURE ACROSS ALL THEMES: compact status bar and WeChat nav in top 7%; page header/scene from 7–25%; subject section at 25–40%; extracurricular section at 42–66%; daily-task section at 68–91%; fixed five-tab bar at 92–100%. All functional text, FOUR activity/task rows and both add buttons must be fully visible. Theme artwork stays mainly in the header and outer margins; content has calm solid backgrounds and clean readable typography. Keep common button sizes, single-column lists and semantic hierarchy. Visual differentiation comes from scene artwork, materials, icons, background and surfaces, not different product behavior.
Exact screen content:
top status “9:41”, top centered sprout brand “知芽”, WeChat menu capsule at upper right;
header title “设置”, subtitle “小禾的学习与日常”, child selector “小禾”.
Section “在学科目”: three well-spaced subject tiles, “语文”, “数学”, “思维拓展”, followed by a small + add control. The third tile “思维拓展” has a small secondary label “自定义”. It MUST use the theme's GENERIC DEFAULT ICON specified below, NOT a custom thinking/puzzle/brain icon. The first two subjects can use a preset book and ruler icon. The purpose is to show that an unknown custom subject always uses the theme default.
Section “课外活动”: row “围棋” with “每周日 14:00–16:00”; row “游泳” with “每周日 17:00–18:00”; button “＋ 添加课外活动”.
Section “每日任务”: row “阅读” with “每天 20 分钟”; row “围棋” with “每天 30 分钟”; button “＋ 添加每日任务”.
Each row has relevant preset icon and a small right disclosure arrow.
The two add buttons must be EXACTLY the same visual style and surface in this theme. No arbitrary default gray native-button background.
Bottom navigation labels in order: “今日” “日程” “记录” “报表” “设置”, with the settings tab selected; home indicator below.
Important behavior constraints for the design: custom subjects get a generic theme fallback; there is NO runtime AI icon generation, no sparkle generation button, no waiting, no icon-generation flow, no request to draw custom icons. Do not put implementation explanations such as “默认图标” inside the product interface. Do not invent scores, streaks, rewards, learning grades or extra business features. All data synthetic; no real children photos.
The six images must feel like themed versions of this SAME page. Keep artwork polished and education-appropriate, with plenty of readable text space.
Specific theme and fallback:
Create a NEW DAYLIGHT FUTURE LEARNING LAB theme, distinctly NOT space, NOT dark cyberpunk, NOT an enterprise dashboard. Bright porcelain-white, pale silver, clean cyan/teal and tiny lime accents. The header is a beautifully rendered original friendly geometric robot in a compact learning lab, arranging a book and small modular geometric objects; use soft ceramic and brushed matte metal materials. Sparse circuit traces, a subtle square microgrid and small translucent acrylic plates around the margins. No planets, stars, rockets or underwater animals. Crisp white content panels with restrained cyan edge details, small modular corner cuts, precise generous typography and warm approachable proportions. The custom “思维拓展” subject tile tagged “自定义” uses ONE SIMPLE CYAN MICROCHIP SYMBOL in a pale cyan hexagonal or rounded-square badge, the same generic fallback for all unknown subjects. Keep familiar preset book/ruler/Go/swim icons as restrained small technical pictograms, no newly invented course-specific graphic. Two identical cyan-teal add buttons with dark navy or clear white text of strong contrast. Five coherent minimal tech tab icons. Technology as curiosity and making things; avoid code dumps, HUD clutter, fake metrics, excessive glows and glossy gradients. Exact shared content, layout and all rows visible.
```
