"""Add a folder of extra club logos to an existing logos/index.json without rebuilding everything.
"Name (Alias)" file names become name + alias. A logo whose name already exists replaces that image.
Usage: python3 tools/add_logos.py FOLDER WWW [kind=c]"""
import sys, os, re, json, unicodedata
from PIL import Image

src, www = sys.argv[1], sys.argv[2]; kind = sys.argv[3] if len(sys.argv) > 3 else "c"
out = os.path.join(www, "logos"); idx_path = os.path.join(out, "index.json")
dec = lambda s: re.sub(r"#U([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
key = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
# files whose name would collide with a famous club, or that are the same club as an existing logo
RENAME = {"Sport Club Internacional": ("Internacional-BA", []), "SC Internacional": ("Internacional-SP", ["SC Internacional (SP)"]),
          "Esporte Clube Cruzeiro (Cruzeiro-RS)": ("Cruzeiro-RS", ["Esporte Clube Cruzeiro"]), "Esporte Clube XV de Novembro (XV de Piracicaba)": ("XV de Piracicaba", ["Esporte Clube XV de Novembro"]),
          "Associação Atlética Internacional (Inter de Limeira)": ("Inter de Limeira", ["Associação Atlética Internacional"]),
          "Club Deportivo Popular Junior (Junior Barranquilla)": ("Junior Barranquilla", ["Club Deportivo Popular Junior", "Junior"]),
          "São Paulo (BA)": ("São Paulo-BA", []), "Luffwaffen SV Hamburg": ("Luftwaffen SV Hamburg", []), "Shenzhen Jianliao": ("Shenzhen Jianlibao", []),
          "guangzhou Evergrande": ("Guangzhou Evergrande", ["Guangzhou FC"]), "Bordeaux": ("Bordeaux", ["Girondins de Bordeaux", "FC Girondins de Bordeaux"]),
          "AA São Bento": ("AA São Bento", []), "Albion": ("Albion", []), "Colorado": ("Colorado EC", ["Colorado-PR"]), "Paulista": ("Paulista", ["Paulista FC"]),
          "Atlético Futebol Clube": ("Atlético Futebol Clube", []), "CSKA Moscow": ("CSKA Moscow", ["CSKA Moskva", "CSKA Moscou"])}
ALIAS_ONLY = {"Racing Genk": "Genk", "Shandong Luneng": "Shandong Taishan"}   # same club as an EA logo: keep the EA image
NATIONS = {"Yugoslavia": ["Iugoslávia"], "Soviet Union": ["União Soviética", "URSS"], "Czechoslovakia": ["Tchecoslováquia"]}
j = json.load(open(idx_path, encoding="utf-8"))
E = j["e"]
added = replaced = 0
for f in sorted(os.listdir(src)):
    if not f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")): continue
    raw = dec(os.path.splitext(f)[0]).strip()
    if raw in ALIAS_ONLY:
        ex = next(e for e in E if e[1] == ALIAS_ONLY[raw]); ex[3] = list(dict.fromkeys(ex[3] + [raw])); continue
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", raw)
    name, aliases = (m[1].strip(), [m[2].strip()]) if m else (raw, [])
    if raw in RENAME: name, aliases = RENAME[raw]; aliases = list(aliases)
    k = "n" if name in NATIONS else kind
    if k == "n": aliases += NATIONS[name]
    im = Image.open(os.path.join(src, f)).convert("RGBA"); bb = im.getbbox()
    if bb: im = im.crop(bb)
    im.thumbnail((128, 128), Image.LANCZOS)
    ex = next((e for e in E if e[0] == k and key(e[1]) == key(name)), None)
    if ex:
        rel = ex[2]; ex[3] = list(dict.fromkeys(ex[3] + [a for a in aliases if key(a) != key(ex[1])])); replaced += 1
    else:
        n = max([int(e[2].split("/")[1].split(".")[0]) for e in E if e[0] == k] + [-1]) + 1
        rel = f"{k}/{n}.webp"; E.append([k, name, rel, aliases]); added += 1
    im.save(os.path.join(out, rel), "WEBP", quality=82, method=6)
# common short names that the extra (historic) logos must not steal
EXTRA_ALIASES = {"Hamburger SV": ["Hamburg", "Hamburgo", "HSV"], "Standard de Liege": ["Liège", "Liege", "Standard Liège", "Standard de Liège"],
                 "Shenzhen Peng City": ["Shenzhen"], "Dalian Yingbo": ["Dalian"], "S.V. Zulte Waregem": ["Waregem", "Zulte Waregem", "Zulte-Waregem"],
                 "Anápolis FC": ["Anápolis", "Anapolis"], "Colorado Rapids": ["Colorado"], "1. FC Union Berlin": ["Union Berlin"], "SK Rapid Wien": ["Rapid Wien", "Rapid Viena"],
                 "VfB Stuttgart": ["VfB"], "FC CFR 1907 Cluj": ["CFR Cluj", "CFR"]}
for e in E:
    if e[1] in EXTRA_ALIASES: e[3] = list(dict.fromkeys(e[3] + EXTRA_ALIASES[e[1]]))
json.dump(j, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("added", added, "replaced", replaced, "total", len(E))
