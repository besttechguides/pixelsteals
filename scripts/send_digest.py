#!/usr/bin/env python3
"""Email today's deals to confirmed contacts via Resend. Env: RESEND_API_KEY, SIGNING_SECRET, WORKER_URL. DRY_RUN=1 to skip sending."""
import json, os, hmac, hashlib, urllib.request, urllib.parse, html, datetime, sys
KEY=os.environ.get("RESEND_API_KEY"); SECRET=os.environ.get("SIGNING_SECRET",""); WORKER=os.environ.get("WORKER_URL","").rstrip("/")
DRY=os.environ.get("DRY_RUN")=="1"; FROM="PixelSteals <deals@pixelsteals.com>"; SITE="https://pixelsteals.com/"
if not DRY and not (KEY and SECRET and WORKER): print("Missing RESEND_API_KEY/SIGNING_SECRET/WORKER_URL; skipping send."); sys.exit(0)
def api(path, method="GET", body=None, headers=None):
    h={"Authorization":f"Bearer {KEY}","Content-Type":"application/json","User-Agent":"PixelSteals/1.0"}; h.update(headers or {})
    r=urllib.request.Request("https://api.resend.com"+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
    with urllib.request.urlopen(r,timeout=60) as x: return json.load(x)
d=json.load(open("deals.json"))
UK={"Steam","GOG","Humble Store","GreenManGaming","Fanatical","Epic Games Store","Gamesplanet UK","WinGameStore"}
_ep={g["title"].lower() for g in d["epic"]}
deals=sorted([x for x in d["deals"] if x["title"].lower() not in _ep],key=lambda x:(x["store"] not in UK, x["store"]!="Gamesplanet UK", -x["savings"]))[:10]
e=html.escape
G="#39ff14"; BG="#0b0b10"; CARD="#15151d"; FONT="font-family:Arial,Helvetica,sans-serif"
TODAY=datetime.date.today(); DATELINE=f"{TODAY:%A} {TODAY.day} {TODAY:%B %Y}"
def ends(g):
    try: t=datetime.datetime.fromisoformat((g.get("ends") or "").replace("Z","+00:00")); return f"{t:%a} {t.day} {t:%b}"
    except Exception: return "soon"
def usd(v): return f"US${float(v):.2f}"
TOP=deals[0] if deals else None
def preheader():
    p=[]
    if d["epic"]: p.append(f'{d["epic"][0]["title"]} free on Epic')
    if TOP: p.append(f'{TOP["title"]} -{TOP["savings"]}%')
    return " + ".join(p)+f" and {len(deals)} more PC deals today"
def intro():
    s="Morning, deal hunters! "
    if d["epic"]: s+=f'Epic is giving away {", ".join(g["title"] for g in d["epic"])} free right now. '
    if TOP: s+=f'Top steal of the day: {TOP["title"]} at {TOP["savings"]}% off at {TOP["store"]}. '
    return s+"Here's everything worth grabbing today."
def btn(url,label): return f'<a href="{e(url)}" style="display:inline-block;background:{G};color:#000;{FONT};font-size:14px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;text-decoration:none;padding:12px 22px;border-radius:4px">{label} &rarr;</a>'
def img(src,alt): return f'<img src="{e(src)}" alt="{e(alt)}" width="552" style="display:block;width:100%;max-width:552px;height:auto;border:0">' if src else ""
def head(t): return f'<tr><td style="padding:26px 24px 8px;{FONT};color:{G};font-size:13px;font-weight:bold;letter-spacing:2px;text-transform:uppercase">{t}</td></tr>'
def card(inner): return f'<tr><td style="padding:8px 24px 14px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD};border-top:4px solid {G}">{inner}</table></td></tr>'
def body(unsub):
    out=[]
    out.append(f'<div style="display:none;max-height:0;overflow:hidden">{e(preheader())}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;</div>')
    out.append(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BG}"><tr><td align="center" style="padding:20px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{BG}">')
    out.append(f'<tr><td style="padding:24px 24px 4px;{FONT};font-size:34px;font-weight:900;letter-spacing:4px;color:#fff">PIXEL<span style="color:{G}">STEALS</span></td></tr>')
    out.append(f'<tr><td style="padding:0 24px 6px;{FONT};color:#9a9aa8;font-size:13px">Today&rsquo;s PixelSteals &middot; {DATELINE}</td></tr>')
    out.append(f'<tr><td style="padding:0 24px 4px;{FONT};color:#77778a;font-size:11px">#ad &ndash; contains affiliate links; we may earn a commission at no extra cost to you. <a href="{SITE}affiliate.html" style="color:#9a9aa8">Disclosure</a></td></tr>')
    out.append(f'<tr><td style="padding:18px 24px 6px;{FONT};color:#e6e6e6;font-size:16px;line-height:25px">{e(intro())}</td></tr>')
    if d["epic"]:
        out.append(head("&#127873; Free on Epic (UK)"))
        for g in d["epic"]:
            out.append(card(f'<tr><td>{img(g.get("img"),g["title"])}</td></tr><tr><td style="padding:16px 18px 4px;{FONT}"><a href="{e(g["url"])}" style="color:#fff;text-decoration:none;font-size:21px;line-height:27px;font-weight:bold">{e(g["title"])}</a></td></tr><tr><td style="padding:4px 18px 12px;{FONT};color:{G};font-size:15px;font-weight:bold">FREE until {ends(g)}</td></tr><tr><td style="padding:0 18px 20px">{btn(g["url"],"Claim free")}</td></tr>'))
    out.append(head("&#128293; Today&rsquo;s top PC deals"))
    for g in deals:
        out.append(card(f'<tr><td>{img(g.get("img"),g["title"])}</td></tr><tr><td style="padding:14px 18px 4px;{FONT}"><span style="display:inline-block;background:#ff2e63;color:#fff;font-weight:bold;font-size:13px;padding:3px 8px;border-radius:3px">-{g["savings"]}%</span> <a href="{e(g["url"])}" style="color:#fff;text-decoration:none;font-size:19px;line-height:25px;font-weight:bold">{e(g["title"])}</a></td></tr><tr><td style="padding:6px 18px 12px;{FONT};color:#cfcfcf;font-size:15px"><b style="color:{G};font-size:18px">{usd(g["sale"])}</b> <s style="color:#77778a">{usd(g["normal"])}</s> &middot; at {e(g["store"])}</td></tr><tr><td style="padding:0 18px 18px">{btn(g["url"],"Get deal")}</td></tr>'))
    out.append(f'<tr><td style="padding:10px 24px 4px;{FONT};color:#9a9aa8;font-size:12px">Prices in US dollars from CheapShark; UK prices in &pound; may differ, so check before buying.</td></tr>')
    out.append(f'<tr><td align="center" style="padding:22px 24px">{btn(SITE,"See all deals at pixelsteals.com")}</td></tr>')
    out.append(f'<tr><td style="padding:0 24px 10px;{FONT};color:#cfcfcf;font-size:14px;line-height:22px">Want more? Browse our <a href="{SITE}guides/" style="color:{G}">free-to-play picks and buying guides</a>. Discord alerts are coming soon.</td></tr>')
    out.append(f'<tr><td style="padding:8px 24px 24px;{FONT};color:#fff;font-size:15px">Happy hunting,<br><b>The PixelSteals team</b></td></tr>')
    out.append(f'<tr><td style="padding:16px 24px 30px;border-top:1px solid #222;{FONT};color:#77778a;font-size:12px;line-height:18px">You&rsquo;re getting this because you confirmed a PixelSteals subscription at pixelsteals.com. <a href="{e(unsub)}" style="color:#9a9aa8">Unsubscribe</a> &middot; <a href="{SITE}privacy.html" style="color:#9a9aa8">Privacy</a></td></tr>')
    out.append('</table></td></tr></table>')
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;padding:0;background:{BG}">'+"".join(out)+'</body></html>'
def text(unsub):
    L=[f"PIXELSTEALS - {DATELINE}","#ad - contains affiliate links: "+SITE+"affiliate.html","",intro(),""]
    if d["epic"]:
        L.append("FREE ON EPIC (UK)"); L+= [f'- {g["title"]} - FREE until {ends(g)}\n  {g["url"]}' for g in d["epic"]]; L.append("")
    L.append("TODAY'S TOP PC DEALS"); L+=[f'- {g["title"]} -{g["savings"]}%: {usd(g["sale"])} (was {usd(g["normal"])}) at {g["store"]}\n  {g["url"]}' for g in deals]
    L+=["","Prices in US dollars from CheapShark; UK prices may differ.","All deals: "+SITE,"","Happy hunting,","The PixelSteals team","",f"Unsubscribe: {unsub}",f"Privacy: {SITE}privacy.html"]
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
subject=(f"🎁 {d['epic'][0]['title']} free on Epic + " if d["epic"] else "🔥 ")+f"{len(deals)} PC deals up to -{max([g['savings'] for g in deals] or [0])}%"
msgs=[{"from":FROM,"to":[m],"subject":subject,"html":body(unsub_link(m)),"text":text(unsub_link(m)),
       "headers":{"List-Unsubscribe":f"<{unsub_link(m)}>","List-Unsubscribe-Post":"List-Unsubscribe=One-Click"}} for m in confirmed]
if DRY:
    u="https://example.invalid/unsub"; print(body(u))
    if os.environ.get("DRY_TEXT"): open(os.environ["DRY_TEXT"],"w").write("Subject: "+subject+"\n\n"+text(u))
    sys.exit(0)
print(f"{len(confirmed)} confirmed contacts")
for i in range(0,len(msgs),100):
    api("/emails/batch","POST",msgs[i:i+100],{"Idempotency-Key":f"digest-{datetime.date.today()}-{i}"})
print("sent", len(msgs))
