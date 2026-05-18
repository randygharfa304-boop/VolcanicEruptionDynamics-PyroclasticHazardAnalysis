"""
Volcanic Eruption Hazard Analysis Script
ParaView Python Automation for Eruption Dynamics & PDC Investigation

Author: Randy Gharfa, Computational Geophysicist
Purpose: Multi-phase volcanic flow analysis, tephra tracking, hazard mapping

Usage:
  pvpython volcanic_hazard_analysis.py
  OR in ParaView: Tools > Python Shell > Run Script
"""

try:
    from paraview.simple import *
except ImportError:
    print("ParaView not available - running standalone analysis")

import math
import os

# ============================================================================
# ERUPTION PARAMETERS
# ============================================================================

ERUPTION_PARAMS = {
    'volcano_height': 2800,      # m
    'crater_radius': 400,        # m
    'magma_temp': 1150,          # °C
    'eruption_velocity': 350,    # m/s
    'column_height': 15000,      # m (target)
    'vei': 4.5                   # Volcanic Explosivity Index
}

HAZARD_THRESHOLDS = {
    'ash_lethal': 0.1,           # kg/m³ - respiratory hazard
    'pdc_lethal': 1.0,           # kg/m³ - pyroclastic density current
    'thermal_burn': 100,         # °C - thermal injury threshold
    'so2_danger': 100,           # ppm - toxic gas threshold
}


