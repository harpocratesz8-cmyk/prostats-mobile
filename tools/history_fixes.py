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


# ======================= review round 2 =======================
RENAME_ALL.update({
    "1. FC Frankfurt/Oder": "1. FC Frankfurt", "Vorwärts Berlin": "1. FC Frankfurt", "FC Homburg/Saar": "FC 08 Homburg",
    # Korea (current club names / logos)
    "Daewoo Royals": "Busan IPark", "Pusan Daewoo Royals": "Busan IPark", "Busan Icons": "Busan IPark", "Busan I'Park": "Busan IPark",
    "Lucky-Goldstar Hwangso": "FC Seoul", "Anyang LG Cheetahs": "FC Seoul", "POSCO Atoms": "FC Pohang Steelers", "Pohang Steelers": "FC Pohang Steelers",
    "Yukong Elephants": "Jeju SK FC", "Bucheon SK": "Jeju SK FC", "Ulsan Hyundai Horang-i": "Ulsan HD FC", "Ulsan HD": "Ulsan HD FC",
    "Chunan Ilhwa Chunma": "Seongnam FC", "Ilhwa Chunma": "Seongnam FC", "Seongnam Ilhwa Chunma": "Seongnam FC", "Songnam Ilhwa Chunma": "Seongnam FC",
    "Seongnam Ulhwa Chunma": "Seongnam FC", "Songnam Ulhwa Chunma": "Seongnam FC", "Chonbuk Hyundai Dinos": "Jeonbuk Hyundai Motors FC",
    "Chonbuk Hyundai Motors": "Jeonbuk Hyundai Motors FC", "Jeonbuk Hyundai Motors": "Jeonbuk Hyundai Motors FC", "Suwon S. Bluewings": "Suwon Samsung Bluewings",
    "Chunnam Dragons": "Jeonnam Dragons", "Taejon Citizen": "Daejeon Hana Citizen FC",
    # Denmark / Bahia: AaB (Aalborg) is not AAB (Associação Atlética da Bahia)
    "AAB": "AAB-BA",
    # Scotland
    "Dumbarton & Rangers": "Dumbarton", "Inverness Caled. Thistle": "Inverness Caled.Thistle", "Inverness Caledonian Thistle": "Inverness Caled.Thistle",
    "Hamilton Academicals": "Hamilton Academical", "Queen Of The South": "Queen of the South", "Vale Of Leven": "Vale of Leven",
    # Spain
    "Hércules FC": "Hércules CF", "Real Murcia FC": "Real Murcia CF", "Castilla CF": "Real Madrid Castilla C.F.", "Racing de Irún": "Real Unión Club",
    "Real Unión de Irún": "Real Unión Club", "Ciclista de San Sebastián": "Real Sociedad de Fútbol", "Vigo Sporting": "R.C. Celta de Vigo",
    "Recreativo de Huelva": "RC Recreativo de Huelva", "RC Deportivo": "R.C. Deportivo de A Coruña", "RC Deportivo de La Coruña": "R.C. Deportivo de A Coruña",
    "Centro de Deportes Sabadell": "Centro de Deportes Sabadell", "Gimnastica de Madrid": "Gimnástica de Madrid",
    # USA
    "St. Louis Busch Seniors": "St. Louis Scott Gallagher",
    # France
    "Olympique de Lyon": "Olympique Lyonnais", "Lille Olympique Sporting Club": "LOSC Lille", "Lille OSC": "LOSC Lille", "LOSC Lille Métropole": "LOSC Lille", "Lille": "LOSC Lille",
    "Olympique Gymnaste Club de Nice": "OGC Nice", "Nice": "OGC Nice", "Racing Club de Lens": "RC Lens", "Racing Club Lensois": "RC Lens", "Lens": "RC Lens",
    "Racing Club de Strasbourg": "Strasbourg", "Racing Club de Strasbourg Alsace": "Strasbourg", "RC Strasbourg": "Strasbourg",
    "Association de la Jeunesse Auxerroise": "AJ Auxerre", "AJ Auxerroise": "AJ Auxerre", "Auxerre": "AJ Auxerre",
    "Montpellier H.S.C.": "Montpellier", "Montpellier-Hérault FC": "Montpellier", "Montpellier-Hérault SC": "Montpellier", "Montpellier Paillade Sport Club": "Montpellier",
    "Stade Olympique Montpelliérain": "Montpellier", "Sp. Ol. Montpelliérrains": "Montpellier", "Sports Ol. Montpelliérains": "Montpellier",
    "Le Havre Athletic Club": "Le Havre AC", "Havre Athletic Club": "Le Havre AC", "Le Havre": "Le Havre AC",
    "Sporting Club de Bastia": "SC Bastia", "Sporting Étoile Club Bastia": "SC Bastia", "SEC Bastia": "SC Bastia", "Bastia": "SC Bastia",
    "Association Sportive Nancy Lorraine": "AS Nancy Lorraine", "AS Nancy-Lorraine": "AS Nancy Lorraine",
    "FC Cette": "Football Club de Sète", "FC Sète": "Football Club de Sète", "FC Sochaux-Montbéliard": "Football Club de Sochaux-Montbeliard",
    "Football Club de Sochaux-Montbéliard": "Football Club de Sochaux-Montbeliard", "Football Club Sochaux-Montbéliard": "Football Club de Sochaux-Montbeliard", "Sochaux": "Football Club de Sochaux-Montbeliard",
    "Stade Malherbe Caen Calvados Basse-Normandie": "Stade Malherbe Caen", "Angers Sporting Club de l'Ouest": "Angers SCO", "SCO Angers": "Angers SCO",
    "Gazélec Football Club Ajaccio": "Gazélec Ajaccio", "Espérance Sportive Troyes Aube Champagne": "ESTAC Troyes", "AS Troyes": "ESTAC Troyes",
    "CA des Sports Généraux": "CASG Paris", "CA de la Soc. Générale": "CASG Paris", "FC Lorient Bretagne Sud": "FC Lorient", "Football Club Lorient": "FC Lorient", "Lorient": "FC Lorient",
    "FC Rouen": "Football Club Rouennais", "Football Club Rouen": "Football Club Rouennais", "Rouen": "Football Club Rouennais", "Racing Club de France": "Racing Club de Paris",
    "Red Star Olympique": "Red Star FC", "Red Star Olympique Audonien": "Red Star FC", "Red Star Amical Club": "Red Star FC", "Red Star Olympique Aud.": "Red Star FC",
    "Paris Saint-Germain Football Club": "Paris Saint-Germain", "Paris Saint-Germain FC": "Paris Saint-Germain",
    "Girondins A.S.P. de Bordeaux": "Bordeaux", "Girondins de Bordeaux F.C.": "Bordeaux", "Girondins de Bordeaux FC": "Bordeaux", "Girondins A.S.P.": "Bordeaux",
    "Stade Rennais UC": "Stade Rennais FC", "Stade Rennais Université Club": "Stade Rennais FC", "Stade Rennais Football Club": "Stade Rennais FC", "Stade Rennais": "Stade Rennais FC", "Rennes": "Stade Rennais FC",
    "Association Sportive de Monaco": "AS Monaco", "Association Sportive de Monaco Football": "AS Monaco", "Association Sportive de Monaco Football Club": "AS Monaco", "Monaco": "AS Monaco",
    "Association Sportive de Saint-Étienne": "AS Saint-Étienne", "Association Sportive de Saint-Étienne Loire": "AS Saint-Étienne",
    "Association Sportive de Saint-Étienne de Loire": "AS Saint-Étienne", "AS Saint-Etienne": "AS Saint-Étienne", "Saint-Etienne": "AS Saint-Étienne",
    "Football Club de Nantes": "FC Nantes", "Nantes": "FC Nantes", "CS Metz": "FC Metz", "Football Club de Metz": "FC Metz", "Football Club Tours": "Tours FC",
    "Nīmes Olympique": "Nîmes Olympique", "Nîmes": "Nîmes Olympique", "Stade Franēais": "Stade Français", "La Berrichonne de Chāteauroux": "La Berrichonne de Châteauroux",
    "La Berrichonne Châteauroux": "La Berrichonne de Châteauroux", "Évian Thonon Gaillard Football Club": "Evian Thonon Gaillard Football Club",
    "Evian-Thonon Gaillard FC": "Evian Thonon Gaillard Football Club", "Union Sportive Valenciennes-Anzin": "Valenciennes Football Club",
    "Union Sportive Valenciennes-Anzin Arrondissement": "Valenciennes Football Club", "US Valenciennes-Anzin": "Valenciennes Football Club",
    "Union Athlétique Sedan-Torcy": "UA Sedan-Torcy", "Reims": "Stade de Reims", "Marseille": "Olympique de Marseille", "Olympique Marseille": "Olympique de Marseille",
    "Strasbourg": "Strasbourg", "Bordeaux": "Bordeaux", "Toulouse": "Toulouse FC",
    # Netherlands
    "Quick (Den Haag)": "Quick Den Haag", "Haarlem": "HFC Haarlem", "N.E.C.": "N.E.C. Nijmegen", "N.E.C": "N.E.C. Nijmegen", "Roda JC Kerkrade": "Roda J.C.", "Rapid J.C.": "Roda J.C.",
    # Brazil
    "Paysandu-RJ": "Paissandu-RJ", "Ferroviário (PR)": "Ferroviário-PR", "Ferroviário-PR": "Ferroviário-PR", "Sport Club São Paulo (RS)": "Sport Club São Paulo",
    "AAB (Salvador)": "AAB-BA", "OB": "Odense Boldklub", "Atlético Aviación": "Club Atlético de Madrid",
})
RENAME_COMP.update({
    "Copa Libertadores": {"Barcelona": "Barcelona SC", "América": "América de Cali", "Nacional": "Club Nacional de Football"},
    "FIFA Intercontinental Cup": {"Nacional": "Club Nacional de Football"},
    "U.S. Open Cup": {"Vasco da Gama": "Bridgeport Vasco de Gama", "Eintracht Frankfurt": "SC Eintracht", "Eintracht": "SC Eintracht"},
    "Campeonato Cearense": {"Tramways": "Tramways-CE"},
    "Campeonato Pernambucano": {"Tramways": "Transways-PE"},
    "Campeonato Paranaense": {"Ferroviário-PR": "Ferroviário-PR", "Ferroviário": "Ferroviário-PR", "Colorado": "Colorado EC"},
    "Campeonato Gaúcho": {"Cruzeiro": "Cruzeiro-RS", "São Paulo-RS": "Sport Club São Paulo", "São Paulo": "Sport Club São Paulo", "Pelotas": "EC Pelotas", "Bagé": "GE Bagé"},
    "Liga Profesional de Fútbol": {"Arsenal": "Arsenal de Sarandí"}, "Copa Argentina": {"Arsenal": "Arsenal de Sarandí"},
    "Trofeo de Campeones Superliga": {"Arsenal": "Arsenal de Sarandí"},
    "Supercopa Argentina": {"Arsenal FC": "Arsenal de Sarandí", "Arsenal": "Arsenal de Sarandí", "CA Boca Juniors": "Boca Juniors", "CA River Plate": "River Plate"},
    "KNVB Beker": {"Quick (Den Haag) 2": "Quick Den Haag"},
})
# with a logo of their own now (exact names still win over this list)
NO_LOGO -= {"1. FC Frankfurt/Oder", "Club Nacional (Paraguai)"}
RENAME_ALL["Nacional (Asunción)"] = "Club Nacional"
SET.update({
    ("KNVB Beker", "1982"): ("AZ Alkmaar", "F.C. Utrecht", ""),
    ("Coupe de France", "1944"): ("Équipe Fédérale Nancy-Lorraine", "Équipe Fédérale Reims-Champagne"),
    ("Coupe de France", "1957"): ("Toulouse Football Club", None),
    ("Ligue 2 BKT", "1952/53"): ("Toulouse Football Club", None),
    ("U.S. Open Cup", "1955"): ("SC Eintracht", None),
    ("Campeonato Catarinense", "1956"): ("Operário-SC", None),
})
ADD.update({
    "Copa del Rey": [["1904", 1904, "Athletic de Bilbao", "", "w/o"], ["2020", 2020, "Real Sociedad de Fútbol", "Athletic de Bilbao", "1-0"]],
    "Campeonato Carioca": [["1937", 1937, "São Cristóvão", "", ""], ["1979 Especial", 1979, "Flamengo", "", ""]],
    "Campeonato Catarinense": [["1926", 1926, "Avaí", "", ""], ["1983", 1983, "Joinville", "", ""], ["2024", 2024, "Criciúma", "", ""]],
    "Scottish Premiership": [["1891", 1891, "Rangers", "", ""]],
})
DROP |= {("Ligue 1", s) for s in ("1939/40", "1940/41", "1941/42", "1942/43", "1943/44", "1944/45")}
def _rows(lst):
    out = []
    for lab, ch, ru in lst:
        m = re.match(r"^(\d{4})(?:/(\d{2}))?", lab); y = int(m[1]) + (1 if m[2] else 0)
        out.append([lab, y, ch, ru, ""])
    return out
