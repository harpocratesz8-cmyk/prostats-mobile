// compare history.json against refs/<Comp name prefix>.txt ; lines "season | champ | runner-up?"
const fs=require("fs"),vm=require("vm"),path=require("path"),ctx={console};vm.createContext(ctx);
const R=require("path").resolve(__dirname,"../..")+"/";
vm.runInContext(fs.readFileSync(R+"src/logodb.js","utf8")+";this.C=ClubDB;this.N=NatDB;this.lkey=lkey;",ctx);
const j=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/index.json","utf8"));ctx.C.load(j);ctx.N.load(j);
const H=JSON.parse(fs.readFileSync(R+"ProStats-Mobile/web/www/logos/history.json","utf8"));
const nl=new Set((H.nl||[]).map(ctx.lkey)); const lin=H.lin||{}; const al=H.alias||{};
const ALIAS=JSON.parse(fs.existsSync(__dirname+"/refs/alias.json")?fs.readFileSync(__dirname+"/refs/alias.json","utf8"):"{}");
function team(n,nat){ n=al[n]||n; const base=n.replace(/\s*\([^)]*\)\s*$/,""); let e=null;
  if(nl.has(ctx.lkey(n))||nl.has(ctx.lkey(base))) e=ctx.C.exact.get(ctx.lkey(n))||null; else e=nat?(ctx.N.strict(n)||ctx.C.strict(n)):ctx.C.strict(n);
  if(lin[n]||lin[base]) return team(lin[n]||lin[base],nat); return e?e.n:"~"+base; }
function refTeam(n,nat){ n=ALIAS[n]||n; let t=team(n,nat); if(t[0]==="~"){ const e=(nat?ctx.N:ctx.C).resolve(n); if(e) t=e.n; } return t; }
const norm=s=>s.replace(/\./g,"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(w=>w.length>2&&!/^(fc|cf|club|sc|ac|the|de|football|calcio|united)$/.test(w));
function jac(a,b){ const A=new Set(norm(a.replace(/^~/,""))),B=new Set(norm(b.replace(/^~/,""))); if(!A.size||!B.size) return 0; let i=0; for(const x of A) if(B.has(x)) i++; return (i===Math.min(A.size,B.size))?1:i/(A.size+B.size-i); }
function same(a,b,ra,rb){ if(a===b) return true; if(a[0]!=="~"&&b[0]!=="~"&&jac(a,b)>=0.5) return true; return ra!==undefined && jac(ra,rb)>=0.5; }
function endYear(s){ let m=s.match(/^(\d{4})\s*[–-]\s*(\d{2,4})/); if(m){ const y=+m[1]; let e=m[2].length===2?Math.floor(y/100)*100+ +m[2]:+m[2]; if(e<y) e+=100; return e;} return +s.match(/\d{4}/)[0]; }
const files=process.argv.slice(2).length?process.argv.slice(2):fs.readdirSync(__dirname+"/refs").filter(f=>f.endsWith(".txt"));
let total=0;
for(const f of files){ const name=path.basename(f,".txt"); const comp=H.c.find(c=>c.n===name)||H.c.find(c=>c.n.startsWith(name));
  if(!comp){ console.log(`## ${name}: COMPETIÇÃO NÃO ENCONTRADA`); continue; }
  const nat=/Copa do Mundo|UEFA Euro$|Copa Am|Nations|Gold Cup|AFCON|Asian Cup/.test(comp.n);
  const ref={}; for(const ln of fs.readFileSync(__dirname+"/refs/"+f.replace(/^.*\//,""),"utf8").split("\n")){ if(!ln.trim()||ln.startsWith("#")) continue;
    const p=ln.split("|").map(s=>s.trim()); const y=endYear(p[0]); (ref[y]=ref[y]||[]).push({s:p[0],c:ALIAS[p[1]]||p[1],r:ALIAS[p[2]]||p[2]||""}); }
  const ours={}; for(const r of comp.r){ (ours[r[1]]=ours[r[1]]||[]).push(r); }
  const out=[]; const years=[...new Set([...Object.keys(ref),...Object.keys(ours)].map(Number))].sort((a,b)=>a-b);
  const careerFuture=y=>y>2026;
  for(const y of years){ const R_=ref[y]||[], O=ours[y]||[];
    if(!R_.length){ out.push(`${y}: app tem [${O.map(r=>r[0]+" "+r[2]).join(" / ")}] — fonte não tem`); continue; }
    if(!O.length){ out.push(`${y}: FALTA no app — fonte: ${R_.map(x=>x.s+" "+x.c+(x.r?" (vice "+x.r+")":"")).join(" / ")}`); continue; }
    const oc=O.map(r=>team(r[2],nat)), rc=R_.map(x=>refTeam(x.c,nat));
    for(let i=0;i<rc.length;i++) if(!oc.some((o,k)=>same(o,rc[i],O[k][2],R_[i].c))) out.push(`${y}: CAMPEÃO app=${O.map(r=>r[2]).join("/")} [${oc.join("/")}]  fonte=${R_[i].c} [${rc[i]}]`);
    for(let i=0;i<oc.length;i++) if(!rc.some((r,k)=>same(oc[i],r,O[i][2],R_[k].c))) out.push(`${y}: campeão extra no app ${O[i][2]}`);
    if(R_.length===1&&O.length===1&&R_[0].r&&!/^(none|—|-)$/i.test(R_[0].r)){ const a=team(O[0][3]||"",nat), b=refTeam(R_[0].r,nat); if(!O[0][3]) {} else if(!same(a,b,O[0][3],R_[0].r)) out.push(`${y}: VICE app=${O[0][3]} [${a}]  fonte=${R_[0].r} [${b}]`); }
  }
  total+=out.length; console.log(`## ${comp.n} — ${out.length} divergência(s)`); out.forEach(l=>console.log("  "+l)); }
console.log("TOTAL",total);
