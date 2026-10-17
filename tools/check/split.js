// candidate split identities: two different crest entries in the same competition whose names look alike
const fs=require("fs"),vm=require("vm"),ctx={console};vm.createContext(ctx);
const R=require("path").resolve(__dirname,"../..")+"/";
vm.runInContext(fs.readFileSync(R+"src/logodb.js","utf8")+";this.C=ClubDB;this.N=NatDB;this.lkey=lkey;",ctx);
const j=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/index.json","utf8"));ctx.C.load(j);ctx.N.load(j);
const H=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/history.json","utf8"));
const nl=new Set((H.nl||[]).map(ctx.lkey)); const lin=H.lin||{}; const al=H.alias||{};
const eq=new Map(); for(const g of H.eq||[]) for(const n of g) eq.set(n,g[0]);
function team(n){ n=al[n]||n; const base=n.replace(/\s*\([^)]*\)\s*$/,""); let e=null;
  if(nl.has(ctx.lkey(n))||nl.has(ctx.lkey(base))) e=ctx.C.exact.get(ctx.lkey(n))||null; else e=ctx.C.strict(n);
  if(lin[n]||lin[base]) return team(lin[n]||lin[base]); const k=e?e.n:"~"+base; return eq.get(k)||k; }
const STOP=/^(fc|cf|club|sc|ac|the|de|da|do|football|calcio|united|city|sport|sporting|clube|esporte|atletico|athletic|real|fk|if|ik|sk|sv|vfb|vfl|bk|cd|ca|ec|se|us|as|ss|afc|futebol|futbol|deportivo|ff|bsc|tsv|ksv|kv|rc|rcd|cs|union|wanderers|rovers|town|county|olympique|racing|national|nacional|internacional|academica|association|associação|esportiva|recreativo|rangers|celtic|calcio)$/;
const tok=s=>s.replace(/^~/,"").replace(/\./g,"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(w=>w.length>2&&!STOP.test(w));
const seen=new Set();
for(const c of H.c){ const ids=new Map(); for(const r of c.r) for(const n of [r[2],r[3]]) if(n){ const t=team(n); if(!ids.has(t)) ids.set(t,n); }
  const ks=[...ids.keys()];
  for(let a=0;a<ks.length;a++) for(let b=a+1;b<ks.length;b++){ const A=tok(ks[a]),B=tok(ks[b]); if(!A.length||!B.length) continue;
    const i=A.filter(x=>B.includes(x)).length; if(i&&(i===Math.min(A.length,B.length))){ const key=[ks[a],ks[b]].sort().join(" ⇄ "); if(seen.has(key)) continue; seen.add(key); console.log(`${c.n}: ${ks[a]}  ⇄  ${ks[b]}`); } } }