# whole seasons rewritten from the user's lists: competition -> {season: [(label, champion, runner-up), ...]}
REPLACE = {
    "Campeonato Baiano": {"1938": [("1938", "Botafogo-BA", ""), ("1938", "Bahia", "")], "1999": [("1999", "Vitória", "Esporte Clube Poções"), ("1999", "Bahia", "Esporte Clube Poções")]},
    "Campeonato Gaúcho": {"1918": [("1918", "GE Brasil", ""), ("1918", "Cruzeiro-RS", ""), ("1918", "14 de Julho", "")]},
    "Ligue 2 BKT": {"1933/34": [("1933/34 Nord", "Red Star FC", ""), ("1933/34 Sud", "Olympique Alèsien", "")], "1938/39": [("1938/39", "Red Star FC", "")],
                    "1945/46": [("1945/46 Nord", "FC Nancy", ""), ("1945/46 Sud", "Montpellier", "")], "1952/53": [("1952/53", "Toulouse Football Club", "")]},
    "LaLiga Hypermotion": {},
}
for lab, ch in [("1970/71", "Paris Saint-Germain"), ("1971/72", "Valenciennes Football Club"), ("1972/73", "RC Lens"), ("1973/74", "LOSC Lille"), ("1974/75", "AS Nancy Lorraine"),
                ("1975/76", "Angers SCO"), ("1976/77", "Strasbourg"), ("1977/78", "LOSC Lille"), ("1978/79", "Football Club de Gueugnon"), ("1979/80", "AJ Auxerre"),
                ("1980/81", "Stade Brestois 29"), ("1981/82", "Toulouse FC"), ("1982/83", "Stade Rennais FC"), ("1983/84", "Tours FC"), ("1984/85", "Le Havre AC"),
                ("1985/86", "Racing Club de Paris"), ("1986/87", "Montpellier"), ("1987/88", "Strasbourg"), ("1988/89", "Olympique Lyonnais"), ("1989/90", "AS Nancy Lorraine"),
                ("1990/91", "Le Havre AC"), ("1991/92", "Bordeaux"), ("1992/93", "Football Club de Martigues")]:
    REPLACE["Ligue 2 BKT"][lab] = [(lab, ch, "")]
