"""Builds the bundled logo database (web/www/logos) from the EA FC logo folders.
Usage: python3 -I tools/build_logos.py <folder with the 3 EA FC folders> <output www dir>
Each image is resized to 128px WebP; index.json maps names + aliases (PT/EN) to files."""
import sys, os, re, json
from PIL import Image

SRC, WWW = sys.argv[1], sys.argv[2]
OUT = os.path.join(WWW, "logos")
dec = lambda s: re.sub(r"#U([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)

# ---- national teams: English file names -> Portuguese names / common variants ----
PT = {"Afghanistan":"Afeganistão","Albania":"Albânia","Algeria":"Argélia","American Samoa":"Samoa Americana","Andorra":"Andorra","Angola":"Angola","Anguilla":"Anguila",
"Antigua and Barbuda":"Antígua e Barbuda","Argentina":"Argentina","Armenia":"Armênia","Aruba":"Aruba","Australia":"Austrália","Austria":"Áustria","Azerbaijan":"Azerbaijão",
"Bahamas":"Bahamas","Bahrain":"Bahrein","Bangladesh":"Bangladesh","Barbados":"Barbados","Belarus":"Bielorrússia","Belgium":"Bélgica","Belize":"Belize","Benin":"Benin",
"Bermuda":"Bermudas","Bhutan":"Butão","Bolivia":"Bolívia","Bosnia":"Bósnia e Herzegovina","Botswana":"Botsuana","Brazil":"Brasil","British Virgin Islands":"Ilhas Virgens Britânicas",
"Brunei":"Brunei","Bulgaria":"Bulgária","Burkina Faso":"Burkina Faso","Burundi":"Burundi","Cambodia":"Camboja","Cameroon":"Camarões","Canada":"Canadá","Cape Verde":"Cabo Verde",
"Cayman Islands":"Ilhas Cayman","Central African Republic":"República Centro-Africana","Chad":"Chade","Chile":"Chile","China PR":"China","Chinese Taipei (China PR)":"Taipé Chinesa",
"Colombia":"Colômbia","Comoros":"Comores","Congo":"Congo","Cook Islands":"Ilhas Cook","Costa Rica":"Costa Rica","Croatia":"Croácia","Cuba":"Cuba","Curaçao":"Curaçao","Cyprus":"Chipre",
"Czechia":"República Tcheca","Côte d'Ivoire":"Costa do Marfim","Democratic Republic of Congo":"RD Congo","Denmark":"Dinamarca","Djibouti":"Djibuti","Dominica":"Dominica",
"Dominican Republic":"República Dominicana","East Timor":"Timor-Leste","Ecuador":"Equador","Egypt":"Egito","El Salvador":"El Salvador","England":"Inglaterra","Equatorial Guinea":"Guiné Equatorial",
"Eritrea":"Eritreia","Estonia":"Estônia","Eswatini":"Essuatíni","Ethiopia":"Etiópia","Faroe Islands":"Ilhas Faroé","Fiji":"Fiji","Finland":"Finlândia","France":"França","Gabon":"Gabão",
"Georgia":"Geórgia","Germany":"Alemanha","Ghana":"Gana","Gibraltar":"Gibraltar","Greece":"Grécia","Greenland":"Groenlândia","Grenada":"Granada","Guam":"Guam","Guatemala":"Guatemala",
"Guinea":"Guiné","Guinea-Bissau":"Guiné-Bissau","Guyana":"Guiana","Haiti":"Haiti","Honduras":"Honduras","Hong Kong":"Hong Kong","Hungary":"Hungria","Iceland":"Islândia","India":"Índia",
"Indonesia":"Indonésia","Iran":"Irã","Iraq":"Iraque","Israel":"Israel","Italy":"Itália","Jamaica":"Jamaica","Japan":"Japão","Jordan":"Jordânia","Kazakhstan":"Cazaquistão","Kenya":"Quênia",
"Kosovo":"Kosovo","Kuwait":"Kuwait","Laos":"Laos","Latvia":"Letônia","Lebanon":"Líbano","Lesotho":"Lesoto","Liberia":"Libéria","Libya":"Líbia","Liechtenstein":"Liechtenstein",
"Lithuania":"Lituânia","Luxembourg":"Luxemburgo","Macau":"Macau","Madagascar":"Madagascar","Malaysia":"Malásia","Mali":"Mali","Malta":"Malta","Mauritania":"Mauritânia","Mauritius":"Maurício",
"Mexico":"México","Moldova":"Moldávia","Mongolia":"Mongólia","Montenegro":"Montenegro","Montserrat":"Montserrat","Morocco":"Marrocos","Mozambique":"Moçambique","Myanmar":"Mianmar",
"Namibia":"Namíbia","Nepal":"Nepal","Netherlands":"Holanda","New Caledonia":"Nova Caledônia","New Zealand":"Nova Zelândia","Nicaragua":"Nicarágua","Niger":"Níger","Nigeria":"Nigéria",
"North Korea":"Coreia do Norte","Northern Ireland":"Irlanda do Norte","Norway":"Noruega","Oman":"Omã","Pakistan":"Paquistão","Palestine":"Palestina","Panama":"Panamá",
"Papua New Guinea":"Papua-Nova Guiné","Paraguay":"Paraguai","Peru":"Peru","Philippines":"Filipinas","Poland":"Polônia","Portugal":"Portugal","Puerto Rico":"Porto Rico","Qatar":"Catar",
"Republic of Ireland":"Irlanda","Romania":"Romênia","Russia":"Rússia","Rwanda":"Ruanda","Saint Lucia":"Santa Lúcia","Saint Vincent and the Grenadines":"São Vicente e Granadinas",
"Samoa":"Samoa","San Marino":"San Marino","Saudi Arabia":"Arábia Saudita","Scotland":"Escócia","Senegal":"Senegal","Serbia":"Sérvia","Seychelles":"Seicheles","Sierra Leone":"Serra Leoa",
"Singapore":"Singapura","Slovakia":"Eslováquia","Slovenia":"Eslovênia","Solomon Islands":"Ilhas Salomão","Somalia":"Somália","South Africa":"África do Sul","South Korea":"Coreia do Sul",
"South Sudan":"Sudão do Sul","Spain":"Espanha","Sri Lanka":"Sri Lanka","Suriname":"Suriname","Sweden":"Suécia","Switzerland":"Suíça","Syria":"Síria","São Tomé & Príncipe":"São Tomé e Príncipe",
"Tahiti":"Taiti","Tajikistan":"Tajiquistão","Tanzania":"Tanzânia","Thailand":"Tailândia","The Democratic Republic of the Congo":"República Democrática do Congo","The Gambia":"Gâmbia",
"The Kyrgyz Republic":"Quirguistão","The United States Virgin Islands":"Ilhas Virgens Americanas","Togo":"Togo","Tonga":"Tonga","Trinidad and Tobago":"Trinidad e Tobago","Tunisia":"Tunísia",
"Turkmenistan":"Turcomenistão","Turks and Caicos Islands":"Ilhas Turcas e Caicos","Uganda":"Uganda","Ukraine":"Ucrânia","United Arab Emirates":"Emirados Árabes Unidos",
"United States of America":"Estados Unidos","Uruguay":"Uruguai","Uzbekistan":"Uzbequistão","Vanuatu":"Vanuatu","Venezuela":"Venezuela","Vietnam":"Vietnã","Wales":"País de Gales",
"Yemen":"Iêmen","Zambia":"Zâmbia","Zimbabwe":"Zimbábue"}
NATION_EXTRA = {"United States of America":["EUA","USA","United States","Seleção Americana"],"Netherlands":["Países Baixos","Holland"],"Czechia":["Tchéquia","Czech Republic","República Checa"],
"Bosnia":["Bosnia and Herzegovina","Bósnia"],"China PR":["China"],"South Korea":["Coreia","Korea Republic"],"Republic of Ireland":["Ireland","República da Irlanda"],
"Côte d'Ivoire":["Ivory Coast","Costa do Marfim"],"England":["Seleção Inglesa"],"Brazil":["Seleção Brasileira","Seleção"],"Wales":["Gales"],"Iran":["Irão"],"Russia":["Russia"],
"Cape Verde":["Cabo Verde"],"Democratic Republic of Congo":["República Democrática do Congo","DR Congo"],"The Gambia":["Gambia"],"The Kyrgyz Republic":["Kyrgyzstan","Quirguízia"],
"Eswatini":["Suazilândia","Swaziland"],"Turkey":["Turquia"],"Scotland":["Escocia"]}

# ---- leagues / competitions ----
LEAGUE_ALIASES = {
"3. Liga (Alemanha)":["3. Liga","3 Liga Alemanha","Terceira Divisão Alemã"],
"3F Superliga (Dinamarca)":["Superliga Dinamarquesa","Danish Superliga","3F Superliga"],
"Allsvenskan (Suecia)":["Allsvenskan","Liga Sueca"],
"Brack Super League (Suiça)":["Swiss Super League","Super League Suíça","Liga Suíça","Brack Super League"],
"Bundesliga (Alemanha)":["Bundesliga","1. Bundesliga","Bundesliga Alemã","Liga Alemã"],
"Bundesliga 2 (Alemanha)":["2. Bundesliga","Bundesliga 2","2 Bundesliga"],
"Chinese Super League (China)":["Chinese Super League","Superliga Chinesa","CSL"],
"Copa Do Mundo":["World Cup","FIFA World Cup","Copa do Mundo FIFA","Copa do Mundo da FIFA"],
"EFL Championship (Inglaterra)":["Championship","EFL Championship","Championship Inglesa"],
"EFL League One (Inglaterra)":["League One","EFL League One"],
"EFL League Two (Inglaterra)":["League Two","EFL League Two"],
"Eliteserien (Noruega)":["Eliteserien","Liga Norueguesa"],
"Eredivisie (Paises Baixos)":["Eredivisie","Liga Holandesa"],
"Österreichische Fußball-Bundesliga (Austria)":["Ö. Bundesliga","Österreichische Bundesliga","Austrian Bundesliga","Bundesliga Austríaca","Admiral Bundesliga","Bundesliga Austria","O. Bundesliga"],
"Brasileirão":["Brasileirão Série A","Brasileirão Seria A","Brasileirao Serie A","Brasileiro Série A","Campeonato Brasileiro","Campeonato Brasileiro Série A","Série A Brasil","Brasileirão Betano"],
"Serie B":["Brasileirão Série B","Brasileirão Seria B","Brasileiro Série B","Série B","Campeonato Brasileiro Série B","Série B Brasil"],
"Serie C":["Brasileirão Série C","Brasileirão Seria C","Série C","Série C Brasil"],
"Serie D":["Brasileirão Série D","Brasileirão Seria D","Série D","Série D Brasil"],
"Copa Do Brasil":["Copa do Brasil","Copa Betano do Brasil"],
"Copa Libertadores":["Conmebol Libertadores","Libertadores","Libertadores da América","Copa Libertadores da América","Taça Libertadores"],
"Copa Sudamericana":["Copa Sul-Americana","Sul-Americana","Sudamericana","Conmebol Sudamericana","Conmebol Sul-Americana"],
"South American Recopa":["Recopa Sul-Americana","Recopa Sudamericana","Recopa","Conmebol Recopa"],
"Super Copa Do Brasil":["Supercopa do Brasil","Supercopa Do Brasil","Super Copa do Brasil"],
"Copa América":["Copa América","Conmebol Copa América"],
"FIFA Club World Cup":["Mundial de Clubes","Club World Cup","Mundial de Clubes da FIFA","Copa do Mundo de Clubes","FIFA Club World Cup"],
"Indian Super League (India)":["Indian Super League","ISL"],
"Isuzu UTE A-League (Australia)":["A-League","A League","Liga Australiana"],
"Jupiler Pro League (Belgica)":["Jupiler Pro League","Pro League","Liga Belga"],
"K League 1 (Coreia do Sul)":["K League 1","K League","K-League"],
"LALIGA EA SPORTS (Espanha)":["La Liga","LaLiga","Liga Espanhola","LaLiga Santander","LaLiga EA Sports","Primera División"],
"LALIGA HYPERMOTION (Espanha)":["La Liga 2","LaLiga 2","LaLiga Hypermotion","Segunda División","Segunda Divisão Espanhola"],
"Liga BBVA MX (Mexico)":["Liga MX","Liga BBVA MX","Liga Mexicana"],
"Liga Portugal (Portugal)":["Liga Portugal","Primeira Liga","Liga Portuguesa","Liga NOS","Liga Betclic","Liga Portugal Betclic"],
"Liga Profesional de Fútbol (Argentina)":["Liga Argentina","Liga Profesional","Primera División Argentina","Liga Profesional de Fútbol"],
"Ligue 1 McDonald's (França)":["Ligue 1","Liga Francesa","Ligue 1 Uber Eats"],
"Ligue 2 BKT (França)":["Ligue 2","Ligue 2 BKT"],
"Major League Soccer (Estados Unidos)":["MLS","Major League Soccer"],
"PKO Bank Polski Ekstraklasa (Polonia)":["Ekstraklasa","Liga Polonesa"],
"Premier League (Inglatera)":["Premier League","Premier","Liga Inglesa","EPL","English Premier League"],
"ROSHN Saudi League (Arabia Saudita)":["Saudi Pro League","Saudi League","Liga Saudita","ROSHN Saudi League"],
"SSE Airtricity Men's Premier Division (irlanda)":["League of Ireland","Premier Division","Liga Irlandesa"],
"SUPERLIGA (Romenia)":["Superliga Romena","Liga 1 Romênia","SuperLiga Romania"],
"Scottish Premiership (Escocia)":["Scottish Premiership","Premiership","Liga Escocesa"],
"Serie A Enilive (Italia)":["Serie A","Série A Italiana","Serie A TIM","Serie A Italia","Calcio Serie A","Liga Italiana"],
"Serie BKT (Italia)":["Serie B Italia","Serie BKT","Série B Italiana","Serie B Italiana"],
"Trendyol Süper Lig (Turquia)":["Süper Lig","Super Lig","Liga Turca","Trendyol Super Lig"],
"UEFA Champions League":["Champions League","Champions","Liga dos Campeões","UCL","Liga dos Campeões da UEFA"],
"UEFA Conference League":["Conference League","UECL","Liga Conferência","Conference"],
"UEFA Europa League":["Europa League","Liga Europa","UEL"],
"UEFA Super Cup":["Supercopa da UEFA","Supercopa Europeia","Super Cup UEFA","UEFA Supercup"],
}
TEAM_ALIASES = {
"Wattener SG Tirol":["WSG Tirol","WSG Swarovski Tirol","Tirol"],"SK Rapid Wien":["SK Rapid","Rapid Wien","Rapid Viena"],"Lask":["LASK","LASK Linz"],"SK Puntigamer Sturm Graz":["Sturm Graz","SK Sturm Graz"],"FK Austria Wien":["Austria Wien","Austria Viena"],"FC Blau Weiß Linz":["Blau-Weiß Linz","BW Linz"],"RZ Pellets Wolfsberger AC":["Wolfsberger AC","WAC","Wolfsberg"],"TSV Prolactal Hartberg":["TSV Hartberg","Hartberg"],"CASHPOINT SCR Altach":["SCR Altach","Altach"],"SV Guntamatic Ried":["SV Ried","Ried"],"Grazer AK 1902":["Grazer AK","GAK"],"SK Austria Klagenfurt":["Austria Klagenfurt","Klagenfurt"],"Dinamo Zagreb":["GNK Dinamo Zagreb"],"Dynamo Kyiv":["Dínamo de Kiev","Dynamo Kiev"],"Shakhtar Donetsk":["Shakhtar"],"SK Slavia Praha":["Slavia Praga","Slavia Prague"],"Sparta Praha":["Sparta Praga","Sparta Prague"],"Olympiacos":["Olympiakos","Olimpiacos"],
"F.C. Internazionale Milano":["Inter","Inter de Milão","Inter Milan","Internazionale"],"A.C. Milan":["Milan","AC Milan"],"F.C. Barcelona":["Barcelona","Barça","Barca"],
"Real Madrid C.F.":["Real Madrid"],"Club Atlético de Madrid":["Atlético de Madrid","Atletico Madrid","Atlético Madrid","Atleti"],"FC Bayern München":["Bayern","Bayern de Munique","Bayern Munich","Bayern Munique"],
"Bayer 04 Leverkusen":["Leverkusen","Bayer Leverkusen"],"Paris Saint-Germain":["PSG","Paris SG"],"Manchester City":["Man City"],"Manchester United":["Man United","Man Utd","Manchester Utd"],
"Tottenham Hotspur":["Tottenham","Spurs"],"Sport Lisboa e Benfica":["Benfica"],"Futebol Clube do Porto":["Porto","FC Porto"],"Sporting Clube de Portugal":["Sporting","Sporting CP","Sporting Lisboa"],
"Sporting Clube de Braga":["Braga","SC Braga"],"Juventus F.C.":["Juventus","Juve"],"S.S.C. Napoli":["Napoli","Nápoles"],"A.S. Roma":["Roma"],"S.S. Lazio":["Lazio"],
"Borussia Dortmund":["Dortmund","BVB"],"Borussia Mönchengladbach":["Gladbach","Monchengladbach"],"RB Leipzig":["Leipzig"],"RB Salzburg":["Salzburg","Red Bull Salzburg"],
"Olympique Lyonnais":["Lyon"],"Olympique de Marseille":["Marseille","Olympique Marseille"],"AS Monaco":["Monaco"],"LOSC Lille":["Lille"],"OGC Nice":["Nice"],"Stade Rennais FC":["Rennes"],"RC Lens":["Lens"],
"Atlético Mineiro":["Atlético-MG","Atletico MG","Atlético MG","Galo"],"América Mineiro":["America-MG","América-MG","America MG"],"Atlético Paranaense":["Athletico-PR","Athletico Paranaense","Atlético-PR","Athletico"],
"Atlético Goianiense":["Atlético-GO","Atletico GO"],"São Paulo":["São Paulo FC","Sao Paulo"],"Vasco da Gama":["Vasco"],"Bragantino":["Red Bull Bragantino","RB Bragantino"],
"Internacional":["Inter de Porto Alegre","Internacional-RS","Inter-RS"],"Sport":["Sport Recife"],"Ceará":["Ceará SC"],"Avaí FC":["Avaí"],"Bahia":["EC Bahia"],"Vitória":["Vitória BA","EC Vitória"],
"Club Atlético River Plate":["River Plate","River"],"Club Atlético Boca Juniors":["Boca Juniors","Boca"],"Racing Club de Avellaneda":["Racing","Racing Club"],"Club Atlético Independiente":["Independiente"],
"Club Atlético Vélez Sarsfield":["Vélez","Velez Sarsfield"],"Al-Nassr Football Club":["Al Nassr","Al-Nassr"],"Al-Hilal Saudi Football Club":["Al Hilal","Al-Hilal"],"Al-Ittihad Club":["Al Ittihad","Al-Ittihad"],
"Al-Ahli Saudi Football Club":["Al Ahli","Al-Ahli"],"Inter Miami CF":["Inter Miami"],"Los Angeles Galaxy":["LA Galaxy"],"Los Angeles FC":["LAFC"],"PSV":["PSV Eindhoven"],"AZ Alkmaar":["AZ"],
"Galatasaray A.Ş.":["Galatasaray"],"Fenerbahçe SK":["Fenerbahçe"],"Beşiktaş JK":["Besiktas","Beşiktaş"],"Club de Fútbol América":["Club América","América do México"],
"Club Deportivo Guadalajara":["Chivas","Guadalajara"],"Club Tigres U.A.N.L.":["Tigres"],"Club de Fútbol Monterrey Rayados":["Monterrey"],"Club Deportivo Cruz Azul":["Cruz Azul"],"Pumas":["Pumas UNAM","UNAM"],
"Football Club København":["Copenhagen","Copenhague","FC Copenhagen","København"],"BSC Young Boys":["Young Boys"],"FC Basel 1893":["Basel","Basileia"],"Sheffield Utd":["Sheffield United"],
"West Brom":["West Bromwich","West Bromwich Albion"],"Wolverhampton Wanderers":["Wolves","Wolverhampton"],"Brighton & Hove Albion":["Brighton"],"Nottingham Forest":["Forest"],
"Newcastle United":["Newcastle"],"Athletic Club":["Athletic Bilbao","Bilbao"],"Real Betis Balompié":["Betis","Real Betis"],"Real Sociedad de Fútbol":["Real Sociedad"],"Sevilla F.C.":["Sevilla","Sevilha"],
"Valencia C.F.":["Valencia","Valência"],"Villarreal C.F.":["Villarreal"],"R.C. Celta de Vigo":["Celta","Celta de Vigo"],"R.C.D. Espanyol de Barcelona":["Espanyol"],"R.C.D. Mallorca":["Mallorca","Maiorca"],
"Club Atlético Osasuna":["Osasuna"],"Girona F.C.":["Girona"],"A.C.F. Fiorentina":["Fiorentina"],"Atalanta Bergamasca Calcio":["Atalanta"],"Bologna F.C. 1909":["Bologna","Bolonha"],
"TSG 1899 Hoffenheim":["Hoffenheim"],"SC Freiburg":["Freiburg"],"1. FSV Mainz 05":["Mainz"],"VfL Wolfsburg":["Wolfsburg"],"SV Werder Bremen":["Werder Bremen","Bremen"],"FC Schalke 04":["Schalke"],
"1. FC Köln":["Köln","Colônia","Koln"],"VfB Stuttgart":["Stuttgart"],"Eintracht Frankfurt":["Frankfurt"],"West Ham United":["West Ham"],"Celtic":["Celtic Glasgow"],"Rangers":["Glasgow Rangers"],
}

CUP_ALIASES = {
"AIFF Super Cup (Copa Principal India)":["AIFF Super Cup","Super Cup India"],"Allianz Cup":["Taça da Liga","Allianz Cup","Taça da Liga Portugal"],
"Campeones Cup (Campeão da Liga BBVA MX e da MLS Cup)":["Campeones Cup"],"Campeón de Campeones":["Campeon de Campeones"],"Chinese FA Cup":["Copa da China","FA Cup China"],
"Chinese FA Super Cup":["Supercopa da China"],"Club Orange FAI Cup":["FAI Cup","Copa da Irlanda"],"Community Shield":["FA Community Shield","Supercopa da Inglaterra","Community Shield"],
"Copa Argentina":["Copa da Argentina"],"Copa del Rey":["Copa do Rei","Copa del Rei","Copa da Espanha"],"Coppa Italia":["Copa da Itália","Copa Itália"],
"Coupe de France":["Copa da França"],"Croky Cup (Belgica)":["Croky Cup","Copa da Bélgica","Belgian Cup"],"Cupa României Betano":["Copa da Romênia","Cupa Romaniei"],
"Cupen (Noruega)":["Copa da Noruega","NM Cup","Norwegian Cup"],"DFB-Pokal":["DFB Pokal","Copa da Alemanha","German Cup"],"Danish Cup":["Copa da Dinamarca"],"Durand Cup (india)":["Durand Cup"],
"EFL Carabao Cup":["Carabao Cup","EFL Cup","League Cup","Copa da Liga Inglesa","Copa da Liga"],"Emirates FA Cup":["FA Cup","Copa da Inglaterra"],
"Franz Beckenbauer Supercup":["DFL-Supercup","DFL Supercup","Supercopa da Alemanha","German Super Cup","DFL Super Cup"],"Hahn Australia Cup":["Australia Cup","Copa da Austrália"],
"Johan Cruijff Schaal":["Supercopa da Holanda","Johan Cruyff Shield","Johan Cruijff Shield"],"K League Super Cup":["Supercopa da Coreia"],"KNVB Beker":["Copa da Holanda","KNVB Cup","Dutch Cup"],
"King's Cup (Arabia Saudita)":["King's Cup","Kings Cup","Copa do Rei Saudita","King Cup"],"Korea Cup":["Copa da Coreia","FA Cup Coreia"],"Leagues Cup (MLS e Liga BBVA MX)":["Leagues Cup"],
"MLS Cup":["MLS Cup","Final da MLS"],"Premier Sports Cup":["Scottish League Cup","Copa da Liga Escocesa"],"President of Ireland's Cup":["President's Cup Ireland"],
"Puchar Polski (Polonia)":["Puchar Polski","Copa da Polônia"],"Saudi Super Cup":["Supercopa Saudita"],"Schweizer Cup":["Copa da Suíça","Swiss Cup"],"Scottish Cup":["Copa da Escócia"],
"Supercopa Argentina":["Supercopa da Argentina"],"Supercopa Internacional (Argentina)":["Supercopa Internacional"],"Supercopa de España":["Supercopa da Espanha","Spanish Super Cup"],
"Supercoppa Italiana":["Supercopa da Itália","Supercopa Italiana","Italian Super Cup"],"Supercupa României":["Supercopa da Romênia"],"Superpuchar Polski":["Supercopa da Polônia"],
"Supertaça Cândido de Oliveira":["Supertaça","Supercopa de Portugal","Supertaça de Portugal"],"Svenska Cupen":["Copa da Suécia","Swedish Cup"],"TFF Süper Kupa":["Supercopa da Turquia","Turkish Super Cup","Super Kupa"],
"Taça de Portugal Placard":["Taça de Portugal","Copa de Portugal"],"Trofeo de Campeones":["Trofeo de Campeones","Trofeo de Campeones Argentina"],"Trophée des Champions":["Supercopa da França","Trophee des Champions"],
"U.S. Open Cup":["US Open Cup","Copa dos EUA"],"UNIQA ÖFB Cup (Austria)":["ÖFB Cup","OFB Cup","Copa da Áustria"],"Vertu Trophy (League One e League Two)":["Vertu Trophy","EFL Trophy"],
"Volkswagen Supercup":["Volkswagen Supercup"],"Ziraat Türkiye Kupası":["Copa da Turquia","Turkish Cup","Türkiye Kupası"],
}
TROPHY_EXTRA = {"FIFA World Cup":["Copa do Mundo","Copa Do Mundo","World Cup","Copa do Mundo FIFA"],"Brasileirão":["Brasileirão Série A","Brasileirão Seria A","Campeonato Brasileiro"],
"Serie B":["Brasileirão Série B","Brasileirão Seria B","Série B"],"Serie C":["Brasileirão Série C","Série C"],"Serie D":["Brasileirão Série D","Série D"],
"Österreichische Fußball-Bundesliga":["Ö. Bundesliga","Austrian Bundesliga","Bundesliga Austríaca"],"Carabao Cup":["EFL Carabao Cup","EFL Cup","League Cup"],
"MLS Cup (FInal da MLS)":["MLS Cup"],"US Cup":["U.S. Open Cup","US Open Cup"],"Recopa Sulamericana":["Recopa Sul-Americana","South American Recopa","Recopa"],
"Super Copa Do Brasil":["Supercopa do Brasil"],"Copa Libertadores":["Conmebol Libertadores","Libertadores"],"Copa Sudamericana":["Copa Sul-Americana","Sul-Americana"],
"Taça de Portugal":["Taça de Portugal Placard"],"Franz Beckenbauer Supercup":["DFL-Supercup","DFL Supercup"],"Serie BKT":["Serie B Italia"],"King's Cup":["Kings Cup"],
"Trofeo de Campeones (Argentina)":["Trofeo de Campeones"],"LaLiga Hypermotion":["La Liga 2","LaLiga 2"],"Liga BBVA MX":["Liga MX"]}

def slug(i): return f"{i}.webp"
entries = []
def add(kind, folder, files_alias, size=128):
    d = os.path.join(SRC, folder); os.makedirs(os.path.join(OUT, kind), exist_ok=True)
    files = sorted(os.listdir(d))
    for f in files:
        if not f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")): continue
        name = dec(os.path.splitext(f)[0]).strip()
        idx = len([e for e in entries if e["t"] == kind])
        im = Image.open(os.path.join(d, f)).convert("RGBA")
        bbox = im.getbbox()
        if bbox: im = im.crop(bbox)
        im.thumbnail((size, size), Image.LANCZOS)
        rel = f"{kind}/{slug(idx)}"
        im.save(os.path.join(OUT, rel), "WEBP", quality=82, method=6)
        aliases = files_alias(name)
        entries.append({"t": kind, "n": name, "f": rel, "a": aliases})

folders = os.listdir(SRC)
fold = lambda key: next(x for x in folders if dec(x).upper().startswith(key) or (key not in ("LOGO TODAS AS LIGAS",) and key in dec(x).upper()))
def club_al(n): return TEAM_ALIASES.get(n, [])
def nat_al(n): return [PT[n]] + NATION_EXTRA.get(n, []) if n in PT else NATION_EXTRA.get(n, [])
def lg_al(n):
    base = re.sub(r"\s*\([^)]*\)\s*$", "", n).strip()
    al = LEAGUE_ALIASES.get(n, [])
    return ([base] if base != n else []) + al
bare = lambda n: re.sub(r"\s*\([^)]*\)\s*$", "", n).strip()
def cup_al(n): return ([bare(n)] if bare(n) != n else []) + CUP_ALIASES.get(n, [])
ALL_AL = {}
for dct in (LEAGUE_ALIASES, CUP_ALIASES):
    for k, v in dct.items(): ALL_AL.setdefault(bare(k).lower(), []).extend([k] + v)
def tr_al(n):
    al = ([bare(n)] if bare(n) != n else []) + TROPHY_EXTRA.get(n, []) + ALL_AL.get(bare(n).lower(), [])
    return list(dict.fromkeys(a for a in al if a != n))
add("c", fold("TIMES"), club_al)
add("n", fold("SELE"), nat_al)
add("l", fold("LOGO TODAS AS LIGAS"), lg_al)
add("k", fold("DENTRO DAS LIGAS"), cup_al)
add("t", fold("TROFEUS"), tr_al, 256)
missing = [k for k in LEAGUE_ALIASES if not any(e["n"] == k for e in entries)]
missing_t = [k for k in list(TEAM_ALIASES)+list(CUP_ALIASES) if not any(e["n"] == k for e in entries)]
json.dump({"v": 1, "e": [[e["t"], e["n"], e["f"], e["a"]] for e in entries]}, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, separators=(",", ":"))
tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print(len(entries), "logos", round(tot / 1e6, 2), "MB", "| unmatched alias keys:", missing, missing_t)
