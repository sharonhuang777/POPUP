# 思考过程 · 三点图标动画（动态 WebP，透明背景）

设计稿里该图标的显示尺寸是 20×20pt。文件按 120×120px 输出（相当于 6 倍图），30fps。

| 文件 | 内容 | 时长 | 播放 |
|---|---|---|---|
| `thinking_dots_loop.webp` | 三个点（黄 #FFD17A、珊瑚 #F2836E、浅粉 #FFB8A6）绕中心旋转，靠近时有融合的粘连效果 | 2.3s，首尾无缝 | 无限循环 |
| `thinking_dots_merge_once.webp` | 先旋转 1 秒，再用 1.1 秒合并成一个珊瑚色圆点（#E8645F），最后停住 | 2.4s | 只播一次，停在最后一帧 |

- 默认用的是有损压缩版，各约 60KB。`lossless/` 里是无损版（约 90–110KB），边缘略干净一点。
- 对应设计稿：每一行思考中是 loop；该行洞察出现时切到 merge_once；之后设计稿里图标会再缩小到 80%、透明度降到 45%，这一步建议客户端直接用透明度和缩放动画来做（0.6s，ease）。
- 安卓：API 28+ 用 `AnimatedImageDrawable`，低版本用 Glide 或 Fresco；iOS：用 SDWebImage（SDWebImageWebPCoder）或 iOS 14+ 原生解码。
