"""Parse the user's hand-made champions lists (leagues + cups TXT) into logos/history.json.
Output: {"v":1, "c":[{"n": name, "g": country, "r": [[season, endYear, champion, runnerUp, score], ...]}]}
Usage: python3 tools/build_history.py LIGAS.txt COPAS.txt OUT.json"""
import re, sys, json, unicodedata

SEASON_HEAD = re.compile(r"^(\d{4}(?:\s*[/-]\s*\d{2,4})?|\d{2}/\d{2})(?=[\s:\-]|$)")
LABEL_YEAR = re.compile(r"^([^\t]*?\b(?:19|20)\d{2}(?:/\d{2,4})?\b[^\t]*?)(?:\t+|\s{2,})(.+)$")
SCORE = re.compile(r"(?<![\d/,.])(\d{1,2})\s?-\s?(\d{1,2})(?![\d/])")
DATE_VENUE = re.compile(r"^\d{1,2}/\s?\d{1,2}(?:/\d{2})?\s+.*?(?:\t+|\s{2,})")
MONTH_DAY = re.compile(r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}\s+")
FMT = {"Schweizer Cup": "venue", "Trophée des Champions": "venue", "Coppa Itália": "win_ab", "Supercopa de España": "win_ab",
       "Campeón de Campeones": "ab_win", "Super Copa Do Brasil": "ab_win", "Supercoppa": "ab_score", "Svenska Cupen": "ab_score",
       "Liga MX Clausura e Liga MX Apertura": "cols"}
SKIP = re.compile(r"no winners|not held|n/a|w/o|n[aã]o (contestado|disputado|realizad)|cancel|abandon|suspens|no competition|void|não houve|nao houve|interromp", re.I)
FLAG = re.compile(r"[\U0001F1E6-\U0001F1FF]")

COMP_RENAME = {"League 1": "Ligue 1", "Budesliga": "2. Bundesliga", "Liga MX Clausura e Liga MX Apertura": "Liga MX",
               "Copa Do Brasil": "Copa do Brasil", "Super Copa Do Brasil": "Supercopa do Brasil", "Serie B": "Brasileirão Série B",
               "Serie C": "Brasileirão Série C", "Serie D": "Brasileirão Série D", "Copa Do Nordeste": "Copa do Nordeste",
               "COPA VERDE": "Copa Verde", "SUPERLIGA": "SuperLiga", "Coppa Itália": "Coppa Italia",
               "Supercoppa": "Supercoppa Italiana", "Cupen": "Norwegian Cup (Cupen)", "Copa Sul-americana": "Copa Sul-Americana",
               "Liga Portugal (Portugal)": "Liga Portugal", "UEFA Eurocopa": "UEFA Euro"}

def norm_season(s):
    s = re.sub(r"\s+", "", s).replace("-", "/")
    m = re.fullmatch(r"(\d{2})/(\d{2})", s)
    if m: a = int(m[1]); y = (1900 if a >= 50 else 2000) + a; return f"{y}/{m[2]}", y + 1
    m = re.fullmatch(r"(\d{4})/(\d{2,4})", s)
    if m: a = int(m[1]); return f"{a}/{m[2][-2:]}", a + 1
    return s, int(s[:4])

def label_season(label):
    m = re.search(r"\b((?:19|20)\d{2})(?:/(\d{2,4}))?\b", label)
    y = int(m[1]); end = y + 1 if m[2] else y
    if re.fullmatch(r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", label.strip()): return str(y), y
    return re.sub(r"\s+", " ", label).strip(), end

def clean_team(s):
    s = s.strip().strip(":").strip()
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"#\d+\b", "", s)
    s = re.sub(r"\(\s*\d+\s*(?:\.?º|°)?\s*\)", "", s)        # (1)  (30.º)
    s = re.sub(r"\(\s*\d+\.º\s*\)", "", s)
    s = re.sub(r"\(\s*(?:after playoff|in [^)]*|\d{1,2}/\d{1,2}/\d{2,4})\s*\)", "", s, flags=re.I)
    s = re.sub(r"\s\d+\.$", "", s)                           # "Bayern Munich 21."
    s = re.sub(r"\b(aet|asdet|agg|replay|pen)\b.*$", "", s, flags=re.I)
    s = s.replace("*", "")
    s = re.sub(r"\s+", " ", s).strip(" -–,;")
    return s

