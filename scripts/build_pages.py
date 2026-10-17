#!/usr/bin/env python3
"""Build PixelSteals content pages. Static guides + data pages regenerated from deals.json."""
import json, re, html, datetime, os, urllib.parse
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
e = html.escape
LOADED = "https://go.loaded.com/KBLBry"  # Loaded (formerly CDKeys) via Impact
def loaded(dest=None): return LOADED + ("?u=" + urllib.parse.quote(dest, safe="") if dest else "")
AMZ_TAG = "trustedtrad07-21"; AMAZON = "https://www.amazon.co.uk/gp/goldbox?tag=" + AMZ_TAG
def amazon_tag(u):  # tag an existing amazon.co.uk product link with our Associates tag
    p = urllib.parse.urlsplit(u)
    if not p.netloc.endswith("amazon.co.uk"): return u
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if k != "tag"] + [("tag", AMZ_TAG)]
    return urllib.parse.urlunsplit(p._replace(query=urllib.parse.urlencode(q)))
SPON = 'rel="sponsored nofollow noopener" target="_blank"'
idx = open("index.html").read()
STYLE = re.search(r"<style>.*?</style>", idx, re.S).group(0)
ADS = re.search(r'<script async src="https://pagead2\.googlesyndication\.com[^>]*></script>', idx)
ADS = ADS.group(0) if ADS else ""
EXTRA = "<style>nav a{margin-right:16px;text-decoration:none}article{max-width:760px}article h2{margin-top:1.6em}table{border-collapse:collapse;width:100%;margin:1em 0}td,th{border-bottom:1px solid #223;padding:8px;text-align:left}.date{color:var(--m);font-size:.9rem}</style>"
NAV = '<nav><a href="/">Deals</a><a href="/guides/">Guides</a><a href="/about.html">About</a><a href="/contact.html">Contact</a></nav>'
FOOT = '<footer class="w"><p>PixelSteals is independent and not affiliated with Epic Games, Valve, Microsoft or any store. <a href="/affiliate.html">Affiliate disclosure</a> · <a href="/privacy.html">Privacy policy</a> · <a href="/about.html">About</a> · <a href="/contact.html">Contact</a> · <a href="'+LOADED+'" '+SPON+'>Partner: Loaded</a> · <a href="'+AMAZON+'" '+SPON+'>Game deals on Amazon UK</a></p><p>Some links are affiliate links; we may earn a commission at no extra cost to you. As an Amazon Associate we earn from qualifying purchases. Deal data via <a href="https://www.cheapshark.com">CheapShark</a> and the Epic Games Store. Prices change fast; always check the store before buying.</p></footer>'
def page(path, title, desc, body):
    h = (f"<!doctype html><html lang=en-GB><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
         f"<title>{e(title)} – PixelSteals</title><meta name=description content=\"{e(desc)}\"><link rel=canonical href=\"https://pixelsteals.com/{path.replace('index.html','')}\">"
         f"{STYLE}{EXTRA}{ADS}</head><body><header class=w><a class=logo href=/>Pixel<span>Steals</span></a> {NAV}</header>"
         f"<main class=w><article>{body}</article></main>{FOOT}</body></html>")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True); open(path, "w").write(h)

