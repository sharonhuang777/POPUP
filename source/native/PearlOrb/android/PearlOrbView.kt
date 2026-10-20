// PearlOrb — native Android port of the Popup "pearl orb" WebGL animation
// (voice match standard / priority, text match). Same fragment shader, same timing code, same
// render-resolution rule as the web version (V2Think1 / V2VoiceThink1 / TextThink boards).
//
// Usage:
//   val orb = PearlOrbView(context)            // or <com.popup.orb.PearlOrbView .../> in XML
//   orb.palette = PearlOrbPalette.STANDARD     // STANDARD (普通语音) / PRIORITY (加速语音) / TEXT (文字匹配)
//   orb.thinking = true                        // matching pages use the thinking state
//   // size it to 300dp x 300dp like the design (any square size works)
//
// Requirements: OpenGL ES 2.0, minSdk 21. No other dependencies.
package com.popup.orb

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.SurfaceTexture
import android.opengl.EGL14
import android.opengl.EGLConfig
import android.opengl.EGLContext
import android.opengl.EGLDisplay
import android.opengl.EGLSurface
import android.opengl.GLES20
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.util.AttributeSet
import android.view.Choreographer
import android.view.TextureView
import android.view.View
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.exp
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sin

/** 15 colours, same order and values as the web palettes (POPUP_PURPLE / POPUP_VOICE / POPUP_MIST). */
enum class PearlOrbPalette(val rgb: FloatArray) {
        STANDARD(floatArrayOf(0.48f, 0.3f, 0.79f, 1.02f, 0.91f, 0.8f, 0.7f, 0.49f, 0.92f, 0.7f, 0.54f, 1.0f, 1.0f, 0.83f, 0.6f, 0.69f, 0.61f, 0.83f, 0.6f, 0.43f, 0.88f, 0.68f, 0.53f, 0.92f, 1.0f, 0.87f, 0.67f, 0.87f, 0.73f, 1.0f, 0.56f, 0.39f, 0.77f, 0.19f, 0.105f, 0.34f, 0.88f, 0.79f, 1.02f, 0.75f, 0.63f, 1.0f, 1.2f, 0.76f, 0.38f)),
        PRIORITY(floatArrayOf(0.8f, 0.38f, 0.4f, 1.02f, 0.91f, 0.8f, 0.96f, 0.62f, 0.6f, 1.0f, 0.6f, 0.56f, 1.0f, 0.83f, 0.6f, 0.9f, 0.7f, 0.68f, 0.94f, 0.54f, 0.52f, 0.96f, 0.6f, 0.56f, 1.0f, 0.87f, 0.67f, 1.0f, 0.8f, 0.76f, 0.78f, 0.4f, 0.42f, 0.32f, 0.1f, 0.12f, 1.02f, 0.87f, 0.83f, 1.0f, 0.72f, 0.68f, 1.2f, 0.76f, 0.38f)),
        TEXT(floatArrayOf(0.34f, 0.55f, 0.84f, 1.0f, 0.95f, 0.9f, 0.6f, 0.78f, 0.98f, 0.62f, 0.76f, 1.0f, 0.86f, 0.78f, 1.0f, 0.66f, 0.78f, 0.9f, 0.5f, 0.7f, 0.92f, 0.6f, 0.76f, 0.96f, 0.88f, 0.8f, 1.0f, 0.78f, 0.9f, 1.0f, 0.4f, 0.58f, 0.82f, 0.1f, 0.18f, 0.34f, 0.84f, 0.92f, 1.02f, 0.68f, 0.84f, 1.0f, 1.1f, 0.84f, 0.66f));

    companion object {
        val KEYS = arrayOf("deep", "light", "fold", "film", "film2", "back", "boost", "rim", "rim2", "inner", "edge", "envLo", "envHi", "thread", "warm")
    }
}

class PearlOrbView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : TextureView(context, attrs), TextureView.SurfaceTextureListener {

    /** Colour set. Can be changed at any time. */
    var palette: PearlOrbPalette = PearlOrbPalette.STANDARD
        set(value) { field = value; renderer?.post { it.palette = value } }

    /** true = "thinking" (matching pages), false = idle. Eases over ~0.4 s like the web version. */
    var thinking: Boolean = true
        set(value) { field = value; renderer?.post { it.thinking = value } }

    /** Web renders at min(devicePixelRatio, 1.5) and caps the canvas at 680 px, then the browser
     *  scales it up. Keep 1.5 for a 1:1 match; raise it (e.g. 3f) for a sharper orb. */
    var maxRenderScale: Float = 1.5f