def split_cols(s):
    return [c for c in re.split(r"\t+|\s{2,}", s.strip()) if c.strip()]

def looks_team(c):
    c = c.strip()
    return bool(c) and bool(re.search(r"[A-Za-zÀ-ÿ]", c)) and not re.fullmatch(r"[\d.,\s%º°-]+", c) and not re.match(r"^(aet|asdet|agg|pen|\[|\(|replay|in |att)", c, re.I)

def prep(body):
    body = MONTH_DAY.sub("", body.strip())
    body = re.sub(r"^#\s*", "", body)
    body = re.sub(r"\s\(([A-Z]{2,6})\)", "", body)                       # (NAFBL) league tags
    body = re.sub(r"\bann\b", "0-0", body)
    body = re.sub(r"\((\d+-\d+)\s*Pen\)", r"[\1 pen]", body, flags=re.I)
    body = re.sub(r"\(\s*(\d+-\d+)\s*,\s*(\d+-\d+)\s*\)", r"  \1 \2  ", body)
    body = re.sub(r"\(\s*(\d+-\d+)\s*(?:\(\s*(?:Pen\s*)?(\d+-\d+)\s*\))?\s*\)", lambda m: f"  {m[1]}  " + (f"[{m[2]} pen]  " if m[2] else ""), body)  # Copa Argentina
    return body

def winner_of(a, b, w):
    k = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    if k(w) and (k(w) in k(b) or k(b) in k(w)) and not (k(w) in k(a) and len(k(a)) >= len(k(b))): return b, a
    return a, b

def parse_match(body):
    """returns (teamA, goalsA, goalsB, teamB) or None; supports '0-0 2-1' two-leg lines (sum)"""
    body = DATE_VENUE.sub("", body.strip())
    ms = list(SCORE.finditer(body))
    if not ms: return None
    first = ms[0]; a = clean_team(body[:first.start()])
    if not looks_team(a): return None
    # consecutive scores right after the first one belong to the same tie (two legs / agg)
    last = first; ga = int(first[1]); gb = int(first[2]); i = 1
    while i < len(ms) and re.fullmatch(r"\s*", body[last.end():ms[i].start()]):
        ga += int(ms[i][1]); gb += int(ms[i][2]); last = ms[i]; i += 1
    rest = body[last.end():]
    rest = re.split(r"\t+|\s{2,}|\[|\(|\bagg\b|\baet\b|\bAET\b", rest.strip())[0]
    b = clean_team(rest)
    if not looks_team(b): return None
    pm = re.search(r"(\d{1,2})\s?-\s?(\d{1,2})\s*(?:pen|p\b)", body[last.end():], re.I)
    return a, ga, gb, b, (int(pm[1]), int(pm[2])) if pm else None

def ab_to_match(body):
    """'A - B   venue   2-1' -> 'A  2-1  B'"""
    m = re.match(r"^(.*?)\s+[-–]\s+(.*)$", body)
    if not m: return body
    a = m[1]; rest = split_cols(m[2]); b = rest[0] if rest else ""
    sc = SCORE.search(m[2]); 
    if not sc: return body
    tail = m[2][sc.end():]
    return f"{a}  {sc[1]}-{sc[2]}  {b}  {tail}"

def is_header(line):
    if not line or line[0] in " \t•": return False
    if FLAG.search(line[:4]): return True
    if SEASON_HEAD.match(line): return False
    if LABEL_YEAR.match(line) and not line.rstrip().endswith(":"): return False
    return line.rstrip().endswith(":")

def header_name(line):
    s = FLAG.sub("", line).strip().rstrip(":").strip()
    s = re.sub(r"\{.*?\}", "", s)
    s = re.sub(r"\s*\((Segundo|Extinta)[^)]*(\)|$)", "", s).strip()
    if ":" in s: s = s.split(":", 1)[1].strip()          # "Dinamarca: Danish Cup (Pokalen)"
    s = re.sub(r"\s*\(\s*$", "", s).strip()
    return s

