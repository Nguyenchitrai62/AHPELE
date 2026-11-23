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
  python3 ahpele_drawing.py census SHEET --legend DIR [--page 1] [--dpi D] [--rot 0,90,180,270] [--scales 1]
                                  [--min 0.6] [--exclude x0,y0,x1,y1] (repeatable) [--out DIR]
      all legend symbols in one pass: DIR holds one crop per symbol (the symbol only, no legend text), named by its
      mark (A.png, B.png), cut at the SAME dpi. Every place goes to the mark that fits best; census.csv has one row per
      place (x, y, mark, score, missing and extra ink, the runner-up, band), plus an overlay and crops to review.
      "likely" needs a high score, no clear rival and almost the same ink; everything else is REVIEW. Isolated
      symbol-sized shapes that no mark fits are listed (shapes touching linework are not: read the sheet as well).
  python3 ahpele_drawing.py mark  SHEET --points pts.csv [--page 1] [--dpi D] [--out marked.png]
      draw your own counted items (csv with x,y in px of the same dpi, optional label) to check nothing is missed
      or counted twice.

SHEET can be a PDF (page rendered with PyMuPDF or pdftoppm) or an image (PNG, JPG, TIFF). Needs Pillow; `find` and
`census` need numpy (and scipy for unmatched shapes). Knows nothing about any particular drawing set.
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
        sys.exit(f"{s}: a box needs x0,y0,x1,y1")
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


def ncc(gray, tpl, cache=None):
    """Normalised cross-correlation of a template over an image (numpy FFT), 'valid' region. `cache` (a dict) keeps the
    image transforms between templates of one sheet."""
    import numpy as np
    H, W = gray.shape
    th, tw = tpl.shape
    t = tpl - tpl.mean()
    tnorm = np.sqrt((t ** 2).sum()) or 1.0
    cache = {} if cache is None else cache
    if "shape" not in cache or cache["shape"][0] < H + th - 1 or cache["shape"][1] < W + tw - 1:
        cache["shape"] = tuple(n + (n % 2) for n in (H + (max(th, 256) if H > 512 else th),
                                                     W + (max(tw, 256) if W > 512 else tw)))
        cache["F"] = np.fft.rfft2(gray, cache["shape"])
        cache["c1"] = np.cumsum(np.cumsum(np.pad(gray, ((1, 0), (1, 0))), 0), 1)
        cache["c2"] = np.cumsum(np.cumsum(np.pad(gray ** 2, ((1, 0), (1, 0))), 0), 1)
    fshape, F = cache["shape"], cache["F"]
    T = np.fft.rfft2(t[::-1, ::-1], fshape)
    corr = np.fft.irfft2(F * T, fshape)[th - 1:H, tw - 1:W]

    def box(c):
        return c[th:, tw:] - c[:-th, tw:] - c[th:, :-tw] + c[:-th, :-tw]
    n = th * tw
    s1, s2 = box(cache["c1"]), box(cache["c2"])
    var = np.maximum(s2 - s1 ** 2 / n, 1e-9)
    return corr / (np.sqrt(var) * tnorm)


