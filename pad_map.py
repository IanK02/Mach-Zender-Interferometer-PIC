# pad_map.py -- single source of truth for chip pads and PCB bond fingers

# ---- Die ----
DIE_W_UM, DIE_H_UM = 13000.0, 1200.0

# ---- Chip pads (positions are pad CENTERS, origin = die lower-left) ----
# One column per MZI heater: +12 V (HI) pad on the bottom edge, LO pad directly
# above it on the top edge.
PAD_SIZE_UM = 100.0
PAD_PITCH_UM = 2500.0         # column pitch (along each edge)
PAD_ROW_Y_BOTTOM_UM = 100.0   # HI pads
PAD_ROW_Y_TOP_UM = DIE_H_UM - 100.0  # LO pads

N_HEATERS = 4
NETS = [f"HTR{k}_{s}" for k in range(1, N_HEATERS + 1) for s in ("HI", "LO")]

# x of each heater's pad column, centered on the die
COLUMN_X_UM = [
    DIE_W_UM / 2 + (k - (N_HEATERS - 1) / 2) * PAD_PITCH_UM for k in range(N_HEATERS)
]

# Pad numbers: HTRn_HI = 2n-1 (bottom), HTRn_LO = 2n (top)
PADS = [
    {
        "num": i + 1,
        "net": net,
        "side": "bottom" if net.endswith("_HI") else "top",
        "x_um": COLUMN_X_UM[i // 2],
        "y_um": PAD_ROW_Y_BOTTOM_UM if net.endswith("_HI") else PAD_ROW_Y_TOP_UM,
    }
    for i, net in enumerate(NETS)
]

# ---- PCB bond fingers (mm). One finger directly outside each chip pad (below
# the die for bottom pads, above it for top pads), so finger pitch equals
# PAD_PITCH_UM (2.5 mm) and each bond runs straight out. ----
FINGER_W_MM, FINGER_L_MM = 1.0, 1.0
FINGER_GAP_MM = 1.0   # die edge -> finger inner edge
MAX_BOND_MM = 2.5     # sanity limit on wire-bond length


def check():
    """Make sure every pad is fully on the die and pads don't overlap."""
    half = PAD_SIZE_UM / 2
    ok = True
    for p in PADS:
        x, y = p["x_um"], p["y_um"]
        if not (half <= x <= DIE_W_UM - half and half <= y <= DIE_H_UM - half):
            print(f"ERROR: pad {p['num']} ({p['net']}) sticks off the die")
            ok = False
    for side in ("bottom", "top"):
        xs = sorted(p["x_um"] for p in PADS if p["side"] == side)
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        if gaps and min(gaps) < PAD_SIZE_UM + 50:
            print(f"ERROR: {side} pads too close, nearly touching")
            ok = False
        if gaps and min(gaps) / 1000 < FINGER_W_MM + 0.5:
            print(f"ERROR: {side} PCB fingers less than 0.5 mm apart")
            ok = False
    return ok


if __name__ == "__main__":
    for p in PADS:
        print(f"pad {p['num']}  {p['net']:8s}  {p['side']:6s}  "
              f"x={p['x_um']:7.1f} um  y={p['y_um']:6.1f} um")
    print("OK" if check() else "PROBLEMS FOUND")
