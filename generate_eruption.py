"""
Volcanic Eruption Dynamics & Pyroclastic Hazard Analysis Generator
Time-Series Simulation of Stratovolcano Eruption with Multi-Phase Flow

Author: Randy Gharfa, Computational Geophysicist
Application: ParaView Volcanic Hazard Visualization & Analysis
"""
import math
import os
import random

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

# Time evolution (eruption phases)
NUM_TIMESTEPS = 16
TIME_START = 0.0
TIME_END = 480.0  # seconds (8-minute eruption sequence)
DT = (TIME_END - TIME_START) / (NUM_TIMESTEPS - 1)

# Volcano geometry (Stratovolcano profile)
VOLCANO_BASE_RADIUS = 3000    # m
VOLCANO_HEIGHT = 2800         # m
CRATER_RADIUS = 400           # m
CRATER_DEPTH = 200            # m
CONDUIT_RADIUS = 50           # m

# Domain parameters
nx, ny, nz = 60, 60, 80
spacing_xy = 120  # m (horizontal)
spacing_z = 80    # m (vertical)
origin = (-3600, -3600, -500)

# Magma properties
MAGMA_TEMPERATURE = 1150      # °C (basaltic-andesitic)
MAGMA_VISCOSITY = 1e4         # Pa·s
MAGMA_DENSITY = 2600          # kg/m³
GAS_FRACTION = 0.04           # 4% dissolved volatiles

# Eruption parameters
ERUPTION_VELOCITY = 350       # m/s (exit velocity)
MASS_FLUX = 1e7               # kg/s (VEI 4-5)
COLUMN_HEIGHT = 15000         # m (target)
PYROCLASTIC_THRESHOLD = 0.3   # Density ratio for column collapse

# Atmospheric conditions
ATM_TEMPERATURE_GROUND = 15   # °C
LAPSE_RATE = 6.5              # °C per 1000m
WIND_SPEED_GROUND = 5         # m/s
WIND_DIRECTION = 45           # degrees (from north)

# Volcanic gases (mass fractions)
GASES = {
    'H2O': 0.80,
    'CO2': 0.12,
    'SO2': 0.05,
    'H2S': 0.02,
    'HCl': 0.01
}

def distance_2d(x, y, cx, cy):
    return math.sqrt((x-cx)**2 + (y-cy)**2)

def distance_3d(x, y, z, cx, cy, cz):
    return math.sqrt((x-cx)**2 + (y-cy)**2 + (z-cz)**2)

def volcano_topography(x, y):
    """
    Generate stratovolcano elevation profile.
    Returns elevation in meters.
    """
    r = distance_2d(x, y, 0, 0)
    
    if r > VOLCANO_BASE_RADIUS:
        return 0  # Flat surrounding terrain
    
    # Exponential-gaussian cone profile
    cone_height = VOLCANO_HEIGHT * math.exp(-2 * (r / VOLCANO_BASE_RADIUS)**2)
    
    # Add crater depression at summit
    if r < CRATER_RADIUS:
        crater_factor = 1 - (r / CRATER_RADIUS)**2
        cone_height -= CRATER_DEPTH * crater_factor
    
    # Add some asymmetry (volcanic ridges)
    angle = math.atan2(y, x)
    ridge_factor = 1 + 0.15 * math.sin(3 * angle) * (r / VOLCANO_BASE_RADIUS)
    
    return cone_height * ridge_factor

def volcanic_structure(x, y, z):
    """
    Define internal volcanic structure.
    Returns: (material_type, in_volcano)
    0=atmosphere, 1=volcanic_rock, 2=magma_chamber, 3=conduit, 4=crater
    """
    r_xy = distance_2d(x, y, 0, 0)
    surface_z = volcano_topography(x, y)
    
    # Above surface = atmosphere
    if z > surface_z:
        # Check if in crater
        if r_xy < CRATER_RADIUS and z < surface_z + 100:
            return 4, True  # Crater zone (active)
        return 0, False
    
    # Underground structure
    if z < 0:
        return 1, True  # Bedrock below sea level
    
    # Conduit (vertical pipe to surface)
    if r_xy < CONDUIT_RADIUS:
        if z > surface_z - 500:  # Upper conduit
            return 3, True
    
    # Magma chamber (oblate spheroid at depth)
    chamber_center = (0, 0, -2000)
    chamber_rx, chamber_ry, chamber_rz = 800, 800, 400
    
    dx = (x - chamber_center[0]) / chamber_rx
    dy = (y - chamber_center[1]) / chamber_ry
    dz = (z - chamber_center[2]) / chamber_rz
    
    if dx**2 + dy**2 + dz**2 < 1:
        return 2, True  # Magma chamber
    
    # Volcanic edifice
    if z < surface_z:
        return 1, True
    
    return 0, False

