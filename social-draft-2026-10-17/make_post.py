from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350; BG=(11,13,23); G=(57,255,20); WHITE=(232,236,255); MUTE=(160,170,200); CARD=(21,26,46)
PS="/usr/share/fonts/truetype/sand-box/google/Press Start 2P/PressStart2P-Regular.ttf"
PX="/usr/share/fonts/truetype/sand-box/google/Pixelify Sans/PixelifySans-VariableFont_wght.ttf"
def pxf(s,w="Bold"):
    f=ImageFont.truetype(PX,s)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
# subtle pixel grid
for x in range(0,W,24): d.line((x,0,x,H),fill=(16,19,32))
for y in range(0,H,24): d.line((0,y,W,y),fill=(16,19,32))
# banner characters at bottom, faded in from top
ban=Image.open("src/banner.png").convert("RGB")
crop=ban.crop((400,70,1280,610)); bw=W; bh=int(crop.height*bw/crop.width); crop=crop.resize((bw,bh),Image.NEAREST)
by=H-bh-70
mask=Image.new("L",(bw,bh),255); md=ImageDraw.Draw(mask)
for i in range(220): md.line((0,i,bw,i),fill=int(255*i/220))
img.paste(crop,(0,by),mask)
d=ImageDraw.Draw(img)
def ctext(y,t,f,fill,glow=False):
    b=d.textbbox((0,0),t,font=f); x=(W-(b[2]-b[0]))//2-b[0]
    if glow:
        g=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g); gd.text((x,y),t,font=f,fill=G+(170,))
        g=g.filter(ImageFilter.GaussianBlur(10)); img.paste(g,(0,0),g)
    ImageDraw.Draw(img).text((x,y),t,font=f,fill=fill)
    return b
# logo
f=pxf(64); a,bb="Pixel","Steals"
wa=d.textlength(a,font=f); wb=d.textlength(bb,font=f); x=(W-wa-wb)/2
d.text((x,38),a,font=f,fill=WHITE); d.text((x+wa,38),bb,font=f,fill=G)
# headline
hf=ImageFont.truetype(PS,58); ctext(150,"FREE GAMES",hf,G,glow=True); ctext(228,"TODAY",hf,G,glow=True)
d=ImageDraw.Draw(img)
ctext(316,"SATURDAY 17 OCTOBER 2026",pxf(36,"SemiBold"),WHITE)
games=[("Bad Cheese","src/bad-cheese.png"),("Agent A: A puzzle in disguise","src/agent-a.png")]
y=384; CH=270
for t,p in games:
    d.rounded_rectangle((50,y,1030,y+CH),radius=18,fill=CARD,outline=(40,90,40),width=3)
    iw,ih=400,225; im=Image.open(p).convert("RGB").resize((iw,ih),Image.LANCZOS)
    m=Image.new("L",(iw,ih),0); ImageDraw.Draw(m).rounded_rectangle((0,0,iw,ih),radius=12,fill=255)
    img.paste(im,(72,y+(CH-ih)//2),m); d=ImageDraw.Draw(img)
    tx=500; maxw=1010-tx
    # wrap title
    tf=ImageFont.truetype(PS,30); words=t.split(); lines=[]; cur=""
    for w_ in words:
        s=(cur+" "+w_).strip()
        if d.textlength(s,font=tf)<=maxw: cur=s
        else: lines.append(cur); cur=w_
    lines.append(cur)
    ty=y+26
    for ln in lines: d.text((tx,ty),ln,font=tf,fill=WHITE); ty+=46
    # FREE badge
    bf=ImageFont.truetype(PS,26); bt="FREE"; bwid=d.textlength(bt,font=bf)
    by2=ty+12; d.rectangle((tx,by2,tx+bwid+28,by2+46),fill=G); d.text((tx+14,by2+10),bt,font=bf,fill=BG)
    d.text((tx+bwid+44,by2+6),"Epic Games Store",font=pxf(30,"SemiBold"),fill=G)
    d.text((tx,by2+62),"Free until Thu 22 Oct, 4pm UK",font=pxf(28,"Regular"),fill=MUTE)
    y+=CH+24
# next week teaser
ty=y+10
ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle((50,ty-14,1030,ty+96),radius=16,fill=(11,13,23,235),outline=G+(255,),width=2)
img.paste(ov,(0,0),ov); d=ImageDraw.Draw(img)
ctext(ty,"NEXT FREE ON EPIC • FROM THU 22 OCT",pxf(30,"SemiBold"),G)
ctext(ty+44,"Sker Ritual  +  Home - A Unique Horror Adventure",pxf(32,"Medium"),WHITE)
# footer
d=ImageDraw.Draw(img); d.rectangle((0,H-110,W,H),fill=(5,7,11)); d.line((0,H-110,W,H-110),fill=G,width=4)
uf=ImageFont.truetype(PS,46); ctext(H-84,"pixelsteals.com",uf,G,glow=True)
img.save("post-45.png"); print(img.size, "cards end", y)