def run_volcanic_analysis_paraview():
    """
    Complete volcanic eruption analysis in ParaView.
    Implements workflows for:
    1. Eruption column visualization with isosurfaces
    2. Tephra trajectory tracking with pathlines
    3. Pyroclastic flow mapping
    4. Hazard zone delineation
    """
    
    print("="*70)
    print("VOLCANIC ERUPTION DYNAMICS & HAZARD ANALYSIS")
    print("ParaView Multi-Phase Flow Visualization")
    print("="*70)
    
    # =========================================================================
    # LOAD DATA
    # =========================================================================
    print("\n--- Loading Eruption Simulation Data ---")
    
    eruption_pvd = "volcanic_eruption.pvd"
    if not os.path.exists(eruption_pvd):
        eruption_pvd = "../eruption-simulation/volcanic_eruption.pvd"
    
    if not os.path.exists(eruption_pvd):
        print(f"ERROR: Cannot find {eruption_pvd}")
        return
    
    eruption = PVDReader(FileName=eruption_pvd)
    RenameSource("Eruption_Column", eruption)
    
    time_steps = eruption.TimestepValues
    print(f"  Loaded eruption data: {len(time_steps)} timesteps")
    print(f"  Time range: {time_steps[0]:.0f} to {time_steps[-1]:.0f} s")
    
    # Load tephra particles
    tephra_pvd = "tephra_trajectories.pvd"
    if not os.path.exists(tephra_pvd):
        tephra_pvd = "../eruption-simulation/tephra_trajectories.pvd"
    
    tephra = PVDReader(FileName=tephra_pvd)
    RenameSource("Tephra_Particles", tephra)
    print("  Loaded tephra particle data")
    
    # Load topography
    topo_vtk = "volcano_topography.vtk"
    if not os.path.exists(topo_vtk):
        topo_vtk = "../eruption-simulation/volcano_topography.vtk"
    
    if os.path.exists(topo_vtk):
        topography = LegacyVTKReader(FileNames=[topo_vtk])
        RenameSource("Volcano_DEM", topography)
        print("  Loaded volcano topography")
    
    time_keeper = GetTimeKeeper()
    
    # =========================================================================
    # WORKFLOW 1: ERUPTION COLUMN ISOSURFACES
    # =========================================================================
    print("\n--- Workflow 1: Eruption Column Visualization ---")
    
    # Go to peak eruption
    peak_time = time_steps[len(time_steps)//2]
    time_keeper.Time = peak_time
    UpdatePipeline(proxy=eruption)
    
    # Ash concentration isosurfaces
    iso_ash_low = Contour(Input=eruption)
    iso_ash_low.ContourBy = ['POINTS', 'ash_concentration']
    iso_ash_low.Isosurfaces = [0.01]  # Light ash
    RenameSource("Ash_Plume_Outer", iso_ash_low)
    UpdatePipeline(proxy=iso_ash_low)
    
    iso_ash_high = Contour(Input=eruption)
    iso_ash_high.ContourBy = ['POINTS', 'ash_concentration']
    iso_ash_high.Isosurfaces = [0.1]  # Dense ash
    RenameSource("Ash_Plume_Core", iso_ash_high)
    UpdatePipeline(proxy=iso_ash_high)
    
    print("  Created ash concentration isosurfaces (0.01, 0.1)")
    
    # Temperature isosurfaces
    iso_temp = Contour(Input=eruption)
    iso_temp.ContourBy = ['POINTS', 'temperature']
    iso_temp.Isosurfaces = [100, 300, 600]  # °C
    RenameSource("Thermal_Zones", iso_temp)
    UpdatePipeline(proxy=iso_temp)
    
    print("  Created temperature isosurfaces (100, 300, 600°C)")
    
    # =========================================================================
    # WORKFLOW 2: TEPHRA TRAJECTORY PATHLINES
    # =========================================================================
    print("\n--- Workflow 2: Tephra Ballistic Tracking ---")
    
    # Apply pathlines to tephra
    pathlines = TemporalParticlesToPathlines(Input=tephra)
    pathlines.MaskPoints = 1
    pathlines.MaxTrackLength = 5000
    pathlines.IdChannelArray = 'ParticleID'
    RenameSource("Tephra_Trajectories", pathlines)
    UpdatePipeline(proxy=pathlines)
    
    print("  Created tephra trajectory pathlines")
    print("  Color by 'Diameter' for size distribution")
    print("  Color by 'Temperature' for cooling history")
    
    pathline_data = servermanager.Fetch(pathlines)
    n_paths = pathline_data.GetNumberOfCells() if pathline_data else 0
    print(f"  Total trajectories: {n_paths}")
    
    # =========================================================================
    # WORKFLOW 3: PYROCLASTIC DENSITY CURRENT ANALYSIS
    # =========================================================================
    print("\n--- Workflow 3: Pyroclastic Flow (PDC) Mapping ---")
    
    # Threshold for PDC regions
    pdc_zone = Threshold(Input=eruption)
    pdc_zone.Scalars = ['POINTS', 'PDC_density']
    pdc_zone.LowerThreshold = 1.0
    pdc_zone.UpperThreshold = 100.0
    pdc_zone.ThresholdMethod = 'Between'
    
    RenameSource("PDC_Zone", pdc_zone)
    UpdatePipeline(proxy=pdc_zone)
    
    pdc_data = servermanager.Fetch(pdc_zone)
    n_pdc = pdc_data.GetNumberOfPoints() if pdc_data else 0
    print(f"  PDC-affected cells: {n_pdc:,}")
    
    # PDC flow vectors
    if n_pdc > 0:
        pdc_glyphs = Glyph(Input=pdc_zone)
        pdc_glyphs.GlyphType = 'Arrow'
        pdc_glyphs.OrientationArray = ['POINTS', 'Velocity']
        pdc_glyphs.ScaleArray = ['POINTS', 'PDC_density']
        pdc_glyphs.ScaleFactor = 50
        RenameSource("PDC_Flow_Vectors", pdc_glyphs)
        UpdatePipeline(proxy=pdc_glyphs)
        print("  Created PDC flow vector glyphs")
    
    # =========================================================================
    # WORKFLOW 4: HAZARD ZONE DELINEATION
    # =========================================================================
    print("\n--- Workflow 4: Volcanic Hazard Mapping ---")
    
    # High hazard zones
    hazard_high = Threshold(Input=eruption)
    hazard_high.Scalars = ['POINTS', 'hazard_index']
    hazard_high.LowerThreshold = 0.7
    hazard_high.UpperThreshold = 1.0
    hazard_high.ThresholdMethod = 'Between'
    
    RenameSource("Hazard_Zone_HIGH", hazard_high)
    UpdatePipeline(proxy=hazard_high)
    
    high_data = servermanager.Fetch(hazard_high)
    n_high = high_data.GetNumberOfPoints() if high_data else 0
    
    # Moderate hazard
    hazard_moderate = Threshold(Input=eruption)
    hazard_moderate.Scalars = ['POINTS', 'hazard_index']
    hazard_moderate.LowerThreshold = 0.3
    hazard_moderate.UpperThreshold = 0.7
    hazard_moderate.ThresholdMethod = 'Between'
    
    RenameSource("Hazard_Zone_MODERATE", hazard_moderate)
    UpdatePipeline(proxy=hazard_moderate)
    
    mod_data = servermanager.Fetch(hazard_moderate)
    n_mod = mod_data.GetNumberOfPoints() if mod_data else 0
    
    print(f"  High hazard zone: {n_high:,} cells")
    print(f"  Moderate hazard zone: {n_mod:,} cells")
    
    # =========================================================================
    # WORKFLOW 5: SO2 GAS DISPERSION
    # =========================================================================
    print("\n--- Workflow 5: Volcanic Gas (SO2) Dispersion ---")
    
    so2_threshold = Threshold(Input=eruption)
    so2_threshold.Scalars = ['POINTS', 'SO2_concentration']
    so2_threshold.LowerThreshold = 10  # ppm
    so2_threshold.UpperThreshold = 10000
    so2_threshold.ThresholdMethod = 'Between'
    
    RenameSource("SO2_Plume", so2_threshold)
    UpdatePipeline(proxy=so2_threshold)
    
    so2_data = servermanager.Fetch(so2_threshold)
    n_so2 = so2_data.GetNumberOfPoints() if so2_data else 0
    print(f"  SO2 plume extent: {n_so2:,} cells (>10 ppm)")
    
    # =========================================================================
    # ERUPTION INTENSITY TIMELINE
    # =========================================================================
    print("\n--- Eruption Intensity Analysis ---")
    
    intensity_timeline = []
    max_ash_timeline = []
    
    for t_idx, t_val in enumerate(time_steps):
        time_keeper.Time = t_val
        UpdatePipeline(proxy=eruption)
        
        # Get intensity data
        data = servermanager.Fetch(eruption)
        
        # Find maximum values
        intensity_array = data.GetPointData().GetArray('eruption_intensity')
        ash_array = data.GetPointData().GetArray('ash_concentration')
        
        max_intensity = 0
        max_ash = 0
        
        if intensity_array:
            for i in range(intensity_array.GetNumberOfTuples()):
                val = intensity_array.GetValue(i)
                if val > max_intensity:
                    max_intensity = val
        
        if ash_array:
            for i in range(ash_array.GetNumberOfTuples()):
                val = ash_array.GetValue(i)
                if val > max_ash:
                    max_ash = val
        
        intensity_timeline.append((t_val, max_intensity))
        max_ash_timeline.append((t_val, max_ash))
    
    print("\n  Eruption intensity timeline:")
    for t, intensity in intensity_timeline:
        bar = "█" * int(intensity * 20)
        phase = "Pre" if t < 50 else "Onset" if t < 150 else "Sustained" if t < 350 else "Waning"
        print(f"    t={t:3.0f}s [{phase:9}]: {bar} {intensity:.2f}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("VOLCANIC HAZARD ANALYSIS SUMMARY")
    print("="*70)
    
    print(f"\nERUPTION CHARACTERISTICS:")
    print(f"  VEI Estimate: {ERUPTION_PARAMS['vei']}")
    print(f"  Duration: {time_steps[-1]:.0f} s ({time_steps[-1]/60:.1f} min)")
    print(f"  Peak intensity timestep: {intensity_timeline[len(intensity_timeline)//2][0]:.0f} s")
    
    print(f"\nHAZARD ASSESSMENT:")
    print(f"  High hazard zone: {n_high:,} cells")
    print(f"  PDC-affected area: {n_pdc:,} cells")
    print(f"  SO2 plume extent: {n_so2:,} cells")
    print(f"  Tephra trajectories: {n_paths}")
    
    print(f"\nVISUALIZATIONS CREATED:")
    print("  - Ash concentration isosurfaces (outer/core plume)")
    print("  - Temperature isosurfaces (thermal hazard)")
    print("  - Tephra trajectory pathlines")
    print("  - PDC flow vectors")
    print("  - Hazard zone classifications")
    print("  - SO2 gas dispersion plume")
    
    print("\nRECOMMENDATIONS:")
    print("  1. Evacuate high hazard zones before eruption")
    print("  2. Monitor PDC runout for valley communities")
    print("  3. Issue ash fall warnings downwind")
    print("  4. Track SO2 dispersion for air quality alerts")


def standalone_analysis():
    """Standalone analysis without ParaView."""
    print("="*70)
    print("STANDALONE VOLCANIC ANALYSIS")
    print("="*70)
    
    vtk_dir = "."
    if not os.path.exists("eruption_0000.vtk"):
        vtk_dir = "../eruption-simulation"
    
    if not os.path.exists(os.path.join(vtk_dir, "eruption_0000.vtk")):
        print("VTK files not found.")
        return
    
    print(f"\nAnalyzing files in: {vtk_dir}")
    print(f"Volcano Height: {ERUPTION_PARAMS['volcano_height']} m")
    print(f"Eruption Velocity: {ERUPTION_PARAMS['eruption_velocity']} m/s\n")
    
    for t_idx in range(16):
        filename = os.path.join(vtk_dir, f"eruption_{t_idx:04d}.vtk")
        if not os.path.exists(filename):
            continue
        
        # Quick parse for max temperature
        max_temp = 0
        reading_temp = False
        
        with open(filename, 'r') as f:
            for line in f:
                if "SCALARS temperature" in line:
                    reading_temp = True
                    continue
                elif line.startswith("SCALARS"):
                    reading_temp = False
                    continue
                elif line.startswith("LOOKUP_TABLE"):
                    continue
                
                if reading_temp:
                    try:
                        val = float(line.strip())
                        if val > max_temp:
                            max_temp = val
                    except:
                        pass
        
        print(f"  Timestep {t_idx}: Max temp = {max_temp:.0f}°C")


if __name__ == "__main__":
    try:
        from paraview.simple import GetActiveSource
        run_volcanic_analysis_paraview()
    except ImportError:
        standalone_analysis()
