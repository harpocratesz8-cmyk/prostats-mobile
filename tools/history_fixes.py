"""Corrections applied on top of the parsed TXT lists (tools/build_history.py).
Everything here comes from the user's reviews: club lineages (titles follow the club), names that must
point to a specific logo, seasons the lists got wrong and competitions that need special handling."""
import re, unicodedata

def k(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", str(s).lower().replace("ĳ", "ij")).encode("ascii", "ignore").decode())

COUNTRY = {"alemanha": "Alemanha", "arabiasaudita": "Arábia Saudita", "argentina": "Argentina", "australia": "Austrália", "austria": "Áustria",
           "belgica": "Bélgica", "brasil": "Brasil", "china": "China", "coreiadosul": "Coreia do Sul", "dinamarca": "Dinamarca", "escocia": "Escócia",
           "espanha": "Espanha", "estadosunidos": "Estados Unidos", "franca": "França", "holanda": "Holanda", "india": "Índia", "inglaterra": "Inglaterra",
           "irlanda": "Irlanda", "italia": "Itália", "mexico": "México", "noruega": "Noruega", "polonia": "Polônia", "portugal": "Portugal",
           "romenia": "Romênia", "suecia": "Suécia", "suica": "Suíça", "turquia": "Turquia"}
COMP_COUNTRY = {"A-League": "Austrália", "Durand Cup": "Índia", "King's Cup": "Arábia Saudita"}
INTL = {"Copa do Mundo", "FIFA Intercontinental Cup", "FIFA Club World Cup", "UEFA Champions League", "UEFA Europa League",
        "UEFA Conference League", "UEFA Super Cup", "Copa Libertadores", "Copa Sul-Americana", "Recopa Sul-Americana", "UEFA Euro"}
COMP_NAME = {"Arábia Saudita": "King's Cup", "Danish Cup (Pokalen)": "Danish Cup", "AIFF Super Cup / Federation Cup": "AIFF Super Cup"}

# ---------- names valid in every competition ----------
RENAME_ALL = {
    # Germany
    "Hannoverscher SV 96": "Hannover 96", "Phönix Karlsruhe": "Karlsruher SC", "Braunschweiger TSV Eintracht": "Braunschweig TSV Eintracht",
    "Eintracht Braunschweig": "Braunschweig TSV Eintracht", "1.FC Pforzheim": "1. CfR Pforzheim", "Vorwärts Berlin": "1. FC Frankfurt/Oder",
    "Union Oberschöneweide": "1. FC Union Berlin", "Kieler SV Holstein": "Holstein Kiel", "FV Holstein Kiel": "Holstein Kiel",
    "Viktoria 89 Berlin": "Berliner FC Viktoria 89", "Admira Wien": "FC Admira Wacker", "First Vienna FC": "First Vienna FC 1894", "First Vienna": "First Vienna FC 1894",
    "FC Sankt Pauli": "FC St. Pauli", "FC Homburg/Saar": "FC 08 Homburg", "FC Bayer 05 Uerdingen": "KFC Uerdingen 05", "Bayer 05 Uerdingen": "KFC Uerdingen 05",
    "TSV Bayer 04 Leverkusen": "Bayer 04 Leverkusen", "DSC Arminia Bielefeld": "DSC Arminia Bielefeld", "Tennis Borussia Berlin": "Tennis Borussia Berlin",
    "VfB Leipzig": "1. FC Lokomotive Leipzig", "1. FC Lok Leipzig": "1. FC Lokomotive Leipzig", "1.FC Lok Leipzig": "1. FC Lokomotive Leipzig",
    "Kickers Offenbach": "Offenbach FC Kickers", "Offenbacher FC Kickers": "Offenbach FC Kickers", "1. FC Nuremberg": "1. FC Nürnberg", "FC Nuremberg": "1. FC Nürnberg",
    "1860 Munich": "TSV 1860 München", "Rapid Vienna": "SK Rapid Wien", "Union 92 Berlin": "BFC Union 92 Berlin", "FC Bayern München II": "FC Bayern München II",
    # Austria
    "Austria Salzburg": "RB Salzburg", "Amateure": "FK Austria Wien", "Wiener Amateur-SV": "FK Austria Wien", "Austria": "FK Austria Wien", "Austria Wien": "FK Austria Wien",
    "SC Austria": "FK Austria Wien", "Wacker Innsbruck": "Fußballclub Wacker Innsbruck", "FC Wacker Innsbruck": "Fußballclub Wacker Innsbruck",
    "FC Tirol Innsbruck": "Fußballclub Wacker Innsbruck", "FC Swarovski Tirol": "Fußballclub Wacker Innsbruck", "Admira": "FC Admira Wacker", "Wacker": "FC Admira Wacker",
    "Wacker Wien": "FC Admira Wacker", "FC Admira Wacker Mödling": "FC Admira Wacker", "WAC": "Wiener AC", "Wiener AF": "WAF",
    # Belgium
    "FC Liége": "RFC Liège", "FC Liège": "RFC Liège", "Union": "Union Saint-Gilloise", "Union St-Gilloise": "Union Saint-Gilloise", "Beerschot": "K Beerschot VAC",
    "FC Mechelen": "KV Mechelen", "YRKV Mechelen": "KV Mechelen", "Daring CB": "Daring Club de Bruxelles", "Daring": "Daring Club de Bruxelles", "Racing CB": "Racing Brussel",
    "Racing Gent": "KRC Gent", "Antwerpen": "Antwerp", "Waregem": "KSV Waregem", "La Louvière": "Louvieroise", "Kortrijk": "Kortrijk", "Lierse SK": "Lierse",
    "AA Gent": "Gent", "SK Beveren": "Beveren", "Zulte-Waregem": "S.V. Zulte Waregem", "Anderlecht abd": "Anderlecht",
    # Netherlands
    "H.V.V.": "HVV", "R.A.P.": "RAP", "H.F.C.": "HFC Haarlem", "H.B.S.": "HBS", "Quick (Den Haag)": "Quick Den Haag", "Sparta": "Sparta Rotterdam", "Go Ahead": "Go Ahead Eagles",
    "Be Quick (Groningen)": "Be Quick Groningen", "N.A.C.": "NAC Breda", "R.C.H.": "RCH", "Feijenoord": "Feyenoord", "S.C. Enschede": "SC Enschede", "P.S.V.": "PSV",
    "A.D.O.": "ADO Den Haag", "De Volewijckers": "De Volewijckers", "B.V.V.": "BVV", "S.V.V.": "SVV", "Eindhoven": "EVV Eindhoven", "Rapid J.C.": "Roda JC Kerkrade",
    "D.O.S.": "DOS", "D.W.S.": "DWS", "A.Z. '67": "AZ Alkmaar", "A.Z.": "AZ Alkmaar", "AZ '67": "AZ Alkmaar", "F.C. Twente": "FC Twente", "Heracles": "Heracles Almelo",
    # Romania (Steaua / CCA / FCSB share one history)
    "C.C.A. București": "FCSB", "Steaua București": "FCSB", "Steaua Bucuresti": "FCSB", "F.C.S.B.": "FCSB", "C.F.R. Cluj": "CFR Cluj", "C.F.R. București": "CFR București",
    # Saudi Arabia
    "Al-Nasr": "Al-Nassr", "Al-Ittifaq": "Al-Ettifaq", "Al-Fat'h": "Al-Fateh", "Al-Wahda": "Al-Wehda", "Al-Taawun": "Al-Taawoun", "Al-Faysali": "Al-Faisaly",
    "Faiha'a": "Fayha FC", "Al-Wehda Club": "Al-Wehda",
    # China
    "Shanghai SIPG": "Shanghai Port", "Dalian Wanda": "Dalian Shide", "Dalian Wanda Shide": "Dalian Shide", "Dalian": "Dalian Shide",
    "Beijing Hyundai Cars": "Beijing Guo'an", "Beijing Guoan": "Beijing Guo'an", "Beijing Xuehua": "Beijing Guo'an", "Beijing Guona": "Beijing Guo'an",
    "Liaoning": "Liaoning Hongyun", "Liaoning Tianlun": "Liaoning Whowin", "Tianjin": "Tianjin Jinmen Tiger", "Tianjin Teda": "Tianjin Jinmen Tiger",
    "Jiangsu Sainty": "Jiangsu Suning", "Guangdong": "Guangdong Winnerway", "Guangdong Wanbao": "Guangdong Winnerway", "Guangzhou": "Guangzhou Evergrande",
    "Jinan Taishan": "Shandong Taishan", "Jinan Taishan Jiangjun": "Shandong Taishan", "Shandong Luneng": "Shandong Taishan", "Shandong Luneng Taishan": "Shandong Taishan",
    "Chongqing Longxin": "Chongqing Liangjiang Athletic", "Shanghai Shenhua SVA": "Shanghai Shenhua", "p Guangzhou Evergrande": "Guangzhou Evergrande",
    # South America / others
    "Estudiantes": "Estudiantes de La Plata", "Estudiantes (LP)": "Estudiantes de La Plata", "Estudiantes de L.P.": "Estudiantes de La Plata", "Estudiantes (La Plata)": "Estudiantes de La Plata",
    "Shahtar Donetsk": "Shakhtar Donetsk", "Tigres UANL": "Club Tigres U.A.N.L.", "UANL": "Club Tigres U.A.N.L.", "U.A.N.L.": "Club Tigres U.A.N.L.",
    "Zenit": "Zenit St. Petersburg", "Zenit St.Peterburg": "Zenit St. Petersburg", "Girondins Bordeaux": "Bordeaux", "Girondins de Bordeaux": "Bordeaux",
    "America (Cali)": "América de Cali", "América (Cali)": "América de Cali", "América Cali": "América de Cali", "Atlético Nacional Medellín": "Atlético Nacional S.A.",
    "Atlético Nacional": "Atlético Nacional S.A.", "LDU": "LDU de Quito", "LDU (Quito)": "LDU de Quito", "Olimpia Asunción": "Olimpia",
    "Nacional (Asunción)": "Club Nacional (Paraguai)", "Independiente Santa Fe": "Independiente Santa Fe", "Junior (Barranquilla)": "Junior Barranquilla",
    "Crvena zvezda Beograd": "Crvena zvezda", "CSKA Moskva": "CSKA Moscow", "Wolverhampton Wand": "Wolverhampton Wanderers", "Eintracht Frankft.": "Eintracht Frankfurt",
    "Borussia MG": "Borussia Mönchengladbach", "Paris St-Germain": "Paris Saint-Germain", "Paris St.Germain": "Paris Saint-Germain", "PSG": "Paris Saint-Germain",
    "Olympique Lyon": "Olympique Lyonnais", "Español": "RCD Espanyol", "RCD Español": "RCD Espanyol", "Machester City": "Manchester City",
    "Dnipro Dnipropetrovsk": "Dnipro Dnipropetrovsk", "Atlético-PR": "Athletico Paranaense", "Athletico-PR": "Athletico Paranaense", "Clube Atlético Paranaense": "Athletico Paranaense", "Atlético Paranaense": "Athletico Paranaense", "Borussia M'gladbach": "Borussia Mönchengladbach",
    "Tigre": "Club Atlético Tigre", "Atlanta": "Club Atlético Atlanta", "Gimnasia": "Club de Gimnasia y Esgrima La Plata", "Gimnasia (LP)": "Club de Gimnasia y Esgrima La Plata",
    "Talleres (C)": "Club Atlético Talleres de Córdoba", "Talleres": "Club Atlético Talleres de Córdoba", "CA Talleres (Córdoba)": "Club Atlético Talleres de Córdoba",
    "Central Córdoba": "Club Central Córdoba de Santiago del Estero", "CA Central Córdoba (Santiago del Estero)": "Club Central Córdoba de Santiago del Estero",
    "CA Central Córdoba": "Club Central Córdoba de Santiago del Estero", "CA Patronato Juventud Católica": "Patronato", "Arsenal de Sarandi": "Arsenal de Sarandí",
    # Brazil: official long names in the national lists -> the names the logos use
    "Esporte Clube Bahia": "Bahia", "Sociedade Esportiva Palmeiras": "Palmeiras", "Botafogo de Futebol e Regatas": "Botafogo", "Cruzeiro Esporte Clube": "Cruzeiro",
    "Clube Náutico Capibaribe": "Náutico", "São Paulo Futebol Clube": "São Paulo", "Sport Club Internacional": "Internacional", "Grêmio Foot-ball Portoalegrense": "Grêmio",
    "Grêmio FBPA": "Grêmio", "Bangu Atlético Clube": "Bangu", "Clube Atlético Bragantino": "Bragantino", "CA Bragantino": "Bragantino", "Esporte Clube Vitória": "Vitória",
    "Associação Portuguesa de Desportos": "Portuguesa", "Etti Jundiaí Futebol Ltda.": "Paulista", "ABC Futebol Clube": "ABC FC", "Oeste Futebol Clube": "Osasco Sporting",
    "Santa Cruz Futebol Clube": "Santa Cruz", "Esporte Clube XV de Novembro": "XV de Piracicaba", "Retrô Futebol Clube Brasil": "Retrô",
    "Ferroviário Atlético Clube": "Ferroviário", "Tupi Foot Ball Club": "Tupi Football Club", "SE Gama": "SE Gama", "America-RJ": "América Football Club",
    "SC Internacional-SP": "Internacional-SP", "Paulistano-SP": "Paulistano", "AA das Palmeiras": "AA Palmeiras", "Palestra Itália": "Palmeiras",
    "Fiorentino": "Clube Atlético Juventus", "Americano-RS": "Club Americano-RS", "Farroupilha": "Grêmio Atlético Farroupilha", "Internacional-PR": "International Foot-Ball Club",
    "Atlético (Alagoinhas)": "Atlético de Alagoinhas", "Atlético FC": "Atlético Futebol Clube", "Guarany": "Associação Desportiva Guarany",
    "Colo Colo (Ilhéus)": "Colo Colo de Futebol e Regatas", "Guarany Sport Club": "Guarany de Sobral",
}
# keyed by the full name including "(city)" when the same club name exists in several states
RENAME_FULL = {
    "América Futebol Clube (Belo Horizonte)": "América Mineiro", "América Futebol Clube (Natal-RN)": "América-RN",
    "Botafogo Futebol Clube (João Pessoa-PB)": "Botafogo PB", "Botafogo Futebol Clube (Ribeirão Preto-SP)": "Botafogo SP",
    "Guarany Sport Club (Sobral-CE)": "Guarany de Sobral", "SE Gama (Gama, DF)": "SE Gama",
}
RENAME_COMP = {
    "Copa Libertadores": {"Barcelona": "Barcelona SC", "América": "América de Cali"},
    "Recopa Sul-Americana": {"Arsenal": "Arsenal de Sarandí"},
    "Copa Sul-Americana": {"Arsenal": "Arsenal de Sarandí", "América (Cd. México)": "Club de Fútbol América"},
    "Supercopa Argentina": {"Arsenal FC": "Arsenal de Sarandí", "CA Boca Juniors": "Boca Juniors", "CA River Plate": "River Plate"},
    "Supercopa Internacional (Argentina)": {"CA Boca Juniors": "Boca Juniors", "CA River Plate": "River Plate"},
    "Campeonato Gaúcho": {"Cruzeiro": "Cruzeiro-RS", "São Paulo-RS": "Sport Club São Paulo (RS)", "São Paulo": "Sport Club São Paulo (RS)", "Pelotas": "EC Pelotas", "Bagé": "GE Bagé"},
    "Campeonato Baiano": {"Botafogo": "Botafogo-BA", "Fluminense": "Fluminense-BA", "Ypiranga": "Ypiranga-BA", "Ypiranga(Salvador)": "Ypiranga-BA", "Sport Bahia": "Sport Bahia", "Internacional": "Internacional-BA", "São Paulo": "São Paulo-BA", "Atlético": "Atlético de Alagoinhas", "Colo Colo": "Colo Colo de Futebol e Regatas"},
    "Campeonato Paranaense": {"Ferroviário-PR": "Ferroviário (PR)", "Colorado": "Colorado EC"},
    "ÖFB Cup": {"SV Pasching 16": "FC Juniors OÖ", "FC Pasching": "FC Juniors OÖ"},
    "Österreichische Fußball-Bundesliga": {"LASK Linz": "LASK"},
}
# names that exist in the logo database for a DIFFERENT club: shown with initials instead of a wrong crest
NO_LOGO = {"Botafogo-BA", "Fluminense-BA", "Ypiranga-BA", "Paysandu-RJ", "Caxias-SC", "América-SC", "América-CE", "América-PE", "São Paulo Athletic", "BFC Union 92 Berlin", "FC Bayern München II", "1. FC Frankfurt/Oder", "KRC Gent", "Germinal Ekeren", "EVV Eindhoven", "Club Nacional (Paraguai)",
           "Barcelona SC", "Sport Club São Paulo (RS)", "EC Pelotas", "GE Bagé", "Ferroviário (PR)", "SE Gama", "Colo Colo de Futebol e Regatas", "Guarany de Sobral",
           "Racing Mechelen", "CFR București", "FC 08 Homburg", "Union Luxembourg", "Sport Bahia", "Chongqing Liangjiang Athletic", "Liaoning Bird", "Qingdao Beilaite",
           "Liaoning Fushun", "Chongqing Lifan", "São Raimundo Esporte Clube"}
# different database entries of the same club (titles add up, one crest)
EQUIV = [["Boca Juniors", "Club Atlético Boca Juniors"], ["Estudiantes de La Plata", "Club Estudiantes de La Plata"], ["Fayha FC", "Al-Fayha Club"],
         ["Club Atlético River Plate", "River Plate"]]
LOGO_ALIAS = {}

# ---------- season corrections ----------
# (competition, season) -> champion, runner-up   (None = keep)
SET = {
    ("Copa Sul-Americana", "2007"): ("Arsenal de Sarandí", "Club de Fútbol América"),
    ("Copa Sul-Americana", "2012"): ("São Paulo", "Club Atlético Tigre"),
    ("Recopa Sul-Americana", "2007"): ("Arsenal de Sarandí", "Boca Juniors"),
    ("Chinese FA Cup", "1991"): ("Shanghai Shenhua", "Guangzhou Evergrande"),
    ("Croky Cup", "1912"): ("Racing Brussel", None),
    ("Croky Cup", "1935"): ("Daring Club de Bruxelles", None),
    ("Croky Cup", "1974"): ("KSV Waregem", None),
    ("Croky Cup", "1997"): ("Germinal Ekeren", None),
    ("Croky Cup", "1971"): ("K Beerschot VAC", None),
    ("Croky Cup", "1979"): ("K Beerschot VAC", None),
}
ADD = {
    "Copa Sul-Americana": [["2012", 2012, "São Paulo", "Club Atlético Tigre", ""], ["2016", 2016, "Chapecoense", "Atlético Nacional S.A.", ""]],
    "Bundesliga": [["1893/94", 1894, "Berliner FC Viktoria 89", "", ""]],
    "Campeonato Paranaense": [["2002", 2002, "Athletico Paranaense", "", ""]],
    "Campeonato Paulista": [["1933", 1933, "Albion", "", ""], ["1934", 1934, "Clube Atlético Juventus", "", ""]],
}
DROP = {("Croky Cup", "1908"), ("Croky Cup", "1909")}
# two champions per season written as "A, B" in the Brazilian state lists
SPLIT_COMPS = re.compile(r"^Campeonato ")
# 2. Bundesliga with North / South groups: the "runner-up" column is the other group's champion
TWO_GROUPS = {"2. Bundesliga": {"1974/75", "1975/76", "1976/77", "1977/78", "1978/79", "1979/80", "1980/81", "1991/92"}}
# Recopa Sul-Americana: the list uses the year of the qualifying titles, the final is played the next year
SHIFT_YEAR = {"Recopa Sul-Americana": 1}
# titles that predate the lists (so star counts match the real totals)
BASE = {"Serie A": {"Genoa": 9, "Pro Vercelli": 7, "Milan AC": 3, "Juventus FC": 2, "FC Internazionale": 2, "Bologna": 2, "Torino": 1, "Casale": 1, "Novese": 1}}

def rename(n, comp):
    if not n: return n
    n = n.replace("ĳ", "ij").replace("Ĳ", "IJ")
    base = re.sub(r"\s*\([^)]*\)\s*$", "", n).strip()
    if n in RENAME_FULL: return RENAME_FULL[n]
    cm = RENAME_COMP.get(comp, {})
    for cand in (n, base):
        if cand in cm: return cm[cand]
    for cand in (n, base):
        if cand in RENAME_ALL: return RENAME_ALL[cand]
    if re.match(r"^CA\s+[A-Z]", n) and comp and "Argentin" in comp: return n[3:]
    return n

ARG_TAGS = ["Apertura", "Clausura", "Metropolitano", "Nacional", "Inicial", "Final", "Transición", "Copa de Honor", "Copa Campeonato", "Copa de Oro", "Tabla Anual", "Superliga"]
def arg_label(lb):
    m = re.search(r"\b((?:19|20)\d{2})(/\d{2,4})?\b", lb)
    if not m: return lb
    y = m[1] + (("/" + m[2][1:][-2:]) if m[2] else "")
    tag = next((t for t in ARG_TAGS if t.lower() in lb.lower()), "")
    return f"{y} {tag}".strip()

def apply(out):
    for c in out:
        c["n"] = COMP_NAME.get(c["n"], c["n"])
        g = COUNTRY.get(k(c["g"]), c["g"])
        c["g"] = "" if c["n"] in INTL else COMP_COUNTRY.get(c["n"], g)
    by = {c["n"]: c for c in out}
    # the Danish 2004/05+ champions were pasted at the end of the Scottish list
    sc, dk = by.get("Scottish Premiership"), by.get("3F Superliga")
    if sc and dk:
        mv = [r for r in sc["r"] if "/" in r[0]]; sc["r"] = [r for r in sc["r"] if "/" not in r[0]]; dk["r"].extend(mv)
    for c in out:
        n = c["n"]; rows = []
        for r in c["r"]:
            r[2] = rename(r[2], n); r[3] = rename(r[3], n)
            if n in TWO_GROUPS and r[0] in TWO_GROUPS[n] and r[3]:
                rows.append([r[0] + " Norte", r[1], r[2], "", ""]); rows.append([r[0] + " Sul", r[1], r[3], "", ""]); continue
            if SPLIT_COMPS.match(n) and "," in r[2]:
                for part in [p.strip() for p in r[2].split(",") if p.strip()]: rows.append([r[0], r[1], rename(part, n), "", ""])
                continue
            if (n, r[0]) in DROP: continue
            fx = SET.get((n, r[0]))
            if fx:
                if fx[0]: r[2] = fx[0]
                if fx[1] is not None: r[3] = fx[1]
            rows.append(r)
        if n in SHIFT_YEAR:
            for r in rows:
                m = re.match(r"^(\d{4})(.*)$", r[0])
                if m: r[0] = str(int(m[1]) + SHIFT_YEAR[n]) + m[2]; r[1] += SHIFT_YEAR[n]
        have = {(r[0], k(r[2])) for r in rows}
        for a in ADD.get(n, []):
            seasons = {r[0] for r in rows}
            if (a[0], k(a[2])) in have: continue
            if a[0] in seasons and n in ("Copa Sul-Americana", "King's Cup"): rows = [r for r in rows if r[0] != a[0]]
            rows.append(list(a))
        # same season + same champion twice (lists that repeat a season) -> once
        seen = set(); uniq = []
        for r in rows:
            key = (r[0], k(r[2]))
            if key in seen: continue
            seen.add(key); uniq.append(r)
        c["r"] = sorted(uniq, key=lambda r: (r[1], r[0]))
        if n in BASE: c["b"] = BASE[n]
        if re.match(r"^(Campeonato |Copa do Nordeste|Copa Verde|Supercopa do Brasil)", n): c["em"] = 5   # state leagues end by May
        if n == "Liga Profesional de Fútbol":
            for r in c["r"]: r[0] = arg_label(r[0])
    return out
