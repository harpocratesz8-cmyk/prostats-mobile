"""Parse the user's hand-made champions lists (leagues + cups TXT) into logos/history.json.
Output: {"v":1, "c":[{"n": name, "g": country, "r": [[season, endYear, champion, runnerUp, score], ...]}]}
Usage: python3 tools/build_history.py tools/history_src/ligas.txt tools/history_src/copas.txt tools/history_src/extra.txt ProStats-Mobile/web/www/logos/history.json
Corrections from the user's reviews live in tools/history_fixes.py."""
import re, sys, json, unicodedata, difflib, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history_fixes as FX

SEASON_HEAD = re.compile(r"^(\d{4}(?:\s*[/\-–]\s*\d{2,4})?|\d{2}/\d{2})\+?(?=[\s:\-]|$)")
LABEL_YEAR = re.compile(r"^([^\t]*?\b(?:19|20)\d{2}(?:/\d{2,4})?\b[^\t]*?)(?:\t+|\s{2,})(.+)$")
SCORE = re.compile(r"(?<![\d/,.])(\d{1,2})\s?[-–]\s?(\d{1,2})(?![\d/])")
# "Rangers   4  Aberdeen   0"  /  "Queen's Park   1:2  Third Lanark   1:0" (replays)  /  "w/o ... dna"
SPACED = re.compile(r"^(?P<a>\S.*?)\s{2,}(?P<ga>\d+(?::\d+)*|w/o)\s{2,}(?P<b>\S.*?)\s{2,}(?P<gb>\d+(?::\d+)*|dna)(?P<note>\s.*)?$")
DATE_VENUE = re.compile(r"^\d{1,2}/\s?\d{1,2}(?:/\d{2})?\s+.*?(?:\t+|\s{2,})")
MONTH_DAY = re.compile(r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}\s+")
FMT = {"Schweizer Cup": "venue", "Trophée des Champions": "venue", "Coppa Itália": "win_ab", "Supercopa de España": "win_ab",
       "Campeón de Campeones": "ab_win", "Super Copa Do Brasil": "ab_win", "Supercoppa": "ab_score", "Svenska Cupen": "ab_score", "KNVB Beker": "ab_score",
       "Liga MX Clausura e Liga MX Apertura": "cols"}
SKIP = re.compile(r"not contested|no winners|not held|n/a|n/p|unofficial war|n[aã]o (contestad|disputad|realizad)|cancel|abandon|suspens|no competition|void|não houve|nao houve|interromp", re.I)
FLAG = re.compile(r"[\U0001F1E6-\U0001F1FF]")

COMP_RENAME = {"League 1": "Ligue 1", "Budesliga": "2. Bundesliga", "Liga MX Clausura e Liga MX Apertura": "Liga MX",
               "Copa Do Brasil": "Copa do Brasil", "Super Copa Do Brasil": "Supercopa do Brasil", "Serie B": "Brasileirão Série B",
               "Serie C": "Brasileirão Série C", "Serie D": "Brasileirão Série D", "Copa Do Nordeste": "Copa do Nordeste",
               "COPA VERDE": "Copa Verde", "SUPERLIGA": "SuperLiga", "Coppa Itália": "Coppa Italia",
               "Supercoppa": "Supercoppa Italiana", "Cupen": "Norwegian Cup (Cupen)", "Copa Sul-americana": "Copa Sul-Americana",
               "Liga Portugal (Portugal)": "Liga Portugal", "UEFA Eurocopa": "UEFA Euro"}

def norm_season(s):
    s = re.sub(r"\s+", "", s).replace("–", "/").replace("-", "/").rstrip("+")
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
    body = re.sub(r"\babd\b\s*", "", body)
    body = re.sub(r"(\d+-\d+)p\b", r"[\1 pen]", body)
    body = re.sub(r"\((\d+-\d+)\s*Pen\)", r"[\1 pen]", body, flags=re.I)
    body = re.sub(r"\(\s*(\d+-\d+)\s*,\s*(\d+-\d+)\s*\)", r"  \1 \2  ", body)
    body = re.sub(r"\(\s*(\d+-\d+)\s*(?:\(\s*(?:Pen\s*)?(\d+-\d+)\s*\))?\s*\)", lambda m: f"  {m[1]}  " + (f"[{m[2]} pen]  " if m[2] else ""), body)  # Copa Argentina
    return body

