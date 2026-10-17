"""Adds player faces (Football Manager facepack images, named by FM unique ID) to the app.
Usage: python3 tools/build_faces.py FACES_DIR LIST.csv ProStats-Mobile/web/www
LIST.csv columns: liga,clube,jogador,idade,fm_id   (made from sortitoutsi squad pages)
Writes logos/p/<id>.webp (128px) and merges logos/faces.json = {"v":1,"e":[[id,name,club,league],...]}"""
import sys, csv, json, pathlib
from PIL import Image
src, lst, www = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
out = www / "logos" / "p"; out.mkdir(parents=True, exist_ok=True)
idx_p = www / "logos" / "faces.json"
idx = json.loads(idx_p.read_text()) if idx_p.exists() else {"v": 1, "e": []}
have = {e[0]: e for e in idx["e"]}
added = 0
for r in csv.DictReader(open(lst, encoding="utf-8")):
    fid = r["fm_id"]; f = src / f"{fid}.png"
    if not f.exists(): continue
    im = Image.open(f).convert("RGBA"); im.thumbnail((128, 128), Image.LANCZOS)
    im.save(out / f"{fid}.webp", "WEBP", quality=78, method=4)
    have[fid] = [fid, r["jogador"], r["clube"], r["liga"]]; added += 1
idx["e"] = sorted(have.values(), key=lambda e: (e[3], e[2], e[1]))
idx_p.write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
print("faces:", added, "total", len(idx["e"]), "size MB", round(sum(p.stat().st_size for p in out.glob("*.webp")) / 1e6, 1))
