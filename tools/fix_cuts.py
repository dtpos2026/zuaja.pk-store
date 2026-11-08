import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
S=Path(sys.argv[1]); U=Path(sys.argv[2]); C=S/"new/cut"
def neutral(key):
    p=Image.open(C/f"{key}.png").convert("RGBA"); x=np.asarray(p).astype(np.float32); a=x[...,3]>200
    rgb=x[...,:3]
    # blue cast removal: pixels where blue dominates (wall showing through / reflected) -> grey with same luminance
    lum=rgb@np.array([.299,.587,.114])
    blu=(rgb[...,2]-np.maximum(rgb[...,0],rgb[...,1]))
    w=np.clip(blu/25,0,1)[...,None]
    rgb=rgb*(1-w)+lum[...,None]*w
    # white balance on bright neutral-ish pixels (white bottle body)
    br=(lum>170)&a&(np.ptp(rgb,axis=2)<40)
    if br.sum()>500:
        m=rgb[br].mean(0); rgb=np.clip(rgb*(m.mean()/m),0,255)
    x[...,:3]=rgb; Image.fromarray(x.astype(np.uint8)).save(C/f"{key}.png")
for k in ["haldi-front","haldi-back","haldi-about","amla-front","amla-front2","amla-side","pair"]: neutral(k)
def solidify(key,src):
    p=Image.open(C/f"{key}.png").convert("RGBA"); o=np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    lum=o@np.array([.299,.587,.114]); a=np.asarray(p.getchannel("A")).astype(np.float32)/255
    la=np.clip((lum-14)/22,0,1)
    a=np.maximum(a,la*(ndimage.binary_dilation(a>0.3,iterations=6)))
    a=np.maximum(a,ndimage.binary_fill_holes(a>0.5).astype(np.float32))
    rgb=np.asarray(p.convert("RGB")).astype(np.float32)
    edge=(a<0.98)[...,None]; rgb=np.where(edge,np.clip(o/np.maximum(a,1e-3)[...,None],0,255),o)
    q=Image.fromarray(rgb.astype(np.uint8)).convert("RGBA"); q.putalpha(Image.fromarray((a*255).astype(np.uint8))); q.save(C/f"{key}.png")
solidify("neemsoap-box",U/"4c1da0b7-image.jpg"); solidify("herbal-pair",U/"fbf8e243-image.jpg"); solidify("rosemary-back",U/"a715fe8a-image.jpg")
# split herbal pair at the emptiest column in the middle
p=Image.open(C/"herbal-pair.png"); a=np.asarray(p.getchannel("A")); w=a.shape[1]
cols=(a>40).sum(0); mid=slice(int(w*.35),int(w*.65)); cut=int(w*.35)+int(np.argmin(cols[mid]))
p.crop((0,0,cut,a.shape[0])).save(C/"herbal-front.png"); p.crop((cut,0,w,a.shape[0])).save(C/"herbal-back.png")
print("split at",cut,"min col",cols[cut])