def eruption_column_model(x, y, z, time_s, time_fraction):
    """
    Model volcanic eruption column using buoyant plume theory.
    Based on Morton-Taylor-Turner entrainment model.
    """
    # Eruption phases
    if time_fraction < 0.1:
        # Pre-eruption (inflation)
        intensity = time_fraction / 0.1 * 0.3
    elif time_fraction < 0.3:
        # Initial explosive phase
        intensity = 0.3 + (time_fraction - 0.1) / 0.2 * 0.7
    elif time_fraction < 0.7:
        # Sustained eruption
        intensity = 1.0
    elif time_fraction < 0.9:
        # Waning phase
        intensity = 1.0 - (time_fraction - 0.7) / 0.2 * 0.6
    else:
        # Post-eruption
        intensity = 0.4 - (time_fraction - 0.9) / 0.1 * 0.3
    
    intensity = max(0.1, intensity)
    
    # Column centerline
    surface_z = volcano_topography(0, 0)
    
    if z < surface_z:
        return 0, 0, 0, 0, (0, 0, 0)
    
    height_above_vent = z - surface_z
    
    # Plume radius expands with height (entrainment)
    entrainment_coeff = 0.1
    plume_radius = CRATER_RADIUS + entrainment_coeff * height_above_vent
    
    # Wind advection
    wind_speed = WIND_SPEED_GROUND + 0.01 * height_above_vent
    wind_rad = math.radians(WIND_DIRECTION)
    advection_x = wind_speed * math.sin(wind_rad) * height_above_vent / ERUPTION_VELOCITY
    advection_y = wind_speed * math.cos(wind_rad) * height_above_vent / ERUPTION_VELOCITY
    
    # Distance from bent plume axis
    plume_center_x = advection_x
    plume_center_y = advection_y
    r_plume = distance_2d(x - plume_center_x, y - plume_center_y, 0, 0)
    
    if r_plume > plume_radius * 3:
        return 0, 0, 0, 0, (0, 0, 0)
    
    # Gaussian concentration profile
    concentration = math.exp(-2 * (r_plume / plume_radius)**2)
    
    # Temperature (cools with height due to expansion and entrainment)
    ambient_temp = ATM_TEMPERATURE_GROUND - LAPSE_RATE * height_above_vent / 1000
    plume_temp = MAGMA_TEMPERATURE * math.exp(-height_above_vent / 8000)
    temperature = ambient_temp + (plume_temp - ambient_temp) * concentration * intensity
    
    # Particle concentration (ash density)
    max_height = COLUMN_HEIGHT * intensity
    if height_above_vent < max_height:
        height_factor = 1 - (height_above_vent / max_height)**0.5
    else:
        height_factor = 0.1 * math.exp(-(height_above_vent - max_height) / 2000)
    
    ash_concentration = concentration * height_factor * intensity
    
    # SO2 concentration (volcanic gas tracer)
    so2_concentration = ash_concentration * GASES['SO2'] * 1000  # ppm
    
    # Velocity field
    vertical_velocity = ERUPTION_VELOCITY * intensity * concentration * height_factor
    horizontal_vx = wind_speed * math.sin(wind_rad) * (1 - concentration * 0.5)
    horizontal_vy = wind_speed * math.cos(wind_rad) * (1 - concentration * 0.5)
    
    return temperature, ash_concentration, so2_concentration, intensity, (horizontal_vx, horizontal_vy, vertical_velocity)

