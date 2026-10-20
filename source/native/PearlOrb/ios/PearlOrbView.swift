// PearlOrb — native iOS port of the Popup "pearl orb" WebGL animation
// (voice match standard / priority, text match). Same fragment shader (GLSL → SPIR-V → Metal via
// SPIRV-Cross), same timing code, same render-resolution rule as the web version.
//
// Usage:
//   let orb = PearlOrbView(palette: .standard)   // .standard 普通语音 / .priority 加速语音 / .text 文字匹配
//   orb.frame = CGRect(x: 0, y: 0, width: 300, height: 300)   // 300×300 pt in the design
//   view.addSubview(orb)
//
// Requirements: iOS 13+, Metal. No other dependencies, no .metal build step (compiled at runtime).
import MetalKit
import UIKit

public struct PearlOrbPalette {
    /// 15 colours in this order: deep, light, fold, film, film2, back, boost, rim, rim2, inner, edge, envLo, envHi, thread, warm
    public let colors: [SIMD3<Float>]
    public static let standard = PearlOrbPalette(colors: [SIMD3<Float>(0.48, 0.3, 0.79), SIMD3<Float>(1.02, 0.91, 0.8), SIMD3<Float>(0.7, 0.49, 0.92), SIMD3<Float>(0.7, 0.54, 1.0), SIMD3<Float>(1.0, 0.83, 0.6), SIMD3<Float>(0.69, 0.61, 0.83), SIMD3<Float>(0.6, 0.43, 0.88), SIMD3<Float>(0.68, 0.53, 0.92), SIMD3<Float>(1.0, 0.87, 0.67), SIMD3<Float>(0.87, 0.73, 1.0), SIMD3<Float>(0.56, 0.39, 0.77), SIMD3<Float>(0.19, 0.105, 0.34), SIMD3<Float>(0.88, 0.79, 1.02), SIMD3<Float>(0.75, 0.63, 1.0), SIMD3<Float>(1.2, 0.76, 0.38)])   // POPUP_PURPLE
    public static let priority = PearlOrbPalette(colors: [SIMD3<Float>(0.8, 0.38, 0.4), SIMD3<Float>(1.02, 0.91, 0.8), SIMD3<Float>(0.96, 0.62, 0.6), SIMD3<Float>(1.0, 0.6, 0.56), SIMD3<Float>(1.0, 0.83, 0.6), SIMD3<Float>(0.9, 0.7, 0.68), SIMD3<Float>(0.94, 0.54, 0.52), SIMD3<Float>(0.96, 0.6, 0.56), SIMD3<Float>(1.0, 0.87, 0.67), SIMD3<Float>(1.0, 0.8, 0.76), SIMD3<Float>(0.78, 0.4, 0.42), SIMD3<Float>(0.32, 0.1, 0.12), SIMD3<Float>(1.02, 0.87, 0.83), SIMD3<Float>(1.0, 0.72, 0.68), SIMD3<Float>(1.2, 0.76, 0.38)])   // POPUP_VOICE
    public static let text = PearlOrbPalette(colors: [SIMD3<Float>(0.34, 0.55, 0.84), SIMD3<Float>(1.0, 0.95, 0.9), SIMD3<Float>(0.6, 0.78, 0.98), SIMD3<Float>(0.62, 0.76, 1.0), SIMD3<Float>(0.86, 0.78, 1.0), SIMD3<Float>(0.66, 0.78, 0.9), SIMD3<Float>(0.5, 0.7, 0.92), SIMD3<Float>(0.6, 0.76, 0.96), SIMD3<Float>(0.88, 0.8, 1.0), SIMD3<Float>(0.78, 0.9, 1.0), SIMD3<Float>(0.4, 0.58, 0.82), SIMD3<Float>(0.1, 0.18, 0.34), SIMD3<Float>(0.84, 0.92, 1.02), SIMD3<Float>(0.68, 0.84, 1.0), SIMD3<Float>(1.1, 0.84, 0.66)])       // POPUP_MIST
}

public final class PearlOrbView: MTKView, MTKViewDelegate {

