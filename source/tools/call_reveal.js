(function(){
var Q=function(s){return document.querySelector(s)},A=function(s){return [].slice.call(document.querySelectorAll(s))};
var timer=Q('.vc-timer'),tl=Q('.vc-tl'),btn=Q('.vc-reveal'),lab=Q('.vc-rl');
var t=136,mode='down',tick=setInterval(function(){
 if(mode==='down'){if(t>0)t--;}else t++;
 if(timer)timer.textContent=('0'+Math.floor(t/60)).slice(-2)+':'+('0'+t%60).slice(-2);
},1000);
function reveal(who){
 A('.vc-ava[data-who="'+who+'"],.vc-mini[data-who="'+who+'"]').forEach(function(e){e.classList.add('on')});
 var st=Q('.vc-st[data-who="'+who+'"]');if(st){st.textContent='Revealed';st.classList.add('on')}
}
var done=false;
if(btn)btn.addEventListener('click',function(){
 if(done)return;done=true;
 reveal('me');
 lab.textContent='Waiting for him to reveal…';btn.style.opacity='.85';
 setTimeout(function(){
  reveal('him');
  lab.textContent="You're both revealed ✨";
  btn.style.opacity='1';
  if(tl)tl.textContent='talking for';mode='up';t=0;
 },1600);
});
})();
