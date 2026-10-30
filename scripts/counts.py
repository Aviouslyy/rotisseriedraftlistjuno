# Count MTGTop8 non-Commander constructed decks (main+side) per card -> data/ranked.json
import json, re, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

def count(name):
    body = urllib.parse.urlencode({"cards": name, "MD_check": 1, "SB_check": 1, "format": "NCOMF"}).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request("https://www.mtgtop8.com/search", body, {"User-Agent": "rotisserie-list/1.0"})
            html = urllib.request.urlopen(req, timeout=30).read().decode("latin1")
            m = re.search(r"(\d+) decks matching", html)
            return int(m.group(1)) if m else 0
        except Exception:
            time.sleep(2 ** attempt)
    return None

cards = [c for c in json.load(open("data/cards.json")) if not c["type"].startswith("Basic")]
total = count("")  # an unrecognised name returns every deck
with ThreadPoolExecutor(4) as ex:
    for c, n in zip(cards, ex.map(lambda c: count(c["name"].split(" // ")[0]), cards)):
        c["decks"] = 0 if n and n >= total * 0.9 else n  # unrecognised names return ~every deck
cards.sort(key=lambda c: -(c["decks"] or 0))
json.dump({"total": total, "updated": time.strftime("%Y-%m-%d"), "cards": cards}, open("data/ranked.json", "w"))
print(total, sum(c["decks"] is None for c in cards), cards[:5])
