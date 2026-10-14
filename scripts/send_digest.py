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
deals=sorted(d["deals"],key=lambda x:(x["store"] not in UK, x["store"]!="Gamesplanet UK", -x["savings"]))[:10]
e=html.escape
def body(unsub):
    rows="".join(f'<li><a href="{e(g["url"])}"><b>{e(g["title"])}</b></a> – FREE until {e((g.get("ends") or "")[:10])}</li>' for g in d["epic"])
    rows2="".join(f'<li><a href="{e(g["url"])}">{e(g["title"])}</a> – ${e(g["sale"])} <s>${e(g["normal"])}</s> (−{g["savings"]}%) at {e(g["store"])}</li>' for g in deals)
    return f"""<div style="font-family:system-ui;max-width:600px"><p><b>#ad</b> – this email may contain affiliate links; we may earn a commission at no extra cost to you. <a href="{SITE}affiliate.html">Disclosure</a>.</p>
<h2>🎁 Free on Epic (UK)</h2><ul>{rows or '<li>No freebies today.</li>'}</ul><h2>🔥 Today's top PC deals</h2><ul>{rows2}</ul>
<p style="font-size:12px;color:#666">Prices shown in USD from CheapShark; UK store prices in GBP may differ – check before buying. You're getting this because you confirmed a PixelSteals subscription. <a href="{unsub}">Unsubscribe</a> · <a href="{SITE}privacy.html">Privacy</a></p></div>"""
def unsub_link(email):
    t=hmac.new(SECRET.encode(),("unsub:"+email).encode(),hashlib.sha256).hexdigest()[:32]
    return f"{WORKER}/unsubscribe?e={urllib.parse.quote(email)}&t={t}"
contacts=[]; after=None
while not DRY:
    q="/contacts?limit=100"+(f"&after={after}" if after else ""); r=api(q); contacts+=r.get("data",[])
    if not r.get("has_more"): break
    after=r["data"][-1]["id"]
confirmed=[c["email"] for c in contacts if c.get("unsubscribed") is False]
subject=f"PixelSteals {datetime.date.today():%d %b}: {len(d['epic'])} free + {len(deals)} deals"
msgs=[{"from":FROM,"to":[m],"subject":subject,"html":body(unsub_link(m)),
       "headers":{"List-Unsubscribe":f"<{unsub_link(m)}>","List-Unsubscribe-Post":"List-Unsubscribe=One-Click"}} for m in confirmed]
if DRY: print(body("https://example.invalid/unsub")); sys.exit(0)
print(f"{len(confirmed)} confirmed contacts")
for i in range(0,len(msgs),100):
    api("/emails/batch","POST",msgs[i:i+100],{"Idempotency-Key":f"digest-{datetime.date.today()}-{i}"})
print("sent", len(msgs))
