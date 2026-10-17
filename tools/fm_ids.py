"""Probe Wikidata for a Football Manager player-ID property (manual tool, run by the fm-ids workflow)."""
import json, sys, urllib.request, urllib.parse
UA = {"User-Agent": "ProStatsBot/1.0 (personal hobby project)"}
def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
out = sys.argv[1]
for q in ["Football Manager", "sortitoutsi", "FM player", "Sports Interactive"]:
    r = get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbsearchentities", "search": q, "type": "property", "language": "en", "format": "json", "limit": 30}))
    for e in r["search"]: print(q, "|", e["id"], "|", e.get("label"), "|", e.get("description", ""))
