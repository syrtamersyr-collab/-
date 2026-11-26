from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920
bg=Image.open('gl_32.7.png').convert('RGB').resize((W,H))
img=bg.convert('RGBA')
# bottom navy gradient for the title
grad=Image.new('L',(1,H)); 
for y in range(H): grad.putpixel((0,y), int(max(0,min(255,(y-980)/520*235))))
ov=Image.new('RGBA',(W,H),(2,30,62,255)); ov.putalpha(grad.resize((W,H))); img=Image.alpha_composite(img,ov)
L=ImageFont.Layout.RAQM
ruq=lambda s: ImageFont.truetype('aref-ruqaa-arabic-700-normal.ttf',s,layout_engine=L)
rdx=lambda s: ImageFont.truetype('readex700.ttf',s,layout_engine=L)
def text(d,xy,s,f,fill,stroke=0,sc=None,anchor='mm'):
    d.text(xy,s,font=f,fill=fill,anchor=anchor,direction='rtl',language='ar',stroke_width=stroke,stroke_fill=sc)
# glow behind title
gl=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(gl); text(g,(W//2,1250),'ساعة حمص بتحكي',ruq(150),(255,200,90,255))
gl=gl.filter(ImageFilter.GaussianBlur(22)); img=Image.alpha_composite(img,gl)
d=ImageDraw.Draw(img)
text(d,(W//2,1250),'ساعة حمص بتحكي',ruq(150),(255,236,180),stroke=10,sc=(2,40,80))
# hook pill
f=rdx(54); s='شو صار معها بنص الليل؟'; w=d.textlength(s,font=f,direction='rtl',language='ar')+90
d.rounded_rectangle((W//2-w/2,1395,W//2+w/2,1495),50,fill=(80,190,30))
text(d,(W//2,1443),s,f,(255,255,255))
# brand line
text(d,(W//2,1590),'مركز مكة للتقنيات',rdx(50),(255,255,255))
# logo card
logo=Image.open('../assets/logo-vertical.png').convert('RGBA'); lw=140; logo=logo.resize((lw,int(lw*logo.height/logo.width)),Image.LANCZOS)
cw,ch=lw+32,logo.height+28
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((36,40,36+cw,40+ch),24,fill=(0,0,0,110)); img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(12)))
ImageDraw.Draw(img).rounded_rectangle((30,30,30+cw,30+ch),24,fill=(255,255,255,248)); img.paste(logo,(46,44),logo)
d=ImageDraw.Draw(img); text(d,(W//2,1720),'إنترنت هوائي، طاقة شمسية، كاميرات',rdx(40),(200,220,240))
# "play" hint corner
d=ImageDraw.Draw(img)
img.convert('RGB').save('makkah-clock-cover.jpg',quality=94)
