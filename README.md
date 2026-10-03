# 4EWA

# Data Processing and Analysis for 4EWA (placeholder for cool project name)

## Data Collection
A two-dimensional array of bottom mounted sensors including 5 Pressure sensors, 9 Norterk ADVs, 1 Nortek Signature 1000 were deployed in the Ewa Beach region of Oahu, Hawaii from 07/28/2026 to 09/16. Please see associated .kml file for sensor locations and feel free to holla at i1rojas@ucsd.edu for data requests

![Sensor map](ewa_sensor_map.jpg)

Lidar line scans with associated day-long RBR deployments in the nearshore were also conducted on select dates. 

### Sensor Naming Convention

- **First letter**: sensor type. V = Nortek Vector (ADV), P = Paroscientific pressure sensor. The Signature 1000 is `ADCP`.
- **Second letter**: transect line, A–E from **west to east**.
- **Number**:
  - Vectors: approximate deployment depth in meters (e.g. `VA10` = Vector, transect A, ~10 m).
  - Pressure sensors: order along the transect from nearshore (e.g. `PB1`, `PB2`).

Vector IDs were changed on 2026-10-03. The old IDs numbered sensors nearshore → offshore:

| ID | old ID | S/N | depth (m) |
|---|---|---|---|
| VA10 | VA1 | 8190 | 10 |
| VB5 | VB1 | 9649 | 5.5 |
| VC5 | VC1 | 12411 | 5 |
| VC10 | VC2 | 15241 | 10 (co-located with ADCP) |
| VD5 | VD1 | 12596 | 5 |
| VD10 | VD2 | 8195 | 10 |
| VE4 | VE1 | 15254 | 4 |
| VE7 | VE2 | 15056 | 7 |
| VE10 | VE3 | 15048 | 10 |

## Data Processing

### Data files
- `data/processed/{SENSOR}_raw.nc`: all `.vec` files for one Vector merged, with deployment metadata from `sensor_notes.csv` attached. Instrument frame, no QC. Produced by `processing/adv_raw2nc.ipynb`.
- `data/processed/qc/{SENSOR}_QC.nc`: final QC'd product, written at the end of `processing/adv_QC.ipynb`. Every QC choice is recorded in the global attributes (`qc_*`, `rot_*`, `zt_*`).
- Executed QC notebook for each sensor: `processing/qc_runs/adv_QC_{SENSOR}.ipynb`.

### ADVs

#### File Type Conversion
raw data files (.vec) were converted to .nc files using the Dolfyn package. Each ADV contains four .VEC files. The workflow for processing the ADV data is as follows:
1. Combine the four .vec files into a single .nc file using the `dolfyn` package and manifest.csv.
2. Add metadata (sensor_notes.csv)
3. Save as `{SENSOR}_raw.nc`.

**NOTE** had to truncate the fourth .vec file for each ADV. The last chunk of data was corrupted because it was hard stopped once it was connected to nortek software.

#### Quality Control (`processing/adv_QC.ipynb`)
QC steps, in the order they are applied:
- **Seam fillers dropped**: placeholder records at `.vec` file boundaries (p = 0, all beam correlations = 0) are removed.
- **Clock drift**: linear correction from 0 at the first raw sample to the measured drift (`sensor_notes.csv`) at the last. VE4 has an override, documented in `DRIFT_OVERRIDE`.
- **In-water trim**: keep the longest run with p ≥ 3 dbar. Shrink it to where the 1-min heading std is calm, which cuts diver handling. Then remove a 10 s buffer from each end.
- **Atmospheric pressure**: subtract the NOAA 1612340 (Honolulu) hourly barometer, using the pre-deployment in-air offset. The raw channel is kept as `p_raw`.
- **Sound speed**: velocities are rescaled from the configured salinity (33.5) to 35 PSU (~0.1 %).
- **Correlation gate** (Elgar et al., 2005): a velocity sample is bad if any beam correlation is below 0.3 + 0.4·√(fs/25). That is **41.3 % at 2 Hz**, SonTek's 0.7 at 25 Hz relaxed for the extra pings averaged into each slower sample (`vel_corr_ok`). Pressure is not masked.
- **Replacement of bad samples** (Elgar et al., 2005):
  - Runs of bad samples ≤ 1 s are linearly interpolated between the good samples on either side.
  - Longer runs are replaced by a 1-s running mean of the recorded values.
  - `vel_qc_flag` marks each sample: 0 = measured, 1 = linear interpolation, 2 = 1-s running mean. No velocity NaNs remain.
- **SNR flag** (Elgar et al., 2005): SNR = 0.43 dB/count × (amp − in-air noise floor). `vel_low_snr` marks samples with any beam < 8 dB.
  - Elgar's run rule (≤ 0.81 % low-SNR samples) is stored per hour as `seg_snr_ok`, as a flag only.
  - The sensors are always submerged. Low SNR here means clear water, and those samples are only ~1.5× noisier.
- **Hourly segment flag**: `seg_ok` = the 1-h segment has ≤ 10 % running-mean velocity (`seg_runmean_ok`) **and** passes the z² test below (`z2_ok`). `seg_interp_pct` and `seg_runmean_pct` give the hourly fractions.

  Elgar, S., Raubenheimer, B., & Guza, R. T. (2005). Quality control of acoustic Doppler velocimeter data in the surfzone. *Measurement Science and Technology*, 16, 1889–1893. doi:10.1088/0957-0233/16/10/002 (`lit/`)
