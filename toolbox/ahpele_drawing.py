#!/usr/bin/env python3
"""AHPELE drawing reader: tiles, zoomed crops, symbol search and count overlays for raster or PDF drawings.

  python3 ahpele_drawing.py grid  SHEET [--page 1] [--dpi 100] [--cols 4 --rows 3] [--out DIR]
      overview with a labelled grid + one tile per cell (read a sheet cell by cell, refer to places as B3 etc.)
  python3 ahpele_drawing.py crop  SHEET --box x0,y0,x1,y1 [--page 1] [--dpi 300] [--out crop.png]
      zoom on a region; box in fractions of the sheet (0..1) or in pixels of a grid overview (--px --dpi D)
  python3 ahpele_drawing.py find  SHEET --template SYMBOL.png [--page 1] [--dpi D] [--rot 0,90,180,270]
                                  [--scales 0.9,1,1.1] [--min 0.45] [--out DIR]
      every place that looks like the template (cut it from the legend or from one clear instance on the SAME
      sheet at the SAME dpi): candidates.csv (id, x, y in px and as fractions, score, rotation) + overlay.png with
      numbered boxes. Scores >= 0.8 are usually the symbol, 0.45-0.8 must be reviewed one by one (crops are written
      for them), lower ones are dropped. Similar symbols (filled vs open, different inner mark) score high on each
      other: search with each legend symbol and assign each place to the best-scoring one.
  python3 ahpele_drawing.py mark  SHEET --points pts.csv [--page 1] [--dpi D] [--out marked.png]
      draw your own counted items (csv with x,y in px of the same dpi, optional label) to check nothing is missed
      or counted twice.

SHEET can be a PDF (page rendered with PyMuPDF or pdftoppm) or an image (PNG, JPG, TIFF). Needs Pillow; `find`
needs numpy. Knows nothing about any particular drawing set.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    sys.exit("ahpele_drawing needs Pillow (pip install pillow)")
Image.MAX_IMAGE_PIXELS = None


def load(sheet, page=1, dpi=None):
    """Returns an RGB image of the sheet (PDF page rendered at dpi, image file as is or rescaled to dpi)."""
    if sheet.lower().endswith(".pdf"):
        dpi = dpi or 100
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(sheet)
            pix = doc[page - 1].get_pixmap(dpi=dpi)
            return Image.frombytes("RGB", (pix.width, pix.height), pix.samples), dpi
        except ImportError:
            pass
        if not shutil.which("pdftoppm"):
            sys.exit("cannot render PDF: install pymupdf or poppler-utils (pdftoppm)")
        with tempfile.TemporaryDirectory() as td:
            base = os.path.join(td, "p")
            subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", "-f", str(page), "-l", str(page),
                            sheet, base], check=True, capture_output=True, timeout=300)
            return Image.open(base + ".png").convert("RGB"), dpi
    img = Image.open(sheet)
    if getattr(img, "n_frames", 1) > 1:
        img.seek(page - 1)
    img = img.convert("RGB")
    native = img.info.get("dpi", (None,))[0]
    if dpi and native and abs(native - dpi) > 1:
        k = dpi / float(native)
        img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
        return img, dpi
    return img, round(dpi or native or 0)


def cmd_grid(a):
    img, dpi = load(a.sheet, a.page, a.dpi)
    os.makedirs(a.out, exist_ok=True)
    w, h = img.size
    cw, ch = w / a.cols, h / a.rows
    ov = img.copy()
    d = ImageDraw.Draw(ov)
    for i in range(1, a.cols):
        d.line([(i * cw, 0), (i * cw, h)], fill=(255, 0, 0), width=max(1, w // 800))
    for j in range(1, a.rows):
        d.line([(0, j * ch), (w, j * ch)], fill=(255, 0, 0), width=max(1, w // 800))
    tiles = []
    for j in range(a.rows):
        for i in range(a.cols):
            name = f"{chr(65 + i)}{j + 1}"
            d.text((i * cw + 4, j * ch + 4), name, fill=(255, 0, 0))
            box = (int(i * cw), int(j * ch), int((i + 1) * cw), int((j + 1) * ch))
            pad = int(0.05 * min(cw, ch))  # small overlap so symbols on a cell edge appear whole in one tile
            pbox = (max(0, box[0] - pad), max(0, box[1] - pad), min(w, box[2] + pad), min(h, box[3] + pad))
            path = os.path.join(a.out, f"tile_{name}.png")
            tile = img.crop(pbox)
            if a.tile_dpi and dpi and a.tile_dpi != dpi:
                k = a.tile_dpi / dpi
                tile = tile.resize((int(tile.width * k), int(tile.height * k)), Image.LANCZOS)
            tile.save(path)
            tiles.append((name, pbox, path))
    small = ov.copy()
    small.thumbnail((1600, 1600))
    small.save(os.path.join(a.out, "overview.png"))
    print(f"sheet {w}x{h} px at {dpi} dpi; {a.cols}x{a.rows} cells (columns A.., rows 1.., 5% overlap)")
    print(f"overview: {os.path.join(a.out, 'overview.png')}")
    for name, b, p in tiles:
        print(f"  {name}: px {b[0]}..{b[2]} x {b[1]}..{b[3]}  ->  {p}")


def parse_box(s, w, h, px):
    v = [float(x) for x in s.split(",")]
    if len(v) != 4:
        sys.exit("--box needs x0,y0,x1,y1")
    if not px and max(v) <= 1.0:
        v = [v[0] * w, v[1] * h, v[2] * w, v[3] * h]
    return tuple(int(round(x)) for x in v)


def cmd_crop(a):
    img, dpi = load(a.sheet, a.page, a.dpi)
    w, h = img.size
    box = parse_box(a.box, w, h, a.px)
    if a.px and a.px_dpi and dpi and a.px_dpi != dpi:  # pixels given on an overview rendered at another dpi
        k = dpi / a.px_dpi
        box = tuple(int(x * k) for x in box)
    out = img.crop(box)
    out.save(a.out)
    print(f"crop {box} of {w}x{h} px at {dpi} dpi -> {a.out} ({out.width}x{out.height})")


def ncc(gray, tpl):
    """Normalised cross-correlation of a template over an image (numpy FFT), 'valid' region."""
    import numpy as np
    H, W = gray.shape
    th, tw = tpl.shape
    t = tpl - tpl.mean()
    tnorm = np.sqrt((t ** 2).sum()) or 1.0
    fshape = (H + th - 1, W + tw - 1)
    F = np.fft.rfft2(gray, fshape)
    T = np.fft.rfft2(t[::-1, ::-1], fshape)
    corr = np.fft.irfft2(F * T, fshape)[th - 1:H, tw - 1:W]
    c1 = np.cumsum(np.cumsum(np.pad(gray, ((1, 0), (1, 0))), 0), 1)
    c2 = np.cumsum(np.cumsum(np.pad(gray ** 2, ((1, 0), (1, 0))), 0), 1)

    def box(c):
        return c[th:, tw:] - c[:-th, tw:] - c[th:, :-tw] + c[:-th, :-tw]
    n = th * tw
    s1, s2 = box(c1), box(c2)
    var = np.maximum(s2 - s1 ** 2 / n, 1e-9)
    return corr / (np.sqrt(var) * tnorm)


def cmd_find(a):
    try:
        import numpy as np
    except ImportError:
        sys.exit("find needs numpy")
    img, dpi = load(a.sheet, a.page, a.dpi)
    tpl_img = Image.open(a.template).convert("L")
    gray = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    hits = []
    for rot in [int(r) for r in a.rot.split(",")]:
        for sc in [float(s) for s in a.scales.split(",")]:
            t = tpl_img.rotate(rot, expand=True, fillcolor=255)
            if sc != 1.0:
                t = t.resize((max(3, int(t.width * sc)), max(3, int(t.height * sc))), Image.LANCZOS)
            tpl = np.asarray(t, dtype=np.float64) / 255.0
            if tpl.shape[0] >= gray.shape[0] or tpl.shape[1] >= gray.shape[1] or tpl.std() < 1e-3:
                continue
            r = ncc(gray, tpl)
            th, tw = tpl.shape
            ys, xs = np.where(r >= a.min)
            for y, x in zip(ys, xs):
                hits.append((float(r[y, x]), int(x + tw / 2), int(y + th / 2), tw, th, rot, sc))
    hits.sort(key=lambda z: -z[0])
    kept = []  # non-maximum suppression: one candidate per symbol footprint
    for hsc, x, y, tw, th, rot, sc in hits:
        if all(abs(x - k[1]) > 0.6 * max(tw, k[3]) or abs(y - k[2]) > 0.6 * max(th, k[4]) for k in kept):
            kept.append((hsc, x, y, tw, th, rot, sc))
    os.makedirs(a.out, exist_ok=True)
    w, h = img.size
    ov = img.copy()
    d = ImageDraw.Draw(ov)
    rows = []
    review = os.path.join(a.out, "review")
    os.makedirs(review, exist_ok=True)
    for i, (hsc, x, y, tw, th, rot, sc) in enumerate(kept, 1):
        band = "likely" if hsc >= 0.8 else "REVIEW"
        col = (0, 170, 0) if band == "likely" else (255, 140, 0)
        d.rectangle([x - tw / 2, y - th / 2, x + tw / 2, y + th / 2], outline=col, width=max(2, w // 1000))
        d.text((x + tw / 2 + 2, y - th / 2), str(i), fill=col)
        rows.append({"id": i, "x": x, "y": y, "fx": round(x / w, 4), "fy": round(y / h, 4), "score": round(hsc, 3),
                     "rotation": rot, "scale": sc, "band": band})
        if band == "REVIEW":
            m = int(1.5 * max(tw, th))
            img.crop((max(0, x - m), max(0, y - m), min(w, x + m), min(h, y + m))).save(
                os.path.join(review, f"cand_{i:03d}.png"))
    with open(os.path.join(a.out, "candidates.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["id", "x", "y", "fx", "fy", "score", "rotation", "scale", "band"])
        wr.writeheader()
        wr.writerows(rows)
    ov.save(os.path.join(a.out, "overlay.png"))
    n_l = sum(r["band"] == "likely" for r in rows)
    print(f"{len(rows)} candidates on {w}x{h} px at {dpi} dpi: {n_l} likely (score >= 0.8), {len(rows) - n_l} to review"
          f" (crops in {review}); overlay {os.path.join(a.out, 'overlay.png')}; table {os.path.join(a.out, 'candidates.csv')}")
    hist = [0] * 6
    for r in rows:
        hist[min(5, int((r["score"] - a.min) / max(1e-9, (1 - a.min)) * 6))] += 1
    print("score histogram from --min to 1.0:", hist,
          "(a clear gap between two groups usually separates the symbol from look-alikes)")


def cmd_mark(a):
    img, dpi = load(a.sheet, a.page, a.dpi)
    d = ImageDraw.Draw(img)
    r = max(6, img.width // 300)
    n = 0
    with open(a.points, newline="") as fh:
        for row in csv.DictReader(fh):
            x, y = float(row["x"]), float(row["y"])
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 0, 0), width=max(2, r // 3))
            d.text((x + r + 2, y - r), str(row.get("label") or row.get("id") or n + 1), fill=(255, 0, 0))
            n += 1
    img.save(a.out)
    print(f"marked {n} points on {img.width}x{img.height} px at {dpi} dpi -> {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("grid")
    g.add_argument("sheet"); g.add_argument("--page", type=int, default=1); g.add_argument("--dpi", type=int)
    g.add_argument("--cols", type=int, default=4); g.add_argument("--rows", type=int, default=3)
    g.add_argument("--tile-dpi", type=int, dest="tile_dpi"); g.add_argument("--out", default="/tmp/ahpele/grid")
    c = sub.add_parser("crop")
    c.add_argument("sheet"); c.add_argument("--box", required=True); c.add_argument("--page", type=int, default=1)
    c.add_argument("--dpi", type=int); c.add_argument("--px", action="store_true")
    c.add_argument("--px-dpi", type=int, dest="px_dpi"); c.add_argument("--out", default="/tmp/ahpele/crop.png")
    f = sub.add_parser("find")
    f.add_argument("sheet"); f.add_argument("--template", required=True); f.add_argument("--page", type=int, default=1)
    f.add_argument("--dpi", type=int); f.add_argument("--rot", default="0")
    f.add_argument("--scales", default="1.0"); f.add_argument("--min", type=float, default=0.45)
    f.add_argument("--out", default="/tmp/ahpele/find")
    m = sub.add_parser("mark")
    m.add_argument("sheet"); m.add_argument("--points", required=True); m.add_argument("--page", type=int, default=1)
    m.add_argument("--dpi", type=int); m.add_argument("--out", default="/tmp/ahpele/marked.png")
    a = ap.parse_args()
    {"grid": cmd_grid, "crop": cmd_crop, "find": cmd_find, "mark": cmd_mark}[a.cmd](a)


if __name__ == "__main__":
    main()
