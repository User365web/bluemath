let expression = '';
let angleMode = 'DEG';
let memory = 0;
let history = [];
const exprEl = document.getElementById('expression');
const resultEl = document.getElementById('result');
const histEl = document.getElementById('historyList');
const countEl = document.getElementById('historyCount');

function render(){ exprEl.textContent = expression || '0'; }
function insert(v){ expression += v; render(); }
function back(){ expression = expression.slice(0,-1); render(); }
function format(n){ if(!Number.isFinite(n)) return 'Error'; return Number(n.toPrecision(12)).toString(); }
function deg(x){return angleMode==='DEG'?x*Math.PI/180:x}
function inv(x){return angleMode==='DEG'?x*180/Math.PI:x}
function factorial(n){if(n<0||!Number.isInteger(n)||n>170) throw Error('Invalid factorial'); let r=1; for(let i=2;i<=n;i++)r*=i; return r}
function tokenize(s){
  s=s.replace(/×/g,'*').replace(/÷/g,'/').replace(/π/g,'pi').replace(/−/g,'-');
  const tokens=[]; let i=0;
  while(i<s.length){ if(/\s/.test(s[i])){i++;continue;} if(/[0-9.]/.test(s[i])){let j=i+1;while(j<s.length&&/[0-9.eE+-]/.test(s[j])){if((s[j]=='+'||s[j]=='-')&&!/[eE]/.test(s[j-1]))break;j++;} tokens.push({t:'num',v:Number(s.slice(i,j))});i=j;continue;} if(/[a-zA-Z]/.test(s[i])){let j=i+1;while(j<s.length&&/[a-zA-Z]/.test(s[j]))j++;tokens.push({t:'name',v:s.slice(i,j).toLowerCase()});i=j;continue;} if('+-*/^(),!'.includes(s[i])){tokens.push({t:s[i],v:s[i]});i++;continue;} throw Error('Unknown character'); }
  return tokens;
}
function evaluate(s){
  let ts=tokenize(s); let pos=0;
  function primary(){
    let t=ts[pos];
    if(!t) throw Error('Incomplete expression');
    if(t.t==='num'){pos++; return t.v;}
    if(t.t==='name'){
      pos++; const name=t.v;
      if(name==='pi') return Math.PI; if(name==='e') return Math.E;
      if(ts[pos]?.t==='('){pos++; const x=add(); if(ts[pos]?.t!==')')throw Error('Missing )');pos++; return fn(name,x);}
      if(name==='sqrt'||name==='sin'||name==='cos'||name==='tan'||name==='log'||name==='ln'||name==='abs'||name==='asin'||name==='acos'||name==='atan'||name==='exp'||name==='fact') throw Error('Function needs ()');
      throw Error('Unknown name');
    }
    if(t.t==='('){pos++;const x=add();if(ts[pos]?.t!==')')throw Error('Missing )');pos++;return x;}
    if(t.t==='-'){pos++;return -primary();} if(t.t==='+'){pos++;return primary();}
    throw Error('Expected number');
  }
  function power(){let x=primary();while(ts[pos]?.t==='!'){pos++;x=factorial(x)} if(ts[pos]?.t==='^'){pos++;let y=power();x=Math.pow(x,y)}return x;}
  function mul(){let x=power();while(ts[pos]&&['*','/'].includes(ts[pos].t)){let op=ts[pos++].t,y=power();x=op==='*'?x*y:x/y}return x;}
  function add(){let x=mul();while(ts[pos]&&['+','-'].includes(ts[pos].t)){let op=ts[pos++].t,y=mul();x=op==='+'?x+y:x-y}return x;}
  function fn(name,x){const f={sin:v=>Math.sin(deg(v)),cos:v=>Math.cos(deg(v)),tan:v=>Math.tan(deg(v)),asin:v=>inv(Math.asin(v)),acos:v=>inv(Math.acos(v)),atan:v=>inv(Math.atan(v)),sqrt:Math.sqrt,log:v=>Math.log10(v),ln:Math.log,abs:Math.abs,exp:Math.exp,fact:factorial};if(!f[name])throw Error('Unknown function');return f[name](x)}
  const out=add(); if(pos!==ts.length)throw Error('Unexpected input'); return out;
}
function calculate(){try{const val=evaluate(expression);resultEl.textContent=format(val);if(expression){history.unshift({e:expression,r:format(val)});history=history.slice(0,30);renderHistory()}return val}catch(e){resultEl.textContent='Error';return NaN}}
function renderHistory(){countEl.textContent=history.length;histEl.innerHTML=history.length?history.map(x=>`<button class="history-item" onclick="expression=${JSON.stringify(x.e)};render();resultEl.textContent=${JSON.stringify(x.r)}"><small>${escapeHtml(x.e)}</small><strong>${escapeHtml(x.r)}</strong></button>`).join(''):'<p class="muted">Your calculations will appear here.</p>'}
function escapeHtml(x){return x.replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}