    /** Pixel-compare hook: when set, draws a still frame with time = value, activity = 1, extent = 2.9
     *  (same uniforms as the PNGs in reference/frames). null = normal animation. */
    var debugFixedTime: Float? = null
        set(value) { field = value; renderer?.post { it.fixedTime = value } }

    private var renderer: Renderer? = null

    init {
        isOpaque = false
        surfaceTextureListener = this
    }

    override fun onSurfaceTextureAvailable(st: SurfaceTexture, width: Int, height: Int) {
        val (bw, bh) = bufferSize(width, height)
        st.setDefaultBufferSize(bw, bh)
        renderer = Renderer(st, bw, bh, palette, thinking, reduceMotion()).also { it.fixedTime = debugFixedTime; it.start() }
        updateRunning()
    }

    override fun onSurfaceTextureSizeChanged(st: SurfaceTexture, width: Int, height: Int) {
        val (bw, bh) = bufferSize(width, height)
        st.setDefaultBufferSize(bw, bh)
        renderer?.post { it.resize(bw, bh) }
    }

    override fun onSurfaceTextureDestroyed(st: SurfaceTexture): Boolean {
        val r = renderer ?: return true
        r.quit(); renderer = null
        return false   // the render thread releases the SurfaceTexture after tearing down EGL
    }

    override fun onSurfaceTextureUpdated(st: SurfaceTexture) {}

    override fun onWindowVisibilityChanged(visibility: Int) { super.onWindowVisibilityChanged(visibility); updateRunning() }
    override fun onVisibilityChanged(changedView: View, visibility: Int) { super.onVisibilityChanged(changedView, visibility); updateRunning() }

    private fun updateRunning() {
        val visible = windowVisibility == View.VISIBLE && isShown
        renderer?.post { it.setRunning(visible) }
    }

    /** Same rule as PearlOrb.tick(): dpr = min(deviceScale, maxRenderScale); k = min(1, 680 / max(w*dpr, h*dpr)). */
    private fun bufferSize(viewW: Int, viewH: Int): Pair<Int, Int> {
        val density = resources.displayMetrics.density
        val cssW = viewW / density; val cssH = viewH / density
        val dpr = min(density, maxRenderScale)
        val k = min(1f, 680f / max(1f, max(cssW * dpr, cssH * dpr)))
        return Pair(max(1, (cssW * dpr * k).roundToInt()), max(1, (cssH * dpr * k).roundToInt()))
    }

    /** prefers-reduced-motion equivalent: "Remove animations" / animator duration scale 0. */
    private fun reduceMotion(): Boolean =
        if (Build.VERSION.SDK_INT >= 26) !ValueAnimator.areAnimatorsEnabled() else false

