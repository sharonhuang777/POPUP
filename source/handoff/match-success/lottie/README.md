# 匹配成功 · Lottie 版

4 个文件，每个文件包含一页的头像碰撞和全部特效。背景、标题、副标题、数字、匹配度进度条由原生实现。

| 文件 | 页面 | 时长 | 播放方式 |
|---|---|---|---|
| voice_match_success.json | 普通语音匹配成功 | 3.0s | 单次播放 |
| priority_success.json | 加速卡匹配成功（主动方） | 6.6s | 先播 `intro`（0–3.4s），再循环 `loop`（3.4–6.6s，呼吸光） |
| priority_received.json | Special Call（被加速卡用户匹配） | 6.2s | 先播 `intro`（0–3.0s），再循环 `loop`（3.0–6.2s） |
| text_match_success.json | 文字匹配成功 | 2.9s | 单次播放 |

- **画布尺寸：** 402 × 874，60fps。全屏铺在背景之上、文字之下，宽度按屏宽等比缩放，顶部对齐。
- **头像：** 图片资源 id 为 `avatar_left` 和 `avatar_right`，运行时替换成真实头像：
  - iOS 用 `imageProvider`
  - Android 用 `setImageAssetDelegate`
  - Web 改 `assets[].p`

  图片层自带圆形遮罩，白色描边和投影是单独的图层。
- **文字触发：** 文字和数字监听 Lottie 里的 markers 触发，所以和头像碰撞严格同步：

  | marker | 含义 |
  |---|---|
  | `impact` | 撞击 |
  | `title_in` | 标题出现 |
  | `subtitle_in` | 副标题出现 |
  | `count_up` | 数字开始滚动 |
  | `count_pop` | 数字弹一下 |
  | `degree_in` / `degree_fill` | 匹配度胶囊出现 / 进度条填充 |
  | `go_to_call` | 跳转到通话页 |

  文字动画的参数见上一级目录的 README。
- **兼容性：** 只用到形状、纯色和渐变填充、描边、图片和蒙版。模糊和发光已经转成径向渐变，不依赖 blur 效果或混合模式，iOS、Android、Web 三端渲染一致。
- **生成方式：** `tools/lottie_sample.js` 从画板逐帧采样每个元素的变换和透明度，`tools/make_lottie.py` 生成 Lottie，`tools/lottie_compare.js` 用 lottie-web 和画板逐帧对比。目前 4 页的平均像素差都在 0.6/255 以内。