document.querySelectorAll('[data-insert]').forEach(b=>b.addEventListener('click',()=>insert(b.dataset.insert)));
document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>{const a=b.dataset.action;if(a==='back')back();if(a==='equals')calculate();if(a==='mc')memory=0;if(a==='mr')insert(format(memory));if(a==='ms')memory=Number.isFinite(evaluate(expression))?evaluate(expression):memory;if(a==='mplus')memory+=(Number.isFinite(evaluate(expression))?evaluate(expression):0);if(a==='mminus')memory-=(Number.isFinite(evaluate(expression))?evaluate(expression):0)}));
document.querySelectorAll('[data-angle]').forEach(b=>b.addEventListener('click',()=>{angleMode=b.dataset.angle;document.querySelectorAll('[data-angle]').forEach(x=>x.classList.toggle('active',x===b))}));
document.getElementById('clearHistory').addEventListener('click',()=>{history=[];renderHistory()});
document.addEventListener('keydown',e=>{if(e.target.matches('input,textarea,select'))return;if(/[0-9+\-*/().^]/.test(e.key))insert(e.key);else if(e.key==='Enter')calculate();else if(e.key==='Backspace')back()});
function solveQuadratic(){const a=+document.getElementById('qa').value,b=+document.getElementById('qb').value,c=+document.getElementById('qc').value,o=document.getElementById('quadOut');if(!a){o.textContent='a must not be 0.';return}const d=b*b-4*a*c;if(d>=0){const x1=(-b+Math.sqrt(d))/(2*a),x2=(-b-Math.sqrt(d))/(2*a);o.innerHTML=`Roots: <strong>${format(x1)}</strong> and <strong>${format(x2)}</strong>`}else{o.innerHTML=`Complex roots: <strong>${format(-b/(2*a))} ± ${format(Math.sqrt(-d)/(2*a))}i</strong>`}}
function percentage(){const v=+document.getElementById('pctValue').value,r=+document.getElementById('pctRate').value;document.getElementById('pctOut').innerHTML=`${r}% of ${v} = <strong>${format(v*r/100)}</strong>`}
function statistics(){const a=document.getElementById('statsValues').value.split(',').map(Number).filter(Number.isFinite).sort((x,y)=>x-y);const o=document.getElementById('statsOut');if(!a.length){o.textContent='Enter comma-separated numbers.';return}const mean=a.reduce((x,y)=>x+y,0)/a.length,median=a.length%2?a[(a.length-1)/2]:(a[a.length/2-1]+a[a.length/2])/2,sd=Math.sqrt(a.reduce((s,x)=>s+(x-mean)**2,0)/a.length);o.innerHTML=`n=${a.length} · Mean <strong>${format(mean)}</strong> · Median <strong>${format(median)}</strong> · SD <strong>${format(sd)}</strong> · Range <strong>${a[0]}–${a[a.length-1]}</strong>`}
function convertUnits(){const v=+document.getElementById('convValue').value,f=document.getElementById('convFrom').value,t=document.getElementById('convTo').value,o=document.getElementById('convOut');let x=v;const length={meters:1,kilometers:1000,miles:1609.344,feet:.3048},mass={kilograms:1,pounds:.45359237};try{if(f in length&&t in length)x=v*length[f]/length[t];else if(f in mass&&t in mass)x=v*mass[f]/mass[t];else if(f==='celsius'&&t==='fahrenheit')x=v*9/5+32;else if(f==='fahrenheit'&&t==='celsius')x=(v-32)*5/9;else if(f===t)x=v;else throw Error('incompatible');o.innerHTML=`<strong>${format(x)}</strong> ${t}`}catch(e){o.textContent='Choose compatible units.'}}
render();renderHistory();