def parse(path, out):
    lines = open(path, encoding="utf-8").read().replace("\r", "").split("\n")
    comp = None; country = ""; comp_country = ""; mx_base = None; seasons = None; cur = None; skip = False; durand_team = None
    pending_head = None
    def flush():
        nonlocal seasons
        fmt = FMT.get(comp)
        if comp and seasons:
            rows = []
            for s in seasons:
                if s.get("matches"):
                    tot = {}
                    for a, ga, gb, b, _ in s["matches"]:
                        tot[a] = tot.get(a, 0) + ga; tot[b] = tot.get(b, 0) + gb
                    if len(s["matches"]) == 1 or len(tot) != 2:
                        a, ga, gb, b, pn = s["matches"][0]; champ, ru = a, b
                        if FMT.get(comp) == "ab_score":
                            if gb > ga or (ga == gb and pn and pn[1] > pn[0]): champ, ru = b, a
                    else:
                        (t1, g1), (t2, g2) = list(tot.items())
                        if g1 == g2:   # level on aggregate: winner of the last leg, else first-listed team
                            a, ga, gb, b, pn = s["matches"][-1]; champ, ru = (a, b) if ga >= gb else (b, a)
                            if pn: champ, ru = (a, b) if pn[0] >= pn[1] else (b, a)
                        else: champ, ru = (t1, t2) if g1 > g2 else (t2, t1)
                    a, ga, gb, b, _ = s["matches"][0]
                    score = f"{ga}-{gb}" if len(s["matches"]) == 1 else ""
                    if len(s["matches"]) == 1 and champ != a: score = f"{gb}-{ga}"
                    s["champ"], s["ru"], s["score"] = champ, ru, score
                if s.get("champ"): rows.append([s["season"], s["end"], s["champ"], s.get("ru") or "", s.get("score") or ""])
            if rows:
                name = COMP_RENAME.get(comp, comp)
                ex = next((c for c in out if c["n"] == name and c["g"] == comp_country), None)
                if ex: ex["r"].extend(rows)
                else: out.append({"n": name, "g": comp_country, "r": rows})
        seasons = None
    for idx, raw in enumerate(lines):
        line = raw.rstrip()
        st = line.strip()
        if not st or set(st) <= set("-_=") :
            if st and set(st) <= set("-"): pending_head = None
            continue
        if is_header(line) and not st.startswith("NB") and not st.startswith("Nota"):
            name = header_name(line)
            if not name: continue
            # a header followed by another header is a country label
            nxt = next((l for l in lines[idx+1:] if l.strip()), "")
            flag_country = FLAG.search(line[:4]) and ":" not in line
            if (is_header(nxt.rstrip()) and not FLAG.search(nxt[:4])) or flag_country:
                if not re.search(r"Títulos e Vices|Clubes/Regimentos", name): country = name
                continue
            if re.search(r"Títulos e Vices", name): continue
            if re.search(r"Clubes/Regimentos com 1", name): durand_team = None; continue
            if comp == "Copas Campeões e Vices" or name in ("Ligas", "Copas Campeões e Vices"):
                comp = name; continue
            flush(); comp = name; comp_country = country; seasons = []; cur = None; skip = False; durand_team = None; mx_base = None
            continue
        if seasons is None: continue
        if st.startswith("NB") or st.startswith("Nota") or st.startswith("{"):
            skip = True; continue
        if skip:
            if not line[0].isspace() and re.search(r"champions", line, re.I) and not SEASON_HEAD.match(line): skip = False
            continue
        if re.match(r"^\s*(Nord|Season|runners-up)\b", line): continue
        # ---- Durand-style blocks ----
        m = re.match(r"^(.+?)\s*\((\d+)\s*títulos?\)\s*$", st)
        if m: durand_team = clean_team(m[1].split("/")[0]); continue
        m = re.match(r"^•\s*(\d{4}):\s*(.*)$", st)
        if m and durand_team:
            y = int(m[1]); rest = m[2]
            ru = clean_team(re.sub(r"^vs\.?\s*", "", rest)) if rest.lower().startswith("vs") else ""
            seasons.append({"season": str(y), "end": y, "champ": durand_team, "ru": ru}); continue
        m = re.match(r"^•\s*(.+?)\s*\(\d+\):\s*(\d{4})\s*(?:\(vs\.?\s*(.+?)\))?\.?$", st)
        if m:
            seasons.append({"season": m[2], "end": int(m[2]), "champ": clean_team(m[1]), "ru": clean_team(m[3] or "")}); continue
        # ---- continuation lines ----
        if line[0].isspace() and not SEASON_HEAD.match(st):
            if FMT.get(comp) == "cols" and mx_base and not st.startswith("["):
                parts = split_cols(st)
                if len(parts) >= 3:
                    sc = SCORE.findall(st); agg = re.search(r"(\d+)-(\d+)\s*agg", st)
                    seasons.append({"season": f"{mx_base[0]} {parts[0]}", "end": mx_base[1] - (1 if re.match(r"(Winter|Invierno|Apert)", parts[0], re.I) else 0),
                                    "champ": clean_team(parts[1]), "ru": clean_team(parts[2]), "score": f"{agg[1]}-{agg[2]}" if agg else ""})
                continue
            if cur is None: continue
            m2 = re.match(r"^(?:2nd|vice)\s*:\s*(.+)$", st, re.I)
            if m2: cur["ru"] = clean_team(m2[1]); continue
            if st.startswith("["): continue
            body = prep(re.sub(r"^replay\s+", "", st, flags=re.I))
            fmt = FMT.get(comp)
            if fmt == "venue": body = "  ".join(split_cols(body)[1:])
            if fmt == "ab_score": body = ab_to_match(body)
            pm = parse_match(body)
            if pm and cur.get("matches") is not None: cur["matches"].append(pm)
            continue
        # ---- season lines ----
        m = SEASON_HEAD.match(st)
        if m:
            season, end = norm_season(m[1]); body = st[m.end():]
            body = re.sub(r"^\s*[:\-–]\s*", "", body)
        else:
            lm = LABEL_YEAR.match(st)
            if not lm: continue
            season, end = label_season(lm[1]); body = lm[2]
        if FMT.get(comp) == "cols" and not body.strip(): mx_base = (season, end); cur = None; continue
        if SKIP.search(body) or not body.strip(): cur = None; continue
        if any(s["season"] == season for s in seasons) and not re.search(r"[a-z]", season, re.I):
            cur = None; continue   # later tables of the same section (promotion lists, etc.)
        body = prep(body.rstrip(":"))
        fmt = FMT.get(comp)
        cur = {"season": season, "end": end}
        rp = re.search(r"\(runners-up:\s*(.+?)(?:\s{2,}|\*|\))", body)
        if rp: cur["ru"] = clean_team(rp[1]); body = body[:rp.start()]
        if fmt == "venue": body = "  ".join(split_cols(body)[1:])
        if fmt == "ab_score": body = ab_to_match(body)
        if fmt in ("win_ab", "ab_win", "cols"):
            cols = split_cols(re.sub(r"\s[-–]\s", "  ", body))
            cols = [clean_team(c) for c in cols if looks_team(c) and not SCORE.fullmatch(c.strip())]
            cols = [c for c in cols if c]
            if len(cols) < 2: cur = None; continue
            if fmt == "win_ab": w = cols[0]; a, b = cols[1], cols[2] if len(cols) > 2 else ""; champ, ru = winner_of(a, b, w); cur["champ"], cur["ru"] = w, (ru if b else "")
            elif fmt == "ab_win": w = cols[2] if len(cols) > 2 else cols[0]; champ, ru = winner_of(cols[0], cols[1], w); cur["champ"], cur["ru"] = champ, ru
            else:
                cur["champ"], cur["ru"] = cols[0], cols[1]
                agg = re.search(r"(\d+)-(\d+)\s*agg", body) or SCORE.search(body); cur["score"] = f"{agg[1]}-{agg[2]}" if agg else ""
            seasons.append(cur); continue
        pm = parse_match(body)
        if pm: cur["matches"] = [pm]
        else:
            cols = split_cols(DATE_VENUE.sub("", body.strip()))
            cols = [c for c in cols if looks_team(c)]
            if not cols: cur = None; continue
            cur["champ"] = clean_team(cols[0])
            if len(cols) > 1 and len(cols[1]) <= 45: cur["ru"] = clean_team(cols[1])
        seasons.append(cur)
    flush()