for lab, a, b in [("1949/50", "Real Racing Club de Santander", "CD Alcoyano"), ("1950/51", "Real Gijón", "Club Atlético Tetuán"), ("1951/52", "Real Oviedo", "CD Málaga"),
                  ("1952/53", "Club Atlético Osasuna", "Real Jaén CF"), ("1953/54", "CD Alavés", "UD Las Palmas"), ("1954/55", "Cultural y Deportiva Leonesa", "Real Murcia CF"),
                  ("1955/56", "Club Atlético Osasuna", "Real Jaén CF"), ("1956/57", "Real Gijón", "Granada CF"), ("1957/58", "Real Oviedo", "Real Betis Balompié"),
                  ("1958/59", "Real Valladolid Deportivo", "Elche CF"), ("1959/60", "Real Racing Club de Santander", "RCD Mallorca"), ("1960/61", "Club Atlético Osasuna", "CD Tenerife"),
                  ("1961/62", "R.C. Deportivo de A Coruña", "Córdoba CF"), ("1962/63", "Pontevedra CF", "Real Murcia CF"), ("1963/64", "R.C. Deportivo de A Coruña", "UD Las Palmas"),
                  ("1964/65", "Pontevedra CF", "RCD Mallorca"), ("1965/66", "R.C. Deportivo de A Coruña", "Hércules CF"), ("1966/67", "Real Sociedad de Fútbol", "CD Málaga"),
                  ("1967/68", "R.C. Deportivo de A Coruña", "Granada CF")]:
    REPLACE["LaLiga Hypermotion"][lab] = [(lab + " Grupo 1", a, ""), (lab + " Grupo 2", b, "")]
