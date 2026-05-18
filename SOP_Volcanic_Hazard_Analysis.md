# Technical Standard Operating Procedure (SOP)
## Volcanic Eruption Dynamics & Pyroclastic Hazard Analysis in ParaView

**Document Number:** SOP-GEO-VOL-001  
**Version:** 1.0  
**Effective Date:** December 2025  
**Author:** Randy Gharfa, Computational Geophysicist  
**Classification:** Volcanic Hazard Assessment Protocol

---

## 1. Purpose and Scope

This SOP establishes standardized workflows for visualizing and analyzing **volcanic eruption dynamics** using ParaView. The procedures enable:

- **Eruption column visualization** using isosurfaces and volume rendering
- **Tephra trajectory tracking** with temporal pathlines
- **Pyroclastic density current (PDC)** flow mapping
- **Hazard zone delineation** for emergency management
- **Volcanic gas dispersion** modeling

### 1.1 Applicable Standards

- USGS Volcano Hazards Program Guidelines
- IAVCEI (International Association of Volcanology) Protocols
- UNESCO Global Geoparks Network Standards

---

## 2. Input Data Requirements

### 2.1 Time Series Datasets

| File | Description | Timesteps |
|------|-------------|-----------|
| `volcanic_eruption.pvd` | Eruption column + PDC | 16 |
| `tephra_trajectories.pvd` | Volcanic projectiles | 16 |
| `volcano_topography.vtk` | Digital elevation model | Static |

### 2.2 Eruption Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Volcano Height | 2800 m | Stratovolcano |
| Crater Radius | 400 m | Summit crater |
| Magma Temperature | 1150°C | Basaltic-andesitic |
| Eruption Velocity | 350 m/s | Vent exit velocity |
| Mass Flux | 10⁷ kg/s | VEI 4-5 |
| Column Height | 15 km | Target plinian column |

### 2.3 Domain Specifications

- **Horizontal extent:** 7.2 × 7.2 km
- **Vertical extent:** 6.4 km
- **Grid resolution:** 60 × 60 × 80 = 288,000 points
- **Time duration:** 480 seconds (8 minutes)

---

## 3. Procedure 1: Loading Time Series Data

### 3.1 Open Eruption PVD

```
File > Open > volcanic_eruption.pvd
```

### 3.2 Verify Timesteps

- Animation toolbar: **16 timesteps**
- Time range: **0 - 480 seconds**
- Phases: Pre-eruption → Explosive onset → Sustained → Waning

### 3.3 Load Supporting Data

```
File > Open > tephra_trajectories.pvd
File > Open > volcano_topography.vtk
```

---

## 4. Procedure 2: Eruption Column Visualization

### 4.1 Objective
Visualize the volcanic plume structure using isosurfaces of ash concentration and temperature.

### 4.2 Ash Concentration Isosurfaces

1. **Select eruption data**

2. **Apply Contour filter:**
   ```
   Filters > Contour
   ```

3. **Configure for outer plume:**
   - Contour By: `ash_concentration`
   - Isosurface Value: **0.01**
   - Color: Light gray (opacity 0.3)

4. **Add core plume:**
   - Apply second Contour
   - Value: **0.1**
   - Color: Dark gray (opacity 0.7)

### 4.3 Temperature Isosurfaces

```
Filters > Contour
Contour By: temperature
Values: 100, 300, 600 (°C)
```

| Temperature | Color | Significance |
|-------------|-------|--------------|
| 100°C | Yellow | Thermal injury threshold |
| 300°C | Orange | Severe burn hazard |
| 600°C | Red | Lethal thermal zone |

### 4.4 Volume Rendering (Alternative)

```
Representation: Volume
Color By: ash_concentration
Transfer Function: Customize for plume visibility
```

---

## 5. Procedure 3: Tephra Trajectory Pathlines

### 5.1 Objective
Track volcanic projectiles (bombs, lapilli, ash) from vent to landing.

### 5.2 Apply Temporal Pathlines

1. **Select tephra particle source**

2. **Apply filter:**
   ```
   Filters > Temporal > Temporal Particles To Pathlines
   ```

3. **Configure:**
   - Mask Points: **1**
   - Max Track Length: **5000** m
   - ID Channel Array: `ParticleID`

### 5.3 Visualization Options

| Color By | Reveals |
|----------|---------|
| `Diameter` | Size sorting (large bombs fall nearby) |
| `Temperature` | Cooling during flight |
| `SizeClass` | Bomb / Lapilli / Ash classification |
| `Velocity` magnitude | Ejection energy |

### 5.4 Tube Filter for Visibility

```
Filters > Tube
Radius: 20 m (scaled for domain)
```

### 5.5 Interpretation

