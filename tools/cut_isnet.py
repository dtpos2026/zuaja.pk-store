"""Background removal with isnet-general-use via onnxruntime. Usage: cut_isnet.py out_dir key=src [--black] ..."""
import sys
from pathlib import Path
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
M="/root/.rembg/models/isnet-general-use/isnet-general-use.onnx"
s=ort.InferenceSession(M,providers=["CPUExecutionProvider"]); iname=s.get_inputs()[0].name
out=Path(sys.argv[1])
for arg in sys.argv[2:]:
    key,src=arg.split("=",1); black=src.endswith(":black"); src=src.replace(":black","")
    im=Image.open(src).convert("RGB")
    x=np.asarray(im.resize((1024,1024),Image.BILINEAR),np.float32)/255.0
    x=(x-0.5)/1.0
    y=s.run(None,{iname:x.transpose(2,0,1)[None]})[0][0,0]
    y=(y-y.min())/(y.max()-y.min()+1e-6)
    m=Image.fromarray((y*255).astype(np.uint8)).resize(im.size,Image.LANCZOS)
    a=np.asarray(m).astype(np.float32)/255
    a=np.clip((a-0.15)/0.7,0,1)  # firm edges
    rgb=np.asarray(im).astype(np.float32)
    if black:  # un-premultiply against black so glass edges don't keep a dark fringe
        aa=np.maximum(a,1e-3)[...,None]; edge=(a<0.98)[...,None]
        rgb=np.where(edge,np.clip(rgb/aa,0,255),rgb)
    o=Image.fromarray(rgb.astype(np.uint8)).convert("RGBA"); o.putalpha(Image.fromarray((a*255).astype(np.uint8)))
    o.save(out/f"{key}.png"); print(key,o.size,flush=True)
