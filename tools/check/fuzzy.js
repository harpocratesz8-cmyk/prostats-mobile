// every raw name whose crest came from loose matching (not an exact name/alias hit): review for wrong crests
const fs=require("fs"),vm=require("vm"),ctx={console};vm.createContext(ctx);
const R=require("path").resolve(__dirname,"../..")+"/";
vm.runInContext(fs.readFileSync(R+"src/logodb.js","utf8")+";this.C=ClubDB;this.N=NatDB;this.lkey=lkey;",ctx);
const j=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/index.json","utf8"));ctx.C.load(j);ctx.N.load(j);
const H=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/history.json","utf8"));
const nl=new Set((H.nl||[]).map(ctx.lkey)); const lin=H.lin||{}; const al=H.alias||{};
const out=new Map();
for(const c of H.c){ const nat=/Copa do Mundo|UEFA Euro$/.test(c.n); for(const r of c.r) for(const n0 of [r[2],r[3]]){ if(!n0) continue; let n=al[n0]||n0; if(lin[n]) n=lin[n];
  const base=n.replace(/\s*\([^)]*\)\s*$/,""); if(nl.has(ctx.lkey(n))||nl.has(ctx.lkey(base))) continue;
  const db=nat?ctx.N:ctx.C; if(db.exact.get(ctx.lkey(n))||db.exact.get(ctx.lkey(base))||db.exact.get(ctx.lkey(base.replace(/[-\s][A-Z]{2}$/,"")))) continue; const e=db.strict(n)||(nat?ctx.C.strict(n):null); if(!e) continue;
  const k=n+"  →  "+e.n; if(!out.has(k)) out.set(k,new Set()); out.get(k).add(c.n); } }
for(const [k,v] of [...out].sort()) console.log(k+"   ["+[...v].slice(0,3).join(", ")+"]");