def winner_of(a, b, w):
    k = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    if k(w) and (k(w) in k(b) or k(b) in k(w)) and not (k(w) in k(a) and len(k(a)) >= len(k(b))): return b, a
    return a, b

def strip_date_venue(body):
    """'25/09/68 Buenos Aires Estudiantes   1-0 ...': the venue column is 13 characters wide"""
    body = body.expandtabs(8)
    m = re.match(r"^\d{1,2}/\s?\d{1,2}/\d{2}\s", body)
    if m:
        rest = body[m.end():]
        if len(rest) > 14 and rest[12] == " " and rest[13] != " ": return rest[13:]
        if len(rest) > 14 and rest[12] == " ": return rest[13:].lstrip()
    return DATE_VENUE.sub("", body)

def parse_match(body):
    """returns (teamA, goalsA, goalsB, teamB, pens, note, score text) or None; '0-0 2-1' two-leg lines are summed"""
    body = strip_date_venue(body.strip())
    sp = SPACED.match(body)
    if sp:
        a, b = clean_team(sp["a"]), clean_team(sp["b"])
        if looks_team(a) and looks_team(b):
            if sp["ga"] == "w/o": return a, 1, 0, b, None, "w/o", "w/o"
            la = [int(x) for x in sp["ga"].split(":")]; lb = [int(x) for x in sp["gb"].split(":")]
            n = min(len(la), len(lb))
            return a, la[n-1], lb[n-1], b, None, sp["note"] or "", ", ".join(f"{x}-{y}" for x, y in zip(la, lb))
    ms = list(SCORE.finditer(body))
    if not ms: return None
    first = ms[0]; a = clean_team(body[:first.start()])
    if not looks_team(a): return None
    # consecutive scores right after the first one belong to the same tie (two legs / agg)
    last = first; ga = int(first[1]); gb = int(first[2]); i = 1
    while i < len(ms) and re.fullmatch(r"\s*", body[last.end():ms[i].start()]):
        ga += int(ms[i][1]); gb += int(ms[i][2]); last = ms[i]; i += 1
    rest = body[last.end():]
    note = rest
    rest = re.split(r"\t+|\s{2,}|\[|\(\s*(?=\d|in\b|as\b|on\b|at\b|after\b|aet|pen)|\bagg\b|\baet\b|\bAET\b", rest.strip())[0]
    b = clean_team(rest)
    if not looks_team(b): return None
    pm = re.search(r"(\d{1,2})\s?[-–]\s?(\d{1,2})\s*(?:pen|p\b)", note, re.I)
    txt = " ".join(f"{x[1]}-{x[2]}" for x in ms[:i]) + (f" ({pm[1]}-{pm[2]} pen)" if pm else "")
    return a, ga, gb, b, (int(pm[1]), int(pm[2])) if pm else None, note, txt

ABBR = [(r"^Indep\.\s*", "Independiente "), (r"^Ind\.\s*", "Independiente "), (r"\bAtl\.\s*", "Atlético "), (r"^Bor\.\s*", "Borussia "), (r"^Est\.\s*", "Estudiantes ")]
def expand(n):
    for a, b in ABBR: n = re.sub(a, b, n)
    return n
def tkey(n):
    n = re.sub(r"\s*\(.*?\)", "", FX.rename(expand(n), None))
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", n.lower()).encode("ascii", "ignore").decode())
def note_winner(note, a, b):
    m = re.search(r"([A-Z][\w .'’-]+?)\s+won\b", note or "")
    if not m: return None
    w = tkey(m[1])
    if w and (w in tkey(a) or tkey(a) in w): return a, b
    if w and (w in tkey(b) or tkey(b) in w): return b, a
    return None
def same_key(x, k):
    """same team written two ways ("Indep. Santa Fe" / "Independiente Santa Fe"), but "Nacional" is not "Internacional" """
    if x == k: return True
    if difflib.SequenceMatcher(None, x, k).ratio() > 0.84: return True
    lo, hi = sorted((x, k), key=len)
    return len(lo) >= 5 and lo in hi and len(lo) / len(hi) >= 0.7

