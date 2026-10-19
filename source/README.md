# POPUP 北美版本：设计与 Demo 工作说明

这份说明写给之后接手的 Claude 会话，也写给你自己。新会话开始时，请先读这份文件。

## 产出物与链接

| 内容 | 位置 |
|---|---|
| 设计画布（所有画板，用户会直接在上面改） | https://claude.ai/artifact/9zrdKt4LmmsFAKuxXrW3Y1 |
| 交互 Demo（Claude 页面） | https://claude.ai/artifact/LK8xvNTr5zYUSJSfMW1Hih |
| 交互 Demo（对外分享，GitHub Pages） | https://sharonhuang777.github.io/POPUP/ |
| 代码仓库 | github.com/sharonhuang777/POPUP（根目录 `index.html` 就是 Pages 上的 demo） |
| Figma 主稿（Popup 页面导出） | https://www.figma.com/design/ahyASGXkdNrcoNWEfghLfJ |
| Figma「Popup 北美」 | https://www.figma.com/design/inGVkstbsBcINjIRbensA5 （广场 21-xx、引导 10-09 等画板） |

## 目录结构（本文件夹 `source/`）

- `remote/project/*.dc.html`：demo 用到的画板源文件，从画布复制过来。
- `canvas/project/img/`：画布和 demo 共用的图片。
- `demo/shell.html`：demo 外壳，包括手机框、底部导航栏、广场发帖按钮、页面切换。
- `demo/chat.html`：每日对话页，包括逐字打字、思考文案轮换、标题状态。
- `demo/home-preview.html`、`demo/home-insights.js`：首页。
- `demo/outfit.woff2`：Outfit 字体，已内嵌进 demo。国内打不开 Google Fonts，所以不能改回外链。
- `tools/build_demo.py`：把各页面打包成一个单文件 demo。
- `tools/standalone.py`：生成 `demo/standalone/index.html`，也就是 Pages 版本。
- `tools/think_rotate.js`：匹配思考页状态行的轮换文案。
- `tools/call_reveal.js`：语音通话页的揭面交互和计时。
- `tools/drop_patch.py`：个人主页标签掉落动画的补丁。
- `tools/voice_state.js`：语音匹配的剩余免费次数显示（启动页、匹配失败页、通话结束页），次数由 shell 统一管理。
- `tools/queue_tick.js`：排队页的人数、进度条和预计等待倒数，约 5 秒后进入「轮到你」。
- `tools/ended_rate.js`：通话结束页的打星交互。

## 更新 demo 的流程

1. 如果画布上的画板改过，先用 Artifact `read` 读取画布最新的文件。用户会同时在画布上编辑，发布前一定要先读一遍，不然会冲突或覆盖掉用户的修改。然后把读到的文件复制进 `remote/project/`。
2. 运行 `python3 tools/build_demo.py && python3 tools/standalone.py`。
3. 运行 `cp demo/standalone/index.html ../index.html`，然后 commit 并 push 到 main。
4. 用 Artifact 发布 `demo/Popup Demo.html`，url 填 demo 的链接。
5. 画布修改的发布方式：url 填画布链接，root 填画布文件所在目录，file_path 填要改的那个 `project/xxx.dc.html`。

## 已确定的设计决定（不要改回去）

- **个人主页（方案 B）**
  - 紫色云朵封面 `cover-cloud.jpg`。
  - 紫色系实色标签，保留玻璃高光，不要描边。
  - 进入页面时标签有掉落动画。
  - 「Share a fresh moment」发帖卡片，带 Today 时间戳。
  - 帖子距屏幕左右各 16px。
  - 没有 svip / platinum 标识，没有 Cloud 按钮。
- **他人主页**
  - 蓝天封面，蓝色系标签。
  - Follow 按钮是描边样式，Chat now 是 #282828 实色。
  - 没有共同标签，没有「you both love music」。
