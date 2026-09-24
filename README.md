# 4EWA

# Data Processing and Analysis for 4EWA (placeholder for cool project name)

## Data Collection
A two-dimensional array of bottom mounted sensors including 5 Pressure sensors, 9 Norterk ADVs, 1 Nortek Signature 1000 were deployed in the Ewa Beach region of Oahu, Hawaii from 07/28/2026 to 09/16. Please see associated .kml file for sensor locations and feel free to holla at i1rojas@ucsd.edu for data requests

![Sensor map](figs/sensor-map.png)

Lidar line scans with associated day-long RBR deployments in the nearshore were also conducted on select dates. 

### Sensor Naming Convenction


First letter signifies whether it is a vector (V) or pressure sensor (P)

Second letter signifies the transect line ,from east to west, A, B, C, D, E respectively

Third letter is the sensor type number from nearshore to offshore. 

## Data Processing

### ADVs
raw data files (.vec) were converted to .nc files using the Dolfyn package. 