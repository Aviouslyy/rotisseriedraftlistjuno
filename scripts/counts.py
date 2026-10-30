# Count MTGTop8 decks (main+side) per card per format -> data/ranked.json
# Resumable: results are cached in scripts/.cache.json
import json, os, re, threading, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

FMTS = {"ST": "Standard", "PI": "Pioneer", "EXP": "Explorer", "HI": "Historic", "MO": "Modern", "PREM": "Premodern",
        "LE": "Legacy", "VI": "Vintage", "PAU": "Pauper", "PEA": "Peasant", "cEDH": "cEDH", "EDH": "Duel Commander"}
CACHE = "scripts/.cache.json"

def count(name, fmt):
    body = urllib.parse.urlencode({"cards": name, "MD_check": 1, "SB_check": 1, "format": fmt}).encode()
    for attempt in range(5):
        try:
            req = urllib.request.Request("https://www.mtgtop8.com/search", body, {"User-Agent": "rotisserie-list/1.0"})
            html = urllib.request.urlopen(req, timeout=30).read().decode("latin1")
            m = re.search(r"(\d+) decks matching", html)
            return int(m.group(1)) if m else 0
        except Exception:
            time.sleep(2 ** attempt)
    return None

cards = [c for c in json.load(open("data/cards.json")) if not c["type"].startswith("Basic")]
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
lock = threading.Lock()
totals = {f: count("", f) for f in ["", *FMTS]}

def counts(name):
    if name in cache:
        return cache[name]
    q = name.split(" // ")[0]
    # unrecognised names return ~every deck in the format
    hit = lambda f, n: n if n is None or n < totals[f] * 0.9 else 0
    n = {f: 0 for f in FMTS} if hit("", count(q, "")) == 0 else {f: hit(f, count(q, f)) for f in FMTS}
    if None not in n.values():
        with lock:
            cache[name] = n
            if len(cache) % 100 == 0:
                json.dump(cache, open(CACHE, "w"))
    return n

with ThreadPoolExecutor(6) as ex:
    for c, n in zip(cards, ex.map(lambda c: counts(c["name"]), cards)):
        c["counts"] = n
json.dump(cache, open(CACHE, "w"))
json.dump({"formats": FMTS, "totals": {f: totals[f] for f in FMTS}, "updated": time.strftime("%Y-%m-%d"), "cards": cards},
          open("data/ranked.json", "w"))
print(totals, sum(None in c["counts"].values() for c in cards))
