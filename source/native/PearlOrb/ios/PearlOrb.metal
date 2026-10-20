// Generated from shared/pearl_orb.frag (GLSL) with glslangValidator + SPIRV-Cross, plus a vertex_id quad.
// PearlOrbView.swift embeds this same source and compiles it at runtime; this file is for reading/diffing.
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
