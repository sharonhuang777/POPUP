# PearlOrb：匹配页球体动画（iOS / Android 原生）

设计稿里普通语音匹配、加速语音匹配、文字匹配三个思考页的珍珠球，原版是一段 WebGL 着色器加一小段每帧计时代码。这个包把它们原样搬到客户端：

| 场景 | 调色板 | Android | iOS |
|---|---|---|---|
| 普通语音匹配（紫） | POPUP_PURPLE | `PearlOrbPalette.STANDARD` | `.standard` |
| 加速语音匹配（珊瑚） | POPUP_VOICE | `PearlOrbPalette.PRIORITY` | `.priority` |
| 文字匹配（雾蓝） | POPUP_MIST | `PearlOrbPalette.TEXT` | `.text` |

三者用的是同一个着色器、同一套计时逻辑，只是 15 个颜色参数不同。页面上都是「thinking」状态。

## 目录

```
PearlOrb/
├─ android/PearlOrbView.kt     Kotlin，TextureView + OpenGL ES 2.0，单文件，无依赖
├─ ios/PearlOrbView.swift      Swift，MTKView + Metal，单文件，运行时编译着色器，无依赖
├─ ios/PearlOrb.metal          与 Swift 内嵌的着色器源码相同，仅供阅读
├─ shared/pearl_orb.frag       GLSL 着色器（Android 直接使用这一份）
├─ shared/palettes.json        三套调色板
└─ reference/
   ├─ reference.html           Web 原版，浏览器打开即可对照
   └─ frames/*.png             原版着色器在固定参数下的截图，用于逐像素对照
```

## 接入

**Android**（minSdk 21，OpenGL ES 2.0）

```kotlin
val orb = PearlOrbView(context).apply {
    palette = PearlOrbPalette.PRIORITY   // 加速语音
    thinking = true
}
container.addView(orb, 300.dp, 300.dp)   // 设计稿尺寸 300×300
```

也可以在 XML 里写 `<com.popup.orb.PearlOrbView android:layout_width="300dp" android:layout_height="300dp"/>`。包名 `com.popup.orb` 可以随意改。

**iOS**（iOS 13+，Metal）

```swift
let orb = PearlOrbView(palette: .text)   // 文字匹配
orb.frame = CGRect(x: 51, y: 96, width: 300, height: 300)
view.addSubview(orb)
```

背景是透明的，直接叠在页面背景上即可。

## 和 Web 原版一致的地方

1. **着色器**：逐行来自设计稿代码，只做了两处不影响画面的改动：
   - 原版有 6 处 `pow(x, 2.)` 的底数可能为负。GLSL 和 Metal 规定负底数的 `pow` 结果未定义，部分安卓 GPU 和 Metal 会算出 NaN，导致高光丢失。这里改成 `x*x`。已在 Chrome 里用三个时间点对比原版和修改版，像素差为 0。
   - 输出改为预乘 alpha（`rgb*a, a`），因为 Android 和 iOS 的合成器都要求预乘。Web 用的是非预乘，叠到背景上的效果相同。
   - iOS 的 Metal 版本不是手工翻译的，是用 glslangValidator 加 SPIRV-Cross 从同一份 GLSL 自动转换的，语义完全一致。编译时关闭了 fast-math，以贴近 GLSL highp。
2. **计时逻辑**：`tick()` 原样移植，包括：
   - 呼吸节奏 `breath`、思考时的流速变化、缩放 `extent = 2.9 / scale`。
   - `thinking` 和 idle 之间的过渡（指数缓动，系数 2.6）。
   - 单帧时间上限 0.1 秒；切到后台再回来时，第一帧 dt = 0。
3. **渲染分辨率**：Web 按 `min(设备像素比, 1.5)` 渲染，画布最长边不超过 680 px，再由浏览器放大显示，所以原版看起来略柔。原生默认用同样的规则（`maxRenderScale = 1.5`），保证观感一致。想要更锐利，可以把它调到 3。
4. **系统「减少动态效果」**：对应 Web 的 `prefers-reduced-motion`，只画一帧静止画面。
   - iOS 读取「减弱动态效果」。
   - Android 读取「移除动画」或动画时长缩放为 0（API 26+）。

## 如何验证「百分百还原」

- **肉眼对照**：用浏览器打开 `reference/reference.html`，和真机上的 View 并排比较动态效果。
- **像素对照**：
  1. 把 View 设为 600×600 px，并把 `maxRenderScale` 调大，让它以 600 px 渲染。
  2. 设置 `debugFixedTime = 7.3f`（iOS 为 `7.3`），View 会固定画 time=7.3、activity=1、extent=2.9 这一帧。
  3. 截图后和 `reference/frames/<调色板>_t7.3.png` 对比，同目录里还有 t1.6 和 t23.9 两个时间点。
  4. 参考图是非预乘透明 PNG，比较时请把两边叠在同一种背景色上。
  5. 不同 GPU 的浮点精度不同，个别像素允许 1～2 级色差。

## 尚未在真机上跑过

- **Android**：`PearlOrbView.kt` 已用 Kotlin 编译器做过语法和类型检查。因为拿不到 Android SDK，检查时用的是 Android API 的存根，没有在真机上运行过。
- **iOS**：Metal 着色器由工具链自动生成。`PearlOrbView.swift` 在当前环境无法编译（需要 Xcode）。
- 请客户端同学首次接入时按上面的步骤做一次像素对照。