SAUDI = [("1957/58", "Al-Wehda"), ("1958/59", "Al-Ittihad"), ("1959/60", "Al-Ittihad"), ("1960/61", "Al-Ittihad"), ("1961/62", "Al-Hilal"), ("1962/63", "Al-Ahli"),
         ("1963/64", "Al-Ittihad"), ("1964/65", "Al-Hilal"), ("1965/66", "Al-Ahli"), ("1968/69", "Al-Ahli"), ("1970/71", "Al-Ahli"), ("1971/72", "Al-Ahli"),
         ("1972/73", "Al-Ahli"), ("1973/74", "Al-Nassr"), ("1974/75", "Al-Nassr")]
REPLACE["Roshn Saudi League"] = {lab: [(lab, ch, "")] for lab, ch in SAUDI}
DENMARK = [("1912/13", "KB"), ("1913/14", "KB"), ("1915/16", "B 93"), ("1916/17", "KB"), ("1917/18", "KB"), ("1918/19", "AB"), ("1919/20", "B 1903"), ("1920/21", "AB"),
           ("1921/22", "KB"), ("1922/23", "BK Frem"), ("1923/24", "B 1903"), ("1924/25", "KB"), ("1925/26", "B 1903"), ("1926/27", "B 93")]
REPLACE["3F Superliga"] = {lab: [(lab, ch, "")] for lab, ch in DENMARK}
ARG_OLD = [("1891", "Saint Andrew's"), ("1893", "Lomas Athletic"), ("1894", "Lomas Athletic"), ("1895", "Lomas Athletic"), ("1896", "Lomas Athletic"), ("1897", "Lomas Athletic"),
           ("1898", "Lomas Athletic"), ("1899", "Belgrano Athletic"), ("1900", "Alumni"), ("1901", "Alumni"), ("1902", "Alumni"), ("1903", "Alumni"), ("1904", "Belgrano Athletic"),
           ("1905", "Alumni"), ("1906", "Alumni"), ("1907", "Alumni"), ("1908", "Belgrano Athletic"), ("1909", "Alumni"), ("1910", "Alumni"), ("1911", "Alumni"),
           ("1912 AAF", "Quilmes Atlético Club"), ("1912 FAF", "Porteño"), ("1913 AAF", "Racing Club"), ("1913 FAF", "Estudiantes de La Plata"), ("1914 AAF", "Racing Club"),
           ("1914 FAF", "Porteño"), ("1915", "Racing Club"), ("1916", "Racing Club"), ("1917", "Racing Club"), ("1918", "Racing Club"), ("1919 AAF", "Boca Juniors"),
           ("1919 AAmF", "Racing Club"), ("1920 AAF", "Boca Juniors"), ("1920 AAmF", "River Plate"), ("1921 AAF", "Club Atlético Huracán"), ("1921 AAmF", "Racing Club"),
           ("1922 AAF", "Club Atlético Huracán"), ("1922 AAmF", "Club Atlético Independiente"), ("1923 AAF", "Boca Juniors"), ("1923 AAmF", "San Lorenzo de Almagro"),
           ("1924 AAF", "Boca Juniors"), ("1924 AAmF", "San Lorenzo de Almagro"), ("1925 AAF", "Club Atlético Huracán"), ("1925 AAmF", "Racing Club"), ("1926 AAF", "Boca Juniors"),
           ("1926 AAmF", "Club Atlético Independiente"), ("1927", "San Lorenzo de Almagro"), ("1928", "Club Atlético Huracán"), ("1929", "Club de Gimnasia y Esgrima La Plata"),
           ("1930", "Boca Juniors")]
