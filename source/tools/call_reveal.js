// Voice call reveal states, as in Figma (863:243 → 935:2745 → 935:2922 / 935:3113 → 935:2560):
// - countdown from 0:45; under 30s the timer turns red
// - at 0:38 he reveals first: "Revealed ✓" in pink under Him, and the Reveal button starts its sweep
// - tapping Reveal: if he hasn't yet → "Revealed ✓" under Me, button turns dark "waiting for him to reveal...", he reveals 1.6s later
// - both revealed: compatibility shows between the avatars, status + button give way to "we've been chatting for" (counting up)
// - reaching 0:00 without both revealed ends the call
(function(){
var Q=function(s){return document.querySelector(s)},A=function(s){return [].slice.call(document.querySelectorAll(s))};
var root=Q('.vc-root'),timer=Q('.vc-timer'),btn=Q('.vc-reveal'),lab=Q('.vc-rl'),eye=Q('.vc-eye'),up=Q('.vc-up');
var CHECK='<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><circle cx="6" cy="6" r="5" fill="#FF95F1"/><path d="M3.6 6.1l1.6 1.6 3.2-3.4" fill="none" stroke="#170941" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
var left=45,talk=0,him=false,me=false,both=false,ended=false;
function fmt(t){return ('0'+Math.floor(t/60)).slice(-2)+':'+('0'+t%60).slice(-2)}
function show(){
 if(timer){timer.textContent=fmt(left);timer.classList.toggle('warn',left<=30);}
 if(up)up.textContent=fmt(talk);
}
function reveal(who){
 A('.vc-ava[data-who="'+who+'"],.vc-mini[data-who="'+who+'"]').forEach(function(e){e.classList.add('on')});
 var st=Q('.vc-st[data-who="'+who+'"]');if(st){st.innerHTML='Revealed'+CHECK;st.classList.add('on')}
 if(who==='him')him=true;else me=true;
 if(him&&me&&!both){both=true;if(root)root.classList.add('both-on');}
 else if(him&&!me&&btn)btn.classList.add('sweep');
}
show();
setInterval(function(){
 if(both){talk++;show();return;}
 if(left>0)left--;
 if(left===38&&!him)reveal('him');
 show();
 if(left===0&&!ended){ended=true;parent.postMessage({go:'ended'},'*');}
},1000);
if(btn)btn.addEventListener('click',function(){
 if(me)return;
 reveal('me');
 if(both)return;
 btn.classList.remove('sweep');btn.classList.add('wait');
 if(eye)eye.style.display='none';
 lab.textContent='waiting for him to reveal...';
 setTimeout(function(){reveal('him');},1600);
});
})();