out = []
for p in sys.argv[1:-1]: parse(p, out)
INTL = {"Copa do Mundo", "FIFA Intercontinental Cup", "FIFA Club World Cup", "UEFA Champions League", "UEFA Europa League",
        "UEFA Conference League", "UEFA Super Cup", "Copa Libertadores", "Copa Sul-Americana", "Recopa Sul-Americana", "UEFA Euro"}
COUNTRY_FIX = {"A-League": "Austrália", "Durand Cup": "Índia", "Arábia Saudita": "Arábia Saudita"}
byname = {c["n"]: c for c in out}
for c in out:
    if c["n"] in INTL: c["g"] = ""
    if c["n"] in COUNTRY_FIX: c["g"] = COUNTRY_FIX[c["n"]]
    if c["n"] == "Arábia Saudita": c["n"] = "King's Cup"
# the user's file has Danish 2004/05+ champions pasted at the end of the Scottish list
sc, dk = byname.get("Scottish Premiership"), byname.get("3F Superliga")
if sc and dk:
    mv = [r for r in sc["r"] if "/" in r[0]]; sc["r"] = [r for r in sc["r"] if "/" not in r[0]]; dk["r"].extend(mv)
BAD = re.compile(r"not (played|awarded|finished|disputed)|no (championship|winners)|local leagues|^\??$|^[-–]$|title revoked", re.I)
def fix_name(n):
    n = re.sub(r"^.*\(now ([^)]+)\).*$", r"\1", n)
    n = re.sub(r"^[DT]\s+(?=[A-Z])", "", n)
    n = re.sub(r"^\d+\s*[–-]\s*\d+\s+", "", n)
    n = re.sub(r"\s\d+(:\d+)+$", "", n)
    n = re.sub(r"\s\d+\s+[A-Z].*?\s\d+\b.*$", "", n)
    n = re.sub(r"\s*\((North|South|Group [A-Z])\).*$", "", n)
    n = re.sub(r"\s+\d+ points? behind.*$", "", n)
    n = n.replace('"', "")
    return n.strip(" ,;")