d = json.load(open("deals.json"))
upd = datetime.datetime.strptime(d["updated"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=datetime.timezone.utc)
def ukdate(iso):
    if not iso: return "unknown"
    t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    # UK local time: BST (UTC+1) from last Sunday in March to last Sunday in October
    def lastsun(m): x = datetime.datetime(t.year, m, 31, 1, tzinfo=datetime.timezone.utc); return x - datetime.timedelta(days=(x.weekday() + 1) % 7)
    bst = lastsun(3) <= t < lastsun(10); t = t + datetime.timedelta(hours=1 if bst else 0)
    return t.strftime("%-d %B %Y, %H:%M ") + ("BST" if bst else "GMT")
STAMP = f'<p class=date>Last updated: {ukdate(d["updated"])} (data refreshed automatically every day).</p>'
TODAY = "14 October 2026"

# ---------- Epic free games (data page) ----------
cur = "".join(f'<tr><td><a href="{e(g["url"])}" rel=noopener>{e(g["title"])}</a></td><td>Free to claim until {e(ukdate(g["ends"]))}</td></tr>' for g in d["epic"]) or "<tr><td colspan=2>Epic isn't listing a free game right now.</td></tr>"
nxt = "".join(f'<tr><td>{e(g["title"])}</td><td>{e(ukdate(g["starts"]))} to {e(ukdate(g["ends"]))}</td></tr>' for g in d.get("epic_upcoming", [])) or "<tr><td colspan=2>Epic hasn't announced the next free games yet.</td></tr>"
page("guides/free-epic-games.html", "Free Epic Games Store games right now (UK)", "Which games are free on the Epic Games Store right now in the UK, when they end, what's next and how to claim them.", f"""
<h1>Free Epic Games Store games right now (UK)</h1>{STAMP}
<p>The Epic Games Store gives away PC games on a regular rotating schedule. Once you claim a game during its free window it stays in your Epic library permanently, even after the promotion ends. This page is generated straight from Epic's own free-games feed for the UK store, so the titles and times below are the ones Epic is publishing, converted to UK time.</p>
<h2>Free to claim now</h2><table><tr><th>Game</th><th>Offer window</th></tr>{cur}</table>
<h2>Coming next</h2><table><tr><th>Game</th><th>Free window</th></tr>{nxt}</table>
<p>Epic's free games usually switch over on a Thursday at 15:00 UTC, which is 4pm in the UK during British Summer Time and 3pm in winter (GMT). If a window above ends at that time, set a reminder for the afternoon so you don't miss it.</p>
<h2>How to claim a free Epic game</h2>
<ol><li>Create a free account at <a href="https://store.epicgames.com/en-GB/free-games">store.epicgames.com</a> (or sign in with an existing one). Turning on two-factor authentication is worth doing: it protects your library and Epic has historically required it for some promotions.</li>
<li>Open the game's store page from the table above and click <strong>Get</strong>. The price should show as £0.00 at checkout.</li>
<li>Complete the checkout. You won't be asked for card details for a £0 order.</li>
<li>The game now sits in your library. You can download it straight away or months later; claiming is what matters, not installing.</li></ol>
<h2>Things worth knowing</h2>
<ul><li><strong>You need to claim inside the window.</strong> There's no way to add a game after the offer ends without paying.</li>
<li><strong>Age ratings apply.</strong> Some games are rated PEGI 16 or 18, and accounts with parental controls may not be able to claim them.</li>
<li><strong>Mobile freebies are separate.</strong> Epic also runs free games on its mobile store in some regions. This page covers the PC store.</li>
<li><strong>Free doesn't always mean full content.</strong> Occasionally the giveaway is a DLC pack or an edition that needs a base game. The store page says so; read it before you rely on it.</li>
<li><strong>Watch out for scams.</strong> The only place to claim is the official Epic store or launcher. Ignore messages offering "free Epic codes" via links or Discord DMs.</li></ul>
<h2>Is it worth bothering?</h2>
<p>For most PC players, yes. Claiming takes a minute, costs nothing and builds a backlog you can dip into whenever you want something new to play. Many past giveaways have been well-reviewed indie games and the occasional big-name title, so it's a genuinely good habit if you play on PC. If you'd rather not check every week, the free <a href="/">PixelSteals daily email</a> lists each new Epic freebie alongside the day's best PC deals.</p>
<p>Want to pay as little as possible for everything else? Read our guide to <a href="/guides/cheap-pc-games-uk.html">getting PC games cheap, legally, in the UK</a>.</p>""")

# ---------- Weekly deals (data page) ----------
deals = sorted(d["deals"], key=lambda x: -x["savings"])
for g in deals:  # if a deal is ever from Loaded/CDKeys, send it through our tracked deep link
    g["url"] = amazon_tag(g["url"])
    if g["store"].lower() in ("loaded", "cdkeys", "cdkeys.com"): g["url"] = loaded("https://www.loaded.com/catalogsearch/result/?q=" + urllib.parse.quote(g["title"]))
PARTNER = (f'<h2>Partner pick: Loaded</h2><p><a href="{loaded("https://www.loaded.com/pc")}" {SPON}>Loaded (formerly CDKeys)</a> <small>#ad</small> sells digital PC game keys, console credit and gift cards with email delivery. '
           'It isn\'t tracked by CheapShark, so its prices aren\'t in the table above; it\'s worth a look when comparing. Check the region on the product page before you buy.</p>'
           f'<p>Console or accessories instead? See <a href="{AMAZON}" {SPON}>today\'s game deals on Amazon UK</a> <small>#ad</small>. As an Amazon Associate we earn from qualifying purchases.</p>')
rows = "".join(f'<tr><td><a href="{e(g["url"])}" rel="noopener sponsored">{e(g["title"])}</a></td><td>{e(g["store"])}</td><td>${e(g["sale"])}</td><td><s>${e(g["normal"])}</s></td><td>−{g["savings"]}%</td></tr>' for g in deals)
stores = sorted({g["store"] for g in deals})
under5 = [g for g in deals if float(g["sale"]) < 5]
page("guides/best-pc-game-deals.html", "This week's best PC game deals", "The best-rated PC game deals right now across Steam, GOG, Humble and other legitimate stores, updated daily.", f"""
<h1>This week's best PC game deals</h1>{STAMP}
<p>This list is rebuilt automatically every day from <a href="https://www.cheapshark.com">CheapShark</a>, a free price-comparison service that tracks legitimate digital stores. We filter for games that are on sale <em>and</em> have a Metacritic score of 70 or more, then sort by CheapShark's deal rating, which weighs the discount against the game's quality and its price history. Below they're ordered by discount.</p>
<p><strong>About the prices:</strong> CheapShark reports prices in US dollars. UK stores charge in pounds and the UK price isn't always a straight conversion, so treat the figures as a guide and check the price on the store page before you buy. Links go via CheapShark's own redirect links. <a href="/affiliate.html">#ad disclosure</a>.</p>
<h2>Today's list ({len(deals)} deals from {len(stores)} stores)</h2>
<table><tr><th>Game</th><th>Store</th><th>Sale (USD)</th><th>Normal</th><th>Saving</th></tr>{rows}</table>
<p>{len(under5)} of these are under $5 today. Stores in today's list: {e(", ".join(stores))}.</p>{PARTNER}
<h2>How to use a deal list like this</h2>
<ul><li><strong>Check the region.</strong> Keys from some stores are region-locked. All the stores tracked here sell to UK customers, but read the store page for any "not available in your region" note.</li>
<li><strong>Same game, several stores?</strong> Pick the store that delivers to the platform you use. A GOG copy is DRM-free and installs through GOG Galaxy or a plain installer; most other stores give you a Steam key.</li>
<li><strong>Look at what's included.</strong> "Complete", "GOTY" and "Definitive" editions often bundle DLC that's sold separately elsewhere.</li>
<li><strong>Look up the price history.</strong> A big percentage off isn't always the lowest price ever. CheapShark and IsThereAnyDeal both show price history so you can see whether it's worth waiting.</li>
<li><strong>Know your refund rights.</strong> Steam offers refunds within 14 days of purchase if you've played for under two hours. Other stores have their own policies; under UK law your right to cancel a digital download can end once you start downloading, if you agreed to that at checkout.</li></ul>
<p>Prefer free? See what's <a href="/guides/free-epic-games.html">free on the Epic Games Store right now</a>.</p>""")

# ---------- Static guides ----------
page("guides/cheap-pc-games-uk.html", "How to get PC games cheap, legally, in the UK", "A practical UK guide to paying less for PC games: seasonal sales, authorised key stores, bundles, freebies, subscriptions and how to avoid grey-market risks.", f"""
<h1>How to get PC games cheap, legally, in the UK</h1><p class=date>Published {TODAY}. Prices and policies checked against official store pages on that date.</p>
<p>PC gaming has a reputation for being expensive because of the hardware, but the games themselves can be some of the cheapest anywhere, provided you know where to look and you're willing to wait a little. Here's how we'd approach it as a UK player, sticking to legitimate sellers only.</p>
<h2>1. Use the big seasonal sales</h2>
<p>Steam runs several major sales every year, typically a Spring Sale, a Summer Sale in late June to early July, an Autumn Sale around late November and a Winter Sale over Christmas and New Year, plus themed "Next Fest" and genre festivals in between. Valve publishes the dates in advance on its <a href="https://partner.steamgames.com/doc/marketing/upcoming_events">Steamworks events page</a>. GOG, Epic, Humble and Fanatical run their own sales around the same periods. If a game you want isn't urgent, adding it to your Steam wishlist means Steam emails you when it goes on sale.</p>
<h2>2. Compare stores before buying</h2>
<p>Many PC games are sold through several authorised stores at once, and the same game can be noticeably cheaper on one of them. Most give you a Steam key, so you end up with exactly the same game in the same library. Price-comparison sites such as <a href="https://www.cheapshark.com">CheapShark</a> and <a href="https://isthereanydeal.com">IsThereAnyDeal</a> track prices across stores and keep price history, which tells you whether today's "deal" is actually good. Our <a href="/guides/best-pc-game-deals.html">daily deals list</a> is built from CheapShark data.</p>
<h2>3. Stick to authorised key sellers</h2>
<p>Authorised stores buy keys directly from publishers. Well-known UK-accessible examples include Humble Store, Fanatical, Green Man Gaming, GOG and Gamesplanet UK. "Key marketplaces" where individuals resell keys are different: keys can be bought with stolen card details or come from regions where they're cheaper, and they can be revoked by the publisher later, leaving you with nothing. If a price looks far below every authorised store, that's the warning sign.</p>
<h2>4. Claim the freebies</h2>
<p>The Epic Games Store gives away games on a weekly rotation and they're yours to keep once claimed (see <a href="/guides/free-epic-games.html">what's free right now</a>). Amazon Prime members also get free PC games through Prime Gaming, and GOG and Steam occasionally run time-limited giveaways. Claiming a few a month builds a surprisingly large library at no cost.</p>
<h2>5. Bundles</h2>
<p>Humble Bundle and Fanatical sell themed bundles where you get several games for a single price, often well under the cost of one of them on its own. Humble's bundles also let you send part of the price to charity. The catch is that you're usually paying for one or two games you want plus several you don't, so check the line-up first.</p>
<h2>6. Consider a subscription, carefully</h2>
<p>PC Game Pass costs £10.99 a month in the UK at the time of writing (official Xbox store price), and gives you access to a rotating library of several hundred PC games. If you play lots of different games it can be cheaper than buying, but games leave the library and you lose access when you cancel. We compare the options in <a href="/guides/game-pass-vs-buying-uk.html">Game Pass vs buying games: a UK guide</a>.</p>
<h2>7. Look at free-to-play</h2>
<p>Some of the most-played PC games cost nothing up front. They earn money from optional cosmetics or passes, so set yourself a budget. We've picked some with a tech or problem-solving angle in <a href="/guides/free-to-play-for-tech-fans.html">best free-to-play games for AI and tech fans</a>.</p>
<h2>8. Know your rights as a UK buyer</h2>
<p>Digital games count as "digital content" under the Consumer Rights Act 2015, which means they must be of satisfactory quality, fit for purpose and as described. If a game is faulty you're entitled to a repair or replacement, and if that isn't possible, a price reduction or refund. Your 14-day right to cancel an online purchase usually ends once the download starts, provided you agreed to that at checkout, which most stores ask you to do. Steam's own policy is more generous: refunds within 14 days of purchase if you've played for less than two hours. See <a href="https://www.citizensadvice.org.uk/consumer/">Citizens Advice</a> for the details.</p>
<h2>9. Avoid the obvious traps</h2>
<ul><li>"Free game" links in Discord DMs or social media replies are a classic way to steal accounts.</li>
<li>Don't share your Steam or Epic login with a site that promises cheap games or skins.</li>
<li>Turn on two-factor authentication (Steam Guard, Epic 2FA) on every store account.</li>
<li>Pirated copies aren't "cheap", they're illegal, and cracked downloads are a common source of malware.</li></ul>
<h2>The short version</h2>
<p>Wishlist what you want, wait for a sale, compare authorised stores, claim every freebie and only subscribe if you'll actually use it. Do that and the average price you pay per game drops a long way. If you want the deals delivered, the free <a href="/">PixelSteals daily email</a> does the checking for you.</p>""")

page("guides/game-pass-vs-buying-uk.html", "Game Pass vs buying games: a UK guide", "Is Xbox Game Pass or PC Game Pass better value than buying games in the UK? Current UK prices, tiers and a simple way to decide.", f"""
<h1>Game Pass vs buying games: a UK guide</h1><p class=date>Published {TODAY}. UK prices taken from the official Xbox store on that date; Microsoft can change them at any time.</p>
<p>Xbox Game Pass is Microsoft's subscription that gives you access to a library of games for a monthly fee, a bit like Netflix for games. Whether it's better value than buying games depends almost entirely on how you play. Here's what it costs in the UK right now and how to decide.</p>
<h2>Current UK plans</h2>
<table><tr><th>Plan</th><th>UK price</th><th>Main points</th></tr>
<tr><td>Essential</td><td>£6.99/month</td><td>50+ games on console, PC and other devices, online console multiplayer, 5 hours a month of cloud play.</td></tr>
<tr><td>Premium</td><td>£10.99/month</td><td>200+ games, new Xbox-published games within a year of launch, 10 hours a month of cloud play.</td></tr>
<tr><td>PC Game Pass</td><td>£10.99/month</td><td>300+ PC games, new games on day one, EA Play on PC. No cloud play.</td></tr>
<tr><td>Ultimate</td><td>£16.99/month</td><td>400+ games on console and PC, day-one releases, EA Play, Fortnite Crew, Ubisoft+ Classics, 15 hours a month of cloud play.</td></tr></table>
<p>Source: <a href="https://www.xbox.com/en-GB/xbox-game-pass">xbox.com/en-GB</a>. Introductory offers (for example £1 for the first 14 days or first month) are shown to eligible new members when you sign in. Day-one releases exclude Call of Duty titles, according to Microsoft's terms. Library sizes are Microsoft's own rounded figures.</p>
<h2>The real difference: renting vs owning</h2>
<p>With Game Pass you're renting access. Games join and leave the library, and when your subscription stops you can no longer play them (your saves usually remain, and Microsoft offers member discounts if you want to buy a game outright). When you buy a game, you keep the licence for as long as the store exists.</p>
<h2>A simple break-even test</h2>
<p>Work out how many games you'd realistically buy in a year and what you'd pay for them. PC Game Pass at £10.99 a month is £131.88 a year if you subscribe all year. If you'd only buy two or three discounted games in that time, buying is probably cheaper, especially if you shop in sales (see our <a href="/guides/cheap-pc-games-uk.html">guide to cheap PC games</a>). If you'd otherwise buy several new full-price releases, or you like trying lots of games you wouldn't pay for, the subscription can come out well ahead.</p>
<h2>Game Pass tends to suit you if…</h2>
<ul><li>you like sampling lots of different games rather than replaying a few favourites</li>
<li>you want big new Xbox-published releases on day one (PC Game Pass or Ultimate)</li>
<li>you play on both an Xbox and a PC, or want cloud play on a phone or TV (Ultimate)</li>
<li>you're happy to subscribe for a month or two, binge, then cancel</li></ul>
<h2>Buying tends to suit you if…</h2>
<ul><li>you mostly play one or two games for months at a time</li>
<li>you like waiting for sales and building a permanent library</li>
<li>you play lots of games that aren't in the library, which includes most games from Sony, Nintendo, Valve and many independent publishers</li>
<li>you collect freebies from the <a href="/guides/free-epic-games.html">Epic Games Store</a> and only buy occasionally</li></ul>
<h2>Tips for getting the most from Game Pass</h2>
<ul><li><strong>Turn off auto-renew if you're bingeing.</strong> You can do this at account.microsoft.com/services and still keep access until the end of the period you've paid for.</li>
<li><strong>Check "leaving soon".</strong> The Xbox app flags games about to leave the library so you can finish them first.</li>
<li><strong>Know the refund rules.</strong> Microsoft says you can get a refund within 30 days of your first purchase by cancelling, and, once per subscription, a refund of your most recent recurring charge if you cancel and ask within 30 days of being charged.</li>
<li><strong>Watch for price changes.</strong> Microsoft must give at least 30 days' notice of a price increase, so you have time to cancel.</li></ul>
<h2>Our take</h2>
<p>For a PC player who tries lots of new games, a month or two of PC Game Pass now and then is excellent value. For someone who plays a handful of games deeply, buying in sales and claiming free games usually wins. Many people mix both: subscribe when there's a run of games they want, cancel in between, and buy the ones they want to keep forever.</p>""")

page("guides/free-to-play-for-tech-fans.html", "Best free-to-play games for AI and tech fans", "Free PC games and free coding games that reward logic, automation and programming skills, picked for people into AI and tech.", f"""
<h1>Best free-to-play games for AI and tech fans</h1><p class=date>Published {TODAY}. All games listed were free to play at the time of writing; optional in-game purchases may apply.</p>
<p>If you spend your days with AI tools, code or hardware, you'll probably enjoy games that reward systems thinking: optimising, automating and figuring out how things work. These are our picks that cost nothing to start, split into games where you actually write code and well-known free games with plenty of depth for tinkerers.</p>
<h2>Games where you write real code</h2>
<h3>Bitburner (Steam, free)</h3>
<p>An incremental hacking game where you progress by writing JavaScript scripts that automate in-game "servers". It starts simply and ramps up to genuine programming problems: scheduling, resource optimisation and algorithms. It's open source and free on Steam, and it's one of the best ways to practise scripting while feeling like you're playing a game. Fun to pair with an AI coding assistant, if you want to see how well it handles an unfamiliar API.</p>
<h3>CodinGame (browser, free)</h3>
<p><a href="https://www.codingame.com">CodinGame</a> turns programming puzzles into small games and runs regular bot-programming contests in which your AI competes against other players' code. It supports dozens of languages. The multiplayer bot arenas are a great introduction to game-playing AI techniques such as search and heuristics.</p>
<h3>Elevator Saga (browser, free)</h3>
<p>A small open-source browser game where you write the JavaScript that controls a bank of lifts. Each level adds more passengers and tougher targets. It's a neat lesson in why scheduling is hard.</p>
<h3>Robocode (free, open source)</h3>
<p>A long-running programming game where you code a battle tank in Java or .NET and pit it against others. It has been used for years to teach programming and simple AI behaviour.</p>
<h2>Free games with plenty of depth for tinkerers</h2>
<h3>Path of Exile (free, PC)</h3>
<p>An action RPG with a huge passive skill tree and crafting system. Theory-crafting builds is half the game, and the community makes spreadsheets, planners and tools to help. Free to play, supported by cosmetics and optional storage tabs.</p>
<h3>Warframe (free, PC and consoles)</h3>
<p>A co-op sci-fi shooter with deep build customisation and a large player-run economy. Everything that affects gameplay can be earned by playing, though grinding is part of the deal.</p>
<h3>Dota 2 and Counter-Strike 2 (free, Steam)</h3>
<p>Valve's two biggest competitive games are both free. Dota 2 is also part of AI history: OpenAI's "OpenAI Five" bots beat the reigning world champion team, OG, in April 2019, a landmark for reinforcement learning. Playing it gives you a feel for how complex that challenge was.</p>
<h3>Rocket League (free, Epic Games Store)</h3>
<p>Rocket-powered car football with a high skill ceiling that rewards physics intuition. There's an active community building bots for it, too, through the RLBot framework.</p>
<h2>A word on free-to-play spending</h2>
<p>Free-to-play games make money from optional purchases: cosmetics, battle passes and in-game currency. Set a budget and use the parental controls or spending limits on Steam, Epic or Xbox if anyone younger plays on your account. Under UK advertising rules, games must clearly show when something costs real money. If something looks misleading, you can report it to the <a href="https://www.asa.org.uk">ASA</a>.</p>
<p>Want paid games without paying full price? Check <a href="/guides/free-epic-games.html">what's free on Epic right now</a> and <a href="/guides/best-pc-game-deals.html">this week's best PC deals</a>.</p>""")

# ---------- Guides index, about, contact ----------
G = [("free-epic-games.html", "Free Epic Games Store games right now (UK)", "Updated daily from Epic's own feed: what's free, when it ends, what's next and how to claim."),
     ("best-pc-game-deals.html", "This week's best PC game deals", "Updated daily: well-reviewed PC games on sale across legitimate stores."),
     ("cheap-pc-games-uk.html", "How to get PC games cheap, legally, in the UK", "Sales, authorised key stores, bundles, freebies and your rights as a UK buyer."),
     ("game-pass-vs-buying-uk.html", "Game Pass vs buying games: a UK guide", "Current UK Game Pass prices and a simple way to decide whether to subscribe."),
     ("free-to-play-for-tech-fans.html", "Best free-to-play games for AI and tech fans", "Coding games and deep free games for people who like systems.")]
page("guides/index.html", "Guides", "PixelSteals guides to free games, PC game deals and getting more for less as a UK gamer.",
     "<h1>Guides</h1><p>Practical, UK-focused guides to free games and paying less for PC games. The deal pages update automatically every day.</p>" +
     "".join(f'<h2><a href="/guides/{f}">{e(t)}</a></h2><p class=m>{e(s)}</p>' for f, t, s in G))
page("about.html", "About", "About PixelSteals: an independent UK site tracking free games and PC game deals.", """
<h1>About PixelSteals</h1>
<p>PixelSteals is a small, independent UK site for people who love games and tech but don't love paying full price. We track free games and well-reviewed PC deals every day and publish them here and in a free daily email.</p>
<h2>How it works</h2>
<p>Deal data comes from public sources: the Epic Games Store's free-games feed and <a href="https://www.cheapshark.com">CheapShark</a>, a price-comparison service covering legitimate digital stores. Our pages update automatically each morning, with the time of the last update shown on every data page. Our guides are written for UK players, with prices taken from official sources and dated so you know how fresh they are.</p>
<h2>What we won't do</h2>
<ul><li>List grey-market key resellers or anything that infringes copyright.</li><li>Let commissions decide which deals appear. Deals are chosen by discount, rating and price.</li><li>Sell or share your email address.</li></ul>
<h2>How we're funded</h2>
<p>PixelSteals is free. We may earn money from advertising and from affiliate links, which are always disclosed. See our <a href="/affiliate.html">affiliate disclosure</a> and <a href="/privacy.html">privacy policy</a>.</p>
<p>Questions or corrections? <a href="/contact.html">Get in touch</a>.</p>""")
page("contact.html", "Contact", "Contact PixelSteals.", """
<h1>Contact</h1>
<p>Spotted a wrong price, an expired deal or a mistake in a guide? Want to suggest a game or ask about your data? Email us at <a href="mailto:lemondogs@yahoo.co.uk">lemondogs@yahoo.co.uk</a>.</p>
<p>We read everything and aim to reply within a few working days. For data protection requests (access, correction or deletion), please put "Privacy" in the subject line.</p>
<p>To stop receiving our emails, use the unsubscribe link at the bottom of any PixelSteals email; it works instantly.</p>""")
print("built")
