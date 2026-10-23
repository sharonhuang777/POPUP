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
- `native/PearlOrb/`：三种匹配思考页珍珠球的原生实现（Android Kotlin + OpenGL ES、iOS Swift + Metal），着色器与 Web 版一致，附 Web 参考页和逐像素对照图，接入说明见其中的 README。
- `tools/profile_scroll.js`：我的主页上滑时的封面视差、顶栏铺封面色和标题淡入。
- `handoff/match-success/`：4 个匹配成功页的开发交付包，包括时间轴说明（README）、透明动画 WebP 特效、呼吸光 PNG 和参考 MP4。开发反馈 WebP 和原生头像动画可能不同步，已改为 Lottie（`lottie/` 子目录，头像也在 Lottie 里）；WebP 保留作备选。
- `tools/lottie_sample.js`、`tools/make_lottie.py`、`tools/lottie_compare.js`：把画板动效导出为 Lottie（逐帧采样 → 生成 JSON → 和画板逐帧对比）。匹配成功 4 页的 Lottie 在 `handoff/match-success/lottie/`，对照页 https://claude.ai/artifact/1e7G71vDvPASqkRC98QgRK 。
- `tools/render_frames.js`：用 Playwright 逐帧渲染画板，可只保留特效节点并输出透明背景，用于导出 WebP 和参考视频。

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
  - 帖子上滑效果（2026-10-20，画板 ProfileMeScroll，`tools/profile_scroll.js`，参考「他人主页 · 内容贴边」）：封面以约 0.45 倍速度视差上移；白色内容区碰到顶栏时（上滑约 150→204px），顶栏连同状态栏铺满封面取色的紫色 #9466E0，工具按钮变成深色半透明圆底、白色图标；昵称行滑过顶栏后，返回按钮右边淡入白色「Jules」。
  - 没有 svip / platinum 标识，没有 Cloud 按钮。
- **他人主页**
  - 蓝天封面，蓝色系标签。
  - Follow 按钮是描边样式，Chat now 是 #282828 实色。
  - 没有共同标签，没有「you both love music」。
- **广场**
  - 右下角 Threads 风格的发帖按钮：纯白 56px 圆形、柔和阴影、黑色加号 2.3px。
  - 按钮离底部导航栏 32px。