    /// Colour set. Can be changed at any time.
    public var palette: PearlOrbPalette { didSet { redrawIfStill() } }
    /// true = "thinking" (matching pages), false = idle. Eases over ~0.4 s like the web version.
    public var isThinking = true { didSet { redrawIfStill() } }
    /// Web renders at min(devicePixelRatio, 1.5), canvas capped at 680 px, then scaled up by the browser.
    /// Keep 1.5 for a 1:1 match; raise it (e.g. 3) for a sharper orb.
    public var maxRenderScale: CGFloat = 1.5 { didSet { setNeedsLayout() } }
    /// Pixel-compare hook: when set, draws time = value, activity = 1, extent = 2.9
    /// (same uniforms as the PNGs in reference/frames). nil = normal animation.
    public var debugFixedTime: Float? { didSet { redrawIfStill() } }

    private var pipeline: MTLRenderPipelineState?
    private var queue: MTLCommandQueue?
    // --- state, identical to the JS PearlOrb ---
    private var activity: Float = 1
    private var time: Float = 1.6
    private var rhythmTime: Float = 0
    private var last: CFTimeInterval = 0
    private let colorBoost: Float = 1
    private var reduce: Bool { UIAccessibility.isReduceMotionEnabled }

    public init(palette: PearlOrbPalette = .standard, frame: CGRect = .zero) {
        self.palette = palette
        super.init(frame: frame, device: MTLCreateSystemDefaultDevice())
        commonInit()
    }

    required init(coder: NSCoder) {
        self.palette = .standard
        super.init(coder: coder)
        if device == nil { device = MTLCreateSystemDefaultDevice() }
        commonInit()
    }

    private func commonInit() {
        activity = isThinking ? 1 : 0
        isOpaque = false
        backgroundColor = .clear
        layer.isOpaque = false
        colorPixelFormat = .bgra8Unorm
        clearColor = MTLClearColor(red: 0, green: 0, blue: 0, alpha: 0)
        framebufferOnly = true
        autoResizeDrawable = false
        preferredFramesPerSecond = 60
        (layer as? CAMetalLayer)?.magnificationFilter = .linear
        delegate = self
        guard let device = device else { return }
        queue = device.makeCommandQueue()
        let options = MTLCompileOptions()
        options.fastMathEnabled = false            // closest to GLSL highp
        do {
            let lib = try device.makeLibrary(source: PearlOrbView.shaderSource, options: options)
            let desc = MTLRenderPipelineDescriptor()
            desc.vertexFunction = lib.makeFunction(name: "pearlOrbVertex")
            desc.fragmentFunction = lib.makeFunction(name: "pearlOrbFragment")
            desc.colorAttachments[0].pixelFormat = colorPixelFormat
            desc.colorAttachments[0].isBlendingEnabled = false   // shader writes premultiplied colour into a cleared drawable
            pipeline = try device.makeRenderPipelineState(descriptor: desc)
        } catch {
            assertionFailure("PearlOrb shader: \(error)")
        }
        NotificationCenter.default.addObserver(self, selector: #selector(motionSettingChanged),
                                               name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)
        applyMotionSetting()
    }

    deinit { NotificationCenter.default.removeObserver(self) }

    // Same rule as PearlOrb.tick(): dpr = min(screenScale, maxRenderScale); k = min(1, 680 / max(w*dpr, h*dpr)).
    public override func layoutSubviews() {
        super.layoutSubviews()
        let scale = window?.screen.scale ?? UIScreen.main.scale
        let dpr = min(scale, maxRenderScale)
        let w = bounds.width, h = bounds.height
        let k = min(1, 680 / max(1, max(w * dpr, h * dpr)))
        drawableSize = CGSize(width: max(1, (w * dpr * k).rounded()), height: max(1, (h * dpr * k).rounded()))
        redrawIfStill()
    }

    // Web pauses while the page is hidden and restarts with dt = 0.
    public override func didMoveToWindow() {
        super.didMoveToWindow()
        last = 0
        applyMotionSetting()
    }

    @objc private func motionSettingChanged() { applyMotionSetting() }

