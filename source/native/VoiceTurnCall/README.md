# 排队成功 · 轮到你：中间通话动画（Lottie）

- **文件**：`voice_turn_call.json`，Lottie 格式，透明背景，约 34 KB，纯矢量，任意倍率都清晰。
- **画布**：280×280，60fps。球心在画布正中，对应设计稿里球心的位置（画板 x=201, y=342）。
  - 球体 128，三圈波纹从 144 放大到 240（同心）。
  - 放置时把这个 280×280 的视图中心对准球心即可。
- **分段**（文件里已写好 marker）：
  - `intro`：第 0–42 帧（0–0.7s）。球从 60% 弹出放大到 106%，再回到 100%，同时淡入。只播一次。
  - `loop`：第 42–906 帧（0.7–15.1s）。球呼吸缩放（1→1.07，1.6s 一次），电话图标做来电式的轻微摇晃和放大，三圈波纹交替向外扩散（1.8s 一圈，间隔 0.6s）。首尾无缝，循环播放这一段。15.1s 是 1.6 和 1.8 的最小公倍数，所以这一段比较长，但文件很小。

## 播放

- iOS（lottie-ios 4.x）：先 `play(fromMarker: "intro", toMarker: "loop")`，完成后 `play(fromMarker: "loop", toMarker: nil, loopMode: .loop)`；或者直接用帧号 0→42，再 42→906 循环。
- Android（lottie-android 6.x）：先 `setMinAndMaxFrame("intro")` 播一次，然后在 `onAnimationEnd` 里 `setMinAndMaxFrame("loop")`，`repeatCount = LottieDrawable.INFINITE`。
- 系统开启「减弱动态效果」时，停在第 42 帧（完整的静止状态）。
- 浏览器打开 `preview.html` 可以预览，有重播、深色背景、棋盘格（看透明）三个按钮。预览页从 cdnjs 加载 lottie-web，需要联网。

## 与设计稿的差别

- 设计稿的球体有毛玻璃（backdrop blur）和内阴影，Lottie 做不了。这里用渐变叠加近似：顶部高光、底部淡紫内阴影，投影用径向渐变模拟 `0 18px 40px rgba(130,100,210,.28)`。放在页面的浅色背景上，和设计稿基本一致，球体颜色略偏一点紫。
- 网页版里第 2、3 圈波纹在开头会先静止显示一下（CSS 延迟导致的瑕疵），这里改成从一开始就以稳定的节奏扩散。
