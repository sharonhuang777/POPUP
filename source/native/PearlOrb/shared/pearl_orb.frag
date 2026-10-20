precision highp float;
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