    private func applyMotionSetting() {
        if window == nil { isPaused = true; return }
        if reduce { isPaused = true; enableSetNeedsDisplay = true; setNeedsDisplay() }   // one still frame
        else { enableSetNeedsDisplay = false; isPaused = false }
    }

    private func redrawIfStill() { if isPaused && window != nil { setNeedsDisplay() } }

    public func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}

    public func draw(in view: MTKView) {
        let now = CACurrentMediaTime()
        let dt: Float = last != 0 ? Float(min(now - last, 0.1)) : 0
        last = now
        let reduce = self.reduce
        activity += ((isThinking ? 1 : 0) - activity) * (1 - exp(-dt * 2.6))
        if !reduce { rhythmTime += dt }
        let rt = rhythmTime
        let ph = rt * 2.05 + 0.65 * sin(rt * 0.73) + 0.28 * sin(rt * 1.31)
        let breath = (0.029 + 0.010 * sin(rt * 0.47)) * sin(ph - 0.65) + 0.012 * sin(rt * 3.19 + 0.8) + 0.006 * sin(rt * 0.91)
        let ex = max(0, min(1, (breath + 0.057) / 0.114))
        let thinkSpeed: Float = reduce ? 0.92 : 0.45 + 1.90 * ex * ex * (3 - 2 * ex)
        let flowSpeed = 0.24 + activity * (thinkSpeed - 0.24)
        let scale: Float = reduce ? 1 : 1 + activity * breath * 2.1
        let extent = 2.9 / scale
        if !reduce { time += dt * flowSpeed }

        guard let pipeline = pipeline, let queue = queue,
              let pass = currentRenderPassDescriptor, let drawable = currentDrawable,
              let cmd = queue.makeCommandBuffer(), let enc = cmd.makeRenderCommandEncoder(descriptor: pass) else { return }
        let w = Float(drawableSize.width), h = Float(drawableSize.height)
        // Matches struct PearlOrbParams: 6 floats + float2 pad, then 15 × float4 (xyz used).
        let uTime = debugFixedTime ?? time
        let uActivity: Float = debugFixedTime != nil ? 1 : activity
        let uExtent: Float = debugFixedTime != nil ? 2.9 : extent
        var params: [Float] = [uTime, w / h, uActivity, uExtent / h, uExtent, colorBoost, 0, 0]
        for c in palette.colors { params += [c.x, c.y, c.z, 0] }
        enc.setRenderPipelineState(pipeline)
        enc.setFragmentBytes(params, length: params.count * MemoryLayout<Float>.stride, index: 0)
        enc.drawPrimitives(type: .triangle, vertexStart: 0, vertexCount: 6)
        enc.endEncoding()
        cmd.present(drawable)
        cmd.commit()
    }

    static let shaderSource = #"""
#pragma clang diagnostic ignored "-Wmissing-prototypes"

#include <metal_stdlib>
#include <simd/simd.h>

using namespace metal;

struct PearlOrbParams
{
    float time_;
    float aspect_;
    float activity_;
    float pixel_;
    float extent_;
    float colorBoost_;
    float2 pad_;
    float4 cDeep_;
    float4 cLight_;
    float4 cFold_;
    float4 cFilm_;
    float4 cFilm2_;
    float4 cBack_;
    float4 cBoost_;
    float4 cRim_;
    float4 cRim2_;
    float4 cInner_;
    float4 cEdge_;
    float4 cEnvLo_;
    float4 cEnvHi_;
    float4 cThread_;
    float4 cWarm_;
};

struct pearlOrbFragment_out
{
    float4 fragColor [[color(0)]];
};

struct pearlOrbFragment_in
{
    float2 uv [[user(locn0)]];
};

static inline __attribute__((always_inline))
float2x2 rotate(thread const float& a)
{
    float c = cos(a);
    float s = sin(a);
    return float2x2(float2(c, -s), float2(s, c));
}

