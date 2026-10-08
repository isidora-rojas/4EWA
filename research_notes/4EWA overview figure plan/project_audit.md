# 4EWA project audit: what exists and which overview figures are feasible

Audit date 2026-10-08. Read-only. Sources are local files (paths relative to `/Users/isidorarojas/Desktop/DIRECTORY/2026/4EWA`). Numbers computed with `python -I` scripts in the scratchpad (insp.py, tab.py, geo.py, ev.py, at.py, cov.py). No web sources were used, so "citations" are file paths.

## 1. Instrument table (15 instruments)

### Takeaway
Fourteen of the 15 instruments have a QC'd hourly record (9 ADV, 5 Paros). The ADCP has its own QC'd file and hourly table. ADV and ADCP records run about 07-19 to 09-15 (UTC). Paros run 07-28 (PB1, PB2, PC1) or 08-05 (PD1, PE1) to 09-16. Hourly `seg_ok` is 95 to 100 % for every sensor.

### Cited Findings
Time spans are the first and last QC'd sample (`data/processed/qc/{S}_QC.nc`, `time`). `seg_ok` is the fraction of each sensor's own hours with `seg_ok` True (`hour` dim). Depth is the median `depth_h` of the QC'd file (pressure derived). Lat/lon are from `data/metadata/sensor_notes.csv`. "Offshore dist" is computed by projecting positions onto each transect's shore-normal (`Shore Normal Onshore` column) and measuring from the most onshore sensor on that transect (usually the Paros). It is **not** distance from the shoreline (no shoreline or bathymetry file exists).

| ID | type (S/N) | transect | nominal / median depth (m) | offshore dist from transect's shallowest sensor (m) | lat, lon (WGS84) | fs | valid span (UTC) | hours | seg_ok |
|---|---|---|---|---|---|---|---|---|---|
| VA10 | Vector 8190 | A | 10 / 10.4 | single sensor on A | 21.29180, -158.05096 | 2 Hz | 07-19 00:16 to 09-15 21:18 | 1414 | 95.3 % |
| VB5 | Vector 9649 | B | 5.5 / 4.6 | 769 (PB1 at 0, PB2 at 116) | 21.29416, -158.04589 | 2 Hz | 07-19 23:13 to 09-15 20:44 | 1390 | 99.9 % |
| VC5 | Vector 12411 | C | 5 / 5.3 | 535 (PC1 at 0) | 21.29733, -158.04154 | 2 Hz | 07-19 01:41 to 09-15 20:16 | 1412 | 99.8 % |
| VC10 | Vector 15241 | C | 10 / 11.0 | 1191 | 21.29153, -158.04036 | 2 Hz | 07-19 20:34 to 09-15 19:27 | 1392 | 99.9 % |
| VD5 | Vector 12596 | D | 5 / 5.3 | 544 (PD1 at 0) | 21.29819, -158.02864 | 2 Hz | 07-18 22:29 to 09-15 22:10 | 1417 | 94.8 % |
| VD10 | Vector 8195 | D | 10 / 10.9 | 959 | 21.29458, -158.02755 | 2 Hz | 07-20 00:32 to 09-15 23:52 | 1392 | 98.1 % |
| VE4 | Vector 15254 | E | 4 / 4.2 | 280 (PE1 at 0) | 21.30163, -158.02270 | 2 Hz | 07-18 21:14 to 09-15 22:36 | 1418 | 99.7 % |
| VE7 | Vector 15056 | E | 7 / 7.5 | 678 | 21.29801, -158.02199 | 2 Hz | 07-18 19:56 to 09-15 22:59 | 1420 | 98.6 % |
| VE10 | Vector 15048 | E | 10 / 10.7 | 1072 | 21.29444, -158.02146 | 2 Hz | 07-20 01:31 to 09-15 23:23 | 1391 | 98.6 % |
| ADCP | Signature 1000 103043 | C (about 3 m W of VC10) | 10 / 10.9 | 1191 (same as VC10) | 21.29153, -158.04036 | 4 Hz | 07-19 21:07 to 09-15 19:30 | 1391 | 98.9 % any cell; 98.7 % in the 13 usable cells |
| PB1 | Paros 23626 (sensor_notes lists 123626) | B | n/a / 2.3 | 0 | 21.30156, -158.04632 | 2 Hz | 07-28 18:23 to 09-16 22:38 | 1205 | 99.8 % |
| PB2 | Paros 35605 (notes: 135605) | B | n/a / 2.7 | 116 | 21.30057, -158.04594 | 2 Hz | 07-28 19:16 to 09-16 22:24 | 1204 | 99.8 % |
| PC1 | Paros 35604 (notes: 135604) | C | n/a / 2.4 | 0 | 21.30206, -158.04245 | 2 Hz | 07-28 20:25 to 09-16 20:43 | 1201 | 99.8 % |
| PD1 | Paros 35603 (notes: 135603) | D | n/a / 3.0 | 0 | 21.30303, -158.02977 | 2 Hz | 08-05 22:07 to 09-16 19:04 | 1006 | 99.8 % |
| PE1 | Paros 24069 (notes: 124069) | E | n/a / 2.7 | 0 | 21.30418, -158.02343 | 2 Hz | 08-05 21:00 to 09-16 19:42 | 1007 | 99.9 % |

