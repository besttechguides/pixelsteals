#!/usr/bin/env python3
"""Fetch free deal data: Epic free games + CheapShark deals (CheapShark redirect links only)."""
import json, urllib.request, datetime
UA={"User-Agent":"PixelSteals/1.0 (+https://besttechguides.github.io/pixelsteals)"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30) as r: return json.load(r)
out={"updated":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),"epic":[],"epic_upcoming":[],"free_other":[],"deals":[]}
try:
    d=get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-GB&country=GB&allowCountries=GB")
    for e in d["data"]["Catalog"]["searchStore"]["elements"]:
        p=(e.get("promotions") or {}).get("promotionalOffers") or []
        offers=[o for g in p for o in g.get("promotionalOffers",[]) if o.get("discountSetting",{}).get("discountPercentage")==0]
        up=[o for g in ((e.get("promotions") or {}).get("upcomingPromotionalOffers") or []) for o in g.get("promotionalOffers",[]) if o.get("discountSetting",{}).get("discountPercentage")==0]
        if not offers and up:
            out["epic_upcoming"].append({"title":e["title"],"starts":up[0].get("startDate"),"ends":up[0].get("endDate")}); continue
        if not offers: continue
        slug=None
        for m in (e.get("catalogNs") or {}).get("mappings") or []: slug=slug or m.get("pageSlug")
        slug=slug or e.get("productSlug") or e.get("urlSlug")
        img=next((i["url"] for i in e.get("keyImages",[]) if i["type"] in("OfferImageWide","Thumbnail","DieselStoreFrontWide")),"")
        out["epic"].append({"title":e["title"],"ends":offers[0].get("endDate"),"url":f"https://store.epicgames.com/en-GB/p/{slug}" if slug else "https://store.epicgames.com/en-GB/free-games","img":img})
except Exception as ex: print("epic error",ex)
try:
    stores={s["storeID"]:s["storeName"] for s in get("https://www.cheapshark.com/api/1.0/stores")}
    for x in get("https://www.cheapshark.com/api/1.0/deals?pageSize=24&sortBy=Deal%20Rating&onSale=1&metacritic=70"):
        out["deals"].append({"title":x["title"],"store":stores.get(x["storeID"],""),"sale":x["salePrice"],"normal":x["normalPrice"],
          "savings":round(float(x["savings"])),"url":"https://www.cheapshark.com/redirect?dealID="+x["dealID"],"img":x["thumb"]})
except Exception as ex: print("cheapshark error",ex)
try:
    # Free games on other stores via GamerPower (https://www.gamerpower.com). Epic is covered by Epic's own feed above.
    import re
    BAD=re.compile(r"\b(dlc|beta|loot|early access|key giveaway|free[- ]to[- ]play|f2p|demo|playtest|add-?on|expansion|bundle|pack)\b",re.I)
    seen={g["title"].lower() for g in out["epic"]}
    now=datetime.datetime.now(datetime.timezone.utc)
    for x in get("https://www.gamerpower.com/api/giveaways?platform=pc&type=game"):
        raw=x.get("title","")
        if x.get("type")!="Game" or x.get("status")!="Active": continue
        m=re.search(r"\(([^)]+)\)",raw)
        store=(m.group(1) if m else "").strip()
        if not store or "epic" in store.lower() or "epic games" in (x.get("platforms") or "").lower(): continue
        store={"Indiegala":"IndieGala","Itch.io":"itch.io"}.get(store,store)
        title=re.sub(r"\s*\([^)]*\)\s*(Key\s+)?Giveaway\s*$","",raw,flags=re.I).strip() or raw
        if BAD.search(raw) or BAD.search(x.get("description","")[:160]): continue
        if title.lower() in seen: continue
        ends=None
        ed=x.get("end_date") or ""
        if re.match(r"\d{4}-\d\d-\d\d",ed):
            t=datetime.datetime.strptime((ed+" 23:59:59")[:10]+" "+(ed[11:19] if len(ed)>=19 else "23:59:59"),"%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
            if t<=now: continue
            ends=t.strftime("%Y-%m-%dT%H:%M:%SZ")
        url=x.get("open_giveaway_url") or x.get("gamerpower_url")
        if not url: continue
        seen.add(title.lower())
        out["free_other"].append({"title":title,"store":store,"url":url,"img":x.get("image") or x.get("thumbnail") or "","ends":ends})
    out["free_other"].sort(key=lambda g:(g["ends"] is None,g["ends"] or ""))
    out["free_other"]=out["free_other"][:12]
except Exception as ex: print("gamerpower error",ex)
json.dump(out,open("deals.json","w"),indent=1)
print(len(out["epic"]),"epic",len(out["free_other"]),"free_other",len(out["deals"]),"deals")
