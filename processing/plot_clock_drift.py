"""Figure: the linear clock-drift correction applied to every Vector and the ADCP.

Reads the drift and raw record span from the QC'd files' attributes (qc_clock_*), so it shows what was
applied, not what sensor_notes.csv says. Rule (adv_QC / adcp_QC section 1):
    t_true = t - drift * (t - t_raw_start) / (t_raw_end - t_raw_start)
so the correction added to each timestamp grows linearly from 0 at the first raw sample to -drift at the last.
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

root = Path(__file__).resolve().parents[1]
qc = root / "data" / "processed" / "qc"

SENSORS = ["VA1", "VB1", "VC1", "VC2", "ADCP", "VD1", "VD2", "VE1", "VE2", "VE3"]   # by transect, A -> E
FILES = {s: qc / (f"{s}_trim.nc" if s != "ADCP" else "ADCP_qc.nc") for s in SENSORS}

# sensor_notes.csv drift for the sensors whose applied value differs (DRIFT_OVERRIDE in the notebooks)
CSV_DRIFT = {"ADCP": -6.0}
NOTES = {
    "ADCP": "CSV −6 s (dashed) → −5.062 s\nfrom VC2 wave-band lag",
    "VE1": "CSV +36006.126* (PC on HST)\n− 36000 s → +6.126 s",
}

BLUE, INK, MUTED, GRID, KEPT = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df", "#eeede9"


def meta(s):
    with xr.open_dataset(FILES[s]) as ds:
        a = ds.attrs
        return dict(drift=float(a["qc_clock_drift_s"]),
                    t0=pd.Timestamp(a["qc_clock_raw_start"]), t1=pd.Timestamp(a["qc_clock_raw_end"]),
                    k0=pd.Timestamp(a["qc_trim_t_in"]), k1=pd.Timestamp(a["qc_trim_t_out"]))


m = {s: meta(s) for s in SENSORS}

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False})
fig, axs = plt.subplots(2, 5, figsize=(15, 6.4), sharex=True, sharey=True, constrained_layout=True)

for ax, s in zip(axs.flat, SENSORS):
    d = m[s]
    t = pd.date_range(d["t0"], d["t1"], periods=200)
    corr = -d["drift"] * (t - d["t0"]) / (d["t1"] - d["t0"])        # s added to the timestamps

    ax.axvspan(d["k0"], d["k1"], color=KEPT, lw=0, zorder=0)
    ax.axhline(0, color=GRID, lw=1, zorder=1)
    if s in CSV_DRIFT:
        c = -CSV_DRIFT[s] * (t - d["t0"]) / (d["t1"] - d["t0"])
        ax.plot(t, c, color=MUTED, lw=1.2, ls="--", zorder=2)
    ax.plot(t, corr, color=BLUE, lw=2, zorder=3)
    ax.plot([d["t0"], d["t1"]], [0, -d["drift"]], "o", ms=5, color=BLUE, mec="white", mew=1.5, zorder=4)

    ax.annotate(f"{-d['drift']:+.3f} s", (d["t1"], -d["drift"]), xytext=(-4, 7 if d["drift"] < 0 else -12),
                textcoords="offset points", ha="right", color=INK, fontsize=9)
    ax.set_title(f"{s}   drift {d['drift']:+.3f} s", loc="left", color=INK, fontsize=10, fontweight="bold")
    if s in NOTES:
        ax.text(0.03, 0.04 if d["drift"] < 0 else 0.96, NOTES[s], transform=ax.transAxes, fontsize=7.5,
                color=MUTED, va="bottom" if d["drift"] < 0 else "top")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=[1, 15]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

for ax in axs[:, 0]:
    ax.set_ylabel("correction added to timestamp (s)")
for ax in axs[-1]:
    ax.set_xlabel("2026 (UTC, raw clock)")
axs[0, 0].set_ylim(-12.5, 15.5)

fig.suptitle("Clock-drift correction, linear over the raw record:  "
             r"$t_\mathrm{true} = t - \mathrm{drift}\cdot\frac{t - t_\mathrm{raw\,start}}{t_\mathrm{raw\,end} - t_\mathrm{raw\,start}}$"
             "      (drift + = sensor clock fast)",
             x=0.01, ha="left", fontsize=11, color=INK)
fig.text(0.99, 0.965, "shaded = trimmed window kept in the QC product;  dots = clock set (0 s) and drift check",
         ha="right", va="bottom", fontsize=8, color=MUTED)

out = root / "figs" / "qc" / "clock_drift_all.png"
fig.savefig(out, dpi=200)
print(out)
for s in SENSORS:
    d = m[s]
    k = [-d["drift"] * (x - d["t0"]) / (d["t1"] - d["t0"]) for x in (d["k0"], d["k1"])]
    print(f"{s:5s} drift {d['drift']:+7.3f} s  raw {d['t0']:%m-%d %H:%M} -> {d['t1']:%m-%d %H:%M}  "
          f"correction over kept window {k[0]:+.3f} -> {k[1]:+.3f} s")
