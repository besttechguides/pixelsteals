#!/usr/bin/env python3
"""Fetch free deal data: Epic free games + CheapShark deals (CheapShark redirect links only)."""
import json, urllib.request, datetime
UA={"User-Agent":"PixelSteals/1.0 (+https://besttechguides.github.io/pixelsteals)"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30) as r: return json.load(r)
out={"updated":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),"epic":[],"epic_upcoming":[],"deals":[]}
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
json.dump(out,open("deals.json","w"),indent=1)
print(len(out["epic"]),"epic",len(out["deals"]),"deals")