REPLACE["Liga Profesional de Fútbol"] = {}
for lab, ch in ARG_OLD: REPLACE["Liga Profesional de Fútbol"].setdefault(lab.split()[0], []).append((lab, ch, ""))

# Serie A before the single-table era (the TXT list starts in 1929/30); 1926/27 Torino was revoked
SERIE_A_OLD = [("1898", "Genoa C.F.C."), ("1899", "Genoa C.F.C."), ("1900", "Genoa C.F.C."), ("1901", "A.C. Milan"), ("1902", "Genoa C.F.C."), ("1903", "Genoa C.F.C."),
               ("1904", "Genoa C.F.C."), ("1905", "Juventus F.C."), ("1906", "A.C. Milan"), ("1907", "A.C. Milan"), ("1908", "Pro Vercelli"), ("1909", "Pro Vercelli"),
               ("1909/10", "F.C. Internazionale Milano"), ("1910/11", "Pro Vercelli"), ("1911/12", "Pro Vercelli"), ("1912/13", "Pro Vercelli"), ("1913/14", "Casale"),
               ("1914/15", "Genoa C.F.C."), ("1919/20", "F.C. Internazionale Milano"), ("1920/21", "Pro Vercelli"), ("1921/22", "Pro Vercelli"), ("1921/22", "Novese"),
               ("1922/23", "Genoa C.F.C."), ("1923/24", "Genoa C.F.C."), ("1924/25", "Bologna F.C. 1909"), ("1925/26", "Juventus F.C."), ("1927/28", "Torino F.C."),
               ("1928/29", "Bologna F.C. 1909")]
