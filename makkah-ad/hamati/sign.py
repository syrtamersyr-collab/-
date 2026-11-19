import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W,H=1460,450
src=np.float32([[0,0],[W,0],[W,H],[0,H]])
dst=np.float32([[88,128],[803,278],[803,482],[72,372]])
M=cv2.getPerspectiveTransform(src,dst); Mi=np.linalg.inv(M)
base=Image.open('scenes/s3.png').convert('RGBA'); A=np.array(base)
# 1) clean sign face: unwarp, blur heavily (keeps the lighting, kills ghost letters), keep the glowing bottom edge
face=cv2.warpPerspective(A,Mi,(W,H),flags=cv2.INTER_CUBIC)
clean=cv2.GaussianBlur(face,(0,0),28)
# subtle brushed-metal grain + top-to-bottom sheen
rng=np.random.default_rng(3); grain=(rng.standard_normal((H,W))*3).astype(np.float32)
grain=cv2.GaussianBlur(grain,(0,0),sigmaX=12,sigmaY=.6)
cf=clean.astype(np.float32); cf[...,:3]+=grain[...,None]
sheen=np.linspace(18,-14,H,dtype=np.float32)[:,None,None]; cf[...,:3]+=sheen
cf[...,3]=255; flat=Image.fromarray(cf.clip(0,255).astype(np.uint8))
# keep original bottom light strip
strip=Image.fromarray(face).crop((0,H-40,W,H)); flat.paste(strip,(0,H-40))
d=ImageDraw.Draw(flat)
# 2) logo panel with soft shadow
px0,py0,px1,py1=40,36,384,H-44
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((px0+10,py0+14,px1+10,py1+14),22,fill=(0,20,30,150))
flat=Image.alpha_composite(flat,sh.filter(ImageFilter.GaussianBlur(14))); d=ImageDraw.Draw(flat)
d.rounded_rectangle((px0,py0,px1,py1),22,fill=(255,255,255,255))
d.rounded_rectangle((px0+8,py0+8,px1-8,py1-8),16,outline=(80,190,30,255),width=4)
logo=Image.open('/home/user/-/makkah-ad/winter/assets/logo-vertical.png').convert('RGBA')
logo.thumbnail((px1-px0-70,py1-py0-46),Image.LANCZOS)
flat.paste(logo,(px0+(px1-px0-logo.width)//2,py0+(py1-py0-logo.height)//2),logo)
# 3) channel letters: extruded 3D, gradient face, cyan halo
f1=ImageFont.truetype('fonts/ReadexPro-700-ar.ttf',176,layout_engine=ImageFont.Layout.RAQM)
f2=ImageFont.truetype('fonts/ReadexPro-700-ar.ttf',70,layout_engine=ImageFont.Layout.RAQM)
tx,ty=(px1+W)//2+10,168
def mask(text,font,xy,anchor='mm'):
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).text(xy,text,font=font,anchor=anchor,fill=255,direction='rtl',language='ar'); return m
m1=mask('مركز مكة',f1,(tx,ty))
halo=Image.new('RGBA',(W,H),(120,235,255,0)); halo.putalpha(m1.filter(ImageFilter.GaussianBlur(22)).point(lambda v:int(v*.75)))
flat=Image.alpha_composite(flat,halo)
for k in range(12,0,-1):  # extrusion
    sh=Image.new('RGBA',(W,H),(10,60,72,255) if k>1 else (6,40,50,255)); sh.putalpha(ImageChops.offset(m1,k,k))
    flat=Image.alpha_composite(flat,sh)
grad=np.zeros((H,W,4),np.uint8); g=np.linspace(255,214,H)[:,None]
grad[...,0]=g; grad[...,1]=np.minimum(255,g+6); grad[...,2]=255; grad=Image.fromarray(grad); grad.putalpha(m1)
flat=Image.alpha_composite(flat,grad)
# 4) green pill subtitle
pw,ph=440,96; pcx,pcy=tx,350
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((pcx-pw//2+6,pcy-ph//2+8,pcx+pw//2+6,pcy+ph//2+8),ph//2,fill=(0,20,30,140))
flat=Image.alpha_composite(flat,sh.filter(ImageFilter.GaussianBlur(8))); d=ImageDraw.Draw(flat)
d.rounded_rectangle((pcx-pw//2,pcy-ph//2,pcx+pw//2,pcy+ph//2),ph//2,fill=(80,190,30,255))
d.text((pcx,pcy-2),'للتقنيات',font=f2,anchor='mm',fill=(255,255,255,255),direction='rtl',language='ar')
# 5) warp back with feathered mask
warp=cv2.warpPerspective(np.array(flat),M,(1080,1920),flags=cv2.INTER_CUBIC)
mk=np.zeros((1920,1080),np.uint8); cv2.fillConvexPoly(mk,dst.astype(np.int32),255); mk=cv2.GaussianBlur(mk,(0,0),1.2)
warp[...,3]=mk
out=Image.alpha_composite(base,Image.fromarray(warp)); out.convert('RGB').save('scenes/s3.png')