def pyroclastic_flow_model(x, y, z, time_s, time_fraction):
    """
    Model pyroclastic density current (PDC) for column collapse scenarios.
    """
    if time_fraction < 0.25:
        return 0, 0, 0, (0, 0, 0)
    
    # PDC initiates from column collapse
    collapse_time = (time_fraction - 0.25) / 0.75
    
    # Flow front propagation (radial + downslope)
    flow_velocity = 80  # m/s average
    max_runout = 8000   # m
    current_runout = min(max_runout, flow_velocity * (time_s - 0.25 * TIME_END))
    
    if current_runout < 100:
        return 0, 0, 0, (0, 0, 0)
    
    # Distance from vent
    r_xy = distance_2d(x, y, 0, 0)
    surface_z = volcano_topography(x, y)
    height_above_ground = z - surface_z
    
    # PDC is gravity-driven, follows topography
    if r_xy > current_runout or height_above_ground > 500 or height_above_ground < 0:
        return 0, 0, 0, (0, 0, 0)
    
    # Radial sectors (PDCs often channelized)
    angle = math.atan2(y, x)
    # Preferential flow in 3 directions
    sector_factor = 0.5 + 0.5 * max(
        math.cos(angle - math.radians(0)),
        math.cos(angle - math.radians(120)),
        math.cos(angle - math.radians(240))
    )**4
    
    # Flow thickness decreases with distance
    flow_thickness = 200 * (1 - r_xy / max_runout) * sector_factor
    
    if height_above_ground > flow_thickness:
        return 0, 0, 0, (0, 0, 0)
    
    # PDC properties
    in_flow = height_above_ground < flow_thickness
    
    if in_flow:
        # Temperature (extremely hot)
        pdc_temp = 400 + 300 * (1 - height_above_ground / flow_thickness)
        
        # Density (decreases with height in flow)
        pdc_density = 50 * (1 - height_above_ground / flow_thickness)**2
        
        # Velocity (radially outward, following slope)
        radial_v = flow_velocity * (1 - r_xy / max_runout)**0.5
        vx = radial_v * x / max(r_xy, 1)
        vy = radial_v * y / max(r_xy, 1)
        vz = -20 * (height_above_ground / flow_thickness)  # Settling
        
        return pdc_temp, pdc_density, 1.0, (vx, vy, vz)
    
    return 0, 0, 0, (0, 0, 0)

def calculate_hazard_index(x, y, z, ash_conc, pdc_density, temperature, time_fraction):
    """
    Calculate volcanic hazard index for emergency planning.
    """
    surface_z = volcano_topography(x, y)
    height_above_ground = z - surface_z
    
    if height_above_ground < 0 or height_above_ground > 100:
        return 0  # Only surface hazards
    
    hazard = 0
    
    # Ash fall hazard
    if ash_conc > 0.01:
        hazard += min(1.0, ash_conc * 5) * 0.3
    
    # PDC hazard (lethal)
    if pdc_density > 1:
        hazard += min(1.0, pdc_density / 20) * 0.5
    
    # Thermal hazard
    if temperature > 100:
        hazard += min(1.0, (temperature - 100) / 300) * 0.2
    
    return min(1.0, hazard)

def generate_tephra_particles(time_s, time_fraction):
    """
    Generate volcanic tephra (bombs, lapilli, ash) particles.
    """
    particles = []
    
    if time_fraction < 0.1:
        return particles
    
    intensity = min(1.0, (time_fraction - 0.1) / 0.2) if time_fraction < 0.3 else 1.0
    if time_fraction > 0.7:
        intensity *= (1 - (time_fraction - 0.7) / 0.3)
    
    n_particles = int(intensity * 300)
    
    random.seed(42 + int(time_s))
    
    surface_z = volcano_topography(0, 0)
    
    for i in range(n_particles):
        # Ejection from crater
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(math.radians(60), math.radians(90))  # Near-vertical
        
        # Initial position (crater)
        r_init = random.uniform(0, CRATER_RADIUS * 0.8)
        px = r_init * math.cos(theta)
        py = r_init * math.sin(theta)
        pz = surface_z + random.uniform(50, 200)
        
        # Ejection velocity
        v_mag = ERUPTION_VELOCITY * random.uniform(0.3, 1.0)
        vx = v_mag * math.sin(phi) * math.cos(theta) + random.gauss(0, 20)
        vy = v_mag * math.sin(phi) * math.sin(theta) + random.gauss(0, 20)
        vz = v_mag * math.cos(phi)
        
        # Ballistic trajectory (time evolution)
        g = 9.81
        t_flight = time_s - 0.1 * TIME_END - (i / n_particles) * 50
        if t_flight > 0:
            px += vx * t_flight
            py += vy * t_flight
            pz += vz * t_flight - 0.5 * g * t_flight**2
            vz -= g * t_flight
        
        # Clast size (log-normal distribution)
        size_class = random.choices(
            ['bomb', 'lapilli', 'coarse_ash', 'fine_ash'],
            weights=[0.05, 0.15, 0.30, 0.50]
        )[0]
        
        if size_class == 'bomb':
            diameter = random.uniform(64, 300)  # mm
            density = 2400
        elif size_class == 'lapilli':
            diameter = random.uniform(2, 64)
            density = 2200
        elif size_class == 'coarse_ash':
            diameter = random.uniform(0.25, 2)
            density = 2000
        else:
            diameter = random.uniform(0.01, 0.25)
            density = 1800
        
        # Temperature (cools during flight)
        temp = MAGMA_TEMPERATURE * math.exp(-t_flight / 100) if t_flight > 0 else MAGMA_TEMPERATURE
        
        if pz > 0:  # Above ground
            particles.append({
                'pos': (px, py, pz),
                'vel': (vx, vy, vz),
                'diameter': diameter,
                'density': density,
                'temperature': temp,
                'size_class': ['bomb', 'lapilli', 'coarse_ash', 'fine_ash'].index(size_class),
                'id': i
            })
    
    return particles