REPLACE["Serie A"] = {}
for lab, ch in SERIE_A_OLD: REPLACE["Serie A"].setdefault(lab, []).append((lab, ch, ""))
BASE.pop("Serie A", None)   # those titles are now real rows of the list

# ======================= review round 3 (list "Times sem escudo") =======================
RENAME_ALL.update({
    "Liaoning Bird": "Liaoning Fushun", "Chongqing Lifan": "Chongqing Liangjiang Athletic", "Qingdao Beilaite": "Qingdao Hainiu",
    "Chicago Croatian": "Chicago Croatia", "St. Louis Central Breweries": "St. Louis Shamrocks", "Philadelphia United German-Hungarian": "Philadelphia United German-Hungarians",
    "Racing Club Roubaisien": "Racing Club Roubaix", "P.E.C.": "PEC Zwolle", "P.E.C. Zwolle": "PEC Zwolle", "Border Security Force": "Border Security Force - BSF", "JCT FC": "JCT Mills",
    "The Wednesday": "Sheffield Wednesday", "Preston NE": "Preston North End", "Tottenham Hostpur": "Tottenham Hotspur", "Bournemouth & Boscombe Athletic": "AFC Bournemouth",
    "Brighton & Hove Alb": "Brighton & Hove Albion", "Limerick United": "Limerick", "Waterford United": "Waterford F.C.", "Ambrosiana-Inter": "F.C. Internazionale Milano",
    "Lanerossi Vicenza": "Vicenza", "Pescara": "Delfino Pescara 1936", "Sampiedarenese": "Sampierdarenese", "Tijuana": "Club Tijuana Xoloitzcuintles de Caliente",
    "Tecos UAG": "U.A.G.", "Bodø/Glimt": "FK BodøGlimt", "SOFK Lyn": "Lyn", "Vålerengen": "Vålerengens IF", "Odd Grenland": "Odd", "FK Skeid": "Skeid", "Moss FK": "Moss",
    "Stabæk Fotball": "Stabæk", "Fram": "Fram IF", "Larvik Turn": "Larvik Turn IF", "Gjøvik/Lyn": "Gjøvik-Lyn", "Follo": "Follo FK", "CWKS Warszawa": "Legia Warszawa",
    "ŁKS-Ptak Łódź": "ŁKS Łódź", "Unia Chorzów": "Ruch Chorzów", "Gwardia Kraków": "Wisła Kraków", "Budowlani Gdańsk": "Lechia Gdańsk", "Leixões SC": "Leixões Sport Club",
    "SC Beira Mar": "SC Beira-Mar", "U.C.A.S. Petroșani": "Jiul Petroșani", "România Cluj": "Victoria Cluj", "C.S.U. Cluj": "Universitatea Sibiu",
    "Colentina București": "Colentina", "Hälsingborgs IF": "Helsingborgs IF", "IK Sleipner": "IF Sleipner", "FC Sankt Gallen": "FC St. Gallen 1879",
    "Montriond Lausanne": "FC Lausanne-Sport", "Lausanne-Sports": "FC Lausanne-Sport", "Brühl Sankt Gallen": "SC Brühl St. Gallen", "Akhisar Belediye": "Akhisarspor",
    "Başakşehir": "Rams Başakşehir Futbol Kulübü", "Başakşehir FK": "Rams Başakşehir Futbol Kulübü", "İstanbul BB SK": "Rams Başakşehir Futbol Kulübü",
    "İstanbul Başakşehir": "Rams Başakşehir Futbol Kulübü", "Queen's Regiment": "The Queen's Royal Regiment", "Vitória SC Guimarães": "Vitória SC Guimarães",
})
# own crest, but the titles belong to the successor (FIFA counts West Germany's World Cups for Germany)
LINEAGE = {"West Germany": "Germany"}

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
            if (SPLIT_COMPS.match(n) and "," in r[2]) or "(shared)" in r[2]:
                r[2] = re.sub(r"\s*\(shared\)", "", r[2])
                for part in [p.strip() for p in r[2].split(",") if p.strip()]: rows.append([r[0], r[1], rename(part, n), "", ""])
                continue
            if (n, r[0]) in DROP: continue
            fx = SET.get((n, r[0]))
            if fx:
                if fx[0]: r[2] = fx[0]
                if fx[1] is not None: r[3] = fx[1]
                if len(fx) > 2: r[4] = fx[2]
            rows.append(r)
        if n in SHIFT_YEAR:
            for r in rows:
                m = re.match(r"^(\d{4})(.*)$", r[0])
                if m: r[0] = str(int(m[1]) + SHIFT_YEAR[n]) + m[2]; r[1] += SHIFT_YEAR[n]
        if n == "Community Shield":
            extra = []
            for r in rows:
                m = re.match(r"^(\d{4})\*\s+(.+)$", r[0])
                if m: r[0] = m[1]; r[3] = ""; extra.append([m[1], r[1], rename(m[2].strip(), n), "", "shared"]); r[4] = "shared"
            rows += extra
        for sn, lst in REPLACE.get(n, {}).items():
            rows = [r for r in rows if not (r[0] == sn or r[0].startswith(sn + " "))] + _rows(lst)
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
            for r in c["r"]:
                if not re.search(r"\bAA(m)?F\b|FAF", r[0]): r[0] = arg_label(r[0])
    return out