    // ------------------------------------------------------------------------------------------
    private class Renderer(
        private val texture: SurfaceTexture,
        private var w: Int, private var h: Int,
        var palette: PearlOrbPalette, var thinking: Boolean,
        private val reduce: Boolean
    ) : Choreographer.FrameCallback {
        private val thread = HandlerThread("PearlOrb").apply { start() }
        private val handler = Handler(thread.looper)
        private var display: EGLDisplay = EGL14.EGL_NO_DISPLAY
        private var context: EGLContext = EGL14.EGL_NO_CONTEXT
        private var surface: EGLSurface = EGL14.EGL_NO_SURFACE
        private var program = 0
        private val uni = HashMap<String, Int>()
        private var running = false
        private var scheduled = false

        // --- state, identical to the JS PearlOrb ---
        private var activity = if (thinking) 1f else 0f
        private var time = 1.6f
        private var rhythmTime = 0f
        private var lastNanos = 0L
        private val colorBoost = 1f
        var fixedTime: Float? = null
        private var quadBuffer: java.nio.FloatBuffer? = null   // kept alive: GL reads it on every draw

        fun start() = handler.post { initGl() }
        fun post(block: (Renderer) -> Unit) { handler.post { block(this); if (running && !scheduled) schedule() } }
        fun quit() { handler.post { stopFrames(); releaseGl(); texture.release(); thread.quitSafely() } }
        fun resize(nw: Int, nh: Int) { w = nw; h = nh }

        fun setRunning(on: Boolean) {
            if (on == running) return
            running = on
            if (on) { lastNanos = 0L; schedule() } else stopFrames()
        }

        private fun schedule() { if (!scheduled) { scheduled = true; Choreographer.getInstance().postFrameCallback(this) } }
        private fun stopFrames() { if (scheduled) { Choreographer.getInstance().removeFrameCallback(this); scheduled = false } }

        override fun doFrame(frameTimeNanos: Long) {
            scheduled = false
            if (!running || program == 0) return
            tick(frameTimeNanos)
            if (!reduce) schedule()          // web: reduced motion draws a single still frame
        }

        private fun tick(now: Long) {
            val dt = if (lastNanos != 0L) min((now - lastNanos) / 1e9f, 0.1f) else 0f
            lastNanos = now
            val target = if (thinking) 1f else 0f
            activity += (target - activity) * (1f - exp(-dt * 2.6f))
            if (!reduce) rhythmTime += dt
            val rt = rhythmTime
            val ph = rt * 2.05f + 0.65f * sin(rt * 0.73f) + 0.28f * sin(rt * 1.31f)
            val breath = (0.029f + 0.010f * sin(rt * 0.47f)) * sin(ph - 0.65f) + 0.012f * sin(rt * 3.19f + 0.8f) + 0.006f * sin(rt * 0.91f)
            val ex = ((breath + 0.057f) / 0.114f).coerceIn(0f, 1f)
            val thinkSpeed = if (reduce) 0.92f else 0.45f + 1.90f * ex * ex * (3f - 2f * ex)
            val flowSpeed = 0.24f + activity * (thinkSpeed - 0.24f)
            val scale = if (reduce) 1f else 1f + activity * breath * 2.1f
            val extent = 2.9f / scale
            if (!reduce) time += dt * flowSpeed
            val ft = fixedTime
            val uTime = ft ?: time
            val uActivity = if (ft != null) 1f else activity
            val uExtent = if (ft != null) 2.9f else extent

            GLES20.glViewport(0, 0, w, h)
            GLES20.glClearColor(0f, 0f, 0f, 0f)
            GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT)
            GLES20.glUseProgram(program)
            GLES20.glUniform1f(uni.getValue("time"), uTime)
            GLES20.glUniform1f(uni.getValue("aspect"), w.toFloat() / h)
            GLES20.glUniform1f(uni.getValue("activity"), uActivity)
            GLES20.glUniform1f(uni.getValue("pixel"), uExtent / h)
            GLES20.glUniform1f(uni.getValue("extent"), uExtent)
            GLES20.glUniform1f(uni.getValue("colorBoost"), colorBoost)
            val c = palette.rgb
            PearlOrbPalette.KEYS.forEachIndexed { i, k ->
                GLES20.glUniform3f(uni.getValue("c" + k.replaceFirstChar { it.uppercase() }), c[i * 3], c[i * 3 + 1], c[i * 3 + 2])
            }
            GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, 6)
            EGL14.eglSwapBuffers(display, surface)
        }

        private fun initGl() {
            display = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY)
            val ver = IntArray(2); EGL14.eglInitialize(display, ver, 0, ver, 1)
            val attribs = intArrayOf(
                EGL14.EGL_RED_SIZE, 8, EGL14.EGL_GREEN_SIZE, 8, EGL14.EGL_BLUE_SIZE, 8, EGL14.EGL_ALPHA_SIZE, 8,
                EGL14.EGL_RENDERABLE_TYPE, EGL14.EGL_OPENGL_ES2_BIT, EGL14.EGL_NONE)
            val configs = arrayOfNulls<EGLConfig>(1); val n = IntArray(1)
            EGL14.eglChooseConfig(display, attribs, 0, configs, 0, 1, n, 0)
            context = EGL14.eglCreateContext(display, configs[0], EGL14.EGL_NO_CONTEXT,
                intArrayOf(EGL14.EGL_CONTEXT_CLIENT_VERSION, 2, EGL14.EGL_NONE), 0)
            surface = EGL14.eglCreateWindowSurface(display, configs[0], texture, intArrayOf(EGL14.EGL_NONE), 0)
            EGL14.eglMakeCurrent(display, surface, surface, context)

            program = link(compile(GLES20.GL_VERTEX_SHADER, VERT), compile(GLES20.GL_FRAGMENT_SHADER, FRAG))
            GLES20.glUseProgram(program)
            val quad = floatArrayOf(-1f, -1f, 1f, -1f, -1f, 1f, -1f, 1f, 1f, -1f, 1f, 1f)
            val buf = ByteBuffer.allocateDirect(quad.size * 4).order(ByteOrder.nativeOrder()).asFloatBuffer().apply { put(quad); position(0) }
            quadBuffer = buf
            val loc = GLES20.glGetAttribLocation(program, "position")
            GLES20.glEnableVertexAttribArray(loc)
            GLES20.glVertexAttribPointer(loc, 2, GLES20.GL_FLOAT, false, 0, buf)
            (listOf("time", "aspect", "activity", "pixel", "extent", "colorBoost") +
                PearlOrbPalette.KEYS.map { "c" + it.replaceFirstChar { ch -> ch.uppercase() } })
                .forEach { uni[it] = GLES20.glGetUniformLocation(program, it) }
            GLES20.glDisable(GLES20.GL_BLEND)   // the shader writes premultiplied colour straight into a cleared buffer
            if (running) schedule()
        }

        private fun compile(type: Int, src: String): Int {
            val s = GLES20.glCreateShader(type)
            GLES20.glShaderSource(s, src); GLES20.glCompileShader(s)
            val ok = IntArray(1); GLES20.glGetShaderiv(s, GLES20.GL_COMPILE_STATUS, ok, 0)
            check(ok[0] != 0) { "PearlOrb shader: " + GLES20.glGetShaderInfoLog(s) }
            return s
        }

        private fun link(vs: Int, fs: Int): Int {
            val p = GLES20.glCreateProgram()
            GLES20.glAttachShader(p, vs); GLES20.glAttachShader(p, fs); GLES20.glLinkProgram(p)
            val ok = IntArray(1); GLES20.glGetProgramiv(p, GLES20.GL_LINK_STATUS, ok, 0)
            check(ok[0] != 0) { "PearlOrb link: " + GLES20.glGetProgramInfoLog(p) }
            return p
        }

        private fun releaseGl() {
            if (program != 0) { GLES20.glDeleteProgram(program); program = 0 }
            if (display != EGL14.EGL_NO_DISPLAY) {
                EGL14.eglMakeCurrent(display, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_CONTEXT)
                EGL14.eglDestroySurface(display, surface)
                EGL14.eglDestroyContext(display, context)
                EGL14.eglTerminate(display)
            }
            display = EGL14.EGL_NO_DISPLAY
        }
    }

    companion object {
        private const val VERT = """attribute vec2 position;
varying vec2 uv;
void main(){
  uv=position*.5+.5;
  gl_Position=vec4(position,0.,1.);
}
"""

        /** shared/pearl_orb.frag — the web shader verbatim, except (1) pow(x, 2.) on bases that can be
         *  negative is written as x*x (pow is undefined for x < 0 in GLSL/Metal; Chrome output is
         *  pixel-identical) and (2) the colour is written premultiplied for the Android compositor. */
        private const val FRAG = """precision highp float;
varying vec2 uv;
uniform float time,aspect,activity,pixel,extent,colorBoost;
uniform vec3 cDeep,cLight,cFold,cFilm,cFilm2,cBack,cBoost,cRim,cRim2,cInner,cEdge,cEnvLo,cEnvHi,cThread,cWarm;
float sq(float x){
  return x*x;
}
mat2 rotate(float a){
  float c=cos(a),s=sin(a);
  return mat2(c,-s,s,c);
}
vec3 flow(vec3 p,float t){
  p.xy=rotate(-.12+.06*sin(t*.10))*p.xy;
  p.xz=rotate(.45*p.y+.25*sin(t*.27))*p.xz;
  p.y+=.12*sin(p.z*2.8+t*.34);
  return p;
}
float phase(vec3 p,float t){
  vec3 q=flow(p,t);
  float curl=.57*sin(q.y*3.5+.28*sin(t*.29));
  return (q.x-curl+q.z*.90)*4.8+.22*sin(q.z*3.4-t*.25);
}
float field(vec3 p,float t){
  return sin(phase(p,t));
}
vec3 studio(vec3 r){
  vec3 env=mix(cEnvLo,cEnvHi,smoothstep(-.8,.8,r.y));
  float strip=exp(-sq((r.x+.36)/.070));
  float fine=exp(-sq((r.x-.22)/.022));
  float warm=exp(-sq((r.y+.25+r.x*.55)/.060));
  float thread=exp(-sq(sin(r.y*10.+r.x*1.6)*17.));
  float white=pow(max(0.,dot(r,normalize(vec3(.25,.65,.72)))),32.);
  env+=vec3(1.,.98,1.)*(strip*3.1+fine*2.4+white*1.5);
  env+=cWarm*warm*2.6;
  env+=mix(cThread,vec3(1.,.89,.70),smoothstep(-1.,1.,r.y))*thread*.52;
  return env;
}
void main(){
  vec2 p=(uv-.5)*vec2(aspect,1.)*extent;
  float rr=dot(p,p),r=sqrt(rr);
  float edge=1.-smoothstep(1.-pixel,1.+pixel,r);
  if(edge<.001){
    gl_FragColor=vec4(0.);
    return;
  }
  float z=sqrt(max(0.,1.-rr));
  vec3 surface=normalize(vec3(p,z));
  vec3 ray=refract(vec3(0.,0.,-1.),surface,1./1.16);
  vec3 entry=vec3(p,z);
  float travel=max(.001,-2.*dot(entry,ray));
  float stepSize=travel/96.;
  vec3 col=vec3(0.);
  float trans=1.;
  float definition=0.;
  float t=time*1.55;
  float lastField=field(entry,t);
  for(int i=1;i<=96;i++){
    float distance=float(i)*stepSize;
    vec3 pos=entry+ray*distance;
    float d=field(pos,t);
    if(d*lastField<0. && trans>.015){
      float along=lastField/(lastField-d);
      vec3 hit=entry+ray*(distance-stepSize+stepSize*along);
      float e=.003;
      vec3 n=normalize(vec3(field(hit+vec3(e,0,0),t)-field(hit-vec3(e,0,0),t),field(hit+vec3(0,e,0),t)-field(hit-vec3(0,e,0),t),field(hit+vec3(0,0,e),t)-field(hit-vec3(0,0,e),t)));
      if(dot(n,ray)>0.)n=-n;
      float facing=max(0.,dot(n,-ray));
      float grazing=pow(1.-facing,2.);
      vec3 reflected=reflect(ray,n);
      float pearl=.5+.5*sin(hit.y*3.2+hit.z*3.5+hit.x*2.7+t*.10);
      vec3 tint=mix(cDeep,cLight,pearl*.75);
      float diffuse=.60+.40*abs(dot(n,normalize(vec3(-.35,.70,.80))));
      vec3 material=tint*diffuse*.66+studio(reflected)*(.44+.4*grazing);
      float foldShade=(1.-smoothstep(.30,.82,pearl))*smoothstep(.12,.75,abs(n.y));
      material=mix(material,material*cFold,foldShade*.46);
      material+=mix(cFilm,cFilm2,pearl)*pow(grazing,1.5)*1.25;
      float opacity=(.62+.28*grazing)*smoothstep(0.,.15,1.-length(hit))*smoothstep(.01,.18,facing);
      definition+=trans*opacity*foldShade;
      col+=trans*opacity*material;
      trans*=1.-opacity;
    }
    lastField=d;
  }
  vec3 back=mix(cBack,vec3(.97,.93,1.03),smoothstep(-1.,1.,p.y));
  back=mix(back,mix(cBoost,vec3(1.,.89,1.04),smoothstep(-1.,1.,p.y)),colorBoost*.65);
  col+=trans*back;
  float fresnel=pow(1.-z,3.);
  vec3 rim=mix(cRim,cRim2,.5+.5*sin(atan(p.y,p.x)*2.4+.7));
  col=mix(col,rim,fresnel*.24);
  vec3 sr=reflect(vec3(0.,0.,-1.),surface);
  col+=studio(sr)*(.035+fresnel*.10);
  float box=smoothstep(.43,.45,sr.x)*(1.-smoothstep(.70,.72,sr.x))*smoothstep(.30,.32,sr.y)*(1.-smoothstep(.69,.71,sr.y))*smoothstep(-.10,.30,sr.z);
  col+=vec3(1.,.99,1.)*box*.14;
  float spec=pow(max(dot(surface,normalize(vec3(-.58,.8,1.8))),0.),150.);
  col+=vec3(1.,.97,.91)*spec*.8;
  float rimline=exp(-sq((r-.983)*160.));
  float innerRim=exp(-sq((r-.961)*125.));
  float angle=atan(p.y,p.x);
  float rimArc=pow(.5+.5*cos(angle*2.-1.15),4.);
  col+=rim*rimline*(.25+rimArc*1.15)+cInner*innerRim*(.08+rimArc*.20);
  col=1.-exp(-col*1.78);
  col=pow(col,vec3(.76));
  float luma=dot(col,vec3(.2126,.7152,.0722));
  float saturation=1.20+colorBoost*.50*(1.-smoothstep(.82,.98,luma));
  col=clamp(mix(vec3(luma),col,saturation),0.,1.);
  col=mix(col,cEdge,innerRim*rimArc*.23);
  float highlight=smoothstep(.76,.96,luma);
  float glassAlpha=min(.98,mix(.56,.96,highlight)+definition*.32);
  glassAlpha=max(glassAlpha,rimArc*(rimline*.94+innerRim*.12));
  float outA=edge*glassAlpha;
  gl_FragColor=vec4(col*outA,outA);
}
"""
    }
}
