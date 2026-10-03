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
- **Correlation mask**: u, v, w are set to NaN wherever any beam correlation is < 70 % (`vel_corr_ok`). Pressure is not masked.
- **SNR flag**: any beam < 5 dB above the in-air noise floor sets `vel_low_snr`. This flag is diagnostic only and is not applied. Small SNR could be due to low flow conditions or small wave days. 
- **Short-gap fill**: NaN runs of ≤ 2 s (4 samples) are filled with a cubic fit (dolfyn `clean_fill`) and marked in `vel_filled`. Longer gaps stay NaN.
- **Hourly segment flag**: `seg_ok` = the 1-h segment has ≤ 10 % NaN velocity.
- **Rotation**: KVH magnetic heading + 9.26° E declination, head up (roll 180°). The result is true ENU (`u_east`, `v_north`) and then shore-normal per transect (`u` onshore, `v` alongshore, `w` up).
- **Z-test**: pressure vs. velocity-predicted pressure spectrum (linear theory) per 1024-s segment. If the record median falls outside 0.5–2, the record is flagged (`zt_status`). This is a flag only and removes no data.

#### Quality Control (ADCP, `processing/adcp_QC.ipynb`)
The same steps adapted for the Signature 1000 (4 Hz, 23 cells), plus a side-lobe surface mask and a seconds-level clock check against the co-located VC10. The final product is `data/processed/qc/ADCP_qc.nc`.

## Figures
- `figs/orientation/`: internal compass pitch, roll, heading and tilt of every sensor, to sanity check the Vector probes.
- `figs/qc/`: one set per sensor: `{SENSOR}_trim`, `_clock_tide`, `_beam`, `_fill`, `_rotate`, `_ztest`. `clock_drift_all.png` covers every sensor.

**planned figs**:
- Deployment overview stack:
  - buoy Hs, Tp, and Dp
  - the tide
  - swell band Hs at every sensor, colored by transect, with a line style for each depth 
  - subtidal current speed 
  - wind, if available...

- 



# Running to do list

- ~~convert .vec files to .nc~~
- ~~inspect kvh files, gopro vids, and field notebook for accurate headings~~
- ~~rotate to earth frame~~
- Paros pressure sensor QC
- save final QC'd product to `data/processed/qc/`