# round 3: names that would borrow another club's crest
RENAME_ALL.update({"Quick (Nijmegen)": "Quick Nijmegen"})
NO_LOGO |= {"Quick Nijmegen", "Académica", "Dinamo Obor București", "S.G. Sibiu"}

# ======================= round 4: full check of every list =======================
RENAME_COMP.setdefault("Liga MX", {}).update({"América": "Club de Fútbol America", "America": "Club de Fútbol America"})
RENAME_COMP.setdefault("Campeón de Campeones", {}).update({"América": "Club de Fútbol America"})
RENAME_COMP.setdefault("Campeones Cup", {}).update({"Club América": "Club de Fútbol America", "America": "Club de Fútbol America"})
RENAME_COMP.setdefault("Leagues Cup", {}).update({"América": "Club de Fútbol America", "Club América": "Club de Fútbol America"})
RENAME_COMP.setdefault("Liga Profesional de Fútbol", {}).update({"Arsenal F.C.": "Arsenal de Sarandí", "Arsenal FC": "Arsenal de Sarandí"})
RENAME_ALL.update({"Wanderers": "Wanderers F.C.", "New York City": "New York City FC"})
NO_LOGO |= {"Wanderers F.C.", "New York City FC", "Los Angeles Kickers", "Los Angeles Maccabee"}
ADD.setdefault("Liga MX", []).extend([["1970 México 70", 1970, "Cruz Azul", "Guadalajara", ""], ["1985 Prode 85", 1985, "Club de Fútbol America", "Tampico-Madero", ""],
                                      ["1986 México 86", 1986, "Monterrey", "Tampico-Madero", ""]])
ADD.setdefault("ÖFB Cup", []).append(["2008", 2008, "SV Horn", "", ""])
ADD.setdefault("Supercopa de España", []).append(["1989", 1989, "Real Madrid CF", "", ""])
REPLACE.setdefault("Brasileirão", {}).update({
    "1967": [("1967 Taça Brasil", "Palmeiras", "Náutico"), ("1967 Robertão", "Palmeiras", "Internacional")],
    "1968": [("1968 Taça Brasil", "Botafogo", "Fortaleza Esporte Clube"), ("1968 Robertão", "Santos", "Internacional")],
    "2020": [("2020", "Flamengo", "Internacional")]})
# Argentina 1931-1934: professional league (LAF) and amateur league (AAmF) side by side
for y, pro, ama in [("1931", "Boca Juniors", "Estudiantil Porteño"), ("1932", "River Plate", "Sportivo Barracas"),
                    ("1933", "San Lorenzo de Almagro", "Dock Sud"), ("1934", "Boca Juniors", "Estudiantil Porteño")]:
    REPLACE["Liga Profesional de Fútbol"][y] = [(y + " LAF", pro, ""), (y + " AAmF", ama, "")]