static inline __attribute__((always_inline))
float3 flow(thread float3& p, thread const float& t)
{
    float param = (-0.119999997317790985107421875) + (0.0599999986588954925537109375 * sin(t * 0.100000001490116119384765625));
    float3 _72 = p;
    float2 _74 = rotate(param) * _72.xy;
    p.x = _74.x;
    p.y = _74.y;
    float param_1 = (0.449999988079071044921875 * p.y) + (0.25 * sin(t * 0.2700000107288360595703125));
    float3 _95 = p;
    float2 _97 = rotate(param_1) * _95.xz;
    p.x = _97.x;
    p.z = _97.y;
    p.y += (0.119999997317790985107421875 * sin((p.z * 2.7999999523162841796875) + (t * 0.3400000035762786865234375)));
    return p;
}

static inline __attribute__((always_inline))
float phase(thread const float3& p, thread const float& t)
{
    float3 param = p;
    float param_1 = t;
    float3 _126 = flow(param, param_1);
    float3 q = _126;
    float curl = 0.569999992847442626953125 * sin((q.y * 3.5) + (0.2800000011920928955078125 * sin(t * 0.2899999916553497314453125)));
    return (((q.x - curl) + (q.z * 0.89999997615814208984375)) * 4.80000019073486328125) + (0.2199999988079071044921875 * sin((q.z * 3.400000095367431640625) - (t * 0.25)));
}

static inline __attribute__((always_inline))
float field(thread const float3& p, thread const float& t)
{
    float3 param = p;
    float param_1 = t;
    return sin(phase(param, param_1));
}

static inline __attribute__((always_inline))
float sq(thread const float& x)
{
    return x * x;
}

static inline __attribute__((always_inline))
float3 studio(thread const float3& r, constant PearlOrbParams& P)
{
    float3 env = mix(P.cEnvLo_.xyz, P.cEnvHi_.xyz, float3(smoothstep(-0.800000011920928955078125, 0.800000011920928955078125, r.y)));
    float param = (r.x + 0.36000001430511474609375) / 0.070000000298023223876953125;
    float strip = exp(-sq(param));
    float param_1 = (r.x - 0.2199999988079071044921875) / 0.02199999988079071044921875;
    float fine = exp(-sq(param_1));
    float param_2 = ((r.y + 0.25) + (r.x * 0.550000011920928955078125)) / 0.0599999986588954925537109375;
    float warm = exp(-sq(param_2));
    float param_3 = sin((r.y * 10.0) + (r.x * 1.60000002384185791015625)) * 17.0;
    float thread0 = exp(-sq(param_3));
    float white = pow(fast::max(0.0, dot(r, float3(0.24957607686519622802734375, 0.648897826671600341796875, 0.718779087066650390625))), 32.0);
    env += (float3(1.0, 0.980000019073486328125, 1.0) * (((strip * 3.099999904632568359375) + (fine * 2.400000095367431640625)) + (white * 1.5)));
    env += ((P.cWarm_.xyz * warm) * 2.599999904632568359375);
    env += ((mix(P.cThread_.xyz, float3(1.0, 0.88999998569488525390625, 0.699999988079071044921875), float3(smoothstep(-1.0, 1.0, r.y))) * thread0) * 0.519999980926513671875);
    return env;
}