- **私聊列表**：没有语音消息。
- **匹配前设备检测**（2026-10-22）：普通/加速语音思考页，在球体和思考卡片之间放一个居中的玻璃胶囊，依次检测麦克风 → 声音 → 网络：每项先显示「Checking …」+ 转圈，约 1.1 秒后右侧图标变成绿色对勾、文字换成「Microphone is on / Sound is on / Network is stable」（文字保持原色，不变绿）；画布画板循环播放，Demo 只播一次，然后向上淡出、下一项从下方进入（每项 1.9 秒，三项约 6 秒后胶囊消失）。思考卡片相应下移 34–38px。检测失败单独一页 VoiceDeviceFail（按东南亚版布局）：顶部次数刷新提示 → 警示球 → 「Make sure before matching」清单（失败项整行标红）→ 清单下方「Network unavailable / Please try again once your connection is back.」→ 底部 Try again / Back home。Demo 右侧有「设备检测失败」按钮。不要把检测放进思考卡片里。
- **匹配成功页**（2026-10-22）：两个头像加速撞上（接触前不减速），撞上瞬间出「Match successfully!」，随后副标题；标题和头像出现后不再消失。彩屑散开后受重力加速下落（不在空中停留）。元素出齐（约 0.9s）后再停 1s 自动进入语音通话。Demo 里所有接通（思考页、排队 Skip、轮到你）都先经过这一页。画布画板播放一次停在终帧，点画板重播。去掉了头像上方的爱心。
- **加速卡匹配成功页**（2026-10-22）：北美版不用闪电，也不直接用思考页的球。用方案 B：一圈柔和的珊瑚色光（模糊光环 + 一道亮光弧，不用硬描边、不用彩虹渐变、不用虚线环和放射线）加速旋转并收成一团光，一闪后两个头像从中心弹出、左右分开再加速撞到一起；撞上即出「Priority Match Success」，「You just skipped 582 people!」数字从 0 跳到 582；撞上时不用普通版的彩带，改成发光粒子（光点向外炸开后微微上飘、闪烁淡出，夹几道放射状短光线）；之后头像后面只留一团会呼吸的柔光。约 2.2s 元素出齐，再停 1s 进入语音通话。Demo 里加速路径（加速思考页、排队 Skip the line、轮到你选 Priority）走这一页，普通路径走匹配成功页。生成脚本 tools/gen_priority_variants.py（方案 A 光尾冲撞仅保留在脚本里）。
- **Demo 里看三种匹配成功**（2026-10-22）：Voice Match 起始 3 次 Standard。第 1 次 Standard：思考 → 排队 → 轮到你，选 Regular 失败一次；第 2 次 Standard：思考 → 普通匹配成功；第 3 次 Standard：思考 → 被别人用加速卡匹配到（Special Call，被匹配方）。点 Priority / 排队 Skip the line / 轮到你选 Priority / 失败页 Use now → 加速卡匹配成功（主动方）。三页都是元素出齐后 1s 进通话。Demo 右侧有「语音匹配 · 直接切到状态」按钮（起始页、普通/加速卡匹配中、排队中、轮到你、匹配失败、三种匹配成功、通话、通话结束），给开发快速查看；窗口宽度小于 900px 时右侧栏隐藏。
- **语音匹配 · 排队 / 失败 / 结束**（参考东南亚版改成北美风格，2026-10-16）
  - 排队、轮到你、匹配失败用启动页的浅色奶油底和玻璃卡片；通话结束页延续通话页的深紫色。
  - Priority 价格统一为 10 金币，划掉的原价是 30。
  - 排队页（2026-10-20 定为方案 E，沿用东南亚排队动画的布局和动效）：标题「You're in line」，副标题「12 people are ahead of you」（数字珊瑚色，demo 里从 12 递减）。中间是 3D 粉色电话亭图 `img/booth.png`（产品提供，轻微上下浮动）；电话亭前一排 5 个头像每 2 秒整体左移一位，中间最大并弹出珊瑚到紫的渐变光圈，两侧渐小渐淡、右进左出；头像阴影不能被遮罩裁掉。底部是预计等待时间卡片和「Skip the line」按钮。之前的大数字 + 进度条方案和 A–D 方案留在画布上作为备选。
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
- **文字匹配成功**（2026-10-22，后改）：匹配中就是文字思考页的球体动画，所以成功页只保留头像碰撞：你和对方的匿名 3D 头像从两侧加速冲进来撞上（接触前不减速，撞后约 0.85s 慢回弹）→「Match degree 86%」进度条（#FF57A8 → #F55E67 横向渐变）填满 →「Chat now!」+ 下落彩屑。去掉了头像轮换、共同标签、百分比胶囊和底部提示卡。画板 TextMatchSuccess 循环演示；Demo 里文字思考页之后进入这一页，只播一次并停在成功画面。生成脚本 tools/gen_text_match.py。
- **语音通话页 His Tag / 底部按钮沿用旧版样式**（2026-10-22，Figma 863:243 的 935:1564 与 935:1514）：His Tag 两行居中，Montserrat 13/12，标签 23px 高、圆角 32、白 10% 底、#BABABA 字，星座标签 #848EFF 30% 底；底部 4 个按钮 44px 圆、间距 17、文字 Montserrat Medium 12 白：Mic on / Loudspeaker 为白 80% 底黑色图标，Game / Gift 为 #6E44D1 → 透明渐变紫圆、白色图标。研发可直接复用旧组件。Vibe check 卡片随之上移到 343。Demo 内嵌 Montserrat（demo/montserrat-500/600.woff2）。
- **普通匹配成功弱化**（2026-10-22）：为了和加速卡区分，普通匹配成功的彩带从 14 片减到 7 片、抛出距离缩短；撞击光圈改成淡紫细线、最高 35% 透明度、只扩到 2.2 倍；中心闪光减到 55%。加速卡两页不变。
- **语音通话揭面状态按 Figma**（2026-10-22，863:243 / 935:2745 / 935:2922 / 935:3113 / 935:2560）：倒计时 ≤30s 变红 #FE6063；揭面后状态文字为粉色 #FF95F1 Montserrat SemiBold 12「Revealed」+ 粉色圆形对勾；对方先揭面时 Reveal 按钮扫光；我先揭面时按钮变 #3C2462 实色「waiting for him to reveal...」；双方都揭面后头像中间出现「90% Compatibility」（#FFF495→#FFFCE2），状态栏和按钮隐藏，换成「we’ve been chatting for」+ 正计时。Demo：倒计时从 0:45 开始，0:38 对方自动先揭面；倒计时到 0 未双方揭面则进入通话结束页。
- **Figma 切图面板**（2026-10-22）：「语音文字匹配过程」页（684:2115）最下方 y=3300 新建「切图 Slices · 北美匹配 / 通话」（953:107）。北美各帧里的图标、图片、背景复制成独立图层，原稿不动：图标 32 个（导出 SVG + PNG@2x/@3x），图片 28 个（PNG@2x/@3x），背景 9 张 402×874（只有底色和光晕，不含 UI，PNG@2x/@3x）。图层名即导出文件名（ic_ / btn_ / img_ / bg_ 前缀）。设计稿再改后需要重新整理。
- **通话缩小成悬浮球**（2026-10-22）：通话页点右上角 ⤡，整页缩放 + 圆形裁切收进右上角 68px 小球（0.42s，cubic-bezier(.4,0,.2,1)），然后回到首页，可以切任意 tab。小球：白色毛玻璃（62% 白 + 16px 模糊 + 白描边 + 淡紫投影），里面是对方头像（未揭面时模糊），外圈两道说话波纹，下方小胶囊显示通话计时（倒计时最后 30s 变红，双方揭面后显示已通话时长），左侧绿点表示通话中。小球可拖动，松手吸到最近的左右边。点小球从小球位置展开回通话页（0.46s）。通话在后台继续计时，倒计时到 0 直接进通话结束页。画板 VoiceCallMinimized 循环演示；Demo 里在通话页点 ⤡ 即可体验。
- **Figma：通话缩小球**（2026-10-22）：「语音文字匹配过程」页通话那一排右侧新增 956:125「Voice call · Minimized · 缩小球（通话中浏览其他页面）」（首页 + 右上角小球）和 956:234「缩小球状态 / 交互说明」（A 未揭面 / B 对方已揭面 / C 最后 30 秒 / D 双方已揭面，附交互参数）。切图面板加了 bg_mini_call_bubble_68 和 bg_mini_call_timer_pill。
- **私聊列表滚动 + Tab 未读**（2026-10-22）：私聊列表加到 17 个会话，列表在页面内滚动，顶部标题栏固定；一旦往上滑，标题栏后面淡入白色毛玻璃条（78% 白 + 20px 模糊 + 底部细线）；再点一次底部「私聊」tab 平滑回到顶部。Tab 栏未读：广场和私聊都用同一种红色数字角标（18px 高、#FF4D5E、1.5px 白描边、白色 10.5px 粗体数字）：广场 5（与广场右上角铃铛的未读数一致，铃铛也换成同样的数字角标），私聊 23（未读会话消息总数）。画板 Messages 自动循环演示滚动；Plaza 画板的铃铛、广场 tab、私聊 tab 都带数字角标。生成脚本 tools/gen_messages.py。
- **Figma：未读角标**（2026-10-22）：「广场/私聊/个人主页」页新建组件「Badge / Unread count」（959:687，在「Icons · 切图（广场用）」下方，数字是组件文字属性 Count，可导出 SVG/PNG）。实例已放到：Popup · Plaza 的广场 tab（5）、私聊 tab（23）、右上角铃铛（5，原小红点已隐藏）；Popup · Messages 的两个 tab；「语音文字匹配过程」页 Popup Home 和缩小球页的 tab 栏。
- **Figma：设备检测图标**（2026-10-23）：切图面板 953:107 最下方新增「Device check」15 个：麦克风 / 声音 / 网络 × 普通（#7356D4）/ 加速（#E8645F），每个都有 24px 带浅色圆底版（ic_check_*_24，胶囊里用的）和 15px 纯图标版（ic_*_15）；另有两色检测中转圈（ic_check_spinner_*_18，App 里 0.8s 一圈匀速旋转）和通过对勾（ic_check_passed_18，#34C27A）。全部可导出 SVG + PNG@2x/@3x。
- **Figma：匹配成功 / 设备检测失败**（2026-10-23）：「语音文字匹配过程」页第二排（y=1000）右侧新增 4 帧，均为可编辑图层（文字、渐变、阴影、SVG 图标），头像为图片填充：1010:130 普通匹配成功、1012:130 加速卡匹配成功（主动方）、1012:147 Special Call（被匹配方）、1012:164 设备检测失败（网络）。画面是动效结束后的静止状态，每帧下方注明对应 Lottie 文件。生成工具 `tools/dom2figma.js`（画板某一时刻 → 图层 JSON），再用 use_figma 绘制。