| Observation | Implication |
|-------------|-------------|
| Steep trajectories | Low-velocity clasts |
| Parabolic arcs | Ballistic bombs |
| Wind-bent paths | Ash advection |

---

## 6. Procedure 4: Pyroclastic Flow (PDC) Analysis

### 6.1 Objective
Map pyroclastic density current extent and intensity.

### 6.2 PDC Zone Extraction

```
Filters > Threshold
Scalars: PDC_density
Lower: 1.0 kg/m³
Upper: 100 kg/m³
```

### 6.3 Flow Vector Visualization

```
Filters > Glyph
Glyph Type: Arrow
Orientation: Velocity
Scale: PDC_density
Scale Factor: 50
```

### 6.4 PDC Hazard Classification

| Density (kg/m³) | Hazard Level |
|-----------------|--------------|
| 1 - 10 | Dilute surge (high mobility) |
| 10 - 50 | Dense flow (destructive) |
| > 50 | Hyper-concentrated (devastating) |

### 6.5 Animation

- Play through timesteps to observe PDC runout
- Note channelization in valleys
- Measure maximum extent

---

## 7. Procedure 5: Hazard Zone Mapping

### 7.1 Hazard Index Thresholds

```
# High Hazard (evacuation required)
Filters > Threshold
Scalars: hazard_index
Range: 0.7 - 1.0
Color: Red

# Moderate Hazard (shelter-in-place)
Range: 0.3 - 0.7
Color: Orange

# Low Hazard (awareness zone)
Range: 0.1 - 0.3
Color: Yellow
```

### 7.2 Hazard Components

The hazard_index integrates:
- **Ash fall** (30% weight): Respiratory, structural
- **PDC exposure** (50% weight): Lethal
- **Thermal** (20% weight): Burns, fires

### 7.3 Export Hazard Map

1. Create horizontal slice at ground level
2. Color by hazard_index
3. Overlay on topography
4. Export as image for emergency services

---

## 8. Procedure 6: Volcanic Gas Dispersion

### 8.1 SO2 Plume Visualization

```
Filters > Threshold
Scalars: SO2_concentration
Lower: 10 ppm
Upper: 10000 ppm
```

### 8.2 SO2 Concentration Levels

| Concentration | Health Effect |
|---------------|---------------|
| 10 ppm | Odor threshold |
| 50 ppm | Eye/throat irritation |
| 100 ppm | Dangerous |
| 500 ppm | Life-threatening |

### 8.3 Plume Tracking

- Animate through timesteps
- Note wind-driven advection
- Identify affected communities downwind

---

## 9. Procedure 7: Cross-Sectional Analysis

### 9.1 Vertical Slice Through Column

```
Filters > Slice
Slice Type: Plane
Origin: (0, 0, 3000)
Normal: (0, 1, 0)  # N-S cross-section
```

### 9.2 Examine:
- Column height evolution
- Entrainment (widening with height)
- Temperature decay
- Particle concentration gradient

### 9.3 Radial Slice (Umbrella Region)

```
Origin: (0, 0, 12000)
Normal: (0, 0, 1)  # Horizontal
```

Shows ash spreading at neutral buoyancy level.

---

## 10. Emergency Management Integration

### 10.1 Real-Time Monitoring Workflow

1. Load latest simulation output
2. Generate hazard zone maps
3. Export for GIS integration
4. Distribute to emergency responders

### 10.2 Evacuation Zone Determination

| Zone | Criteria | Action |
|------|----------|--------|
| Red | hazard_index > 0.7 | Immediate evacuation |
| Orange | 0.3 - 0.7 | Prepare to evacuate |
| Yellow | 0.1 - 0.3 | Stay alert |

### 10.3 Report Generation

Required outputs:
- [ ] Eruption column height estimate
- [ ] PDC maximum runout distance
- [ ] Ash fall distribution map
- [ ] SO2 dispersion forecast
- [ ] Hazard zone boundaries

---

## 11. Quality Assurance

### 11.1 Verification Checklist

- [ ] All 16 timesteps load correctly
- [ ] Topography aligns with eruption data
- [ ] Tephra particles originate from crater
- [ ] PDC flows follow topographic lows
- [ ] Hazard zones are physically reasonable

### 11.2 Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Column invisible | Wrong threshold | Adjust isosurface values |
| Pathlines scattered | Wrong ID array | Use ParticleID |
| PDC floating | Topography mismatch | Check coordinate systems |

---

## 12. References

1. Sparks, R.S.J., et al. (1997). Volcanic Plumes. Wiley.
2. Druitt, T.H. (1998). Pyroclastic density currents. Geol. Soc. London.
3. USGS Volcano Hazards Program: https://volcanoes.usgs.gov/

---

**Document Control:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | R. Gharfa | Initial release |

---

*© 2025 Randy Gharfa. Licensed under MIT License.*
