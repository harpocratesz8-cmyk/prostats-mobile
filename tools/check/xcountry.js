// crests used by domestic competitions of two different countries -> probably a borrowed crest
const fs=require("fs"),vm=require("vm"),ctx={console};vm.createContext(ctx);
const R=require("path").resolve(__dirname,"../..")+"/";
vm.runInContext(fs.readFileSync(R+"src/logodb.js","utf8")+";this.C=ClubDB;this.N=NatDB;this.lkey=lkey;",ctx);
const j=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/index.json","utf8"));ctx.C.load(j);ctx.N.load(j);
const H=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/history.json","utf8"));
const nl=new Set((H.nl||[]).map(ctx.lkey)); const lin=H.lin||{}; const al=H.alias||{};
function team(n){ n=al[n]||n; if(lin[n]) n=lin[n]; const base=n.replace(/\s*\([^)]*\)\s*$/,"");
  if(nl.has(ctx.lkey(n))||nl.has(ctx.lkey(base))) return null; const e=ctx.C.strict(n); return e?e.n:null; }
const INTL=/UEFA|Copa Libertadores|Sul-Americana|Recopa|Intercontinental|Club World|Copa do Mundo|Leagues Cup|Campeones Cup|Euro/;
const use=new Map();
for(const c of H.c){ if(INTL.test(c.n)) continue; for(const r of c.r) for(const n of [r[2],r[3]]){ if(!n) continue; const t=team(n); if(!t) continue;
  if(!use.has(t)) use.set(t,new Map()); const m=use.get(t); const g=c.g||"?"; if(!m.has(g)) m.set(g,new Set()); m.get(g).add(n+" @ "+c.n); } }
for(const [t,m] of use) if(m.size>1) console.log(t+"  ::  "+[...m].map(([g,s])=>g+": "+[...s].slice(0,2).join("; ")).join("  ||  "));