def decide(ms):
    """champion of a season from its match lines: score, then penalties, then an explicit note,
       two legs: points, then aggregate; a third match (play-off / replay) decides on its own"""
    keys = {}
    for m in ms:
        for t in (m[0], m[3]):
            k = tkey(t)
            j = next((x for x in keys if same_key(x, k)), None)
            keys.setdefault(j or k, t)
    def same(t, k): return same_key(tkey(t), k)
    def single(m):
        a, ga, gb, b, pn, note = m[:6]
        if ga != gb: return (a, b) if ga > gb else (b, a)
        if pn and pn[0] != pn[1]: return (a, b) if pn[0] > pn[1] else (b, a)
        return note_winner(note, a, b) or (a, b)
    if len(ms) == 1 or len(keys) != 2: return single(ms[0])
    if len(ms) >= 3: return single(ms[-1])
    (k1, t1), (k2, t2) = list(keys.items())
    pts = {k1: 0, k2: 0}; gl = {k1: 0, k2: 0}
    for a, ga, gb, b, pn, note, *_ in ms:
        ka = k1 if same(a, k1) else k2; kb = k2 if ka == k1 else k1
        gl[ka] += ga; gl[kb] += gb
        if ga > gb: pts[ka] += 2
        elif gb > ga: pts[kb] += 2
        else: pts[ka] += 1; pts[kb] += 1
    if pts[k1] != pts[k2]: return (t1, t2) if pts[k1] > pts[k2] else (t2, t1)
    if gl[k1] != gl[k2]: return (t1, t2) if gl[k1] > gl[k2] else (t2, t1)
    for m in reversed(ms):
        a, ga, gb, b, pn, note = m[:6]
        if pn and pn[0] != pn[1]: return (a, b) if pn[0] > pn[1] else (b, a)
        w = note_winner(note, a, b)
        if w: return w
    return ms[0][0], ms[0][3]

def ab_to_match(body):
    """'A - B   venue   2-1' -> 'A  2-1  B'"""
    m = re.match(r"^(.*?)\s+[-–]\s+(.*)$", body)
    if not m: return body
    a = m[1]; rest = split_cols(m[2]); b = rest[0] if rest else ""
    sc = SCORE.search(m[2]); 
    if not sc: return body
    tail = m[2][sc.end():]
    return f"{a}  {sc[1]}-{sc[2]}  {b}  {tail}"

