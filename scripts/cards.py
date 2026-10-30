# Fetch the card pool from Scryfall into data/cards.json
import json, time, urllib.request, urllib.parse

Q = "(e:MOR or e:ZEN or e:THS or e:DTK or e:EMN or e:DOM or e:IKO or e:VOW or e:WOE or e:BLB or e:FDN or e:FRA) -is:digital"
url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode({"q": Q, "unique": "cards", "order": "name"})
cards = []
while url:
    req = urllib.request.Request(url, headers={"User-Agent": "rotisserie-list/1.0", "Accept": "application/json"})
    page = json.load(urllib.request.urlopen(req))
    for c in page["data"]:
        face = c.get("card_faces", [c])[0]
        cards.append({
            "name": c["name"],
            "set": c["set"].upper(),
            "type": c.get("type_line", ""),
            "rarity": c["rarity"],
            "img": (c.get("image_uris") or face.get("image_uris") or {}).get("normal", ""),
            "url": c["scryfall_uri"].split("?")[0],
        })
    url = page.get("next_page")
    time.sleep(0.1)
json.dump(cards, open("data/cards.json", "w"), indent=0)
print(len(cards))