def shrink(g, k):
    """Block mean by k in both directions."""
    h, w = g.shape[0] // k * k, g.shape[1] // k * k
    return g[:h, :w].reshape(h // k, k, w // k, k).mean((1, 3))


CAP = 6000  # candidates scored at full resolution per template and tile


def matches(gray, tpl, low, cache):
    """(score, x, y) of the template's top-left corner wherever it scores >= low: located on a reduced image where the
    symbol allows it, scored at full resolution; big images are worked in tiles."""
    import numpy as np
    th, tw = tpl.shape
    k = max(1, min(3, min(th, tw) // 12))
    if k not in cache:
        cache[k] = (shrink(gray, k) if k > 1 else gray, {})
    small, subs = cache[k]
    tsmall = shrink(tpl, k) if k > 1 else tpl
    if tsmall.std() < 1e-3 or min(small.shape) <= max(tsmall.shape):
        return []
    out, m, step = set(), k + 1, 1800
    keep = small.size <= 9e6  # keep transforms only when they fit comfortably in memory
    for ty in range(0, small.shape[0], step):
        for tx in range(0, small.shape[1], step):
            tile = small[ty:ty + step + tsmall.shape[0], tx:tx + step + tsmall.shape[1]]
            if tile.shape[0] <= tsmall.shape[0] or tile.shape[1] <= tsmall.shape[1]:
                continue
            r = ncc(tile, tsmall, subs.setdefault((ty, tx), {}) if keep else None)
            pad = np.pad(r, 1, constant_values=-1.0)  # local maxima only
            peak = np.ones(r.shape, bool)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    peak &= r >= pad[1 + dy:1 + dy + r.shape[0], 1 + dx:1 + dx + r.shape[1]]
            ys, xs = np.where(peak & (r >= (low if k == 1 else low - 0.25)))
            if len(ys) > CAP:
                print(f"  note: {len(ys)} candidates in one part of the sheet, best {CAP} scored (raise --min or --exclude text)")
            for i in np.argsort(-r[ys, xs])[:CAP]:
                y0, x0 = (int(ys[i]) + ty) * k, (int(xs[i]) + tx) * k
                if k == 1:
                    out.add((round(float(r[ys[i], xs[i]]), 4), x0, y0))
                    continue
                y0, x0 = max(0, y0 - m), max(0, x0 - m)
                win = gray[y0:y0 + th + 2 * m, x0:x0 + tw + 2 * m]
                if win.shape[0] < th or win.shape[1] < tw:
                    continue
                q = ncc(win, tpl)
                y, x = divmod(int(q.argmax()), q.shape[1])
                if q[y, x] >= low:
                    out.add((round(float(q[y, x]), 4), x0 + x, y0 + y))
    return sorted(out, reverse=True)


def ink_diff(gray, tpl, x, y):
    """(missing, extra): share of the template's ink absent at the place, and ink there that the template lacks, with
    one pixel of tolerance."""
    import numpy as np
    th, tw = tpl.shape
    win = gray[y:y + th, x:x + tw]
    if win.shape != tpl.shape:
        return 1.0, 1.0
    a, b = tpl < 0.6, win < 0.6

    def grow(z):
        p = np.pad(z, 1)
        o = np.zeros(z.shape, bool)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                o |= p[dy:dy + z.shape[0], dx:dx + z.shape[1]]
        return o
    n = max(1, int(a.sum()))
    return float((a & ~grow(b)).sum()) / n, float((b & ~grow(a)).sum()) / n


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


def cmd_census(a):
    try:
        import numpy as np
    except ImportError:
        sys.exit("census needs numpy")
    if not os.path.isdir(a.legend):
        sys.exit(f"--legend {a.legend}: no such directory")
    img, dpi = load(a.sheet, a.page, a.dpi)
    w, h = img.size
    work = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    work = work.copy()
    for spec in a.exclude:  # legend, title block, tables: not counted
        try:
            x0, y0, x1, y1 = parse_box(spec, w, h, a.px)
        except ValueError:
            sys.exit(f"--exclude {spec}: expected x0,y0,x1,y1 (fractions of the sheet, or pixels with --px)")
        work[max(0, min(y0, y1)):max(y0, y1), max(0, min(x0, x1)):max(x0, x1)] = 1.0
    hits, sizes, cache, marks = [], [], {}, []
    for n in sorted(os.listdir(a.legend)):
        if not n.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
            continue
        mark = os.path.splitext(n)[0]
        try:
            g = np.asarray(Image.open(os.path.join(a.legend, n)).convert("L"), dtype=np.float64)
        except OSError:
            print(f"  {mark}: cannot read {n}, skipped")
            continue
        ys, xs = np.where(g < 160)
        if not len(ys):
            print(f"  {mark}: crop is blank, skipped")
            continue
        g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]  # the symbol itself, then a uniform white margin
        sh, sw = g.shape
        if max(sh, sw) > 3 * min(sh, sw):
            print(f"  {mark}: crop is {sw}x{sh} px: check that it holds the symbol only, without legend text")
        marks.append(mark)
        sizes.append((sw, sh))
        tpl_img = Image.fromarray(np.pad(g, 2, constant_values=255).astype("uint8"))
        seen_t = []
        for rot in [int(r) for r in a.rot.split(",")]:
            for sc in [float(v) for v in a.scales.split(",")]:
                t = tpl_img.rotate(rot, expand=True, fillcolor=255)
                if sc != 1.0:
                    t = t.resize((max(3, int(t.width * sc)), max(3, int(t.height * sc))), Image.LANCZOS)
                tpl = np.asarray(t, dtype=np.float64) / 255.0
                if tpl.shape[0] >= h or tpl.shape[1] >= w or tpl.std() < 1e-3:
                    continue
                if any(o.shape == tpl.shape and np.abs(o - tpl).mean() < 0.01 for o in seen_t):
                    continue  # symmetric symbol: same picture after rotation
                seen_t.append(tpl)
                th, tw = tpl.shape
                for v, x, y in matches(work, tpl, a.min, cache):
                    miss, extra = ink_diff(work, tpl, x, y)
                    hits.append((v - 0.5 * (miss + min(extra, 1.0)), v, x + tw / 2.0, y + th / 2.0, tw, th, rot, mark, miss, extra))
    if not marks:
        sys.exit(f"no usable symbol crops in {a.legend}")
    hits.sort(key=lambda z: -z[0])
    cells, places = {}, []  # best fit per place; another mark at the same place becomes the runner-up
    size = max(max(z) for z in sizes) + 4
    for rank, sc, x, y, tw, th, rot, mark, miss, extra in hits:
        cx, cy = int(x // size), int(y // size)
        same = None
        for i in range(cx - 1, cx + 2):
            for j in range(cy - 1, cy + 2):
                for p in cells.get((i, j), []):
                    if abs(x - p["x"]) < 0.6 * min(tw, p["w"]) and abs(y - p["y"]) < 0.6 * min(th, p["h"]):
                        ratio = (tw * th) / float(p["w"] * p["h"])
                        if 0.5 < ratio < 2.0 or mark == p["mark"]:
                            same = same or p
                        elif miss <= 0.1:
                            p["nested"] = True  # a much larger or smaller symbol at the same place: keep both, review
        if same is None:
            p = {"x": x, "y": y, "w": tw, "h": th, "rotation": rot, "mark": mark, "score": sc, "rank": rank, "missing": miss,
                 "extra": extra, "second": "", "second_rank": -9.0, "second_score": 0.0, "nested": False}
            cells.setdefault((cx, cy), []).append(p)
            places.append(p)
        elif mark != same["mark"] and not same["second"]:
            same["second"], same["second_score"], same["second_rank"] = mark, sc, rank
    os.makedirs(os.path.join(a.out, "review"), exist_ok=True)
    ov = img.copy()
    d = ImageDraw.Draw(ov)
    rows = []
    places.sort(key=lambda p: (p["mark"], p["y"], p["x"]))
    for i, p in enumerate(places, 1):
        close = bool(p["second"]) and p["rank"] - p["second_rank"] < a.margin
        good = p["score"] >= 0.8 and p["missing"] <= 0.1 and p["extra"] <= 0.1 and not close and not p["nested"]
        band = "likely" if good else "REVIEW"
        col = (0, 170, 0) if good else (255, 120, 0)
        x0, y0, x1, y1 = p["x"] - p["w"] / 2, p["y"] - p["h"] / 2, p["x"] + p["w"] / 2, p["y"] + p["h"] / 2
        d.rectangle([x0, y0, x1, y1], outline=col, width=max(2, w // 1500))
        d.text((x1 + 2, y0), f"{i}:{p['mark']}", fill=col)
        rows.append({"id": i, "x": round(p["x"]), "y": round(p["y"]), "fx": round(p["x"] / w, 4), "fy": round(p["y"] / h, 4),
                     "mark": p["mark"], "score": round(p["score"], 3), "missing_ink": round(p["missing"], 2),
                     "extra_ink": round(p["extra"], 2), "second": p["second"], "second_score": round(p["second_score"], 3),
                     "rotation": p["rotation"], "band": band})
        if not good:
            m = int(1.5 * max(p["w"], p["h"]))
            c = img.crop((max(0, int(p["x"] - m)), max(0, int(p["y"] - m)), min(w, int(p["x"] + m)), min(h, int(p["y"] + m))))
            c.resize((c.width * 3, c.height * 3), Image.LANCZOS).save(os.path.join(a.out, "review", f"place_{i:03d}.png"))
    with open(os.path.join(a.out, "census.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["id", "x", "y", "fx", "fy", "mark", "score", "missing_ink", "extra_ink", "second",
                                            "second_score", "rotation", "band"])
        wr.writeheader()
        wr.writerows(rows)
    ov.save(os.path.join(a.out, "overlay.png"))
    print(f"{len(rows)} places on {w}x{h} px at {dpi} dpi ({sum(r['band'] == 'REVIEW' for r in rows)} to review)")
    for mark in marks:
        mine = [r for r in rows if r["mark"] == mark]
        rev = [r for r in mine if r["band"] == "REVIEW"]
        scores = sorted((r["score"] for r in mine), reverse=True)
        print(f"  {mark:8s} {len(mine) - len(rev):4d} likely  {len(rev):4d} review"
              + (f"  scores {scores[0]:.2f}..{scores[-1]:.2f}" if scores else "  no place above --min"))
    odd = unmatched(work, places, sizes)
    print(f"isolated symbol-sized shapes that match no legend mark: {len(odd)}"
          + (" (text and dimensions included; first 30)" if len(odd) > 30 else "")
          + (" (x,y): " + "; ".join(f"{x},{y}" for x, y in odd[:30]) if odd else ""))
    print(f"files: {a.out}/census.csv, overlay.png, review/. A score is evidence, not a count: look at the overlay and at every"
          " review crop. Symbols that are not in the legend can look much like one that is: compare outline, fill and"
          " inner marks.")


def unmatched(gray, places, sizes):
    """Centres of connected dark shapes of symbol size that no place covers (needs scipy; empty without it)."""
    import numpy as np
    try:
        from scipy import ndimage
    except ImportError:
        print("(install scipy to list shapes that match no legend mark)")
        return []
    lab, _ = ndimage.label(gray < 0.6, structure=np.ones((3, 3)))
    lo = max(8, 0.7 * min(min(z) for z in sizes))
    hi = 1.5 * max(max(z) for z in sizes)
    out = []
    for sl in ndimage.find_objects(lab):
        bh, bw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not (lo <= bh <= hi and lo <= bw <= hi):
            continue
        x, y = (sl[1].start + sl[1].stop) // 2, (sl[0].start + sl[0].stop) // 2
        if all(abs(x - p["x"]) > 0.6 * max(p["w"], bw) or abs(y - p["y"]) > 0.6 * max(p["h"], bh) for p in places):
            out.append((x, y))
    return out


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
    n = sub.add_parser("census")
    n.add_argument("sheet"); n.add_argument("--legend", required=True); n.add_argument("--page", type=int, default=1)
    n.add_argument("--dpi", type=int); n.add_argument("--rot", default="0,90,180,270"); n.add_argument("--scales", default="1.0")
    n.add_argument("--min", type=float, default=0.6); n.add_argument("--margin", type=float, default=0.08)
    n.add_argument("--exclude", action="append", default=[]); n.add_argument("--px", action="store_true")
    n.add_argument("--out", default="/tmp/ahpele/census")
    m = sub.add_parser("mark")
    m.add_argument("sheet"); m.add_argument("--points", required=True); m.add_argument("--page", type=int, default=1)
    m.add_argument("--dpi", type=int); m.add_argument("--out", default="/tmp/ahpele/marked.png")
    a = ap.parse_args()
    {"grid": cmd_grid, "crop": cmd_crop, "find": cmd_find, "census": cmd_census, "mark": cmd_mark}[a.cmd](a)


if __name__ == "__main__":
    main()