def write_vtk_structured(filename, data, dims, spacing, origin_pt, title):
    """Write VTK structured points file."""
    with open(filename, 'w') as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write(f"{title}\n")
        f.write("ASCII\nDATASET STRUCTURED_POINTS\n")
        f.write(f"DIMENSIONS {dims[0]} {dims[1]} {dims[2]}\n")
        f.write(f"ORIGIN {origin_pt[0]} {origin_pt[1]} {origin_pt[2]}\n")
        f.write(f"SPACING {spacing[0]} {spacing[1]} {spacing[2]}\n")
        f.write(f"POINT_DATA {dims[0]*dims[1]*dims[2]}\n")
        
        for name, values in data.items():
            if name == "Velocity":
                f.write(f"VECTORS {name} float\n")
                for v in values:
                    f.write(f"{v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            else:
                f.write(f"SCALARS {name} float\nLOOKUP_TABLE default\n")
                for v in values:
                    f.write(f"{v:.6f}\n")

def write_particles_vtk(filename, particles, time_s):
    """Write tephra particles as VTK polydata."""
    if not particles:
        with open(filename, 'w') as f:
            f.write("# vtk DataFile Version 3.0\n")
            f.write(f"Volcanic Tephra | t = {time_s:.1f} s\n")
            f.write("ASCII\nDATASET POLYDATA\n")
            f.write("POINTS 0 float\n")
        return
    
    with open(filename, 'w') as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write(f"Volcanic Tephra | t = {time_s:.1f} s\n")
        f.write("ASCII\nDATASET POLYDATA\n")
        f.write(f"POINTS {len(particles)} float\n")
        
        for p in particles:
            f.write(f"{p['pos'][0]:.2f} {p['pos'][1]:.2f} {p['pos'][2]:.2f}\n")
        
        f.write(f"\nVERTICES {len(particles)} {len(particles)*2}\n")
        for i in range(len(particles)):
            f.write(f"1 {i}\n")
        
        f.write(f"\nPOINT_DATA {len(particles)}\n")
        
        f.write("VECTORS Velocity float\n")
        for p in particles:
            f.write(f"{p['vel'][0]:.2f} {p['vel'][1]:.2f} {p['vel'][2]:.2f}\n")
        
        f.write("SCALARS Diameter float\nLOOKUP_TABLE default\n")
        for p in particles:
            f.write(f"{p['diameter']:.4f}\n")
        
        f.write("SCALARS Temperature float\nLOOKUP_TABLE default\n")
        for p in particles:
            f.write(f"{p['temperature']:.1f}\n")
        
        f.write("SCALARS SizeClass int\nLOOKUP_TABLE default\n")
        for p in particles:
            f.write(f"{p['size_class']}\n")
        
        f.write("SCALARS ParticleID int\nLOOKUP_TABLE default\n")
        for p in particles:
            f.write(f"{p['id']}\n")

# ============================================================================
# MAIN GENERATION
# ============================================================================

print("="*70)
print("VOLCANIC ERUPTION DYNAMICS & PYROCLASTIC HAZARD ANALYSIS")
print("Stratovolcano Eruption Simulation with Multi-Phase Flow")
print("="*70)
print(f"\nVolcano Parameters:")
print(f"  Height: {VOLCANO_HEIGHT} m | Crater Radius: {CRATER_RADIUS} m")
print(f"  Magma Temperature: {MAGMA_TEMPERATURE}°C")
print(f"  Eruption Velocity: {ERUPTION_VELOCITY} m/s")
print(f"  Mass Flux: {MASS_FLUX:.0e} kg/s (VEI 4-5)")
print(f"\nGenerating {NUM_TIMESTEPS} timesteps ({TIME_END:.0f} s duration)...")

for t_idx in range(NUM_TIMESTEPS):
    time_s = TIME_START + t_idx * DT
    time_fraction = t_idx / (NUM_TIMESTEPS - 1)
    
    phase = "Pre-eruption" if time_fraction < 0.1 else \
            "Explosive onset" if time_fraction < 0.3 else \
            "Sustained eruption" if time_fraction < 0.7 else \
            "Waning phase" if time_fraction < 0.9 else "Post-eruption"
    
    print(f"\n  Timestep {t_idx}: t = {time_s:.0f} s | Phase: {phase}")
    
    data = {
        "terrain_type": [], "temperature": [], "ash_concentration": [],
        "SO2_concentration": [], "PDC_density": [], "hazard_index": [],
        "eruption_intensity": [], "Velocity": []
    }
    
    for k in range(nz):
        z = origin[2] + k * spacing_z
        for j in range(ny):
            y = origin[1] + j * spacing_xy
            for i in range(nx):
                x = origin[0] + i * spacing_xy
                
                terrain, in_solid = volcanic_structure(x, y, z)
                
                if in_solid and terrain > 0:
                    # Solid volcano
                    if terrain == 2:  # Magma chamber
                        temp = MAGMA_TEMPERATURE
                    elif terrain == 3:  # Conduit
                        temp = MAGMA_TEMPERATURE * 0.9
                    else:
                        depth = volcano_topography(x, y) - z
                        temp = 20 + depth * 0.03  # Geothermal gradient
                    
                    data["terrain_type"].append(terrain)
                    data["temperature"].append(temp)
                    data["ash_concentration"].append(0)
                    data["SO2_concentration"].append(0)
                    data["PDC_density"].append(0)
                    data["hazard_index"].append(0)
                    data["eruption_intensity"].append(0)
                    data["Velocity"].append((0, 0, 0))
                else:
                    # Atmosphere - check for eruption column and PDC
                    col_temp, ash, so2, intensity, col_vel = eruption_column_model(x, y, z, time_s, time_fraction)
                    pdc_temp, pdc_dens, pdc_flag, pdc_vel = pyroclastic_flow_model(x, y, z, time_s, time_fraction)
                    
                    # Combine column and PDC
                    total_temp = max(col_temp, pdc_temp)
                    total_ash = ash + pdc_dens * 0.01
                    
                    # Velocity (dominant flow)
                    if pdc_dens > 1:
                        vel = pdc_vel
                    else:
                        vel = col_vel
                    
                    hazard = calculate_hazard_index(x, y, z, ash, pdc_dens, total_temp, time_fraction)
                    
                    data["terrain_type"].append(0)
                    data["temperature"].append(total_temp)
                    data["ash_concentration"].append(total_ash)
                    data["SO2_concentration"].append(so2)
                    data["PDC_density"].append(pdc_dens)
                    data["hazard_index"].append(hazard)
                    data["eruption_intensity"].append(intensity)
                    data["Velocity"].append(vel)
    
    # Write atmosphere/eruption data
    filename = f"eruption_{t_idx:04d}.vtk"
    write_vtk_structured(filename, data, (nx, ny, nz), 
                         (spacing_xy, spacing_xy, spacing_z), origin,
                         f"Volcanic Eruption | t = {time_s:.0f} s | {phase}")
    print(f"    Created: {filename}")
    
    # Generate tephra particles
    particles = generate_tephra_particles(time_s, time_fraction)
    particle_file = f"tephra_{t_idx:04d}.vtk"
    write_particles_vtk(particle_file, particles, time_s)
    if particles:
        print(f"    Created: {particle_file} ({len(particles)} particles)")

# ============================================================================
# GENERATE STATIC VOLCANO TOPOGRAPHY
# ============================================================================

print("\nGenerating volcano topography mesh...")

topo_data = {"elevation": [], "slope": [], "terrain_class": []}

# Higher resolution for topography
topo_nx, topo_ny = 80, 80
topo_spacing = 100  # m

for j in range(topo_ny):
    y = -4000 + j * topo_spacing
    for i in range(topo_nx):
        x = -4000 + i * topo_spacing
        
        elev = volcano_topography(x, y)
        
        # Calculate slope (for hazard mapping)
        elev_px = volcano_topography(x + topo_spacing, y)
        elev_py = volcano_topography(x, y + topo_spacing)
        slope = math.sqrt((elev_px - elev)**2 + (elev_py - elev)**2) / topo_spacing
        slope_degrees = math.degrees(math.atan(slope))
        
        # Terrain classification
        r = distance_2d(x, y, 0, 0)
        if r < CRATER_RADIUS:
            terrain_class = 4  # Crater
        elif elev > 2000:
            terrain_class = 3  # Summit zone
        elif elev > 1000:
            terrain_class = 2  # Upper flanks
        elif elev > 100:
            terrain_class = 1  # Lower flanks
        else:
            terrain_class = 0  # Surrounding plain
        
        topo_data["elevation"].append(elev)
        topo_data["slope"].append(slope_degrees)
        topo_data["terrain_class"].append(terrain_class)

# Write as 2D structured grid (elevated)
with open("volcano_topography.vtk", 'w') as f:
    f.write("# vtk DataFile Version 3.0\n")
    f.write("Volcano Topography - Digital Elevation Model\n")
    f.write("ASCII\nDATASET STRUCTURED_GRID\n")
    f.write(f"DIMENSIONS {topo_nx} {topo_ny} 1\n")
    f.write(f"POINTS {topo_nx * topo_ny} float\n")
    
    idx = 0
    for j in range(topo_ny):
        y = -4000 + j * topo_spacing
        for i in range(topo_nx):
            x = -4000 + i * topo_spacing
            z = topo_data["elevation"][idx]
            f.write(f"{x:.1f} {y:.1f} {z:.1f}\n")
            idx += 1
    
    f.write(f"\nPOINT_DATA {topo_nx * topo_ny}\n")
    
    f.write("SCALARS Elevation float\nLOOKUP_TABLE default\n")
    for v in topo_data["elevation"]:
        f.write(f"{v:.1f}\n")
    
    f.write("SCALARS Slope float\nLOOKUP_TABLE default\n")
    for v in topo_data["slope"]:
        f.write(f"{v:.2f}\n")
    
    f.write("SCALARS TerrainClass int\nLOOKUP_TABLE default\n")
    for v in topo_data["terrain_class"]:
        f.write(f"{int(v)}\n")

print("  Created: volcano_topography.vtk")

# ============================================================================
# GENERATE PVD FILES
# ============================================================================

print("\nGenerating PVD time series files...")

pvd = '<?xml version="1.0"?>\n<VTKFile type="Collection" version="0.1">\n  <Collection>\n'
for t_idx in range(NUM_TIMESTEPS):
    time_s = TIME_START + t_idx * DT
    pvd += f'    <DataSet timestep="{time_s:.2f}" file="eruption_{t_idx:04d}.vtk"/>\n'
pvd += '  </Collection>\n</VTKFile>\n'

with open("volcanic_eruption.pvd", "w") as f:
    f.write(pvd)
print("  Created: volcanic_eruption.pvd")

pvd_tephra = '<?xml version="1.0"?>\n<VTKFile type="Collection" version="0.1">\n  <Collection>\n'
for t_idx in range(NUM_TIMESTEPS):
    time_s = TIME_START + t_idx * DT
    pvd_tephra += f'    <DataSet timestep="{time_s:.2f}" file="tephra_{t_idx:04d}.vtk"/>\n'
pvd_tephra += '  </Collection>\n</VTKFile>\n'

with open("tephra_trajectories.pvd", "w") as f:
    f.write(pvd_tephra)
print("  Created: tephra_trajectories.pvd")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("GENERATION COMPLETE")
print("="*70)
print(f"Domain: {nx*spacing_xy/1000:.1f} x {ny*spacing_xy/1000:.1f} x {nz*spacing_z/1000:.1f} km")
print(f"Grid: {nx} x {ny} x {nz} = {nx*ny*nz:,} points per timestep")
print(f"Timesteps: {NUM_TIMESTEPS} (t = 0 to {TIME_END:.0f} s)")
print(f"\nFiles Generated:")
print(f"  - volcanic_eruption.pvd (Eruption column + PDC time series)")
print(f"  - tephra_trajectories.pvd (Volcanic projectile tracking)")
print(f"  - volcano_topography.vtk (Static DEM)")
print(f"  - {NUM_TIMESTEPS} eruption VTK files")
print(f"  - {NUM_TIMESTEPS} tephra particle files")