- **广场**
  - 右下角 Threads 风格的发帖按钮：纯白 56px 圆形、柔和阴影、黑色加号 2.3px。
  - 按钮离底部导航栏 32px。
- **私聊列表**：没有语音消息。
- **语音匹配 · 排队 / 失败 / 结束**（参考东南亚版改成北美风格，2026-10-16）
  - 排队、轮到你、匹配失败用启动页的浅色奶油底和玻璃卡片；通话结束页延续通话页的深紫色。
  - Priority 价格统一为 10 金币，划掉的原价是 30。
  - 排队页（2026-10-19 改版）：不再放珍珠球和一排他人头像。上方是珊瑚到紫色渐变的超大数字（前面还有几人），下面写「people ahead of you」，再下面是「Line is moving」状态。往下是一条进度条：用户头像（标「You」）停在已经走过的位置，最右边是珊瑚色的通话按钮（标「Call」）；排队推进时，填充和头像一起向通话按钮移动；进度条上有循环扫光，通话按钮有三圈向外扩散的波纹。底部是预计等待时间和「Skip the line」按钮。
  - 匹配失败页和通话结束页都有「无次数」版本：Standard 按钮置灰，点击后弹提示「No free matches left today. Go Priority to keep matching.」。
  - 通话结束页：没有揭面的对方头像保持模糊，显示「Identity stayed private」；三颗星打分。
  - 顺序是先思考、再排队：Standard 先进思考页，人多时才进排队页，排到后进「轮到你」。
  - Demo 流程：启动页 Standard（消耗 1 次）→ 思考页 → 排队 → 轮到你 → Regular line → 第一次匹配失败 → Standard match（再消耗 1 次）→ 思考页 → 接通（这次不排队）→ 挂断 → 通话结束页（0 次，点 Standard 弹提示）。排队页的 Skip the line 和「轮到你」的 Priority line 直接接通；其他页面的 Priority 走加速思考页。每日共 3 次，启动页显示剩 2 次。
- **语音通话**
  - 深紫色界面，双方头像先用毛玻璃遮住。
  - 点「Reveal to keep talking」后，自己先揭面，约 1.6 秒后对方揭面，倒计时改为正计时。
  - 不用面具（用户觉得 Aura / Masquerade 两版很丑）。
- **每日对话**
  - AI 思考时，三个点右侧的文案会轮换，从下往上切换。
  - 标题下的状态只在 thinking / typing / waiting for you 之间切换。
  - 用户发出的消息气泡右侧显示用户头像（avatar.png，32px 圆形，白色描边）。
  - 导航栏右侧有「更多」按钮（三个点，和返回按钮同款玻璃圆钮）。
  - 点「更多」弹出菜单，里面是「Start a match」（Text or voice · free today），图标用 Popup 珍珠球（40px，不加投影），任何时候都能点。点了以后进入彩色匹配浮层，和答完 3 题的推荐浮层是同一个，只是文案换成「Ready when you are / Let's find someone for you」。从菜单进入时，「Maybe later」只关闭浮层、回到对话，不发消息。
- **匹配思考页**（语音 Standard / Priority、文字匹配，按 2026-10-19 文档）
  - 三段思考文案依次出现在原位置，打完后变成对应的洞察，已完成的洞察保留在上方：
    1. Reviewing what you've shared… → 洞察一
    2. Understanding what helps you open up… → 洞察二
    3. Noticing the kind of connection you want… → 洞察三
  - 三条之后的最后一行固定显示、不再轮换：文字匹配和 Standard 语音是「Searching with the signals you've shared…」，Priority 语音是「Prioritizing your search with the signals you've shared…」。

## 注意事项

- 用户用中文交流，偏好直接改、改完给效果。
- 在 Figma 里，`html_to_figma` 被代理拦截，只能用 `use_figma` 画。图片要用 base64 加 `figma.createImage` 上传，单次调用的代码不能超过 50KB。
