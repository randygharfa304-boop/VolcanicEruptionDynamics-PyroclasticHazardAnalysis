# Volcanic Eruption Dynamics & Pyroclastic Hazard Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ParaView](https://img.shields.io/badge/ParaView-5.10+-green.svg)](https://www.paraview.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)

**Author:** Randy Gharfa, Computational Geophysicist  
**Application:** Volcanic Hazard Visualization & Emergency Management  
**Last Updated:** December 2025

---

## Overview

This portfolio provides a comprehensive workflow for visualizing and analyzing **volcanic eruption dynamics** using ParaView. The time-series simulation models a VEI 4-5 stratovolcano eruption, capturing plume development, pyroclastic density currents, tephra ballistics, and volcanic gas dispersion across an 8-minute eruption sequence.

### Key Features

- 🌋 **16-Timestep Eruption Simulation** (8-minute VEI 4-5 event)
- 🔥 **Eruption Column Isosurfaces** for plume visualization
- 🎯 **Tephra Trajectory Pathlines** tracking volcanic projectiles
- 🌊 **Pyroclastic Flow Mapping** with velocity vectors
- ⚠️ **Hazard Zone Delineation** for emergency management
- 💨 **SO2 Gas Dispersion** modeling
- 🗻 **3D Volcano Topography** with digital elevation model
- 🐍 **Automated Python Analysis** scripts

---

## Repository Structure

```
portfolio-randy-gharfa-volcanic-dynamics/
│
├── eruption-simulation/
│   ├── generate_eruption.py           # Simulation generator
│   ├── volcanic_eruption.pvd          # Eruption time series
│   ├── tephra_trajectories.pvd        # Particle time series
│   ├── volcano_topography.vtk         # DEM surface mesh
│   ├── eruption_XXXX.vtk              # 16 eruption timesteps
│   └── tephra_XXXX.vtk                # 16 particle timesteps
│
├── scripts/
│   └── volcanic_hazard_analysis.py    # Automated analysis
│
├── documentation/
│   └── SOP_Volcanic_Hazard_Analysis.md
│
├── README.md
└── LICENSE
```

---

## Quick Start

### 1. Load Eruption Simulation

```bash
paraview eruption-simulation/volcanic_eruption.pvd
```

### 2. Visualize Eruption Column

```
Filters > Contour
- Contour By: ash_concentration
- Values: 0.01, 0.1
```

### 3. Track Tephra Trajectories

```
File > Open > tephra_trajectories.pvd
Filters > Temporal > Temporal Particles To Pathlines
```

### 4. Map Pyroclastic Flows

```
Filters > Threshold
- Scalars: PDC_density
- Range: 1.0 - 100.0
```

### 5. Run Automated Analysis

```bash
pvpython scripts/volcanic_hazard_analysis.py
```

---

## Eruption Simulation Parameters

### Volcano Characteristics

| Parameter | Value |
|-----------|-------|
| Volcano Type | Stratovolcano |
| Summit Elevation | 2,800 m |
| Crater Radius | 400 m |
| Crater Depth | 200 m |
| Conduit Radius | 50 m |

### Magma Properties

| Property | Value |
|----------|-------|
| Temperature | 1,150°C |
| Composition | Basaltic-andesitic |
| Viscosity | 10⁴ Pa·s |
| Gas Content | 4% (H₂O, CO₂, SO₂) |

### Eruption Dynamics

| Parameter | Value |
|-----------|-------|
| Exit Velocity | 350 m/s |
| Mass Flux | 10⁷ kg/s |
| Column Height | 15 km (target) |
| VEI | 4-5 |
| Duration | 480 s (8 min) |

---

## Scalar Fields

