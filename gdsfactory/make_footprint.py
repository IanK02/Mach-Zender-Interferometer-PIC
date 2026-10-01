# make_footprint.py -- writes the KiCad footprint from pad_map.py
import math
from pathlib import Path

import pad_map as pm

um = lambda v: v / 1000.0  # um -> mm
W, H = um(pm.DIE_W_UM), um(pm.DIE_H_UM)
cx, cy = W / 2, H / 2      # KiCad origin at die center; y points down


def chip_xy(p):
    return um(p["x_um"]) - cx, cy - um(p["y_um"])


y_f = cy + pm.FINGER_GAP_MM + pm.FINGER_L_MM / 2  # |y| of finger centers
ext = y_f + pm.FINGER_L_MM / 2 + 0.25             # courtyard |y|

lines = [
    '(footprint "PIC_MZI_DIE" (version 20240108) (generator "pad_map")',
    '  (layer "F.Cu") (attr smd)',
    f'  (fp_text reference "REF**" (at 0 {-ext - 0.6:.3f}) (layer "F.SilkS")'
    ' (effects (font (size 0.8 0.8) (thickness 0.12))))',
    '  (fp_text value "PIC_MZI_DIE" (at 0 0) (layer "F.Fab")'
    ' (effects (font (size 0.8 0.8) (thickness 0.12))))',
    f'  (fp_rect (start {-cx:.3f} {-cy:.3f}) (end {cx:.3f} {cy:.3f})'
    ' (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))',
    f'  (fp_rect (start {-cx-0.1:.3f} {-cy-0.1:.3f}) (end {cx+0.1:.3f} {cy+0.1:.3f})'
    ' (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
]

for p in pm.PADS:
    xc, yc = chip_xy(p)
    # finger sits directly outside its chip pad: below the die for bottom pads,
    # above it for top pads (KiCad y points down)
    sign = 1 if p["side"] == "bottom" else -1
    x_f, y = xc, sign * y_f
    lines.append(
        f'  (pad "{p["num"]}" smd rect (at {x_f:.3f} {y:.3f})'
        f' (size {pm.FINGER_W_MM} {pm.FINGER_L_MM}) (layers "F.Cu" "F.Mask"))'
    )
    # bond-length sanity check (chip pad -> near end of finger)
    L = math.hypot(x_f - xc, (y - sign * pm.FINGER_L_MM / 2) - yc)
    flag = "  <-- TOO LONG" if L > pm.MAX_BOND_MM else ""
    print(f"pad {p['num']} {p['net']:8s} {p['side']:6s} bond ~{L:.2f} mm{flag}")

half_w = max(cx, max(abs(chip_xy(p)[0]) for p in pm.PADS) + pm.FINGER_W_MM / 2) + 0.3
lines.append(
    f'  (fp_rect (start {-half_w:.3f} {-ext:.3f}) (end {half_w:.3f} {ext:.3f})'
    ' (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))'
)
lines.append(')')

out = Path("pcb/lib/PIC.pretty/PIC_MZI_DIE.kicad_mod")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines))
print(f"Wrote {out}")