- **Rotation**: KVH magnetic heading + 9.26° E declination, head up (roll 180°). The result is true ENU (`u_east`, `v_north`) and then shore-normal per transect (`u` onshore, `v` alongshore, `w` up).
- **z² test** (Elgar et al., 2005, §3.3): compares measured pressure variance with the pressure variance linear theory predicts from horizontal velocity, z² = p² / [(ω/gk)² · cosh²(k d_p)/cosh²(k d_u) · (u² + v²)].
  - Integrated over the wind-wave band, 0.05 < f < 0.20 Hz, for each clock hour (`z2`).
  - d_p and d_u are the heights of the pressure port and the sample volume above the bed.
  - An hour is rejected (`z2_ok` and `seg_ok` False) unless 0.5 < z² < 2.0. No samples are removed.
  - Hours with less than 99 % of their samples, or an internal gap over 2 s (e.g. partial first and last hours), get no z² and fail.
  - `zt_status` summarizes the record median.

#### Quality Control (ADCP, `processing/adcp_QC.ipynb`)
The same steps adapted for the Signature 1000 (4 Hz, 23 cells), plus a side-lobe surface mask and a seconds-level clock check against the co-located VC10. The final product is `data/processed/qc/ADCP_qc.nc`.

## Figures
- `figs/orientation/`: internal compass pitch, roll, heading and tilt of every sensor, to sanity check the Vector probes.
- `figs/qc/`: one set per sensor: `{SENSOR}_trim`, `_clock_tide`, `_beam`, `_fill`, `_rotate`, `_ztest`. `clock_drift_all.png` covers every sensor.

## Future Figures
Planned exploratory figures from the hourly bulk statistics. Each one is paired with the question it is meant to open. Request them by number once the inputs are verified.

**Prerequisites**
- VE7 and VE10 QC.
- An hourly bulk-stats product on a common UTC grid (`data/processed/bulk/{SENSOR}_bulk.nc`).
- Head-motion windows, which mask direction-dependent fields only: wave direction, the u/v split, Sxy and quivers.
- Swell events are defined from the nearest CDIP/NDBC directional buoy: Hs > P90, Tp > ~12 s, S–SW. Normalization uses the in-array 10 m reference (ADCP/VC10).
- Spatial maps are in ENU. Transect plots are in each transect's own shore-normal frame.

### A. Overview and events
1. **Deployment overview stack.** The panels are:
   - Buoy Hs, Tp and Dp.
   - The tide.
   - Swell-band Hs at every sensor, colored by transect, with a line style for each depth.
   - Subtidal current speed.
   - Wind, if available.

   Swell events are shaded. *Which events are worth a case study?*
2. **Pressure spectrogram per sensor** (log f × time), with events marked. Look for dispersive swell arrivals (frequency rising over days), which give the source distance and time. *Do arrivals differ across the array, which would mean refraction or sheltering?*

### B. Spatial structure of waves
3. **Map panels** (lat/lon from `sensor_notes.csv`):
   - Hs_swell / Hs_ref as dots.
   - Mean ENU current vectors.
   - Shown as an event composite, a calm composite, and their difference.

   *Is the alongshore Hs gradient bigger during south swell, from reef or bathymetric focusing?*
4. **Cross-shore transformation.** Hs against h along each transect (B, C, D, E; A has only 10 m). Show the event mean ± spread, with the linear shoaling prediction from the 10 m reference overlaid. *Where does dissipation start, and does it differ between transects (reef roughness)?*
5. **Alongshore variability at fixed depth.**
   - The ~5 m line (VB5, VC5, VD5, VE4) and the 10 m line (VA10, VC10, VD10, VE10).
   - Hs and direction against alongshore position, plotted against buoy direction.

   *Does a change in incident direction switch which part of Ewa gets the energy?*
6. **Infragravity.** Hs_IG / Hs_swell against Hs_swell and against Tp, plus a map of the IG fraction during events. *Bound vs free IG? Is IG enhanced shoreward on the reef transects?*

### C. Currents in time
7. **Tidal ellipse map.** M2 and K1 per sensor, and per depth bin for the ADCP. *Is the tidal flow rectified or phase-lagged along the coast?*
8. **Subtidal current stack.** Alongshore and cross-shore at each sensor, with events shaded and the wind and buoy Hs alongside. *Do events drive alongshore flow, or does the trade-driven background dominate?*
9. **ADCP Hovmöller.** Hourly u and v (time × height), plus mean profiles for events vs calm. *Does undertow appear at 10 m? Is the profile sheared during swell?*

### D. Forcing–response and spatial scales
10. **Forcing scatter plots**, colored by event or calm:
    - Alongshore subtidal v against Sxy (or Hs²·sin2θ).
    - Cross-shore u against Hs²/h (undertow scaling).

    *Is the wave-driven fraction measurable at 5 and 10 m?*
11. **Inter-sensor correlation against separation** for subtidal v and Hs_swell. Split the pairs into alongshore and cross-shore, and fit e-folding length scales for events vs calm. *Does swell shorten or lengthen the current coherence scale?*
12. **EOF of the subtidal ENU currents** across all sensors: mode maps, and PC time series against forcing. *Is there a coherent array-wide mode, such as a recirculation cell?*
13. **Cross-spectra or lag correlation** of the swell-band energy flux between the 10 m and 5 m sensors on each transect. *How much of the flux reaches 5 m, and how does that differ by transect?*

**Phase 2 (after Paros QC):** extend 4, 6 and 13 to the Paros depths. This adds the shallow end of each transect and IG near shore.

# Running to do list

- ~~convert .vec files to .nc~~
- ~~inspect kvh files, gopro vids, and field notebook for accurate headings~~
- ~~rotate to earth frame~~
- Paros pressure sensor QC
- save final QC'd product to `data/processed/qc/`