| Array Name | Description | Units |
|------------|-------------|-------|
| `terrain_type` | 0=Atm, 1=Rock, 2=Magma, 3=Conduit, 4=Crater | - |
| `temperature` | Temperature field | °C |
| `ash_concentration` | Volcanic ash density | kg/m³ |
| `SO2_concentration` | Sulfur dioxide | ppm |
| `PDC_density` | Pyroclastic flow density | kg/m³ |
| `hazard_index` | Integrated hazard (0-1) | - |
| `eruption_intensity` | Relative intensity (0-1) | - |
| `Velocity` | Flow velocity vector | m/s |

---

## Eruption Timeline

```
t = 0 s      ─── PRE-ERUPTION
    │            Inflation, minor degassing
    │
t = 48 s     ─── EXPLOSIVE ONSET
    │            Initial blast, column development
    │
t = 144 s    ─── SUSTAINED ERUPTION
    │            Peak intensity, full column
    │            Pyroclastic flows initiated
    │
t = 336 s    ─── WANING PHASE
    │            Decreasing intensity
    │            PDC runout continuing
    │
t = 480 s    ─── POST-ERUPTION
                 Residual emissions
```

---

## ParaView Workflow Summary

### Workflow 1: Eruption Column (Isosurfaces)

**Purpose:** Visualize plume structure

```
Filters > Contour
- ash_concentration: 0.01 (outer), 0.1 (core)
- temperature: 100, 300, 600°C
```

### Workflow 2: Tephra Trajectories (Pathlines)

**Purpose:** Track volcanic projectiles

```
Filters > Temporal Particles To Pathlines
- ID Channel: ParticleID
- Color by: Diameter, Temperature
```

### Workflow 3: Pyroclastic Flow (Threshold + Glyph)

**Purpose:** Map deadly ground-hugging flows

```
Threshold: PDC_density > 1.0
Glyph: Arrows oriented by Velocity
```

### Workflow 4: Hazard Zones (Threshold)

**Purpose:** Emergency planning zones

| Zone | Hazard Index | Action |
|------|--------------|--------|
| RED | > 0.7 | Evacuate |
| ORANGE | 0.3 - 0.7 | Prepare |
| YELLOW | 0.1 - 0.3 | Alert |

---

## Volcanic Hazards Modeled

### 1. Eruption Column
- Convective plume dynamics
- Ash concentration distribution
- Temperature structure

### 2. Pyroclastic Density Currents
- Column collapse mechanism
- Radial flow propagation
- Valley channelization

### 3. Tephra Fall
- Ballistic bombs (>64mm)
- Lapilli (2-64mm)
- Ash (<2mm)
- Wind advection

### 4. Volcanic Gases
- SO₂ dispersion
- Air quality impacts
- Downwind transport

---

## Applications

This workflow applies to:

- **Emergency Management:** Evacuation planning
- **Volcanology Research:** Eruption dynamics studies
- **Aviation Safety:** Ash cloud tracking
- **Environmental Science:** Gas dispersion modeling
- **Civil Protection:** Hazard zone mapping

---

## Visualization Gallery

### Recommended Views

1. **Oblique 3D:** Eruption column with topography
2. **N-S Cross-section:** Column structure
3. **Plan View:** PDC runout extent
4. **Animation:** Full eruption sequence

### Color Maps

| Field | Recommended Colormap |
|-------|---------------------|
| temperature | Inferno (sequential) |
| ash_concentration | Grays (sequential) |
| hazard_index | RdYlGn_r (diverging) |
| PDC_density | Hot (sequential) |
| SO2_concentration | Plasma (sequential) |

---

## Requirements

- ParaView 5.10+
- Python 3.8+

---

## References

1. Sparks, R.S.J., et al. (1997). Volcanic Plumes. Wiley.
2. Druitt, T.H. (1998). Pyroclastic density currents. Geological Society London.
3. Morton, B.R., Taylor, G.I., Turner, J.S. (1956). Turbulent gravitational convection.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Contact

**Randy Gharfa**  
Computational Geophysicist  
Volcanic Hazard Modeling & Visualization

---

*Part of the Geophysical Hazard Visualization Portfolio*