for c in out:
    rows = []
    for r in c["r"]:
        r[2] = fix_name(r[2]); r[3] = fix_name(r[3])
        if BAD.search(r[3]): r[3] = ""
        if not BAD.search(r[2]): rows.append(r)
    c["r"] = rows
    c["r"].sort(key=lambda r: (r[1], r[0]))
# titles that predate the user's lists (needed so star counts match the real totals)
byname["Serie A"]["b"] = {"Genoa": 9, "Pro Vercelli": 7, "Milan AC": 3, "Juventus FC": 2, "FC Internazionale": 2, "Bologna": 2, "Torino": 1, "Casale": 1, "Novese": 1}
# no Eredivisie list was supplied: last seasons + all-time totals before them (PSV 27 after 2025/26)
out.insert(next(i for i, c in enumerate(out) if c["n"] == "Liga Portugal"), {"n": "Eredivisie", "g": "Holanda",
    "r": [["2021/22", 2022, "Ajax", "PSV", ""], ["2022/23", 2023, "Feyenoord", "PSV", ""], ["2023/24", 2024, "PSV", "Feyenoord", ""],
          ["2024/25", 2025, "PSV", "Ajax", ""], ["2025/26", 2026, "PSV", "", ""]],
    "b": {"Ajax": 35, "PSV": 24, "Feyenoord": 15, "HVV": 10, "Sparta Rotterdam": 6, "RAP": 5, "Go Ahead Eagles": 4, "Willem II": 3, "HBS": 3,
          "AZ": 2, "ADO Den Haag": 2, "Heracles Almelo": 2, "RCH": 2, "FC Twente": 1, "NAC Breda": 1, "DWS": 1, "Be Quick": 1, "SC Enschede": 1, "Quick Den Haag": 1}})
for c in out:
    for r in c["r"]:
        if r[3] and r[3] == r[2]: r[3] = ""
json.dump({"v": 1, "c": out}, open(sys.argv[-1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "competitions", sum(len(c["r"]) for c in out), "rows")