# competition titles written without ":" in the TXT files
NOCOLON_HEADERS = {"Campeonato Mineiro", "Campeonato Catarinense", "Chinese FA Super Cup", "King's Cup", "Saudi Super Cup", "AIFF Super Cup / Federation Cup", "TFF Süper Kupa"}
# former names of a competition inside its own list: not a new competition
SUBTITLES = {"Head of State's Cup", "President's Cup (Cumhurbaskanligi Kupasi)", "Atatürk Cup", "Super Cup"}
def is_header(line):
    if not line or line[0] in " \t•": return False
    if line.strip() in NOCOLON_HEADERS: return True
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
    comp = None; country = ""; comp_country = ""; mx_base = None; nb_seen = False; seasons = None; cur = None; skip = False; durand_team = None
    pending_head = None
    def flush():
        nonlocal seasons
        fmt = FMT.get(comp)
        if comp and seasons:
            rows = []
            for s in seasons:
                if s.get("matches"):
                    champ, ru = decide(s["matches"])
                    flip = lambda t: re.sub(r"(\d+)-(\d+)", lambda q: f"{q[2]}-{q[1]}", t)
                    score = ", ".join((m[6] if tkey(m[0]) == tkey(champ) else flip(m[6])) for m in s["matches"] if m[6])
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
        if st in SUBTITLES: continue
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
            if name in ("Ligas", "Copas Campeões e Vices"): continue
            m0 = re.match(r"^\W*([A-Za-zÀ-ÿ ]+):\s*\S", FLAG.sub("", line).strip())
            if m0: country = m0[1].strip()          # "🇩🇰 Dinamarca: Danish Cup (Pokalen)"
            flush(); comp = name; comp_country = country; seasons = []; cur = None; skip = False; durand_team = None; mx_base = None; nb_seen = False
            continue
        if seasons is None: continue
        if st.startswith("Nota") or st.startswith("{"): continue
        if st.startswith("NB"):
            skip = True; nb_seen = True; continue
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
        m = re.match(r"^•\s*(.+?)\s*\(\d+\):\s*(\d{4}.*)$", st)
        if m:
            for y, ru in re.findall(r"(\d{4})\s*(?:\(vs\.?\s*([^)]+)\))?", m[2]):
                seasons.append({"season": y, "end": int(y), "champ": clean_team(m[1]), "ru": clean_team(ru or "")})
            continue
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
        if "|" in body:      # "1921–22 | North Winner: X #1 | North Runner-up: Y | ..."  /  "| Champion: X | Runner-up: Y"
            f = {k.strip().lower(): v.strip() for k, v in (p.split(":", 1) for p in body.split("|") if ":" in p)}
            if f.get("champion"): seasons.append({"season": season, "end": end, "champ": clean_team(f["champion"]), "ru": clean_team(f.get("runner-up", ""))})
            for side, lab in (("north", "Norte"), ("south", "Sul")):
                if f.get(f"{side} winner"): seasons.append({"season": f"{season} {lab}", "end": end, "champ": clean_team(f[f"{side} winner"]), "ru": clean_team(f.get(f"{side} runner-up", ""))})
            cur = None; continue
        body = re.sub(r"^\+\s*", "", body)
        if SKIP.search(body) or not body.strip(): cur = None; continue
        tg = re.match(r"^\s*\(([A-Za-zÀ-ÿ .]+)\)\s*", body)
        if tg and not re.search(r"[a-z]", season, re.I): season = f"{season} {tg[1].strip()}"; body = body[tg.end():]
        if nb_seen and any(s["season"] == season for s in seasons) and not re.search(r"[a-z]", season, re.I):
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
BAD = re.compile(r"^w/o$|^dna$|cup withheld|no final|not (played|awarded|finished|disputed)|no (championship|winners)|local leagues|^\??$|^[-–]$|title revoked|n[aã]o disputad", re.I)
def fix_name(n):
    n = re.sub(r"^.*\(now ([^)]+)\).*$", r"\1", n)
    n = re.sub(r"^[DTQ]\s+(?=[A-Z])", "", n)
    n = re.sub(r"^w/o\s+", "", n)
    n = re.sub(r"\s\d+\s*\([^)]*penalt[^)]*\)$", "", n)
    n = re.sub(r"(?<=[A-Za-z.)])\s\d$", "", n)
    n = re.sub(r"^\d+\s*[–-]\s*\d+\s+", "", n)
    n = re.sub(r"\s\d+(:\d+)+$", "", n)
    n = re.sub(r"\s\d+\s+[A-Z].*?\s\d+\b.*$", "", n)
    n = re.sub(r"\s*\((North|South|Group [A-Z])\).*$", "", n)
    n = re.sub(r"\s+\d+ points? behind.*$", "", n)
    n = n.replace('"', "")
    n = re.sub(r"^\([^)]*\)\s*", "", n)
    n = re.sub(r"\s*\((Federal|after|as winner)[^)]*\)", "", n)
    if re.match(r"^\d", n) and not re.match(r"^\d+\.\s?[A-Z]", n): n = ""
    if len(n) > 4 and n.isupper() and "." not in n: n = " ".join(w.capitalize() if len(w) > 3 and w.isalpha() else w for w in n.split())
    return expand(n.strip(" ,;"))
for c in out:
    rows = []
    for r in c["r"]:
        r[2] = fix_name(r[2]); r[3] = fix_name(r[3])
        if BAD.search(r[3]): r[3] = ""
        if not BAD.search(r[2]): rows.append(r)
    c["r"] = rows
out = FX.apply(out)
for c in out:
    for r in c["r"]:
        if r[3] and r[3] == r[2]: r[3] = ""
json.dump({"v": 2, "c": out, "alias": FX.LOGO_ALIAS, "nl": sorted(FX.NO_LOGO), "eq": FX.EQUIV}, open(sys.argv[-1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "competitions", sum(len(c["r"]) for c in out), "rows")
