import cv2, numpy as np
from PIL import Image, ImageFilter, ImageDraw
R='/home/user/-/makkah-ad/hamati/raw/'; O='/home/user/-/makkah-ad/hamati/scenes/'
logo=Image.open('/home/user/-/makkah-ad/winter/assets/logo-vertical.png').convert('RGBA')
def fitlogo(w,h):
    l=logo.copy(); l.thumbnail((w,h),Image.LANCZOS); return l
def inpaint_bright(img,box,thr=200,dil=7,rad=9):
    a=np.array(img); x0,y0,x1,y1=box
    sub=a[y0:y1,x0:x1]; g=sub.min(axis=2)
    m=np.zeros(a.shape[:2],np.uint8); m[y0:y1,x0:x1]=(g>thr).astype(np.uint8)*255
    m=cv2.dilate(m,np.ones((dil,dil),np.uint8))
    out=cv2.inpaint(cv2.cvtColor(a,cv2.COLOR_RGB2BGR),m,rad,cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB))
# ---- scene 1: framed logo replaces fake calligraphy
s1=Image.open(R+'s1.png').convert('RGB'); d=ImageDraw.Draw(s1)
a=np.array(s1)
# inner panel of frame
x0,y0,x1,y1=650,0,885,285
d.rounded_rectangle((x0,y0-20,x1,y1),12,fill=(246,239,224))
d.rounded_rectangle((x0+10,y0-20,x1-10,y1-10),8,outline=(196,160,90),width=3)
l=fitlogo(x1-x0-50,y1-y0-40); s1.paste(l,(x0+(x1-x0-l.width)//2,y0+(y1-y0-l.height)//2),l)
# soften to match painterly look
reg=s1.crop((x0-4,0,x1+4,y1+4)).filter(ImageFilter.GaussianBlur(.6)); s1.paste(reg,(x0-4,0))
s1.save(O+'s1.png')
# ---- scene 2: remove glitch spikes around groom's mouth
s2=Image.open(R+'s2.png').convert('RGB')
s2=inpaint_bright(s2,(820,1080,900,1185),thr=185,dil=5,rad=7)
s2.save(O+'s2.png')
# ---- scene 3
s3=Image.open(R+'s3.png').convert('RGB')
s3=inpaint_bright(s3,(45,590,165,695),thr=170,dil=9,rad=11)    # fake glass text
s3=inpaint_bright(s3,(120,190,280,340),thr=140,dil=17,rad=17)  # wifi icon on sign
s3=inpaint_bright(s3,(265,235,800,420),thr=140,dil=13,rad=15)  # stretched sign lettering (re-set in video)
a=np.array(s3).astype(float)
for y in range(0,398):
    ref=a[min(y,380),1068].copy()
    xs=range(938 if y<210 else 966,1050)
    for x in xs: a[y,x]=ref
for y in range(398,446):
    ref=a[380,1068]
    for x in range(966,1050):
        p=a[y,x]
        if not (p[0]>p[2]+12): a[y,x]=ref
s3=Image.fromarray(a.clip(0,255).astype(np.uint8))
reg=s3.crop((930,0,1080,450)).filter(ImageFilter.GaussianBlur(3)); 
mask=Image.new('L',reg.size,0); ImageDraw.Draw(mask).rectangle((10,0,125,392),255); mask=mask.filter(ImageFilter.GaussianBlur(4))
s3.paste(reg,(930,0),mask)
# technician badge: clean white card + tiny logo
d.rounded_rectangle((798,920,872,968),6,fill=(250,250,250))
l=fitlogo(60,44); s3.paste(l,(835-l.width//2,944-l.height//2),l)
s3.save(O+'s3.png')
