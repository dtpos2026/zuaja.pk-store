"""Run Real-ESRGAN (realesr-general-x4v3, SRVGGNetCompact) without PyTorch.

Reads the .pth zip directly, rebuilds the network as an ONNX graph and runs it with onnxruntime.
Usage: python3 -I esrgan_onnx.py <weights.pth> <out_dir> <image.png> [...]
Transparent PNGs keep their (upscaled) alpha.
"""
import io
import pickle
import sys
import zipfile
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper
from PIL import Image

PTH, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def load_pth(path):
    zf = zipfile.ZipFile(path)
    prefix = zf.namelist()[0].split("/")[0]

    class Storage:
        def __init__(self, key, dtype):
            self.key, self.dtype = key, dtype

    def rebuild(storage, offset, size, stride, *args):
        raw = np.frombuffer(zf.read(f"{prefix}/data/{storage.key}"), dtype=storage.dtype)
        n = int(np.prod(size)) if size else 1
        arr = raw[offset:offset + n] if all(s >= 0 for s in stride) else raw
        return np.lib.stride_tricks.as_strided(raw[offset:], shape=size, strides=[s * raw.itemsize for s in stride]).copy() if size else arr.copy()

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if mod == "torch._utils" and name == "_rebuild_tensor_v2":
                return rebuild
            if mod == "torch" and name.endswith("Storage"):
                return {"FloatStorage": np.float32, "HalfStorage": np.float16}.get(name, np.float32)
            if mod == "collections" and name == "OrderedDict":
                import collections
                return collections.OrderedDict
            # weights-only: refuse every other global, so nothing in the file can run code
            raise pickle.UnpicklingError(f"blocked global {mod}.{name}")

        def persistent_load(self, pid):
            _, dtype, key, _loc, _n = pid
            return Storage(key, dtype)

    data = U(io.BytesIO(zf.read(f"{prefix}/data.pkl"))).load()
    return data.get("params_ema") or data.get("params") or data


def build(params):
    keys = sorted({k.split(".")[1] for k in params if k.startswith("body.")}, key=int)
    nodes, inits = [], []
    cur = "x"
    for i in keys:
        w = params[f"body.{i}.weight"].astype(np.float32)
        if w.ndim == 4:
            b = params[f"body.{i}.bias"].astype(np.float32)
            inits += [numpy_helper.from_array(w, f"w{i}"), numpy_helper.from_array(b, f"b{i}")]
            nodes.append(helper.make_node("Conv", [cur, f"w{i}", f"b{i}"], [f"c{i}"], pads=[1, 1, 1, 1]))
            cur = f"c{i}"
        else:  # PReLU slope per channel
            inits.append(numpy_helper.from_array(w.reshape(-1, 1, 1), f"a{i}"))
            nodes.append(helper.make_node("PRelu", [cur, f"a{i}"], [f"p{i}"]))
            cur = f"p{i}"
    nodes.append(helper.make_node("DepthToSpace", [cur], ["ps"], blocksize=4, mode="CRD"))
    inits.append(numpy_helper.from_array(np.array([1, 1, 4, 4], np.float32), "scales"))
    nodes.append(helper.make_node("Resize", ["x", "", "scales"], ["up"], mode="nearest"))
    nodes.append(helper.make_node("Add", ["ps", "up"], ["y"]))
    g = helper.make_graph(nodes, "srvgg", [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, None, None])],
                          [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 3, None, None])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 17)], ir_version=9)
    return m.SerializeToString()


def main():
    sess = ort.InferenceSession(build(load_pth(PTH)), providers=["CPUExecutionProvider"])
    for src in map(Path, sys.argv[3:]):
        im = Image.open(src)
        alpha = im.getchannel("A") if im.mode == "RGBA" else None
        rgb = im.convert("RGB")
        # keep compute bounded: longest side up to 900 px before the x4 pass
        k = min(1.0, 900 / max(rgb.size))
        if k < 1:
            rgb = rgb.resize((round(rgb.width * k), round(rgb.height * k)), Image.LANCZOS)
            if alpha is not None:
                alpha = alpha.resize(rgb.size, Image.LANCZOS)
        x = (np.asarray(rgb).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        y = sess.run(None, {"x": x})[0][0]
        out = Image.fromarray((np.clip(y.transpose(1, 2, 0), 0, 1) * 255).round().astype(np.uint8))
        if alpha is not None:
            out = out.convert("RGBA")
            out.putalpha(alpha.resize(out.size, Image.LANCZOS))
        out.save(OUT / (src.stem + ".png"), optimize=False)
        print(src.name, out.size, flush=True)


if __name__ == "__main__":
    main()
