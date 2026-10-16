(function(){
var P=window.__THINK_PHRASES||[];
function swap(i){
 [].slice.call(document.querySelectorAll('.copy.loop')).forEach(function(el){
  if(el.textContent.indexOf('…')<0)return;
  el.style.transition='filter .28s ease, transform .28s ease';
  el.style.filter='opacity(0) blur(2px)';el.style.transform='translateY(-7px)';
  setTimeout(function(){
   el.style.transition='none';el.textContent=P[i%P.length];el.style.transform='translateY(7px)';
   void el.offsetWidth;
   el.style.transition='filter .32s ease, transform .32s ease';el.style.filter='opacity(1) blur(0)';el.style.transform='none';
  },300);
 });
}
var i=0,iv=null;
function cycle(){clearInterval(iv);i=0;setTimeout(function(){clearInterval(iv);iv=setInterval(function(){i++;swap(i);},1500);},17700);}
cycle();setInterval(cycle,typeof CYCLE_MS!=='undefined'?CYCLE_MS:26000);
})();
