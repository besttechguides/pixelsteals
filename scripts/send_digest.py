#!/usr/bin/env python3
"""Email today's deals to confirmed contacts via Resend. Env: RESEND_API_KEY, SIGNING_SECRET, WORKER_URL. DRY_RUN=1 to skip sending.
Optional IDEMPOTENCY_SUFFIX for same-day Resend keys. Variety mode: when Epic free titles match .github/last-epic, lead with free_other/deals instead."""
import json, os, hmac, hashlib, urllib.request, urllib.parse, html, datetime, sys
KEY=os.environ.get("RESEND_API_KEY"); SECRET=os.environ.get("SIGNING_SECRET",""); WORKER=os.environ.get("WORKER_URL","").rstrip("/")
DRY=os.environ.get("DRY_RUN")=="1"; FROM="PixelSteals <deals@pixelsteals.com>"; SITE="https://pixelsteals.com/"
LOADED="https://go.loaded.com/KBLBry"  # Loaded (formerly CDKeys) via Impact
AMZ_TAG="trustedtrad07-21"; AMAZON="https://www.amazon.co.uk/gp/goldbox?tag="+AMZ_TAG
LAST_EPIC=".github/last-epic"
IDEMPOTENCY_SUFFIX=os.environ.get("IDEMPOTENCY_SUFFIX","").strip()
def amazon_tag(u):
    p=urllib.parse.urlsplit(u)
    if not p.netloc.endswith("amazon.co.uk"): return u
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query) if k!="tag"]+[("tag",AMZ_TAG)]
    return urllib.parse.urlunsplit(p._replace(query=urllib.parse.urlencode(q)))
