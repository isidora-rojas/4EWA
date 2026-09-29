"""Chunked reading of the Signature 1000 .ad2cp file with dolfyn 1.3.0 (dolf_env).

dolfyn.read() fails on S103043A007_HNL_10m.ad2cp as it stands. The recorder corrupted three short
stretches of the file. dolfyn's indexer (the .ad2cp.index file it writes next to the raw file)
resyncs past them, but its reader, which follows the record sizes, runs "Out of sync!" into them:
  - 08-05 14:51:34: 80,520 bytes unreadable, 122 pings (30 s) lost
  - 08-21 11:31:39: a false header (0x18 with config 0x41, dated 1964), 33 pings (8 s) lost
  - 09-15 11:27:19: a false header (0x17 bottom track, dated 1971), 2039 pings (8.5 min) lost
The two false headers also stop dolfyn working out the record layouts ("config are not identical
for id: 0x18"), so they are left out of that step (_calc_config).

Reads are split around these stretches (read_chunk). A read can only end on an ensemble whose
next record is a valid header (dolfyn stops when it reaches the next ensemble), so the last ping
before each stretch is dropped too. The first ping after a stretch can be half-written (08-05:
pressure and heading both about half their true values), so it is dropped as well. Those pings and
the false headers are NaT in ensemble_times. A stretch is found from the index: a record whose content is
impossible here (0x17, or 0x18 with a config other than 0xEF), or a record followed by an
unexpected number of bytes before the next indexed record.

The 0x1A raw-altimeter records (~2 per hour, each its own dolfyn "ensemble") are skipped. dolfyn
1.3.0 miscounts them within an ensemble range, and they are not needed: the AST surface distance
(ast_dist) and the altimeter distance are in every 0x15 burst ping. Their ensembles come back
from dolfyn as empty rows and are NaT in ensemble_times.

Importing this module applies the patches; they only affect dolfyn's Signature reader.
The index (~1.7 GB in memory) is loaded once and cached.
"""
import io
import contextlib
import warnings
import numpy as np
import pandas as pd
import dolfyn
from dolfyn.io import nortek2, nortek2_lib as _lib

warnings.filterwarnings("ignore", message="Skipped ping")
warnings.filterwarnings("ignore", message="Zero/NaN values found in 'time")

_get_index_orig = _lib.get_index
_calc_config_orig = _lib._calc_config
_read_hdr_orig = nortek2._Ad2cpReader._read_hdr
_index_cache = {}
_layout_cache = {}

BURST_B5_CONFIG = 0xEF        # config of every valid 0x18 record in this file
# bytes from the start of a record to the next indexed record, by record ID, in intact data
# (0x15 is occasionally followed by an unindexed 4313-byte record: 4795)
NORMAL_SPACING = {21: (482, 4795), 24: (178,), 26: (3420,)}


def _get_index(infile, reload=False, debug=False):
    if reload or infile not in _index_cache:
        _index_cache[infile] = _get_index_orig(infile, reload, debug)
    return _index_cache[infile]


def _bad_rows(index):
    return (index["ID"] == 23) | ((index["ID"] == 24) & (index["config"] != BURST_B5_CONFIG))


def _calc_config(index):
    return _calc_config_orig(index[~(_bad_rows(index) | (index["ID"] == 26))])


def _read_hdr(self, do_cs=False):
    hdr = _read_hdr_orig(self, do_cs)
    if hdr["id"] == 26:         # raw altimeter -> treated like 0x16 (average), which dolfyn skips
        hdr["id"] = 22
    return hdr


_lib.get_index = _get_index
_lib._calc_config = _calc_config
nortek2._Ad2cpReader._read_hdr = _read_hdr


def layout(fname):
    """Ensemble bookkeeping from the index, cached:
    group     : dolfyn ensemble number of every index row (dolfyn starts a new ensemble at every change
                of the index 'ens' counter; here each ensemble is a 0x18 then a 0x15 record)
    excluded  : ensembles holding a false header (never read)
    cut_after : ensembles after which the file is unreadable up to the next indexed record
                (a read must stop after them and restart at the next ensemble)"""
    if fname not in _layout_cache:
        idx = _get_index(fname)
        group = np.cumsum(_lib._boolarray_firstensemble_ping(idx)) - 1
        pos = idx["pos"].astype(np.int64)
        nxt = np.r_[np.diff(pos), -1]
        odd = np.zeros(len(idx), bool)
        for i, sp in NORMAL_SPACING.items():
            odd |= (idx["ID"] == i) & ~np.isin(nxt, sp)
        odd[-1] = False
        bad = _bad_rows(idx)
        excluded = np.unique(group[bad])
        cut_after = np.setdiff1d(np.unique(group[odd & ~bad]), excluded)
        _layout_cache[fname] = {"group": group, "excluded": excluded, "cut_after": cut_after,
                                "n": int(group[-1] + 1)}
    return _layout_cache[fname]