fragment pearlOrbFragment_out pearlOrbFragment(pearlOrbFragment_in in [[stage_in]], constant PearlOrbParams& P [[buffer(0)]])
{
    pearlOrbFragment_out out = {};
    float2 p = ((in.uv - float2(0.5)) * float2(P.aspect_, 1.0)) * P.extent_;
    float rr = dot(p, p);
    float r = sqrt(rr);
    float edge = 1.0 - smoothstep(1.0 - P.pixel_, 1.0 + P.pixel_, r);
    if (edge < 0.001000000047497451305389404296875)
    {
        out.fragColor = float4(0.0);
        return out;
    }
    float z = sqrt(fast::max(0.0, 1.0 - rr));
    float3 surface = fast::normalize(float3(p, z));
    float3 ray = refract(float3(0.0, 0.0, -1.0), surface, 0.862068951129913330078125);
    float3 entry = float3(p, z);
    float travel = fast::max(0.001000000047497451305389404296875, (-2.0) * dot(entry, ray));
    float stepSize = travel / 96.0;
    float3 col = float3(0.0);
    float trans = 1.0;
    float definition = 0.0;
    float t = P.time_ * 1.5499999523162841796875;
    float3 param = entry;
    float param_1 = t;
    float lastField = field(param, param_1);
    for (int i = 1; i <= 96; i++)
    {
        float _distance = float(i) * stepSize;
        float3 pos = entry + (ray * _distance);
        float3 param_2 = pos;
        float param_3 = t;
        float d = field(param_2, param_3);
        if (((d * lastField) < 0.0) && (trans > 0.014999999664723873138427734375))
        {
            float along = lastField / (lastField - d);
            float3 hit = entry + (ray * ((_distance - stepSize) + (stepSize * along)));
            float e = 0.0030000000260770320892333984375;
            float3 param_4 = hit + float3(e, 0.0, 0.0);
            float param_5 = t;
            float3 param_6 = hit - float3(e, 0.0, 0.0);
            float param_7 = t;
            float3 param_8 = hit + float3(0.0, e, 0.0);
            float param_9 = t;
            float3 param_10 = hit - float3(0.0, e, 0.0);
            float param_11 = t;
            float3 param_12 = hit + float3(0.0, 0.0, e);
            float param_13 = t;
            float3 param_14 = hit - float3(0.0, 0.0, e);
            float param_15 = t;
            float3 n = fast::normalize(float3(field(param_4, param_5) - field(param_6, param_7), field(param_8, param_9) - field(param_10, param_11), field(param_12, param_13) - field(param_14, param_15)));
            if (dot(n, ray) > 0.0)
            {
                n = -n;
            }
            float facing = fast::max(0.0, dot(n, -ray));
            float grazing = pow(1.0 - facing, 2.0);
            float3 reflected = reflect(ray, n);
            float pearl = 0.5 + (0.5 * sin((((hit.y * 3.2000000476837158203125) + (hit.z * 3.5)) + (hit.x * 2.7000000476837158203125)) + (t * 0.100000001490116119384765625)));
            float3 tint = mix(P.cDeep_.xyz, P.cLight_.xyz, float3(pearl * 0.75));
            float diffuse = 0.60000002384185791015625 + (0.4000000059604644775390625 * abs(dot(n, float3(-0.312736928462982177734375, 0.62547385692596435546875, 0.7148272991180419921875))));
            float3 param_16 = reflected;
            float3 material = ((tint * diffuse) * 0.660000026226043701171875) + (studio(param_16, P) * (0.439999997615814208984375 + (0.4000000059604644775390625 * grazing)));
            float foldShade = (1.0 - smoothstep(0.300000011920928955078125, 0.819999992847442626953125, pearl)) * smoothstep(0.119999997317790985107421875, 0.75, abs(n.y));
            material = mix(material, material * P.cFold_.xyz, float3(foldShade * 0.4600000083446502685546875));
            material += ((mix(P.cFilm_.xyz, P.cFilm2_.xyz, float3(pearl)) * pow(grazing, 1.5)) * 1.25);
            float opacity = ((0.62000000476837158203125 + (0.2800000011920928955078125 * grazing)) * smoothstep(0.0, 0.1500000059604644775390625, 1.0 - length(hit))) * smoothstep(0.00999999977648258209228515625, 0.180000007152557373046875, facing);
            definition += ((trans * opacity) * foldShade);
            col += (material * (trans * opacity));
            trans *= (1.0 - opacity);
        }
        lastField = d;
    }
    float3 back = mix(P.cBack_.xyz, float3(0.9700000286102294921875, 0.930000007152557373046875, 1.0299999713897705078125), float3(smoothstep(-1.0, 1.0, p.y)));
    back = mix(back, mix(P.cBoost_.xyz, float3(1.0, 0.88999998569488525390625, 1.03999996185302734375), float3(smoothstep(-1.0, 1.0, p.y))), float3(P.colorBoost_ * 0.64999997615814208984375));
    col += (back * trans);
    float fresnel = pow(1.0 - z, 3.0);
    float3 rim = mix(P.cRim_.xyz, P.cRim2_.xyz, float3(0.5 + (0.5 * sin((precise::atan2(p.y, p.x) * 2.400000095367431640625) + 0.699999988079071044921875))));
    col = mix(col, rim, float3(fresnel * 0.23999999463558197021484375));
    float3 sr = reflect(float3(0.0, 0.0, -1.0), surface);
    float3 param_17 = sr;
    col += (studio(param_17, P) * (0.0350000001490116119384765625 + (fresnel * 0.100000001490116119384765625)));
    float box = (((smoothstep(0.430000007152557373046875, 0.449999988079071044921875, sr.x) * (1.0 - smoothstep(0.699999988079071044921875, 0.7200000286102294921875, sr.x))) * smoothstep(0.300000011920928955078125, 0.319999992847442626953125, sr.y)) * (1.0 - smoothstep(0.689999997615814208984375, 0.709999978542327880859375, sr.y))) * smoothstep(-0.100000001490116119384765625, 0.300000011920928955078125, sr.z);
    col += ((float3(1.0, 0.9900000095367431640625, 1.0) * box) * 0.14000000059604644775390625);
    float spec = pow(fast::max(dot(surface, float3(-0.28246009349822998046875, 0.3896001279354095458984375, 0.8766002655029296875)), 0.0), 150.0);
    col += ((float3(1.0, 0.9700000286102294921875, 0.910000026226043701171875) * spec) * 0.800000011920928955078125);
    float param_18 = (r - 0.982999980449676513671875) * 160.0;
    float rimline = exp(-sq(param_18));
    float param_19 = (r - 0.961000025272369384765625) * 125.0;
    float innerRim = exp(-sq(param_19));
    float angle = precise::atan2(p.y, p.x);
    float rimArc = pow(0.5 + (0.5 * cos((angle * 2.0) - 1.14999997615814208984375)), 4.0);
    col += (((rim * rimline) * (0.25 + (rimArc * 1.14999997615814208984375))) + ((P.cInner_.xyz * innerRim) * (0.07999999821186065673828125 + (rimArc * 0.20000000298023223876953125))));
    col = float3(1.0) - exp((-col) * 1.7799999713897705078125);
    col = pow(col, float3(0.7599999904632568359375));
    float luma = dot(col, float3(0.2125999927520751953125, 0.715200006961822509765625, 0.072200000286102294921875));
    float saturation = 1.2000000476837158203125 + ((P.colorBoost_ * 0.5) * (1.0 - smoothstep(0.819999992847442626953125, 0.980000019073486328125, luma)));
    col = fast::clamp(mix(float3(luma), col, float3(saturation)), float3(0.0), float3(1.0));
    col = mix(col, P.cEdge_.xyz, float3((innerRim * rimArc) * 0.23000000417232513427734375));
    float highlight = smoothstep(0.7599999904632568359375, 0.959999978542327880859375, luma);
    float glassAlpha = fast::min(0.980000019073486328125, mix(0.560000002384185791015625, 0.959999978542327880859375, highlight) + (definition * 0.319999992847442626953125));
    glassAlpha = fast::max(glassAlpha, rimArc * ((rimline * 0.939999997615814208984375) + (innerRim * 0.119999997317790985107421875)));
    float outA = edge * glassAlpha;
    out.fragColor = float4(col * outA, outA);
    return out;
}

// Full-screen quad from vertex_id (same two triangles as the web version).
struct PearlOrbVSOut { float4 position [[position]]; float2 uv [[user(locn0)]]; };
vertex PearlOrbVSOut pearlOrbVertex(uint vid [[vertex_id]])
{
    const float2 quad[6] = { float2(-1,-1), float2(1,-1), float2(-1,1), float2(-1,1), float2(1,-1), float2(1,1) };
    PearlOrbVSOut out;
    out.position = float4(quad[vid], 0.0, 1.0);
    out.uv = quad[vid] * 0.5 + 0.5;
    return out;
}

"""#
}
