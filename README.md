# pyAvMap — Aviation Moving Map

**Status:** Open Source — Experimental Amateur-Built Category  
**License:** See LICENSE  
**Language:** Python 3  
**Copyright:** 2018–2019 MakerPlane

---

## What This Is

pyAvMap is an open-source **aviation moving map library** written in Python. It renders FAA aeronautical charts (sectional, IFR low/high enroute, terminal area) with a GPS-driven aircraft position marker. It is designed to integrate with [pyEfis](../pyEfis) as the moving map panel within a full EFIS display, using flight data from [FIX-Gateway](../fix-gateway).

The map renders from pre-tiled versions of FAA-published raster charts so that real-time panning and zooming are fast even on low-powered embedded hardware like a Raspberry Pi.

## Chart Types Supported

| Type | Directory | FAA Source |
|---|---|---|
| Sectional VFR | `charts/Sectional/<ChartName>/` | FAA Digital Products - Sectional Raster Charts |
| IFR Low Enroute | `charts/IFR/<ChartName>/` | FAA Digital Products - IFR Low Enroute |
| Jet (IFR High) | `charts/Jet/<ChartName>/` | FAA Digital Products - IFR High Enroute |
| Terminal Area | `charts/Terminal/<ChartName>/` | FAA Digital Products - Terminal Area Charts |

![Sectional Example](https://raw.githubusercontent.com/Maker42/pyAvMap/master/doc/SectionalExample.jpg)
![IFR Enroute Example](https://raw.githubusercontent.com/Maker42/pyAvMap/master/doc/IFRExample.jpg)

## Installation

```bash
git clone https://github.com/makerplane/pyAvMap.git
cd pyAvMap

# Optional: install permanently (still in development)
sudo pip3 install .
```

## Chart Preparation

FAA chart files are large GeoTiff files that must be pre-tiled before use. This is a one-time step per chart:

```bash
# Download chart from FAA:
# https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/
# Unzip into the appropriate subdirectory

# For a sectional chart:
mkdir -p charts/Sectional/Albuquerque
# unzip downloaded file into charts/Sectional/Albuquerque/
cd charts/Sectional/Albuquerque
python pyAvMap/make_tiles/make_tiles.py "Albuquerque SEC 101"

# Remove the original large TIFF after tiling:
rm *.tif

# For charts where north is along the width axis (e.g., L-01, L-02 IFR):
python pyAvMap/make_tiles/make_tiles.py "L-01" 1   # the "1" rotates for correct orientation
```

Repeat for each chart you want available. Tiles are small PNG files stored in a directory hierarchy — the map library loads only those tiles visible in the current viewport.

## Dependencies

pyAvMap depends on **pyAvTools**, which must be cloned adjacent to the pyAvMap directory:

```bash
git clone https://github.com/makerplane/pyAvTools.git
```

Or set the `TOOLS_PATH` environment variable to point to the pyAvTools location.

## Integration with pyEfis

pyAvMap is loaded automatically by [pyEfis](../pyEfis) when the `MAP_PATH` environment variable is set or when the `pyAvMap` directory is adjacent to `pyEfis`. Map display is configured in the pyEfis screen YAML definitions.

## Data Flow

```
[FIX-Gateway] ──→ LAT, LONG, HEAD, GS, ALT ──→ [pyAvMap] ──→ [rendered chart tile + ownship symbol]
[faa-cifp-data] ──→ waypoint/procedure overlays ──→ [pyAvMap]
```

## Important Disclaimer

> pyAvMap is developed for Experimental Amateur-Built aircraft use only.  
> FAA chart data is published for planning purposes. Moving map display is **not** a substitute for current official charts or a certified navigation system.  
> Builders are responsible for all integration and safety decisions.