def corrupt_stretches(fname):
    """(first ensemble not read, first ensemble read again) pairs: the last ping before each
    unreadable stretch, the stretch itself and the first ping after it are skipped."""
    L = layout(fname)
    ex = set(L["excluded"].tolist())
    out = []
    for c in sorted(set(L["cut_after"].tolist()) | {e - 1 for e in ex}):
        if c in ex:
            continue
        nxt = c + 1
        while nxt in ex:
            nxt += 1
        out.append((int(c), int(nxt) + 1))   # c and nxt are dropped (see the module docstring)
    return out


def ensemble_times(fname):
    """Timestamp (datetime64[ns]) of the 0x15 ping in every ensemble, from the index.
    Element i is ensemble i as counted by dolfyn.read(nens=...). NaT for ensembles without a
    0x15 record (raw-altimeter-only) and for ensembles holding a false header."""
    idx = _get_index(fname)
    L = layout(fname)
    group = L["group"]
    is21 = (idx["ID"] == 21) & ~np.isin(group, L["excluded"])
    b = idx[is21]
    # the index stores month 1-based (unlike the data records, where dolfyn adds 1); usec100 = 100 us
    t = pd.to_datetime(pd.DataFrame({
        "year": b["year"].astype(int) + 1900, "month": b["month"].astype(int), "day": b["day"],
        "hour": b["hour"], "minute": b["minute"], "second": b["second"],
        "microsecond": b["usec100"].astype(np.int64) * 100}), errors="coerce")
    out = np.full(L["n"], np.datetime64("NaT"), "datetime64[ns]")
    out[group[is21]] = t.values
    for c, nxt in corrupt_stretches(fname):
        out[c:nxt] = np.datetime64("NaT")
    return out


def pieces(fname, ens0, ens1):
    """Split [ens0, ens1) into readable [a, b) ranges around the corrupt stretches."""
    out, a = [], int(ens0)
    for c, nxt in corrupt_stretches(fname):
        if a <= c < ens1:
            out.append((a, c))
            a = max(a, nxt)
        elif c <= a < nxt:
            a = nxt
    if a < ens1:
        out.append((a, int(ens1)))
    return [(a, b) for a, b in out if b > a]


def read_chunk(fname, ens0, ens1):
    """dolfyn.read of ensembles [ens0, ens1), split around the corrupt stretches.
    Returns a list of (Dataset, ensemble numbers of its rows), one per readable piece."""
    out = []
    for a, b in pieces(fname, ens0, ens1):
        with contextlib.redirect_stdout(io.StringIO()):     # dolfyn prints "Reading file ..."
            d = dolfyn.read(fname, nens=(a, b))
        assert d.sizes["time"] == b - a, (d.sizes["time"], a, b)
        out.append((d, np.arange(a, b)))
    return out


def scan(fname, ens, nping=40):
    """Sparse pass over the file: medians of the scalar channels over `nping` pings starting at
    each ensemble in `ens` (positions touching a corrupt stretch are skipped). One reader, index
    loaded once, ~0.2 s per position. Returns a DataFrame, one row per position ('ens' = start)."""
    rdr = nortek2._Ad2cpReader(fname)
    rows = []
    for e in ens:
        if len(pieces(fname, e, e + nping)) != 1 or pieces(fname, e, e + nping)[0] != (e, e + nping):
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            d = rdr.readfile(int(e), int(e) + nping)
        rdr.sci_data(d)
        b = d[21]
        ok = b["year"] > 0                                   # altimeter-only ensembles are empty rows
        h = np.radians(b["heading"][ok])
        rows.append({"ens": int(e), "pressure": np.median(b["pressure"][ok]),
                     "heading": np.degrees(np.arctan2(np.sin(h).mean(), np.cos(h).mean())) % 360,
                     "pitch": np.median(b["pitch"][ok]), "roll": np.median(b["roll"][ok]),
                     "temp": np.median(b["temp"][ok])})
    return pd.DataFrame(rows)