- Paros hourly `seg_ok` is a one-segment-per-file completeness test only (no z2 test). ADV `seg_ok` includes the z2 test. These are not equivalent. Source: `README.md`, `*_QC.nc` attrs.
- Longest bad runs of `seg_ok`: VD5 41 h from 09-12 15:00; VA10 19 h on 09-01 and 19 h on 09-14, 14 h on 09-15; VE7 19 h from 08-15 17:00. Source: cov.py.
- Hours in common 07-19 to 09-15 (1416 h): all 9 ADVs `seg_ok` = 1222 h; all 14 non-ADCP sensors = 823 h; all 15 = 813 h (the ADCP counted as OK only where cells 1 to 13 are OK). Common start of all 14 is 08-05 22:00, common end 09-15 19:00.
- Along-transect geometry (computed from sensor_notes lat/lon):
  - Cross-shore separations: VB5 to PB1 824 m; VC5 to VC10 656 m; VC5 to PC1 535 m; VD5 to VD10 417 m; VD5 to PD1 550 m; VE4 to VE7 409 m; VE7 to VE10 401 m; VE4 to PE1 294 m.
  - Alongshore position (projection on a heading of 80 deg true, an approximation because the sheet's shoreline headings vary from 66 to 93 deg): A about -1250 m, B about -690 to -570 m, C about -180 m, D about +1150 m, E about +1810 m. Spacing between transects is roughly A to B 560 m, B to C 505 m, C to D 970 m, D to E 665 m. Straight-line distances between transect centroids are bigger (926, 614, 1340, 657 m) because the transects are offset cross-shore. Treat both as approximate.
  - The KML in the repo root (`ewa_sensor_map_old.kml`) uses the old IDs (VA1, VB1, ...). It carries the same lat/lon as sensor_notes, plus three drawn transect lines (A, C, E and a D entry), the lidar line scan footprint, RBR positions for 07-21, 07-23, 08-12/13 and 09-11, and a "path from keehi". No newer KML was found.
- Sensor depth in the notes is approximate MSL. Several notes carry a measured value (VD5 -5 / 16 ft, VE7 -7 / 24 ft, VE4 -4 / 14 ft). Median pressure-derived depth differs by up to about 1 m (VB5 nominal 5.5 vs 4.6 median; VC10 10 vs 11.0). This depth includes the tide and the sensor height assumptions.

### Inferences
- Transect A has a single sensor, so cross-shore profiles exist for B, C, D, E only. B has two Paros plus VB5, C has VC10/ADCP, VC5, PC1, D has VD10, VD5, PD1, E has VE10, VE7, VE4, PE1.
- The "5 m line" and "10 m line" for alongshore comparisons are VB5, VC5, VD5, VE4 and VA10, VC10, VD10, VE10 respectively. The actual depths of the 5 m line are 4.2 to 5.3 m.

### Gaps
- Distance to shoreline per transect cannot be computed: no shoreline, topography or bathymetry file is in the project. The KML mentions "White Plains topo points" and a lidar scan, but the data are not on disk (`data/raw` holds only Paros, Signature1000, vectors).
- S/N mismatch: sensor_notes lists Paros S/N with a leading "1" (123626 vs 23626 in the QC files). The README table uses the QC value. Not verified against the instrument labels.
- The README says the deployment ran "07/28 to 09/16". The ADV and ADCP records actually start 07-18/19 and only the Paros start 07-28 / 08-05.

## 2. Data products available per sensor

### Takeaway
ADVs have everything: 2 Hz velocity and pressure, hourly spectra (Spp, Suu, Svv, Sww, co-spectra with E/N velocity, Seta), Hs/Tp/Dm and wave direction. Paros have pressure, Seta and Hs/Tp only, with no direction. The ADCP has a 4 Hz velocity profile (13 usable cells) but no wave spectra file.

### Cited Findings
- `data/processed/qc/{V*}_QC.nc` (about 330 to 350 MB each, 2 Hz): `u` (onshore), `v` (alongshore, +W), `w`, `u_east`, `v_north`, `p`, `p_raw`, `patm`, heading/pitch/roll, beam `amp`/`corr`, `vel_qc_flag`, and per-hour `seg_ok`, `z2`, `z2_IG`, `Hs_SS`, `depth_h`, `wave_dir_h`, `wave_axis_h`, `wave_aniso_h`, `coh_w_dpdt_h`, `Spp_median`. 10.17 M samples for VA10.
- `{V*}_spec.nc` and `{P*}_spec.nc`: hourly, 513 frequencies (0 to 1 Hz, df 0.00195), vars `Seta`, `h_mean`, `Spp`, `Hs`, `Tp`, `Dm`. ADVs also have `Suu`, `Svv`, `Sww`, `Co_pE`, `Co_pN`. Welch with Hann window, nperseg 1024 (512 s), 50 % overlap, averaged per hour, `use_seg_ok` = 1. `Hs` is 0.04 to 0.25 Hz. `Dm` is "mean wave direction, coming FROM, 0.04 to 0.25 Hz", deg true. I confirmed the band integral of `Seta` over 0.04 to 0.25 Hz reproduces `Hs` to better than 0.02 m for all 14 spec files.
- IG and SS Hs are **not stored**; the notebook computes them from `Seta` with `Hs_band` (SS 0.04 to 0.25 Hz, IG 0.004 to 0.04 Hz). I reproduced this. Median IG Hs: 10 m ADVs 0.054 to 0.073 m, 5 m ADVs 0.08 to 0.135 m, Paros 0.16 to 0.21 m. Max IG Hs: 0.77 m (VA10) and 0.80 m (VB5).
- `adv_waves_hourly.csv` (columns sensor,time,Hs,Tp,Dp; 9 ADVs; Hs 0.39 to 5.56 m) and `adv_bulk512.csv` (512 s: Hs, h, u, v, cur_dir, wave_dir; about 9800 to 9970 segments per ADV). Note the README table of bulk ranges (Hs max 6.05 m at VA10) comes from 512 s segments; the hourly maximum is 5.56 m. The README table also has a typo ("2.7git0 m" for VE7).
- `adv_Spp_hourly.nc`: 52 MB, hourly pressure spectra for ADVs (not opened in detail beyond header).
- Paros `{P*}_QC.nc` (non-uniform time, 7167 samples then 16.5 s gap each hour): `p`, `p_raw`, `patm`, `temp`, hourly `seg_ok`, `depth_h`, `Hs_SS` (uncorrected pressure Hs, diagnostic). No velocity and so no direction (`Dm` var in the Paros spec files is present, NaN median, so unusable).
- ADCP: `ADCP_qc.nc` (5.4 GB, 4 Hz, 19.96 M samples), `u`, `v`, `w`, `u_east`, `v_north` on 19 range cells (1.1 to 10.1 m above the transducer, 0.5 m cells), a 5th vertical beam, pressure and surface-track depth, `qc` bit flags. `ADCP_qc_hourly.nc`: per hour and cell `seg_ok`, `z2`, pct flags, and per hour `Hs_SS`, `z2_IG`, `depth_h` (median 10.9 m). `ADCP_QC.nc` and `ADCP_qc.nc` are the same file name on this case-insensitive filesystem. Cells 1 to 13 (1.1 to 7.1 m) have `seg_ok` about 98.9 %; cells 14 to 19 are 0 % (surface mask, `pct_surface` rises above cell 16). Also `ADCP_qc_test.nc` (278 MB, test product) and `ADCP_coarse_scan.csv`.
- Tide and met: `data/metadata/noaa_1612340_water_level.csv` (6 min, 07-18 to 09-19), `noaa_1612340_wind.csv` (hourly, speed, dir, gust; to 09-17), `noaa_1612340_air_pressure.csv` (hourly). Buoy: `cdip238_waves.csv` (30 min, Hs, Tp, Dp; 07-18 to 09-17, 2976 rows; notebook calls it "Barbers Point"). Tide check against Honolulu: ADV `qc_clock_tide_lag_min` 0 (VA10 -2, ADCP -4), Paros -1 to +2 min.
- Headmotion: `data/processed/qc/headmotion/{VB5,VE4,VE7}_headmotion_{events,segments}.csv` plus `processing/looseheadloosedata.ipynb`.

### Inferences
- IG vs SS, SS Hs profiles, and spectrogram figures can be produced for all 14 pressure sensors straight from `*_spec.nc`.
- Direction exists for 9 ADVs only (`Dm` in spec, `Dp` in adv_waves_hourly, `wave_dir` in bulk512), and `Dm` is a mean direction of the 0.04 to 0.25 Hz band, so no swell-only or frequency-resolved directional spectra yet (but `Co_pE`, `Co_pN`, `Suu`, `Svv` exist, so a frequency-resolved Dm can be computed).

### Gaps and caveats (all documented in README or file attrs unless flagged)
- **Paros air offset not applied** (`qc_air_offset_applied = 0`). Pre-deployment in-air offsets are -0.04 to -0.06 dbar, post-recovery +0.06 to +0.09 dbar (11 to 15 cm apart per unit, post affected by the bucket). Absolute mean level (setup, mean depth) from Paros is uncertain by about 0.1 m. `depth_h` and the depth correction for the Hs of Paros are therefore uncertain at the 5 % level for 2.3 to 3 m depths. I did not test the effect.
- **ADV mean pressure offset**: `qc_patm_offset_C_pre/post` is about 8.7 to 10.1 dbar (a large internal offset). The pre-post change is small (below 0.05 dbar) for all except VA10 (0.313 dbar) and VE10 (-0.188 dbar). Any subtidal depth or setup from VA10 and VE10 is unreliable at the 0.2 to 0.3 m level. The reason was not investigated.
- **Loose prong heads**: VB5, VE4, VE7 (README note). Wave direction and the rotated velocity for those are suspect. VE4 wave direction offset vs VE10: `rot_wave_dir_mean_deg` VE4 10.9 deg vs VE10 353.0 deg. The VE4 heading correction from `looseheadloosedata.ipynb` is not applied in `initial_figs.ipynb`. VE10 has `HEADING_OVERRIDE` (KVH 343, per file attrs).
- **Clock**: all clocks assumed UTC, linear drift applied; residual lag against the tide is within +-4 min (VA10 -2, ADCP -4). Clock accuracy to a few seconds for cross-spectra was verified only for PE1 vs VE4 (README) and ADCP vs VC10. Not verified for other pairs. VE4 uses a documented `DRIFT_OVERRIDE` (+6.126 s listed; the notes say the raw value was 36006.126 s, the PC was on Hawaii time).
- **ADCP cell count**: the README says 23 cells; the QC'd file has 19 range cells, 13 usable. Not reconciled (may be the raw instrument config vs the saved file). ADCP wave Hs only as the hourly `Hs_SS`.
- Paros sensors have no compass/orientation and no z2 test. Hourly 16.5 s gap each file is a hazard for spectra at long periods and for cross-spectra with ADVs.
- The ADV Hs uses a cosh(kh) correction with a 0.25 Hz cutoff. At 10 m this amplifies noise (notebook comment: blows up above about 0.3 Hz).

## 3. Feasibility of the candidate figures

### Takeaway
Everything that only needs pressure-derived Hs, spectra, tide, wind, buoy, and ADV velocity is feasible now. What is missing is bathymetry or shoreline data for true cross-shore distance and for shoaling predictions, any setup estimate that needs absolute reference levels (Paros offset unresolved), and any offshore wind beyond the Honolulu station.

### Cited Findings (per candidate)
| Figure | Status | Inputs available | Missing or caveat |
|---|---|---|---|
| Cross-shore Hs profiles (Hs vs depth or vs distance) | Feasible now for B, C, D, E (A has one sensor) | `*_spec.nc` Hs/Seta for 10 m, 7 m, 5 m, 4 m ADVs and Paros (2.3 to 3 m); Paros only after 07-28 or 08-05 | Distance axis is relative (sensor-to-sensor, see table); no bathymetry for linear shoaling prediction or h(x). Depth axis from pressure is available. Event windows before 07-28 have no Paros. |
| IG vs SS | Feasible now | `Seta` in all 14 spec files. Existing `Hs_SS_vs_IG_*.png` covers it | The existing full-record version shows only the 4 10 m and 4 5 m ADVs; Paros panels were not in the full-period figure I viewed (the notebook setup includes P sensors in the 5-column layout; the full-record file shows 8 panels). IG ratio vs depth or vs shoreline distance not yet plotted. |
| Setup (mean water level vs offshore) | Not reliable | `h_mean` per hour, tide at Honolulu | Paros offset not applied (11 to 15 cm uncertainty); VA10 / VE10 offset drift 0.31 / 0.19 dbar; the expected signal for Hs of 2 to 5 m is about 0.05 to 0.3 m at 2 to 3 m depth. Setup can be attempted only as a change relative to a calm baseline per sensor. Not tested. |
| Alongshore heatmaps (time x alongshore position) | Feasible now with irregular alongshore spacing | 4 sensors at the 5 m line and 4 at the 10 m line (+A10) | Only 4 to 5 alongshore positions at each depth; heatmap is coarse, and the A to B to C to D to E alongshore positions are only approximate. A line plot or a small-multiple is more honest. |
| Coverage matrix (sensors x time) | Feasible now | `seg_ok` per hour for all 15 (ADCP via cells) | None. Numbers in section 1. |
| Tide | Feasible now | `noaa_1612340_water_level.csv` (Honolulu Harbor, not on site), plus `h_mean` per sensor | Tide gauge is about 25 km east; lag check agrees within +-4 min and r = 0.98 for Paros (README). Tide is already panel 4 of A1_overview. |
| Mean currents | Feasible now for 9 ADVs and the ADCP profile | `u`, `v`, `u_east`, `v_north` per sample, hourly `bulk512` | VB5, VE4, VE7 direction suspect (loose head). ADV velocity range is -0.75 to +0.62 m/s (README). The map version is already in `initial_figs.ipynb` (B.3b, event vs calm vs difference), saved not verified. |
| Directional estimates | Feasible for the 9 ADVs | `Dm`, `Dp`, `wave_dir` (512 s); `Co_pE`, `Co_pN` for frequency-resolved direction | Not for Paros. Loose-head sensors suspect. `Dm` about 165 to 180 deg at the ADVs vs buoy about 190 deg (see transect C figure). Refraction is the likely reason; not verified. |
| Coherence / phase between sensors | Feasible only on a restricted basis | Raw 2 Hz series for ADVs (uniform), clocks aligned to a few seconds | Needs the Paros gap handling (16.5 s each hour, 512 s segmentation aligned to file starts). Clock accuracy is only verified for a few pairs. At swell frequencies (0.05 to 0.1 Hz) a few seconds is acceptable only for the 10 m / 5 m pairs. No bathymetry for phase speed comparison. |
| Buoy comparison | Feasible now | `cdip238_waves.csv` | Buoy is offshore (Barbers Point per notebook comment; its location is not stored in the project). |
| Wind | Honolulu hourly only | `noaa_1612340_wind.csv` | No local wind. |

### Inferences
- A "deployment overview" figure (buoy Hs/Tp/Dp, tide, SS Hs by sensor, subtidal speed, wind) already exists as `figs/initial/A1_overview.png`, so a new overview should differ (for example add the coverage matrix or an IG panel).

### Gaps
- No bathymetry or shoreline exists locally, so any cross-shore distance, slope, or shoaling-theory curve is out of reach until the lidar or topo data, or the kml-based path, is added.
- I did not run or verify any figure cells in `processing/initial_figs.ipynb`, and I did not test the IG band's validity at the ADCP.

## 4. Three largest swell events

### Takeaway
Ranked by the buoy peak: (1) 8 September, Hs 7.2 m smoothed (7.79 m raw), Tp 13.3 s, from 240 deg; (2) 16 August, Hs 2.3 m smoothed (2.56 m raw), Tp 12.5 s from 198 deg; (3) 24 July, Hs 1.67 m (1.78 raw), Tp 20 s from 191 deg, a long-period south swell. Candidate 4 is 4 September (1.75 to 1.9 m, Tp 10.5 s).

### Cited Findings
Buoy `cdip238_waves.csv`; peaks found on a 3 h running mean with min spacing 3 days and prominence 0.3 m. Sensor values from `adv_waves_hourly.csv` (hourly, 3 h smoothed).

| event | buoy peak time (UTC) | buoy Hs (smoothed / raw max within +-12 h) | buoy Tp, Dp | 10 m sensor Hs | sensor Tp, Dp |
|---|---|---|---|---|---|
| 1 (notebook "Lowell", window 09-07 to 09-09) | 2026-09-08 11:00 | 7.21 / 7.79 m | 13.3 s, 240 deg | VA10 5.44, VD10 5.01, VE10 4.60, VC10 4.38 m (3 h smoothed). Max Hs_SS in spec files: VA10 5.36 m, VD10 4.88, VE10 4.62, VC10 4.43 | Tp 11.6 to 15.1 s; Dp 175 to 204 deg |
| 2 (notebook "Lala", window 08-11 to 08-20) | 2026-08-16 19:30 | 2.28 / 2.56 m | 12.5 s, 198 deg | VA10 3.32, VC10 3.21, VD10 2.99, VE10 2.91 m, all at 08-16 19:00 | Tp 8.5 to 9.5 s; Dp 141 to 153 deg |
| 3 (notebook "Fausto", window 07-19 to 07-27) | 2026-07-24 05:30 | 1.67 / 1.78 m | 20.0 s, 191 deg | VC10 2.43 (07-24 11:00), VA10 2.28 (07-24 07:00), VE10 1.51 (07-24 03:00), VD10 1.47 (07-21 13:00 peak) | Tp 19.7 s; Dp 159 to 173 deg |
| 4 (not named) | 2026-09-04 18:30 | 1.75 / 1.9 m | 10.5 s, 172 deg | 1.6 to 2.1 m | Tp 10.7 to 11.6 s |

- The three event names (Fausto, Lala, Lowell) and windows are defined in `processing/initial_figs.ipynb` (first cell). I did not confirm that these are storm names.
- At the 10 m sensors Hs at the time of the Fausto and Lala peaks exceeds the buoy value (2.4 vs 1.7 m; 3.2 vs 2.3 m). For Lala the sensor Tp (8.5 to 9.5 s) and Dp (141 to 153 deg) differ from the buoy (12.5 s, 198 deg), so the Lala peak at the array was probably a short-period local or different-direction signal, not the buoy swell. Not verified; possible explanations are wind (Honolulu wind peaks near 10 m/s about 08-16, see A1_overview) or a different swell train.
- Event 1 is strongly attenuated across the array: at 5 m VB5 3.2, VD5 2.8, VE7 2.5, VE4 2.2, VC5 2.3 m (spec maxima), against 4.4 to 5.4 m at 10 m. Hs at the Paros: PD1 1.43 m (09-07 22:00), PE1 1.42 m (08-16), and PB1/PB2/PC1 max 1.09 to 1.30 m.

### Gaps
- Buoy Dp for event 1 shifts to 240 deg (WSW), then data points near 300 deg on 09-10 appear in `A1_overview.png`; not examined.
- Tp from the sensors is the peak of the hourly spectrum (quantised) and can jump between swell and wind-sea peaks.

## 5. Existing figures (avoid redundancy)

### Takeaway
There are about 40 PNGs in `figs/initial/`, covering the overview stack, per-group time series, per-transect time series, band splits, Hs_SS vs IG, spectra, spectrograms, z2, and the buoy time series. The deployment overview and the IG-vs-SS scatter already exist.

### Cited Findings
Viewed (V) or inferred from file name and notebook (N):

- `A1_overview.png` (V): 7-panel stack, UTC: buoy Hs, Tp, Dp; Honolulu water level; SS Hs of all 9 ADVs coloured by transect with depth line styles; subtidal speed per ADV; Honolulu wind; swell events shaded (about 7 windows: late July, mid August, around 08-28, early and 09-07 to 09-09).
- `Hs_timeseries.png` (V): three panels: 10 m ADVs Hs, 5 m ADVs Hs, and buoy Hs with Honolulu tide. 3 m y-limit clips the event peaks.
- `bulk_transect{A..E}_2026-07-19_2026-09-16.png` (V for C): 3 panels Hs, Tp, Dm per transect with buoy overlay (grey); Dm is 150 to 185 deg at VC10/VC5 vs 175 to 210 deg at the buoy.
- `Hs_SS_vs_IG_2026-07-19_2026-09-16.png` (V): 8 panels (10 m and 5 m ADVs), Hs_IG vs Hs_SS scatter, colour = date; near-linear with a cluster of high-IG points around late July at VA10, VC10, VB5; Hs_IG up to 0.8 m.
- `Hs_SS_vs_IG_2026-07-19_2026-07-27.png` (N): same, for the Fausto window.
- `bulk_10m_*.png`, `bulk_5m_*.png` (N, six date windows each): 3-panel Hs/Tp/Dm for the four 10 m or four 5 m ADVs.
- `Hs_bands_{10m,5m,reefflat}_*.png` (N, windows 07-19 to 09-16, 08-11 to 08-20, 08-16 to 08-20, 09-07 to 09-09): total, SS, and IG Hs in three panels.
- `A2_spectrogram.png`, `A2_spectrogram_Spp_2026-07-18_2026-09-15.png` (N): pressure spectrogram per sensor, log f vs time.
- `spectrum_p_all.png`, `spectrum_p_2026-07-19_2026-07-27.png` (N): whole-record or event Welch pressure spectra of all sensors, loglog.
- `Hs_timeseries.png`, `Tp_timeseries.png`, `Dp_timeseries.png` (N for the last two): buoy and sensor Tp and Dp time series.
- `z2_hourly.png` (N): hourly z2 per sensor.
- Other folders: `figs/orientation/` (compass pitch, roll, heading, tilt per sensor), `figs/qc/initial/` (per sensor trim, clock_tide, beam, fill, rotate, ztest; `clock_drift_all.png`), `figs/qc/bulk/` and `figs/qc/ADVbulk/` (per-sensor Hs, wave dir, u, v, current dir at 512 s, plus VE10 vs VE4/VE7 direction difference), `figs/qc/paros/`. Also `VA10_Hsig.png`, `VB5_Hsig.png` in the project root.
- Notebook-only figures (not necessarily saved): B.3b mean-current maps (event, calm, difference), surface-elevation spectra for one transect and one event.

### Inferences
- Not yet made, per the README plan and the files: cross-shore Hs vs depth per transect (item 4), alongshore variability at fixed depth (item 5), IG ratio vs Tp or map (item 6), tidal ellipses (7), ADCP Hovmoller (9), forcing scatter (10), correlation vs separation (11), EOF (12), flux ratio 10 m to 5 m (13), coverage matrix.

### Gaps
- I did not open `A2_spectrogram*`, `bulk_10m/5m_*`, `Hs_bands_*`, `spectrum_p_*`, `Tp/Dp_timeseries`, `z2_hourly`, and the `figs/qc` subfolders; their descriptions come from file names and notebook code and are unverified.
- Whether the saved PNGs reflect the current notebook settings (for example SAVE flags are False in several cells) was not checked.