def loaded(dest=None): return LOADED+("?u="+urllib.parse.quote(dest,safe="") if dest else "")
if not DRY and not (KEY and SECRET and WORKER): print("Missing RESEND_API_KEY/SIGNING_SECRET/WORKER_URL; skipping send."); sys.exit(0)
def api(path, method="GET", body=None, headers=None):
    h={"Authorization":f"Bearer {KEY}","Content-Type":"application/json","User-Agent":"PixelSteals/1.0"}; h.update(headers or {})
    r=urllib.request.Request("https://api.resend.com"+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
    with urllib.request.urlopen(r,timeout=60) as x: return json.load(x)
d=json.load(open("deals.json"))
for _g in d["deals"]:
    _g["url"]=amazon_tag(_g["url"])
    if _g["store"].lower() in ("loaded","cdkeys","cdkeys.com"): _g["url"]=loaded("https://www.loaded.com/catalogsearch/result/?q="+urllib.parse.quote(_g["title"]))
UK={"Steam","GOG","Humble Store","GreenManGaming","Fanatical","Epic Games Store","Gamesplanet UK","WinGameStore"}
_ep={g["title"].lower() for g in d["epic"]}
deals=sorted([x for x in d["deals"] if x["title"].lower() not in _ep],key=lambda x:(x["store"] not in UK, x["store"]!="Gamesplanet UK", -x["savings"]))[:10]
e=html.escape
fo=d.get("free_other",[])[:6]
G="#39ff14"; BG="#0b0b10"; CARD="#15151d"; FONT="font-family:Arial,Helvetica,sans-serif"
TODAY=datetime.date.today(); DATELINE=f"{TODAY:%A} {TODAY.day} {TODAY:%B %Y}"
def ends(g):
    try: t=datetime.datetime.fromisoformat((g.get("ends") or "").replace("Z","+00:00")); return f"{t:%a} {t.day} {t:%b}"
    except Exception: return "soon"
def usd(v): return f"US${float(v):.2f}"
TOP=deals[0] if deals else None
def epic_title_list(): return sorted(g["title"] for g in d.get("epic", []))
def read_last_epic():
    try:
        with open(LAST_EPIC) as f: return sorted(line.strip() for line in f if line.strip())
    except FileNotFoundError: return []
def write_last_epic(titles):
    os.makedirs(os.path.dirname(LAST_EPIC) or ".", exist_ok=True)
    with open(LAST_EPIC,"w") as f:
        for t in sorted(titles): f.write(t+"\n")
# Variety when Epic freebies unchanged vs previous successful send
VARIETY=bool(d.get("epic")) and epic_title_list()==read_last_epic()
def preheader():
    p=[]
    if VARIETY:
        if fo: p.append(f'{fo[0]["title"]} free on {fo[0]["store"]}')
        if TOP: p.append(f'{TOP["title"]} -{TOP["savings"]}%')
    else:
        if d["epic"]: p.append(f'{d["epic"][0]["title"]} free on Epic')
        if TOP: p.append(f'{TOP["title"]} -{TOP["savings"]}%')
    return " + ".join(p)+f" and {len(deals)} more PC deals today"
def intro():
    s="Morning, deal hunters! "
    if VARIETY:
        if fo: s+=f'Other stores are giving away {", ".join(g["title"] for g in fo[:3])} free right now. '
        if TOP: s+=f'Top steal of the day: {TOP["title"]} at {TOP["savings"]}% off at {TOP["store"]}. '
        if d["epic"]: s+=f'Epic still has {", ".join(g["title"] for g in d["epic"])} free too. '
    else:
        if d["epic"]: s+=f'Epic is giving away {", ".join(g["title"] for g in d["epic"])} free right now. '
        if TOP: s+=f'Top steal of the day: {TOP["title"]} at {TOP["savings"]}% off at {TOP["store"]}. '
    return s+"Here's everything worth grabbing today."
def btn(url,label): return f'<a href="{e(url)}" style="display:inline-block;background:{G};color:#000;{FONT};font-size:14px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;text-decoration:none;padding:12px 22px;border-radius:4px">{label} &rarr;</a>'
def img(src,alt): return f'<img src="{e(src)}" alt="{e(alt)}" width="552" style="display:block;width:100%;max-width:552px;height:auto;border:0">' if src else ""
def head(t): return f'<tr><td style="padding:26px 24px 8px;{FONT};color:{G};font-size:13px;font-weight:bold;letter-spacing:2px;text-transform:uppercase">{t}</td></tr>'
def card(inner): return f'<tr><td style="padding:8px 24px 14px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD};border-top:4px solid {G}">{inner}</table></td></tr>'
def epic_section():
    rows=[]
    if not d["epic"]: return rows
    rows.append(head("&#127873; Free on Epic (UK)"))
    for g in d["epic"]:
        rows.append(card(f'<tr><td>{img(g.get("img"),g["title"])}</td></tr><tr><td style="padding:16px 18px 4px;{FONT}"><a href="{e(g["url"])}" style="color:#fff;text-decoration:none;font-size:21px;line-height:27px;font-weight:bold">{e(g["title"])}</a></td></tr><tr><td style="padding:4px 18px 12px;{FONT};color:{G};font-size:15px;font-weight:bold">FREE until {ends(g)}</td></tr><tr><td style="padding:0 18px 20px">{btn(g["url"],"Claim free")}</td></tr>'))
    return rows
def fo_section():
    rows=[]
    if not fo: return rows
    rows.append(head("&#127379; Free on other stores"))
    for g in fo:
        rows.append(card(f'<tr><td>{img(g.get("img"),g["title"])}</td></tr><tr><td style="padding:16px 18px 4px;{FONT}"><a href="{e(g["url"])}" style="color:#fff;text-decoration:none;font-size:19px;line-height:25px;font-weight:bold">{e(g["title"])}</a></td></tr><tr><td style="padding:4px 18px 12px;{FONT};color:{G};font-size:15px;font-weight:bold">FREE {("until "+ends(g)) if g.get("ends") else "for a limited time"} <span style="color:#9a9aa8;font-weight:normal">&middot; {e(g["store"])}</span></td></tr><tr><td style="padding:0 18px 18px">{btn(g["url"],"Claim free")}</td></tr>'))
    rows.append(f'<tr><td style="padding:0 24px 4px;{FONT};color:#9a9aa8;font-size:12px">Other-store giveaways via <a href="https://www.gamerpower.com" style="color:#9a9aa8">GamerPower</a>. Check each store page for terms.</td></tr>')
    return rows
def deals_section():
    rows=[head("&#128293; Today&rsquo;s top PC deals")]
    for g in deals:
        rows.append(card(f'<tr><td>{img(g.get("img"),g["title"])}</td></tr><tr><td style="padding:14px 18px 4px;{FONT}"><span style="display:inline-block;background:#ff2e63;color:#fff;font-weight:bold;font-size:13px;padding:3px 8px;border-radius:3px">-{g["savings"]}%</span> <a href="{e(g["url"])}" style="color:#fff;text-decoration:none;font-size:19px;line-height:25px;font-weight:bold">{e(g["title"])}</a></td></tr><tr><td style="padding:6px 18px 12px;{FONT};color:#cfcfcf;font-size:15px"><b style="color:{G};font-size:18px">{usd(g["sale"])}</b> <s style="color:#77778a">{usd(g["normal"])}</s> &middot; at {e(g["store"])}</td></tr><tr><td style="padding:0 18px 18px">{btn(g["url"],"Get deal")}</td></tr>'))
    return rows
def body(unsub):
    out=[]
    out.append(f'<div style="display:none;max-height:0;overflow:hidden">{e(preheader())}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;</div>')
    out.append(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BG}"><tr><td align="center" style="padding:20px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{BG}">')
    out.append(f'<tr><td style="padding:24px 24px 4px;{FONT};font-size:34px;font-weight:900;letter-spacing:4px;color:#fff">PIXEL<span style="color:{G}">STEALS</span></td></tr>')
    out.append(f'<tr><td style="padding:0 24px 6px;{FONT};color:#9a9aa8;font-size:13px">Today&rsquo;s PixelSteals &middot; {DATELINE}</td></tr>')
    out.append(f'<tr><td style="padding:0 24px 4px;{FONT};color:#77778a;font-size:11px">#ad &ndash; contains affiliate links; we may earn a commission at no extra cost to you. <a href="{SITE}affiliate.html" style="color:#9a9aa8">Disclosure</a></td></tr>')
    out.append(f'<tr><td style="padding:18px 24px 6px;{FONT};color:#e6e6e6;font-size:16px;line-height:25px">{e(intro())}</td></tr>')
    if VARIETY:
        out+=fo_section()+deals_section()+epic_section()
    else:
        out+=epic_section()+fo_section()+deals_section()
    out.append(head("&#127918; Partner pick"))
    out.append(card(f'<tr><td style="padding:16px 18px 4px;{FONT}"><a href="{e(LOADED)}" style="color:#fff;text-decoration:none;font-size:19px;line-height:25px;font-weight:bold">Cheap game keys at Loaded</a> <span style="color:#77778a;font-size:12px">#ad</span></td></tr><tr><td style="padding:4px 18px 12px;{FONT};color:#cfcfcf;font-size:14px;line-height:21px">Loaded (formerly CDKeys) sells digital PC game keys, console credit and gift cards with instant email delivery. Check the region on the product page before you buy.</td></tr><tr><td style="padding:0 18px 18px">{btn(LOADED,"Browse Loaded")}</td></tr>'))
    out.append(card(f'<tr><td style="padding:16px 18px 4px;{FONT}"><a href="{e(AMAZON)}" style="color:#fff;text-decoration:none;font-size:19px;line-height:25px;font-weight:bold">Game deals on Amazon UK</a> <span style="color:#77778a;font-size:12px">#ad</span></td></tr><tr><td style="padding:4px 18px 12px;{FONT};color:#cfcfcf;font-size:14px;line-height:21px">Today&rsquo;s Amazon UK deals on games, consoles and accessories.</td></tr><tr><td style="padding:0 18px 18px">{btn(AMAZON,"See Amazon deals")}</td></tr>'))
    out.append(f'<tr><td style="padding:10px 24px 4px;{FONT};color:#9a9aa8;font-size:12px">Prices in US dollars from CheapShark; UK prices in &pound; may differ, so check before buying.</td></tr>')
    out.append(f'<tr><td align="center" style="padding:22px 24px">{btn(SITE,"See all deals at pixelsteals.com")}</td></tr>')
    out.append(f'<tr><td style="padding:0 24px 10px;{FONT};color:#cfcfcf;font-size:14px;line-height:22px">Want more? Browse our <a href="{SITE}guides/" style="color:{G}">free-to-play picks and buying guides</a>. Discord alerts are coming soon.</td></tr>')
    out.append(f'<tr><td style="padding:8px 24px 24px;{FONT};color:#fff;font-size:15px">Happy hunting,<br><b>The PixelSteals team</b></td></tr>')
    out.append(f'<tr><td style="padding:16px 24px 30px;border-top:1px solid #222;{FONT};color:#77778a;font-size:12px;line-height:18px">Follow us: <a href="https://www.instagram.com/pixelsteals/" style="color:#9a9aa8">Instagram</a> &middot; <a href="https://www.tiktok.com/@pixel.steals" style="color:#9a9aa8">TikTok</a> &middot; <a href="https://www.facebook.com/profile.php?id=61595512350372" style="color:#9a9aa8">Facebook</a> &middot; <a href="https://bsky.app/profile/pixelsteals.bsky.social" style="color:#9a9aa8">Bluesky</a><br>You&rsquo;re getting this because you confirmed a PixelSteals subscription at pixelsteals.com. <a href="{e(unsub)}" style="color:#9a9aa8">Unsubscribe</a> &middot; <a href="{SITE}privacy.html" style="color:#9a9aa8">Privacy</a><br>Some links are affiliate links; we may earn a commission at no extra cost to you. As an Amazon Associate we earn from qualifying purchases. <a href="{SITE}affiliate.html" style="color:#9a9aa8">Affiliate disclosure</a></td></tr>')
    out.append('</table></td></tr></table>')
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;padding:0;background:{BG}">'+"".join(out)+'</body></html>'
def text(unsub):
    L=[f"PIXELSTEALS - {DATELINE}","#ad - contains affiliate links. As an Amazon Associate we earn from qualifying purchases. Disclosure: "+SITE+"affiliate.html","",intro(),""]
    def epic_text():
        if not d["epic"]: return []
        return ["FREE ON EPIC (UK)"]+[f'- {g["title"]} - FREE until {ends(g)}\n  {g["url"]}' for g in d["epic"]]+[""]
    def fo_text():
        if not fo: return []
        return ["FREE ON OTHER STORES (via GamerPower)"]+[f'- {g["title"]} ({g["store"]}) - FREE '+(f'until {ends(g)}' if g.get("ends") else 'for a limited time')+f'\n  {g["url"]}' for g in fo]+[""]
    def deals_text():
        return ["TODAY'S TOP PC DEALS"]+[f'- {g["title"]} -{g["savings"]}%: {usd(g["sale"])} (was {usd(g["normal"])}) at {g["store"]}\n  {g["url"]}' for g in deals]
    if VARIETY: L+=fo_text()+deals_text()+([""] if deals else [])+epic_text()
    else: L+=epic_text()+fo_text()+deals_text()
    L+=["","Prices in US dollars from CheapShark; UK prices may differ.","PARTNER PICK (#ad): Cheap game keys at Loaded (formerly CDKeys)","  "+LOADED,"PARTNER PICK (#ad): Game deals on Amazon UK","  "+AMAZON,"","All deals: "+SITE,"Follow us: Instagram @pixelsteals, TikTok @pixel.steals, Facebook https://www.facebook.com/profile.php?id=61595512350372, Bluesky @pixelsteals.bsky.social","","Happy hunting,","The PixelSteals team","",f"Unsubscribe: {unsub}",f"Privacy: {SITE}privacy.html","Some links are affiliate links; we may earn a commission at no extra cost to you. As an Amazon Associate we earn from qualifying purchases."]
    return "\n".join(L)
def unsub_link(email):
    t=hmac.new(SECRET.encode(),("unsub:"+email).encode(),hashlib.sha256).hexdigest()[:32]
    return f"{WORKER}/unsubscribe?e={urllib.parse.quote(email)}&t={t}"
contacts=[]; after=None
while not DRY:
    q="/contacts?limit=100"+(f"&after={after}" if after else ""); r=api(q); contacts+=r.get("data",[])
    if not r.get("has_more"): break
    after=r["data"][-1]["id"]
confirmed=[c["email"] for c in contacts if c.get("unsubscribed") is False]
max_sav=max([g["savings"] for g in deals] or [0]); n=len(deals)
if VARIETY:
    if fo: subject=f"🎁 {fo[0]['title']} free + {n} PC deals up to -{max_sav}%"
    elif TOP: subject=f"🔥 {TOP['title']} −{TOP['savings']}% + {n} PC deals"
    else: subject=f"🔥 {n} PC deals up to -{max_sav}%"
else:
    subject=(f"🎁 {d['epic'][0]['title']} free on Epic + " if d["epic"] else "🔥 ")+f"{n} PC deals up to -{max_sav}%"
msgs=[{"from":FROM,"to":[m],"subject":subject,"html":body(unsub_link(m)),"text":text(unsub_link(m)),
       "headers":{"List-Unsubscribe":f"<{unsub_link(m)}>","List-Unsubscribe-Post":"List-Unsubscribe=One-Click"}} for m in confirmed]
if DRY:
    u="https://example.invalid/unsub"; print("VARIETY="+str(VARIETY)); print("Subject: "+subject); print(body(u))
    if os.environ.get("DRY_TEXT"): open(os.environ["DRY_TEXT"],"w").write("Subject: "+subject+"\nVARIETY="+str(VARIETY)+"\n\n"+text(u))
    sys.exit(0)
UKDATE=datetime.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/London")).date()
print(f"{len(confirmed)} confirmed contacts"); print("VARIETY="+str(VARIETY)); print("Subject: "+subject)
ikey=f"digest-{UKDATE}"+(f"-{IDEMPOTENCY_SUFFIX}" if IDEMPOTENCY_SUFFIX else "")
for i in range(0,len(msgs),100):
    api("/emails/batch","POST",msgs[i:i+100],{"Idempotency-Key":f"{ikey}-{i}"})
print("sent", len(msgs))
write_last_epic(epic_title_list())
