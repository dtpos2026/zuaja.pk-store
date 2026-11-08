"""Real product cut-out -> studio render look on white (same layout as the owner's renders)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
out=Path(sys.argv[1]); logo=Image.open(sys.argv[2]).convert("RGBA"); logo=logo.crop(logo.getbbox())
S=1600
def clean(p):
    from scipy import ndimage
    a=np.asarray(p.getchannel("A"))>40
    lab,n=ndimage.label(a)
    if n>1:
        sz=ndimage.sum(a,lab,range(1,n+1)); keep=np.isin(lab,1+np.where(sz>=0.08*sz.max())[0])
        al=np.asarray(p.getchannel("A")).copy(); al[~ndimage.binary_dilation(keep,iterations=3)]=0
        p.putalpha(Image.fromarray(al))
    return p
def edge_bright(p, dist, thr):
    from scipy import ndimage
    al=np.asarray(p.getchannel("A")).copy(); lum=np.asarray(p.convert("L")).astype(int)
    d=ndimage.distance_transform_edt(al>40)
    al[(d<dist)&(lum>thr)]=0
    p.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(0.7))); return p
def right_blob(p):
    al=np.asarray(p.getchannel("A")).copy(); h,w=al.shape
    cols=np.where((al[int(h*0.55):int(h*0.75)]>40).any(0))[0]
    al[int(h*0.80):, cols.max()+4:]=0; al[int(h*0.80):, :max(cols.min()-4,0)]=0
    p.putalpha(Image.fromarray(al)); return p
def soap(p):
    x=np.asarray(p.convert("RGB")).astype(int); al=np.asarray(p.getchannel("A")).copy(); h=al.shape[0]
    cy=((x[...,1]>x[...,0]+15)|(x[...,2]>x[...,0]+15))&(al>40)
    rows=np.where(cy.sum(1)>0.15*al.shape[1])[0]; rows=rows[rows>h*0.85]
    if len(rows): al[rows.min()-3:]=0
    al[(x.sum(2)>560)&(al>0)]=0
    p.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(0.7))); return p
FIX={"rose-soap":soap,"neem-soap":lambda p:p,
     "zafarani-cream":lambda p:edge_bright(p,14,215),"zuaja-pk-premium-perfume-50-ml":right_blob}
import os
VIVID=os.environ.get("VIVID","0")=="1"; FILL=float(os.environ.get("FILL","0.84"))
def retouch(p):
    a=p.getchannel("A"); rgb=p.convert("RGB")
    x=np.asarray(rgb,np.float32)/255; m=np.asarray(a)>128
    lo,hi=np.percentile(x[m],0.3)*0.7,max(np.percentile(x[m],99.7),0.9)
    x=np.clip((x-lo)/max(hi-lo,1e-3),0,1)
    x=np.clip(x,0,1)
    if VIVID:  # bright catalogue look: S-curve contrast, lifted highlights, richer colour, crisp detail
        x=x+0.35*x*(1-x)*(2*x-1)
        x=x+0.18*np.clip((x-0.55)/0.45,0,1)*(1-x)
        x=np.clip(x,0,1)
    rgb=Image.fromarray((x*255).astype(np.uint8))
    rgb=ImageEnhance.Color(rgb).enhance(1.22 if VIVID else 1.06)
    rgb=rgb.filter(ImageFilter.UnsharpMask(radius=1.4,percent=35,threshold=3))
    if VIVID: rgb=rgb.filter(ImageFilter.UnsharpMask(radius=6,percent=22,threshold=2))
    r=rgb.convert("RGBA"); r.putalpha(a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8)))
    return r
for arg in sys.argv[3:]:
    key,src=arg.split("=",1)
    p=Image.open(src).convert("RGBA"); p=FIX.get(key,lambda q:q)(p); p=clean(p); p=p.crop(p.getbbox()); p=retouch(p)
    r=min(S*FILL/p.height, S*(FILL-0.04)/p.width); p=p.resize((round(p.width*r),round(p.height*r)),Image.LANCZOS)
    c=Image.new("RGBA",(S,S),(255,255,255,255))
    x=(S-p.width)//2; y=(S-p.height)//2-20
    sh=Image.new("L",(S,S),0); d=ImageDraw.Draw(sh); cx=S//2; by=y+p.height
    d.ellipse((cx-p.width*0.42,by-18,cx+p.width*0.42,by+22),fill=70)
    sh=sh.filter(ImageFilter.GaussianBlur(22))
    c.paste((0,0,0,255),(0,0),sh.point(lambda v:int(v*0.6)))
    c.alpha_composite(p,(x,y))
    w=int(S*0.2); lg=logo.resize((w,round(logo.height*w/logo.width)),Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v:int(v*0.55))); m=int(S*0.035)
    c.alpha_composite(lg,(S-w-m,S-lg.height-m))
    c.convert("RGB").save(out/f"{key}.jpg",quality=88,optimize=True,progressive=True); print(key,(out/f"{key}.jpg").stat().st_size//1024,"KB")
