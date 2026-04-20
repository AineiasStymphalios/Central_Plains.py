#
#   FILE:    Mediterranean_Sea.py
#   AUTHOR:  AineiasStymph (Script adapted directly from GRM7584's Earth2, which was based on Sirian's Terra script)
#   PURPOSE: Global map script - Simulates Randomized Mediterranean Sea
#-----------------------------------------------------------------------------
#   Copyright (c) 2008 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import MultilayeredFractal
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
import math

'''
##############################################################################
MULTILAYERED FRACTAL NOTES

The MultilayeredFractal class was created for use with this script.

I worked to make it adaptable to other scripts, though, and eventually it
migrated in to the MapUtil file along with the other primary map classes.

- Bob Thomas July 13, 2005


TERRA NOTES

Terra turns out to be our largest size map. This is the only map script
in the original release of Civ4 where the grids are this large!

This script is also the one that got me started in to map scripting. I had 
this idea early in the development cycle and just kept pestering until Soren 
turned me loose on it, finally. Once I got going, I just kept on going!

- Bob Thomas   September 20, 2005

EARTH2 NOTES

This is based purely on the Terra script, albeit with a lot more similarity
to Earth in terms of landmasses. Rocky Climate and Normal Sea Levels strongly
recommended for maximum earthiness.

##############################################################################
MEDITERRANEAN NOTES

This mapscript is based on Earth2.py.
Below are its features:
- Improved MultilayeredFractal generator
    - Takes matrix inputs
    - More property inputs for regions
- Lattitude-band based Terrain overrides
- Bonus generator
    - Runs strategic and food bonus additions to starting plots (Currently checks for 1 strategic and 2 land food bonuses)
    - Option: Historical resource placement
        - Swaps / removes ahistoric resources
        - Region specific bonus placement
- River generator based on that of Tectonics.py
    - Generates more realistic rivers
    - More control over river frequency
    - Features river deletion / reduction regions (used to reduce rivers in Sahara desert)
    - Custom north-flowing river generator (used for Nile river)
- Two tile coasts (expandCoastToTwoTiles)
- Option: Historical starting locations
    - Historical (Shuffle): Randomly places all players in 5 primary, 5 secondary, and 8 tertiary locations, in order of priority. 
        Remaining players are placed with default methods.
    - Historical (Fixed): If there are any map-appropriate Vanilla BTS Civilizations in the playerlist, they are placed on fixed regions. 
        Remaining players assignments fall back to the Shuffle method, and then to default methods.
- Option: Open / close Suez, Bosporus, Gibraltar straits
- Option: Mountain range settings
    - Realistic: Stronger mountain ranges (Alps, Pyrenees, etc.)
    - Reduced: Nerfs mountain ranges (recommended, unless running AI improvement mods)

- AineiasStymph, March 28, 2026
##############################################################################
CENTRAL PLAINS NOTES
This mapscript is based on my Mediterranean_sea.py.
Below are its new features:
- Improved MultilayeredFractal generator
    - Renamed to GeometricFractal
    - Now takes center X and Y for region inputs.
    - Allows Rectangular and Elliptical fractal masks, with rotation.
- Terrain and Feature generator based on moisture and temperature gradients
- River and Waterway generator
    - Generates rivers / waterways through coordinate inputs
    - Option for landbridges in waterways.
    - *Mostly* functional river merges
- AineiasStymph, 
##############################################################################
'''

    
def getDescription():
    desc = "A procedurally generated Chinese Central Plains map with realistic geography and climate. "
    desc += ". "
    return desc

def isAdvancedMap():
    "This map should show up in simple mode"
    return 0


# -----------------------------------------------------------------------------
# Custom Options
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Custom Options
# -----------------------------------------------------------------------------
def getNumCustomMapOptions():
    return 9

def getCustomMapOptionName(argsList):
    index = argsList[0]
    names = [
        "Starting Plot Min. Food",
        "Historical Resources",
        "Ivory Northern Limit",
        "Great River Options",
        "Other Deep River Options",
        "Lesser River Options",
        "Peak Reduction",
        "Geographic Accuracy",
        "Start Options"
    ]
    if index < len(names):
        return names[index]
    return ""

def getNumCustomMapOptionValues(argsList):
    index = argsList[0]
    if index == 0: return 3 # Food: 0, 1, 2
    if index == 1: return 2 # Corn: Remove, Vanilla
    if index == 2: return 4 # Ivory: Hebei, Shandong, Huai, Yangtze
    if index == 3: return 3 # Great Rivers: Waterway, bridgeless waterway, Regular
    if index == 4: return 3 # Deep Rivers: Waterway, bridgeless waterway, Regular
    if index == 5: return 2 # Lesser Rivers: Generated, Disabled
    if index == 6: return 3 # Peaks: Alpine, Highland, Disabled
    if index == 7: return 3 # Accuracy: High, Medium, Low
    if index == 8: return 2 # Start Options: Default, Fixed-Shuffle
    return 0

def getCustomMapOptionDescAt(argsList):
    index = argsList[0]
    selection = argsList[1]
    if index == 0: # Food
        if selection == 0: return "0"
        if selection == 1: return "At least 1 (Default)"
        return "At least 2"
    if index == 1: # Corn
        if selection == 0: return "Remove Corn (Default)"
        return "Vanilla"
    if index == 2: # Ivory
        if selection == 0: return "Hebei (Shang)"
        if selection == 1: return "Shandong (Western Zhou)"
        if selection == 2: return "Huai River (Warring States) (Default)"
        return "Yangtze (Three Kingdoms)"
    if index == 3: # Great Rivers
        if selection == 0: return "Waterway (Default)"
        if selection == 1: return "Bridgeless Waterway"
        return "Regular River"
    if index == 4: # Deep Rivers
        if selection == 0: return "Waterway"
        if selection == 1: return "Bridgeless Waterway"
        return "Regular River (Default)"
    if index == 5: # Lesser Rivers
        if selection == 0: return "Generated (Default)"
        return "Disabled (Compensated with higher river density)"
    if index == 6: # Peaks
        if selection == 0: return "Flatten Alpine Regions"
        if selection == 1: return "Flatten Alpine and Highland Regions"
        return "Disabled (Default)"
    if index == 7: # Accuracy
        if selection == 0: return "High (Default)"
        if selection == 1: return "Medium"
        return "Low"
    if index == 8: # Start Options
        if selection == 0: return "Vanilla"
        return "Fixed-Shuffle (Spring-Autumn ~ Warring States)"
    return ""

def getCustomMapOptionDefault(argsList):
    index = argsList[0]
    if index == 0: return 1 # 1 Food
    if index == 1: return 0 # Remove Corn
    if index == 2: return 2 # Huai
    if index == 3: return 0 # Waterway
    if index == 4: return 2 # River
    if index == 5: return 0 # Generated
    if index == 6: return 2 # Disabled
    if index == 7: return 0 # High accuracy
    if index == 8: return 1 # starts
    return 0

# -----------------------------------------------------------------------------
# Map Properties
# -----------------------------------------------------------------------------

def getGridSize(argsList):
    # original map projection is 1000x100px = 1:1
    grid_sizes = {
        WorldSizeTypes.WORLDSIZE_DUEL:      (5, 5),
        WorldSizeTypes.WORLDSIZE_TINY:      (6, 6),
        WorldSizeTypes.WORLDSIZE_SMALL:     (8, 8),
        WorldSizeTypes.WORLDSIZE_STANDARD:  (10, 10),
        WorldSizeTypes.WORLDSIZE_LARGE:     (11, 11),
        WorldSizeTypes.WORLDSIZE_HUGE:      (12, 12),
    }
    if argsList[0] == -1:
        return []
    return grid_sizes[argsList[0]]

def isSeaLevelMap():
    return 0

def getWrapX():
    return False

def getWrapY():
    return False

def isClimateMap():
    return 1

def getClimate():
    """This is now ignored by the engine because isClimateMap is 1, 
    but we keep it for safety."""
    return ClimateTypes.CLIMATE_TEMPERATE

_all_start_coords = [] # Store player start coords
def beforeGeneration():
    """
    Official Civ4 hook called before map generation starts.
    Guaranteed to run on Map Regeneration.
    """
    # Clear the starting plot cache so that regeneration reshuffles players
    global _START_PLOT_MAP
    _START_PLOT_MAP = None
    return None

_DEBUG_REGIONS = [] # Global to store regions for sign placement

def _add_region_signs(region_data):
    """Adds map signs to the center of each fractal region."""
    m = CyMap()
    engine = CyEngine()
    iW = m.getGridWidth()
    iH = m.getGridHeight()
    
    for data in region_data:
        name = data[0]
        cx = data[2]
        cy = data[3]
        
        # Convert fractional center to plot coordinates
        iX = int(iW * cx)
        iY = int(iH * cy)
        
        pPlot = m.plot(iX, iY)
        if pPlot and not pPlot.isNone():
            # -1 makes the sign visible to all players (global)
            engine.addSign(pPlot, -1, str(name))



# -----------------------------------------------------------------------------
# GeometricFractal Generator
# -----------------------------------------------------------------------------
class GeometricFractal(CvMapGeneratorUtil.MultilayeredFractal):
    """
    Fractal generator supporting geometric masking and rotation.
    Shapes: RECT, ELLIPSE.
    """
    def generatePlotsByRegion(self, region_data):
        sea = 0 
        
        # Define Terrain Profiles: (HillDensity%, PeakDensity%_of_Hills)
        # Higher HillDensity = less flat land.
        # Higher PeakDensity = more mountains within those hills.
        terrain_profiles = {
            "flat":         (15, 1),
            "plateau":      (60, 10),  # High hills, very few peaks
            "highland":     (75, 40),
            "alpine":       (95, 70),  # Almost no flat land, half peaks
            "default":      (30, 20)
        }
        
        gc = CyGlobalContext()
        m = CyMap()
        iRocky = gc.getInfoTypeForString("CLIMATE_ROCKY")
        if m.getClimate() == iRocky:
            for key in terrain_profiles.keys():
                h_dens, p_dens = terrain_profiles[key]
                # Increase hill chance by 20%, peak chance by 10%
                new_h = int(h_dens * 1.2)
                new_p = int(p_dens * 1.1)
                if new_h > 100: new_h = 100
                if new_p > 100: new_p = 100
                terrain_profiles[key] = (new_h, new_p)

        for data in region_data:
            name, r_type_raw, cx, cy, d1, d2, d3, terrain, grain, h_grain, water_prc = data
            r_type = r_type_raw.upper()
            
            if d3 != 0:
                radius = math.sqrt((d1/2.0)**2 + (d2/2.0)**2)
                west, east, south, north = cx - radius, cx + radius, cy - radius, cy + radius
            else:
                west, east, south, north = cx - (d1/2.0), cx + (d1/2.0), cy - (d2/2.0), cy + (d2/2.0)

            iWest, iEast = max(0, int(self.iW * west)), min(self.iW - 1, int(self.iW * east))
            iSouth, iNorth = max(0, int(self.iH * south)), min(self.iH - 1, int(self.iH * north))
            reg_w, reg_h = iEast - iWest + 1, iNorth - iSouth + 1
            if reg_w <= 0 or reg_h <= 0: continue

            is_subtractive = (terrain == "water")
            if not is_subtractive:
                NiTextOut("Generating %s (Geometric Fractal) ..." % name)
                regionContFrac = CyFractal()
                regionHillsFrac = CyFractal()
                regionPeaksFrac = CyFractal()
                
                # FIX: Pass 0 instead of self.iTerrainFlags to prevent edge-tapering/flattening
                regionContFrac.fracInit(reg_w, reg_h, grain, self.dice, 0, -1, -1)
                regionHillsFrac.fracInit(reg_w, reg_h, h_grain, self.dice, 0, -1, -1)
                regionPeaksFrac.fracInit(reg_w, reg_h, h_grain+1, self.dice, 0, -1, -1)
                
                # Python 2.4 compatible if/else
                if water_prc == 0:
                    iWaterThreshold = -1
                else:
                    iWaterThreshold = regionContFrac.getHeightFromPercent(water_prc + sea)

                h_dens, p_dens = terrain_profiles.get(terrain, terrain_profiles["default"])
                iHillThreshold = regionHillsFrac.getHeightFromPercent(100 - h_dens)
                iPeakThreshold = regionPeaksFrac.getHeightFromPercent(100 - p_dens)

            rad = -math.radians(d3)
            cosA, sinA = math.cos(rad), math.sin(rad)
            
            invRxSq = 0
            invRySq = 0
            if r_type == "ELLIPSE":
                invRxSq = 1.0 / ((d1/2.0)**2)
                invRySq = 1.0 / ((d2/2.0)**2)
            
            hW, hH = d1/2.0, d2/2.0

            for x in range(reg_w):
                world_x = x + iWest
                fx = (world_x / float(self.iW)) - cx
                for y in range(reg_h):
                    world_y = y + iSouth
                    world_i = world_y * self.iW + world_x
                    fy = (world_y / float(self.iH)) - cy

                    rx = fx * cosA - fy * sinA
                    ry = fx * sinA + fy * cosA

                    is_inside = False
                    if r_type == "ELLIPSE":
                        if (rx*rx * invRxSq) + (ry*ry * invRySq) <= 1.0: is_inside = True
                    else: # RECT
                        if abs(rx) <= hW and abs(ry) <= hH: is_inside = True

                    if not is_inside: continue

                    if is_subtractive:
                        self.wholeworldPlotTypes[world_i] = PlotTypes.PLOT_OCEAN
                    else:
                        if regionContFrac.getHeight(x, y) <= iWaterThreshold: continue
                        
                        if regionHillsFrac.getHeight(x, y) >= iHillThreshold:
                            if regionPeaksFrac.getHeight(x, y) >= iPeakThreshold:
                                self.wholeworldPlotTypes[world_i] = PlotTypes.PLOT_PEAK
                            else:
                                self.wholeworldPlotTypes[world_i] = PlotTypes.PLOT_HILLS
                        else:
                            self.wholeworldPlotTypes[world_i] = PlotTypes.PLOT_LAND
        return self.wholeworldPlotTypes

def generatePlotTypes():
    NiTextOut("Setting Plot Types (Python Central Plains) ...")
    
    global _START_PLOT_MAP, _DEBUG_REGIONS
    _START_PLOT_MAP = None

    gc = CyGlobalContext()
    m = CyMap()
    climate = m.getClimate()
    
    accuracy = m.getCustomMapOption(7)
    peak_opt = m.getCustomMapOption(6)
    
    sizekey = m.getWorldSize()
    sizevalues = {
        WorldSizeTypes.WORLDSIZE_DUEL:      (3,2,1),
        WorldSizeTypes.WORLDSIZE_TINY:      (3,2,1),
        WorldSizeTypes.WORLDSIZE_SMALL:     (4,2,1),
        WorldSizeTypes.WORLDSIZE_STANDARD:  (4,2,1),
        WorldSizeTypes.WORLDSIZE_LARGE:     (4,2,1),
        WorldSizeTypes.WORLDSIZE_HUGE:      (5,2,1)
    }
    (ScatterGrain, BalanceGrain, GatherGrain) = sizevalues[sizekey]

    regions = []
    if accuracy == 2: # LOW ACCURACY
        # Create one giant block on the West 50% of the map, fractal terrain on the center 25%, leaving East 25% as Water
        # Name, Type, CX, CY, D1, D2, D3, Terrain, Grain, Hills, Water%
        regions = [
            ("Low_Fractal_Mainland", "Rect", 0.25, 0.50, 0.70, 1.2, 0, "default", ScatterGrain, BalanceGrain, 0),
            ("Low_Fractal_WesternMountains", "Rect", 0.05, 0.50, 0.2, 1.2, 0, "highland", ScatterGrain, GatherGrain, 10),
            ("Low_Fractal_Coast", "Ellipse", 0.4, 0.2, 0.9, 0.9, 0, "default", BalanceGrain, BalanceGrain, 15),
            ("Low_Fractal_North", "Ellipse", 0.8, 0.96, 0.6, 0.4, 45, "default", BalanceGrain, BalanceGrain, 20)
        ]

    else:
        # Input format: NAME, TYPE, CX, CY, D1, D2, D3, TERRAIN, GRAIN, HILLS, WATER
        all_regions = [
            ("Base_MainLand", "Rect", 0.31, 0.50, 0.7615, 1, 0, "default", GatherGrain, ScatterGrain, 0),
            ("Base_Liaoning", "Rect", 0.88, 0.94, 0.231, 0.118, 0, "default", GatherGrain, ScatterGrain, 0),
            ("Base_Rehe", "Rect", 0.74, 0.93, 0.25, 0.138, -45, "plateau", GatherGrain, ScatterGrain, 5),
            ("Base_Liaodong", "Rect", 0.94, 0.82, 0.073, 0.1596, -30, "plateau", GatherGrain, ScatterGrain, 10),
            ("Base_Shandong", "Rect", 0.83, 0.63, 0.171, 0.091, 33.3, "default", GatherGrain, ScatterGrain, 10),
            ("Base_CentralPlains", "Ellipse", 0.60, 0.56, 0.374, 0.381, 0, "flat", GatherGrain, ScatterGrain, 5),
            ("Base_EastChina", "Ellipse", 0.64, 0.26, 0.525, 0.583, 0, "default", GatherGrain, ScatterGrain, 5),
            ("Base_Beijing", "Ellipse", 0.67, 0.80, 0.192, 0.117, 0, "flat", GatherGrain, ScatterGrain, 5),
            ("Yinchuan", "Ellipse", 0.11, 0.75, 0.133, 0.028, 60, "alpine", GatherGrain, GatherGrain, 5),
            ("Bayannur", "Ellipse", 0.19, 0.89, 0.133, 0.028, 37.4, "alpine", GatherGrain, GatherGrain, 5),
            ("Baotou", "Ellipse", 0.36, 0.87, 0.168, 0.028, 0, "alpine", GatherGrain, GatherGrain, 5),
            ("Taihang_Mt", "Rect", 0.52, 0.82, 0.0909, 0.382, -52, "alpine", ScatterGrain, ScatterGrain, 10),
            ("Shanxi", "Rect", 0.40, 0.55, 0.181, 0.073, 0, "highland", ScatterGrain, ScatterGrain, 10),
            ("Shanxi_East", "Rect", 0.50, 0.64, 0.0747, 0.203, 0, "highland", GatherGrain, GatherGrain, 0),
            ("Shaanxi", "Rect", 0.29, 0.60, 0.178, 0.117, 0, "highland", ScatterGrain, ScatterGrain, 20),
            ("Ningxia", "Rect", 0.07, 0.58, 0.178, 0.211, 0, "highland", ScatterGrain, ScatterGrain, 20),
            ("Shangdong_West", "Rect", 0.72, 0.58, 0.129, 0.095, 0, "plateau", ScatterGrain, ScatterGrain, 20),
            ("Sichuan_Guizou", "Rect", 0.21, 0.23, 0.413, 0.465, 0, "plateau", ScatterGrain, ScatterGrain, 20),
            ("sichuan-basin", "Ellipse", 0.13, 0.26, 0.25, 0.225, 0, "flat", BalanceGrain, BalanceGrain, 10),
            ("Sichuan_NW", "Rect", 0.02, 0.39, 0.129, 0.1467, -52, "alpine", ScatterGrain, ScatterGrain, 10),
            ("Sichuan_SW", "Rect", 0.04, 0.08, 0.2427, 0.1594, -41, "alpine", ScatterGrain, ScatterGrain, 5),
            ("Sichuan_NE", "Rect", 0.28, 0.35, 0.248, 0.0475, -13, "alpine", ScatterGrain, ScatterGrain, 10),
            ("Sichuan_East", "Ellipse", 0.32, 0.2, 0.138, 0.1015, -5, "highland", ScatterGrain, ScatterGrain, 10),
            ("Sichuan_SE", "Rect", 0.28, 0.06, 0.1396, 0.1826, -11, "alpine", ScatterGrain, ScatterGrain, 10),
            ("Xian_S", "Rect", 0.30, 0.44, 0.227, 0.044, -4, "alpine", GatherGrain, GatherGrain, 0),
            ("Luoxiao_Mt", "Rect", 0.53, 0.08, 0.1099, 0.166, 0, "alpine", GatherGrain, ScatterGrain, 10),
            ("Wuhan_North", "Ellipse", 0.58, 0.32, 0.186, 0.0813, -18.8, "highland", GatherGrain, GatherGrain, 5),
            ("Hangzhou_West", "Rect", 0.73, 0.25, 0.186, 0.09, 16.2, "plateau", GatherGrain, GatherGrain, 5),
            ("Zhejiang_Fujian", "Ellipse", 0.74, 0.10, 0.422, 0.158, 46.2, "highland", ScatterGrain, BalanceGrain, 10),
        ]

        for r in all_regions:
            name = r[0]
            is_base = (name[:4] == "Base")
            
            if accuracy == 0: # High
                regions.append(r)
            elif accuracy == 1: # Medium
                if is_base: regions.append(r)
            else: # Low
                if is_base: regions.append(r)

    # Peak Reduction Logic
    processed_regions = []
    for r in regions:
        r_list = list(r)
        terrain = r_list[7]
        if peak_opt == 0: # Flatten Alpine
            if terrain == "alpine": r_list[7] = "highland"
        elif peak_opt == 1: # Flatten Highland
            if terrain == "highland": r_list[7] = "plateau"
            if terrain == "alpine": r_list[7] = "highland"
        processed_regions.append(tuple(r_list))

    # Store the list for the debug sign placer
    # _DEBUG_REGIONS = regions


    global plotgen
    plotgen = GeometricFractal()
    return plotgen.generatePlotsByRegion(regions)

# -----------------------------------------------------------------------------
# Terrain & Feature Generator
# -----------------------------------------------------------------------------
def get_plot_moisture(iX, iY, iWidth, iHeight, pFractal, regions_list):
    """Calculates moisture (1.0 Wet to 0.0 Dry) for a specific plot."""
    gc = CyGlobalContext()
    m = CyMap()
    accuracy = m.getCustomMapOption(7) 
    climate = m.getClimate() # Fetch built-in climate selection
    
    fx = float(iX) / float(iWidth)
    fy = float(iY) / float(iHeight)

    # 1. Calculate the Angled Linear Base (1.0 at SE, 0.0 at NW)
    weightY = 0.6
    weightX = 0.4
    linear_base = (weightY * (1.0 - fy)) + (weightX * fx)
        
    # 2. MODULAR PIECEWISE GRADIENT (Remaining distance, gradient slope) 
    control_points = [
        (1.0, 1.0), # SE corner
        (0.5, 0.7), #
        (0.2, 0.2), #
        (0.0, 0.0)  # NW corner
    ]
    
    base_moisture = 0.0
    for i in range(len(control_points) - 1):
        p_high = control_points[i]
        p_low = control_points[i+1]
        if linear_base >= p_low[0]:
            x = linear_base
            x0, y0 = p_low
            x1, y1 = p_high
            dx = x1 - x0
            if dx == 0:
                base_moisture = y0
            else:
                base_moisture = y0 + (x - x0) * (y1 - y0) / dx
            break

    iTropical = gc.getInfoTypeForString("CLIMATE_TROPICAL")
    iArid = gc.getInfoTypeForString("CLIMATE_ARID")
    iCold = gc.getInfoTypeForString("CLIMATE_COLD")

    if climate == iTropical:
        base_moisture = base_moisture + 0.25 
    elif climate == iArid:
        base_moisture = base_moisture - 0.25 
    # elif climate == iCold:
        # base_moisture = base_moisture - 0.10 

    # 3. Accuracy-Based Jitter (Preserved)
    fFractalHeight = float(pFractal.getHeight(iX, iY))
    noise = (fFractalHeight / 255.0) - 0.5
    
    if accuracy == 0: # High
        noise_multiplier = 0.25
    elif accuracy == 1: # Medium
        noise_multiplier = 0.30 
    else: # Low
        noise_multiplier = 0.45 
        
    moisture = base_moisture + (noise * noise_multiplier)
    
    # 4. Climate Regions (Preserved as comments)
    # for name, cx, cy, w, h, delta in regions_list:
    #     if abs(fx - cx) <= (w / 2.0) and abs(fy - cy) <= (h / 2.0):
    #         moisture = moisture + delta

    # 5. Final Clamp
    if moisture < 0.0: moisture = 0.0
    if moisture > 1.0: moisture = 1.0
    return moisture

def get_plot_temp(iX, iY, iWidth, iHeight, pFractal):
    """Calculates temperature (0.0 Cold to 1.0 Warm)."""
    gc = CyGlobalContext()
    m = CyMap()
    accuracy = m.getCustomMapOption(7)
    climate = m.getClimate()
    iCold = gc.getInfoTypeForString("CLIMATE_COLD")
    iTropical = gc.getInfoTypeForString("CLIMATE_TROPICAL")
    
    fx = float(iX) / float(iWidth)
    fy = float(iY) / float(iHeight)
    
    # North-West is Coldest, South-East is Warmest
    weightY = 0.9
    weightX = 0.1
    linear_base = (weightY * (1.0 - fy)) + (weightX * fx)
    
    # --- NEW: Climate-Based Temperature Shifting ---
    if climate == iCold:
        # Allow the full range, shifted down slightly so NW hits absolute zero (Ice)
        base_temp = linear_base - 0.20
    # elif climate == iTropical:
        # # Shift upwards
        # base_temp = linear_base + 0.40
    else:
        # Temperate Mode: NW starts at floor (above Tundra threshold )
        fFloor = 0.4
        base_temp = fFloor + (linear_base * (1.0 - fFloor))
    
    # Accuracy-based Jitter
    fFractalHeight = float(pFractal.getHeight(iX, iY))
    noise = (fFractalHeight / 255.0) - 0.5
    if accuracy == 0: noise_multiplier = 0.15 
    elif accuracy == 1: noise_multiplier = 0.2 
    else: noise_multiplier = 0.3 
    
    temp = base_temp + (noise * noise_multiplier)
    
    if temp < 0.0: temp = 0.0
    if temp > 1.0: temp = 1.0
    return temp

# Define your climate regions globally so both generators can see them (Unused)
    # delta +0.3 makes a region significantly wetter (Desert -> Plains, Plains -> Grass)
    # delta -0.3 makes a region significantly drier (Grass -> Plains, Plains -> Desert)
CLIMATE_REGIONS = [
    # (Name, CenterX, CenterY, Width, Height, MoistureDelta)
    ("Climate_Manchuria", 0.9, 0.85, 0.20, 0.297, 0.2),
    ("Climate_CentralPlains", 0.74, 0.67, 0.52, 0.656, 0.25),
]

class TerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
    def __init__(self, fGrassMoistureThreshold=0.5, fDesertMoistureThreshold=0.2):
        # We call the parent but we will use our own logic in generateTerrainAtPlot
        CvMapGeneratorUtil.TerrainGenerator.__init__(self)
        self.fGrassThreshold = fGrassMoistureThreshold
        self.fDesertThreshold = fDesertMoistureThreshold

    def generateTerrainAtPlot(self, iX, iY):
        pPlot = self.map.plot(iX, iY)
        
        # 1. Handle Water (Early Exit)
        if pPlot.isWater():
            return pPlot.getTerrainType()

        # 2. Fetch Gradients
        temp = get_plot_temp(iX, iY, self.iWidth, self.iHeight, self.deserts)
        moisture = get_plot_moisture(iX, iY, self.iWidth, self.iHeight, self.deserts, CLIMATE_REGIONS)
        
        # 3. Terrain IDs
        iSnow = self.gc.getInfoTypeForString("TERRAIN_SNOW")
        iTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
        iPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
        iDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
        iGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")

        # 4. TERRAIN MATRIX LOGIC
        # Temperature Bands: Cold (< 0.2), Neutral (0.2 - 0.6), Hot (> 0.6)
        # Moisture Bands: Dry (< fDesertThreshold), Neutral (fDesert to fGrass), Wet (> fGrassThreshold)

        if temp < 0.15:
            # --- COLD ZONE ---
            if moisture < self.fDesertThreshold:
                return iSnow    # Dry/Cold = Ice
            else:
                return iTundra  # Neutral/Cold or Wet/Cold = Tundra

        elif temp < 0.60:
            # --- NEUTRAL TEMPERATURE ZONE ---
            if moisture < self.fDesertThreshold:
                return iDesert  # Dry/Neutral = Desert
            elif moisture < self.fGrassThreshold:
                # Neutral/Neutral = Plains
                return iPlains
                # # Neutral/Neutral = Plains-Grass Mix
                # # We use a sub-threshold to split the band
                # fMidNeutral = (self.fDesertThreshold + self.fGrassThreshold) / 2.0
                # if moisture > fMidNeutral:
                    # return iGrass
                # else:
                    # return iPlains
            else:
                return iGrass   # Wet/Neutral = Grass

        else:
            # --- HOT ZONE ---
            if moisture < self.fDesertThreshold:
                return iDesert  # Dry/Hot = Desert
            elif moisture < self.fGrassThreshold:
                return iPlains # Dry/Neutral = Plains
            else:
                return iGrass   # Dry/Hot, Neutral/Hot, or Wet/Hot = Grass

def generateTerrainTypes():
    NiTextOut("Generating Terrain (Python Central Plains) ...")
    
    # We no longer need iDesertPercent or iPlainsPercent because we
    # define the climate via the piecewise moisture gradient.
    # We only pass the thresholds for the terrain bands.
    
    terraingen = TerrainGenerator(
        fGrassMoistureThreshold = 0.5, 
        fDesertMoistureThreshold = 0.2
    )
    
    terrainTypes = terraingen.generateTerrain()
    return terrainTypes


class FeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
    def __init__(self, iJunglePercent=40, iForestPercent=40):
        CvMapGeneratorUtil.FeatureGenerator.__init__(self, iJunglePercent, iForestPercent)
        
        self.gc = CyGlobalContext()
        self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
        self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
        self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
        
        # Initialize fractal for moisture noise
        self.moisture_noise = CyFractal()
        self.moisture_noise.fracInit(self.iGridW, self.iGridH, 3, self.mapRand, 0, -1, -1)

    def addIceAtPlot(self, pPlot, iX, iY, lat):
        # Do nothing - prevents ice placement
        pass

    def addFeaturesAtPlot(self, iX, iY):
        pPlot = self.map.sPlot(iX, iY)
        if pPlot.isWater() or pPlot.getFeatureType() != -1: return

        moisture = get_plot_moisture(iX, iY, self.iGridW, self.iGridH, self.moisture_noise, CLIMATE_REGIONS)
        temp = get_plot_temp(iX, iY, self.iGridW, self.iGridH, self.moisture_noise)
        
        # 1. Jungle Placement (Wet AND Warm)
        if moisture > 0.80:
            if temp > 0.65:
                if self.mapRand.get(100, "J") < self.iJunglePercent:
                    if pPlot.canHaveFeature(self.featureJungle):
                        pPlot.setFeatureType(self.featureJungle, -1)
                        return

        # 2. Forest Placement (Variety based on moisture)
        if moisture > 0.35:
            if self.mapRand.get(100, "F") < self.iForestPercent:
                if pPlot.canHaveFeature(self.featureForest):
                    if moisture > 0.60: iVariety = 0 # Deciduous
                    else: iVariety = 1 # Pine
                    pPlot.setFeatureType(self.featureForest, iVariety)
                    return

        # 3. Desert Features
        if pPlot.getTerrainType() == self.terrainDesert:
            if moisture < 0.20:
                if self.mapRand.get(100, "O") < 5:
                    if pPlot.canHaveFeature(self.featureOasis):
                        pPlot.setFeatureType(self.featureOasis, -1)

def addFeatures():
    NiTextOut("Adding Features (Python Central Plains) ...")
    featuregen = FeatureGenerator()
    featuregen.addFeatures()
    # expandCoastToTwoTiles()
    
    # Debug for fractal regions
    global _DEBUG_REGIONS
    if _DEBUG_REGIONS:
        _add_region_signs(_DEBUG_REGIONS)
    
    return 0

# -----------------------------------------------------------------------------
# Coast distance
# -----------------------------------------------------------------------------
def expandCoastToTwoTiles():
    """Convert all water tiles within 2 tiles of land to coast terrain."""
    map = CyMap()
    gc = CyGlobalContext()
    iW = map.getGridWidth()
    iH = map.getGridHeight()
    coast_id = gc.getInfoTypeForString("TERRAIN_COAST")

    # Collect all land plots
    land_plots = []
    for x in range(iW):
        for y in range(iH):
            if not map.plot(x, y).isWater():
                land_plots.append((x, y))

    # Mark water plots within Manhattan distance <= 2 of any land
    coast_plots = set()
    for lx, ly in land_plots:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 2:   # Manhattan distance
                    nx, ny = lx + dx, ly + dy
                    if 0 <= nx < iW and 0 <= ny < iH:
                        pPlot = map.plot(nx, ny)
                        if pPlot.isWater():
                            coast_plots.add((nx, ny))

    # Apply coast terrain
    for x, y in coast_plots:
        map.plot(x, y).setTerrainType(coast_id, True, True)
        


# -----------------------------------------------------------------------------
# River Generator
# -----------------------------------------------------------------------------
class RiverGenerator:
    """
    From Tectonics.py class riversFromSea.
    Added to generate more natural-looking rivers.
    Input exclude_rects to prevent river generation in certain regions (used for Sahara in this mapscript).
    """
    def __init__(self, river_density=1.0, exclude_rects=None, reduce_rects=None, survival_chance=20):
        """
        exclude_rects: list of (west, south, width, height) – rivers never start or flow here.
        reduce_rects: list of (west, south, width, height) – rivers have only `survival_chance`% chance to flow here.
        river_density: float > 0; 1.0 gives a moderate number of rivers (similar to old divider=2).
        """
        self.gc = CyGlobalContext()
        self.dice = self.gc.getGame().getMapRand()
        self.map = CyMap()
        self.width = self.map.getGridWidth()
        self.height = self.map.getGridHeight()
        self.straightThreshold = 3
        if (self.width * self.height > 400):
            self.straightThreshold = 2
        self.survival_chance = survival_chance
        self.river_density = river_density

        # Convert exclude rectangles
        self.exclude_rects = []
        if exclude_rects:
            for (west, south, width, height) in exclude_rects:
                west_x = int(self.width * west)
                east_x = int(self.width * (west + width))
                south_y = int(self.height * south)
                north_y = int(self.height * (south + height))
                self.exclude_rects.append((west_x, east_x, south_y, north_y))

        # Convert reduce rectangles
        self.reduce_rects = []
        if reduce_rects:
            for (west, south, width, height) in reduce_rects:
                west_x = int(self.width * west)
                east_x = int(self.width * (west + width))
                south_y = int(self.height * south)
                north_y = int(self.height * (south + height))
                self.reduce_rects.append((west_x, east_x, south_y, north_y))

    def is_excluded(self, x, y):
        for (west_x, east_x, south_y, north_y) in self.exclude_rects:
            if west_x <= x <= east_x and south_y <= y <= north_y:
                return True
        return False

    def is_reduced(self, x, y):
        """Return True if the plot lies in a reduce_rect; also roll for chance."""
        for (west_x, east_x, south_y, north_y) in self.reduce_rects:
            if west_x <= x <= east_x and south_y <= y <= north_y:
                # Roll the dice: return True if the roll is < survival_chance (i.e., allowed)
                return self.dice.get(100, "River reduction") < self.survival_chance
        return True   # not in any reduce_rect -> always allowed

    def collateCoasts(self):
        """Return list of land plots adjacent to a large water body."""
        result = []
        for x in range(self.width):
            for y in range(self.height):
                plot = self.map.plot(x, y)
                if plot.isCoastalLand():
                    # Check if any adjacent water plot is large enough
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            adj = self.map.plot(nx, ny)
                            if self.is_water_for_river(adj):
                                result.append(plot)
                                break
        return result

    def seedRivers(self):
        # Base number of rivers proportional to the map's perimeter (width+height)
        # For density 1.0, this gives about the same as the old divider=2.
        base = (self.width + self.height) / 2.0
        riversNumber = int(base * self.river_density) + 1

        self.coasts = self.collateCoasts()
        coastsNumber = len(self.coasts)
        if coastsNumber == 0:
            return

        # Cap to the number of available coastal plots to avoid excessive attempts
        riversNumber = min(riversNumber, coastsNumber)

        coastShare = coastsNumber / riversNumber
        for i in range(riversNumber):
            for attempt in range(50):
                choiceCoast = coastShare * i + self.dice.get(coastShare, "Pick a coast for the river")
                if choiceCoast >= coastsNumber:
                    choiceCoast = coastsNumber - 1
                plot = self.coasts[choiceCoast]
                x, y = plot.getX(), plot.getY()
                # Skip if excluded OR (reduced and dice fails)
                if self.is_excluded(x, y):
                    continue
                if not self.is_reduced(x, y):
                    continue
                (x, y, flow) = self.generateRiverFromPlot(plot, x, y)
                if flow != CardinalDirectionTypes.NO_CARDINALDIRECTION:
                    riverID = self.gc.getMap().getNextRiverID()
                    self.addRiverFrom(x, y, flow, riverID)
                break

    def canFlowFrom(self, plot, upperPlot):
        """Return True if water can flow from `plot` to `upperPlot`."""
        if self.is_water_for_river(plot):
            return False
        if plot.getPlotType() == PlotTypes.PLOT_PEAK:
            return False
        # If the upper plot is in an excluded rectangle, stop
        ux, uy = upperPlot.getX(), upperPlot.getY()
        if self.is_excluded(ux, uy):
            return False
        # If the upper plot is in a reduced rectangle, apply chance
        if not self.is_reduced(ux, uy):
            return False

        if plot.getPlotType() == PlotTypes.PLOT_HILLS:
            return True
        if plot.getPlotType() == PlotTypes.PLOT_LAND:
            if self.is_water_for_river(upperPlot):
                return False
            return True
        return False

    def is_water_for_river(self, plot):
        """Return True only if the plot is water and its area is large enough."""
        if not plot.isWater():
            return False
        area_id = plot.getArea()
        if area_id == -1:
            return False
        area = self.map.getArea(area_id)
        return area.getNumTiles() >= 5   # min_water_area_size fixed at 5

    def generateRiverFromPlot(self, plot, x, y):
        FlowDirection = CardinalDirectionTypes.NO_CARDINALDIRECTION
        if ((y < 1 or y >= self.height - 1) or plot.isNOfRiver() or plot.isWOfRiver()):
            return (x, y, FlowDirection)
        eastX = self.eastX(x)
        westX = self.westX(x)
        otherPlot = True
        eastPlot = self.map.plot(eastX, y)
        if eastPlot.isCoastalLand():
            # Check water using is_water_for_river
            if (self.is_water_for_river(self.map.plot(x, y+1)) or
                self.is_water_for_river(self.map.plot(eastX, y+1))):
                landPlot1 = self.map.plot(x, y-1)
                landPlot2 = self.map.plot(eastX, y-1)
                if landPlot1.isWater() or landPlot2.isWater():
                    otherPlot = True
                else:
                    FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_NORTH
                    otherPlot = False
            if otherPlot:
                if (self.is_water_for_river(self.map.plot(x, y-1)) or
                    self.is_water_for_river(self.map.plot(eastX, y-1))):
                    landPlot1 = self.map.plot(x, y+1)
                    landPlot2 = self.map.plot(eastX, y+1)
                    if landPlot1.isWater() or landPlot2.isWater():
                        otherPlot = True
                    else:
                        FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
                        otherPlot = False
        if otherPlot:
            southPlot = self.map.plot(x, y-1)
            if southPlot.isCoastalLand():
                if (self.is_water_for_river(self.map.plot(eastX, y)) or
                    self.is_water_for_river(self.map.plot(eastX, y-1))):
                    landPlot1 = self.map.plot(westX, y)
                    landPlot2 = self.map.plot(westX, y-1)
                    if landPlot1.isWater() or landPlot2.isWater():
                        otherPlot = True
                    else:
                        FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_EAST
                        otherPlot = False
                if otherPlot:
                    if (self.is_water_for_river(self.map.plot(westX, y)) or
                        self.is_water_for_river(self.map.plot(westX, y-1))):
                        landPlot1 = self.map.plot(eastX, y)
                        landPlot2 = self.map.plot(eastX, y-1)
                        if landPlot1.isWater() or landPlot2.isWater():
                            otherPlot = True
                        else:
                            FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_WEST
        return (x, y, FlowDirection)

    def addRiverFrom(self, x, y, flow, riverID):
        plot = self.map.plot(x, y)
        if self.is_water_for_river(plot):
            return
        eastX = self.eastX(x)
        westX = self.westX(x)
        if self.preventRiversFromCrossing(x, y, flow, riverID):
            return
        plot.setRiverID(riverID)
        if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST) or (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
            plot.setNOfRiver(True, flow)
        else:
            plot.setWOfRiver(True, flow)
        xShift = 0
        yShift = 0
        if flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
            xShift = 1
        elif flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
            xShift = -1
        elif flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
            yShift = -1
        elif flow == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH:
            yShift = 1
        nextX = x + xShift
        nextY = y + yShift
        if nextX >= self.width:
            nextX = 0
        if nextY >= self.height:
            return
        nextPlot = self.map.plot(nextX, nextY)
        if not self.canFlowFrom(plot, nextPlot):
            return
        if plot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW") and self.dice.get(10, "Stop on ice") > 3:
            return
        flatDesert = (plot.getPlotType() == PlotTypes.PLOT_LAND) and (plot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
        turnThreshold = 16
        if flatDesert:
            turnThreshold = 18
        turned = False
        northY = y + 1
        southY = y - 1
        if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST) or (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
            if (northY < self.height) and (self.dice.get(20, "branch from north") > turnThreshold):
                if (self.canFlowFrom(plot, self.map.plot(x, northY)) and
                    self.canFlowFrom(self.map.plot(self.eastX(x), y), self.map.plot(self.eastX(x), northY))):
                    turned = True
                    if flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
                        self.addRiverFrom(x, y, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH, riverID)
                    else:
                        westPlot = self.map.plot(westX, y)
                        westPlot.setRiverID(riverID)
                        self.addRiverFrom(westX, y, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH, riverID)
            if (not turned) and (southY >= 0) and (self.dice.get(20, "branch from south") > turnThreshold):
                if (self.canFlowFrom(plot, self.map.plot(x, southY)) and
                    self.canFlowFrom(self.map.plot(self.eastX(x), y), self.map.plot(self.eastX(x), southY))):
                    turned = True
                    if flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
                        southPlot = self.map.plot(x, y-1)
                        southPlot.setRiverID(riverID)
                        self.addRiverFrom(x, southY, CardinalDirectionTypes.CARDINALDIRECTION_NORTH, riverID)
                    else:
                        westPlot = self.map.plot(westX, southY)
                        westPlot.setRiverID(riverID)
                        self.addRiverFrom(westX, southY, CardinalDirectionTypes.CARDINALDIRECTION_NORTH, riverID)
        else:
            if (self.canFlowFrom(plot, self.map.plot(eastX, y)) and
                self.canFlowFrom(self.map.plot(x, southY), self.map.plot(eastX, y)) and
                (self.dice.get(20, "branch from east") > turnThreshold)):
                turned = True
                if flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
                    eastPlot = self.map.plot(eastX, y)
                    eastPlot.setRiverID(riverID)
                    self.addRiverFrom(eastX, y, CardinalDirectionTypes.CARDINALDIRECTION_WEST, riverID)
                else:
                    northEastPlot = self.map.plot(eastX, y+1)
                    northEastPlot.setRiverID(riverID)
                    self.addRiverFrom(eastX, y+1, CardinalDirectionTypes.CARDINALDIRECTION_WEST, riverID)
            if (not turned) and (self.canFlowFrom(plot, self.map.plot(westX, y)) and
                self.canFlowFrom(self.map.plot(x, southY), self.map.plot(westX, southY)) and
                (self.dice.get(20, "branch from west") > turnThreshold)):
                turned = True
                if flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
                    self.addRiverFrom(x, y, CardinalDirectionTypes.CARDINALDIRECTION_EAST, riverID)
                else:
                    northPlot = self.map.plot(x, y+1)
                    northPlot.setRiverID(riverID)
                    self.addRiverFrom(x, y+1, CardinalDirectionTypes.CARDINALDIRECTION_EAST, riverID)
        spawnInDesert = (not turned) and flatDesert
        if (self.dice.get(10, "straight river") > self.straightThreshold) or spawnInDesert:
            self.addRiverFrom(nextX, nextY, flow, riverID)
        else:
            if not turned:
                plot = self.map.plot(nextX, nextY)
                if (plot.getPlotType() == PlotTypes.PLOT_LAND) and (self.dice.get(10, "Rivers start in hills") > 3):
                    plot.setPlotType(PlotTypes.PLOT_HILLS, True, True)
                    if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST) or (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
                        if southY > 0:
                            self.map.plot(nextX, southY).setPlotType(PlotTypes.PLOT_HILLS, True, True)
                    else:
                        self.map.plot(eastX, nextY).setPlotType(PlotTypes.PLOT_HILLS, True, True)

    def preventRiversFromCrossing(self, x, y, flow, riverID):
        plot = self.map.plot(x, y)
        eastX = self.eastX(x)
        westX = self.westX(x)
        if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
            if (plot.isNOfRiver()):
                return True
            if (self.map.plot(eastX, y).isNOfRiver()):
                return True
            southPlot = self.map.plot(x, y-1)
            if (southPlot.isWOfRiver() and southPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
                return True
            if (plot.isWOfRiver() and plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
                return True
            if (self.map.plot(eastX, y).isWater()):
                return True
            if (self.map.plot(x, y-1).isWater()):
                return True
            if (self.map.plot(eastX, y-1).isWater()):
                return True
        if (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
            if (plot.isNOfRiver()):
                return True
            if (self.map.plot(westX, y).isNOfRiver()):
                return True
            southPlot = self.map.plot(westX, y-1)
            if (southPlot.isWOfRiver() and southPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
                return True
            westPlot = self.map.plot(westX, y)
            if (westPlot.isWOfRiver() and westPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
                return True
            if (self.map.plot(westX, y).isWater()):
                return True
            if (self.map.plot(x, y-1).isWater()):
                return True
            if (self.map.plot(westX, y-1).isWater()):
                return True
        if (flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
            if (plot.isWOfRiver()):
                return True
            eastPlot = self.map.plot(eastX, y)
            if (eastPlot.isNOfRiver() and eastPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
                return True
            if (plot.isNOfRiver() and plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
                return True
            if (self.map.plot(x, y-1).isWOfRiver()):
                return True
            if (self.map.plot(x, y-1).isWater()):
                return True
            if (self.map.plot(x+1, y).isWater()):
                return True
            if (self.map.plot(x+1, y-1).isWater()):
                return True
        if (flow == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
            if (plot.isWOfRiver()):
                return True
            eastPlot = self.map.plot(eastX, y+1)
            if (eastPlot.isNOfRiver() and eastPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
                return True
            northPlot = self.map.plot(x, y+1)
            if (northPlot.isNOfRiver() and northPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
                return True
            if (self.map.plot(x, y+1).isWOfRiver()):
                return True
            if (self.map.plot(x, y+1).isWater()):
                return True
            if (self.map.plot(x+1, y).isWater()):
                return True
            if (self.map.plot(x+1, y+1).isWater()):
                return True
        return False

    def westX(self, x):
        westX = x - 1
        if (westX < 0):
            westX = self.width
        return westX

    def eastX(self, x):
        eastX = x + 1
        if (eastX >= self.width):
            eastX = 0
        return eastX
        

# -----------------------------------------------------------------------------
# Custom River Generator
# -----------------------------------------------------------------------------
class PathNavigator:
    def __init__(self, map, dice):
        self.map = map
        self.dice = dice
        self.iW = map.getGridWidth()
        self.iH = map.getGridHeight()
        self.noise = CyFractal()
        self.noise.fracInit(self.iW, self.iH, 2, self.dice, 0, -1, -1)
        self.size_factor = float(self.iW + self.iH) / 64.0

    def is_ocean(self, x, y):
        if x < 0 or x >= self.iW or y < 0 or y >= self.iH: return False
        pPlot = self.map.plot(x, y)
        if pPlot.isWater():
            pArea = pPlot.area()
            if pArea:
                if pArea.getNumTiles() >= 10: return True
        return False

    def is_any_water(self, x, y):
        if x < 0 or x >= self.iW or y < 0 or y >= self.iH: return False
        return self.map.plot(x, y).isWater()

    def get_best_move(self, cx, cy, tx, ty, visited, is_water_path, meander):
        best_score = 999999.0
        best_move = None
        accuracy = self.map.getCustomMapOption(7)
        dist_to_target = math.sqrt((cx - tx)**2 + (cy - ty)**2)

        if is_water_path:
            moves = [(1,0), (-1,0), (0,1), (0,-1)]
        else:
            moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            
        for move in moves:
            nx, ny = cx + move[0], cy + move[1]
            if nx < 0 or nx >= self.iW or ny < 0 or ny >= self.iH: continue
            
            bVisited = False
            for v in visited:
                if nx == v[0] and ny == v[1]:
                    bVisited = True
                    break
            if bVisited: continue
            
            if is_water_path:
                bSkip2x2 = False
                if accuracy == 2 or dist_to_target < 4:
                    bSkip2x2 = True
                else:
                    for adj in [(1,0), (-1,0), (0,1), (0,-1)]:
                        if self.is_ocean(nx + adj[0], ny + adj[1]):
                            bSkip2x2 = True
                            break
                
                if not bSkip2x2:
                    if self.is_any_water(nx-1, ny) and self.is_any_water(nx, ny-1) and self.is_any_water(nx-1, ny-1): continue
                    if self.is_any_water(nx+1, ny) and self.is_any_water(nx, ny-1) and self.is_any_water(nx+1, ny-1): continue
                    if self.is_any_water(nx-1, ny) and self.is_any_water(nx, ny+1) and self.is_any_water(nx-1, ny+1): continue
                    if self.is_any_water(nx+1, ny) and self.is_any_water(nx, ny+1) and self.is_any_water(nx+1, ny+1): continue

            dist = math.sqrt((nx - tx)**2 + (ny - ty)**2)
            n_val = (self.noise.getHeight(nx, ny) / 100.0) - 0.5
            score = dist * (1.0 + (n_val * meander))
            
            if score < best_score:
                best_score = score
                best_move = (nx, ny, move[0], move[1])
        return best_move

    def generate_path(self, start, end, meander, is_water_path):
        curr_x, curr_y = start
        path = [(curr_x, curr_y)]
        visited = [(curr_x, curr_y)]
        
        max_steps = (abs(curr_x - end[0]) + abs(curr_y - end[1])) * 4
        for i in range(max_steps):
            if curr_x == end[0] and curr_y == end[1]: break
            move = self.get_best_move(curr_x, curr_y, end[0], end[1], visited, is_water_path, meander)
            if not move: break
            curr_x, curr_y = move[0], move[1]
            path.append((curr_x, curr_y))
            visited.append((curr_x, curr_y))
            
            if is_water_path:
                if self.is_ocean(curr_x, curr_y):
                    break
            else:
                # Standard River: Stop if we hit ANY water
                # We skip i=0 to allow rivers to start adjacent to water
                if i > 0:
                    if self.is_any_water(curr_x, curr_y):
                        break
        return path
    
class WaterwayMaker:
    def __init__(self, navigator):
        self.nav = navigator
        self.map = navigator.map

    def build(self, checkpoints, meander, bridge_spacing, bBridgesEnabled=True):
        full_path = []
        for i in range(len(checkpoints) - 1):
            start = (int(self.nav.iW * checkpoints[i][0]), int(self.nav.iH * checkpoints[i][1]))
            end = (int(self.nav.iW * checkpoints[i+1][0]), int(self.nav.iH * checkpoints[i+1][1]))
            segment = self.nav.generate_path(start, end, meander, True)
            if i == 0:
                full_path.extend(segment)
            else:
                full_path.extend(segment[1:])
            if segment:
                if self.nav.is_ocean(segment[-1][0], segment[-1][1]):
                    break
        
        self._apply_to_map(full_path, bridge_spacing, bBridgesEnabled)

    def _apply_to_map(self, path, bridge_spacing, bBridgesEnabled):
        if not path: return
        riverID = self.map.getNextRiverID()
        self.map.incrementNextRiverID()
        step_count = 0
        next_gap = int((self.nav.dice.get(3, "G") + bridge_spacing) * self.nav.size_factor)
        if next_gap < 2: next_gap = 2

        for i in range(len(path)):
            x, y = path[i]
            pPlot = self.map.plot(x, y)
            
            # Force Ocean on last tile or existing ocean
            if i == len(path) - 1 or self.nav.is_ocean(x, y):
                pPlot.setPlotType(PlotTypes.PLOT_OCEAN, True, True)
                step_count = 0
                continue

            bIsBridge = False
            # Only evaluate bridge logic if bBridgesEnabled is True
            if bBridgesEnabled:
                if step_count >= next_gap:
                    bNearOcean = False
                    for adj in [(1,0), (-1,0), (0,1), (0,-1)]:
                        if self.nav.is_ocean(x+adj[0], y+adj[1]):
                            bNearOcean = True
                            break
                    if not bNearOcean:
                        bIsBridge = True

            if bIsBridge:
                pPlot.setPlotType(PlotTypes.PLOT_LAND, True, True)
                pPlot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
                
                # Flatten 8-way adjacent peaks
                for adj_x in range(-1, 2):
                    for adj_y in range(-1, 2):
                        if adj_x == 0 and adj_y == 0: continue
                        nx, ny = x + adj_x, y + adj_y
                        if nx >= 0 and nx < self.nav.iW and ny >= 0 and ny < self.nav.iH:
                            pAdj = self.map.plot(nx, ny)
                            if pAdj.getPlotType() == PlotTypes.PLOT_PEAK:
                                pAdj.setPlotType(PlotTypes.PLOT_HILLS, True, True)
                
                dx, dy, ndx, ndy = 0, 0, 0, 0
                if i > 0: dx, dy = x - path[i-1][0], y - path[i-1][1]
                if i < len(path)-1: ndx, ndy = path[i+1][0] - x, path[i+1][1] - y
                self._apply_bridge_flags(x, y, dx, dy, ndx, ndy, riverID)
                step_count = 0
                next_gap = int((self.nav.dice.get(3, "G") + bridge_spacing) * self.nav.size_factor)
                if next_gap < 2: next_gap = 2
            else:
                pPlot.setPlotType(PlotTypes.PLOT_OCEAN, True, True)
                step_count += 1

    def _apply_bridge_flags(self, x, y, dx, dy, ndx, ndy, rID):
        N, S, E, W = CardinalDirectionTypes.CARDINALDIRECTION_NORTH, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH, CardinalDirectionTypes.CARDINALDIRECTION_EAST, CardinalDirectionTypes.CARDINALDIRECTION_WEST
        corner = "STRAIGHT"
        if dy==1 and ndx==1: corner="S_E"
        elif dy==1 and ndx==-1: corner="S_W"
        elif dy==-1 and ndx==1: corner="N_E"
        elif dy==-1 and ndx==-1: corner="N_W"
        elif dx==-1 and ndy==-1: corner="E_S"
        elif dx==1 and ndy==-1: corner="W_S"
        elif dx==-1 and ndy==1: corner="E_N"
        elif dx==1 and ndy==1: corner="W_N"

        if corner == "STRAIGHT":
            p = self.map.plot(x, y)
            if dx != 0:
                flow = E
                if dx != 1: flow = W
                p.setNOfRiver(True, flow)
            elif dy != 0:
                flow = N
                if dy != 1: flow = S
                p.setWOfRiver(True, flow)
            p.setRiverID(rID)
        elif corner == "S_E":
            p=self.map.plot(x-1, y); p.setWOfRiver(True, N); p.setRiverID(rID)
            p=self.map.plot(x, y+1); p.setNOfRiver(True, E); p.setRiverID(rID)
        elif corner == "S_W":
            p=self.map.plot(x, y); p.setWOfRiver(True, N); p.setRiverID(rID)
            p=self.map.plot(x, y+1); p.setNOfRiver(True, W); p.setRiverID(rID)
        elif corner == "N_E":
            p=self.map.plot(x-1, y); p.setWOfRiver(True, S); p.setRiverID(rID)
            p=self.map.plot(x, y); p.setNOfRiver(True, E); p.setRiverID(rID)
        elif corner == "N_W":
            p=self.map.plot(x, y); p.setWOfRiver(True, S); p.setNOfRiver(True, W); p.setRiverID(rID)
        elif corner == "E_S":
            p=self.map.plot(x-1, y); p.setWOfRiver(True, S); p.setRiverID(rID)
            p=self.map.plot(x, y+1); p.setNOfRiver(True, W); p.setRiverID(rID)
        elif corner == "W_S":
            # --- INCORPORATED YOUR FIX ---
            p=self.map.plot(x, y); p.setWOfRiver(True, S); p.setRiverID(rID)
            p=self.map.plot(x, y+1); p.setNOfRiver(True, E); p.setRiverID(rID)
        elif corner == "E_N":
            p=self.map.plot(x-1, y); p.setWOfRiver(True, N); p.setRiverID(rID)
            p=self.map.plot(x, y); p.setNOfRiver(True, W); p.setRiverID(rID)
        elif corner == "W_N":
            p=self.map.plot(x, y); p.setWOfRiver(True, N); p.setNOfRiver(True, E); p.setRiverID(rID)

class StandardRiverMaker:
    def __init__(self, navigator):
        self.nav = navigator
        self.map = navigator.map

    def build(self, checkpoints, meander):
        riverID = self.map.getNextRiverID()
        self.map.incrementNextRiverID()
        for i in range(len(checkpoints) - 1):
            start = (int(self.nav.iW * checkpoints[i][0]), int(self.nav.iH * checkpoints[i][1]))
            end = (int(self.nav.iW * checkpoints[i+1][0]), int(self.nav.iH * checkpoints[i+1][1]))
            path = self.nav.generate_path(start, end, meander, False)
            if not path: break
            
            for j in range(len(path)-1):
                curr, next = path[j], path[j+1]
                dx, dy = next[0]-curr[0], next[1]-curr[1]
                bStop = self._apply_river_flags(curr[0], curr[1], dx, dy, riverID)
                if bStop: return

    def _apply_river_flags(self, x, y, dx, dy, rID):
        N, S, E, W = CardinalDirectionTypes.CARDINALDIRECTION_NORTH, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH, CardinalDirectionTypes.CARDINALDIRECTION_EAST, CardinalDirectionTypes.CARDINALDIRECTION_WEST
        bStop = False
        
        # Horizontal
        if dx != 0:
            if dx == 1:
                tx = x
                flow = E
                look_x = tx + 1
            else:
                tx = x - 1
                flow = W
                look_x = tx - 1
            
            # Stop at ANY water (Lake or Coast)
            if self.nav.is_any_water(look_x, y) or self.nav.is_any_water(look_x, y-1):
                bStop = True
            
            p = self.map.plot(tx, y)
            if p:
                if not self.nav.is_any_water(tx, y):
                    if not self.nav.is_any_water(tx, y-1):
                        if self._check_merge(tx, y, False, flow): 
                            bStop = True
                        p.setNOfRiver(True, flow)
                        p.setRiverID(rID)
            if bStop: return True

        # Vertical
        if dy != 0:
            tx = x + dx - 1
            if dy == 1:
                ty = y
                flow = N
                look_y = ty + 1
            else:
                ty = y - 1
                flow = S
                look_y = ty - 1
            
            # Stop at ANY water (Lake or Coast)
            if self.nav.is_any_water(tx, look_y) or self.nav.is_any_water(tx+1, look_y):
                bStop = True
                
            p = self.map.plot(tx, ty)
            if p:
                if not self.nav.is_any_water(tx, ty):
                    if not self.nav.is_any_water(tx+1, ty):
                        if self._check_merge(tx, ty, True, flow): 
                            bStop = True
                        p.setWOfRiver(True, flow)
                        p.setRiverID(rID)
        return bStop

    def _check_merge(self, x, y, is_vertical, flow):
        N, S, E, W = CardinalDirectionTypes.CARDINALDIRECTION_NORTH, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH, CardinalDirectionTypes.CARDINALDIRECTION_EAST, CardinalDirectionTypes.CARDINALDIRECTION_WEST
        if is_vertical:
            if flow == N:
                p=self.map.plot(x, y+1)
                if p and ((p.isWOfRiver() and p.getRiverNSDirection()==N) or (p.isNOfRiver() and p.getRiverWEDirection()==W)): return True
                p=self.map.plot(x+1, y+1)
                if p and (p.isNOfRiver() and p.getRiverWEDirection()==E): return True
            else:
                p=self.map.plot(x, y)
                if p and (p.isNOfRiver() and p.getRiverWEDirection()==W): return True
                p=self.map.plot(x, y-1)
                if p and (p.isWOfRiver() and p.getRiverNSDirection()==S): return True
                p=self.map.plot(x+1, y)
                if p and (p.isNOfRiver() and p.getRiverWEDirection()==E): return True
        else:
            if flow == E:
                p=self.map.plot(x, y)
                if p and (p.isWOfRiver() and p.getRiverNSDirection()==N): return True
                p=self.map.plot(x, y-1)
                if p and (p.isWOfRiver() and p.getRiverNSDirection()==S): return True
                p=self.map.plot(x+1, y)
                if p and (p.isNOfRiver() and p.getRiverWEDirection()==E): return True
            else: # W
                p=self.map.plot(x-1, y)
                if p and ((p.isNOfRiver() and p.getRiverWEDirection()==W) or (p.isWOfRiver() and p.getRiverNSDirection()==N)): return True
                p=self.map.plot(x-1, y-1)
                if p and (p.isWOfRiver() and p.getRiverNSDirection()==S): return True
        return False

def addRivers():
    m = CyMap()
    m.recalculateAreas()
    gc = CyGlobalContext()
    dice = gc.getGame().getMapRand()
    
    # Initialize the new Class-based system
    nav = PathNavigator(m, dice)
    waterways = WaterwayMaker(nav)
    rivers = StandardRiverMaker(nav)
    
    # Fetch Map Options
    great_is_waterway = (m.getCustomMapOption(3) == 0) or (m.getCustomMapOption(3) == 1)
    deep_is_waterway = (m.getCustomMapOption(4) == 0) or (m.getCustomMapOption(4) == 1)
    lesser_enabled = (m.getCustomMapOption(5) == 0)
    accuracy = m.getCustomMapOption(7)
    
    # Waterway Bridge binaries
    bGreatBridge = (m.getCustomMapOption(3) == 0)
    bDeepBridge = (m.getCustomMapOption(4) == 0)

    ##################################################################################################
    # 1. Historical Rivers
    ##################################################################################################

    if accuracy == 2: # LOW ACCURACY
        # Simplified Great Rivers: West to East
        
        # Function-like logic to get jitter: 
        # dice.get(21, ...) returns 0 to 20. 
        # (0 to 20 - 10) / 200.0 results in -0.05 to +0.05.

        # Yellow River Checkpoints (Base Y: 0.75)
        y_j1 = (float(dice.get(21, "Yellow Jitter 1")) - 10.0) / 200.0
        y_j2 = (float(dice.get(21, "Yellow Jitter 2")) - 10.0) / 200.0
        y_j3 = (float(dice.get(21, "Yellow Jitter 3")) - 10.0) / 200.0
        yellow_low = [(0.1, 0.75 + y_j1), (0.4, 0.75 + y_j2), (1.0, 0.75 + y_j3)]
        
        # Huai River Checkpoints (Base Y: 0.50)
        h_j1 = (float(dice.get(21, "Huai Jitter 1")) - 10.0) / 200.0
        h_j2 = (float(dice.get(21, "Huai Jitter 2")) - 10.0) / 200.0
        h_j3 = (float(dice.get(21, "Huai Jitter 3")) - 10.0) / 200.0
        Huai_low = [(0.1, 0.5 + h_j1), (0.4, 0.5 + h_j2), (1.0, 0.5 + h_j3)]
        
        # Yangtze River Checkpoints (Base Y: 0.25)
        l_j1 = (float(dice.get(21, "Long Jitter 1")) - 10.0) / 200.0
        l_j2 = (float(dice.get(21, "Long Jitter 2")) - 10.0) / 200.0
        l_j3 = (float(dice.get(21, "Long Jitter 3")) - 10.0) / 200.0
        yangtze_low = [(0.1, 0.25 + l_j1), (0.4, 0.25 + l_j2), (1.0, 0.25 + l_j3)]
        
        if great_is_waterway:
            waterways.build(yellow_low, meander=0.15, bridge_spacing=4, bBridgesEnabled=bGreatBridge)
            waterways.build(Huai_low, meander=0.15, bridge_spacing=4, bBridgesEnabled=bGreatBridge)
            waterways.build(yangtze_low, meander=0.15, bridge_spacing=4, bBridgesEnabled=bGreatBridge)
        else:
            rivers.build(yellow_low, meander=0.2)
            rivers.build(Huai_low, meander=0.2)
            rivers.build(yangtze_low, meander=0.2)

    else:  # MEDIUM OR HIGH
        ###################
        # 1. Great Rivers
        ###################

        # YELLOW RIVER - Xian to Mouth
        yellow = [
            (0.343, 0.5),   # Xi'an Junction
            (0.515, 0.513), # Zhengzhou
            (0.73, 0.73)    # Mouth
        ]
        if great_is_waterway:
            waterways.build(yellow, meander=0.2, bridge_spacing=4, bBridgesEnabled=bGreatBridge)
        else:
            rivers.build(yellow, meander=0.2)
        
        # YANGTZE RIVER - Chongqing to Mouth
        Yangtze_coords = [
            (0.18, 0.23),   # Chongqing
            (0.233, 0.294), # 
            (0.43, 0.2), # Dongting lake
            (0.538, 0.261), # Wuhan
            (0.756, 0.358), # Nanjing
            (0.932, 0.342)  # Shanghai Mouth
        ]
        if great_is_waterway:
            waterways.build(Yangtze_coords, meander=0.12, bridge_spacing=5, bBridgesEnabled=bGreatBridge)
        else:
            rivers.build(Yangtze_coords, meander=0.12)
        
        ###################
        # 2. Deep Rivers
        ###################
        
        # HUAI RIVER
        huai = [
            (0.59, 0.41), # source
            (0.83, 0.53)  # mouth
        ]
        if deep_is_waterway:
            waterways.build(huai, meander=0.1, bridge_spacing=4, bBridgesEnabled=bDeepBridge)
        else:
            rivers.build(huai, meander=0.1)
        
        # Han River -> Yangtze
        han = [
            (0.24, 0.41),   # Source
            (0.41, 0.38),   # Xiangyang
            (0.538, 0.24)   # Wuhan Junction
        ]
        if deep_is_waterway:
            waterways.build(han, meander=0.1, bridge_spacing=4, bBridgesEnabled=bDeepBridge)
        else:
            rivers.build(han, meander=0.1)
        
        ###################
        # 3. Lesser Rivers and Tributaries
        ###################
        if lesser_enabled:
            # Wei River -> Yellow River
            wei = [(0.2, 0.499), (0.4, 0.5)]
            rivers.build(wei, meander=0.1)

            # YELLOW RIVER North Bend
            yellow_north = [
                (0.015, 0.648), (0.109, 0.662), (0.194, 0.86), (0.353, 0.844), 
                (0.343, 0.475)
            ]
            rivers.build(yellow_north, meander=0.2)
            
            # Xiang River -> Yangtze
            xiang = [(0.42, 0.02), (0.45, 0.55)]
            rivers.build(xiang, meander=0.2)
            
            # Gan River -> Yangtze
            gan = [(0.62, 0.04), (0.64, 0.55)]
            rivers.build(gan, meander=0.2)

            # Rest of Yangzte River -> Yangtze
            yangtze_remainder = [(0.04, 0.11), (0.23, 0.25)]
            rivers.build(yangtze_remainder, meander=0.1)
            
            # Jialing River -> Yangtze
            jialing = [(0.11, 0.46), (0.2, 0.20)]
            rivers.build(jialing, meander=0.1)
            
            # Min River -> Yangtze
            Min = [(0.03, 0.45), (0.17, 0.11)]
            rivers.build(Min, meander=0.1)
            
            # Liao River (Manchuria)
            Liao = [(0.99, 0.99), (0.87, 0.86)]
            rivers.build(Liao, meander=0.3)
            
            # Hai river basin (Beijing)
            Hai = [(0.57, 0.85), (0.75, 0.76)]
            rivers.build(Hai, meander=0.3)

    ##############################
    # 4. Standard River Generation
    ##############################

    if lesser_enabled:
        rand_river_density = 0.2
    elif accuracy < 2: # Med/High with lesser disabled
        rand_river_density = 0.6
    else: # Low accuracy
        rand_river_density = 0.5
    
    riverGen = RiverGenerator(river_density=rand_river_density)
    riverGen.seedRivers()

    return None

# -----------------------------------------------------------------------------
# Starting plot
# -----------------------------------------------------------------------------

_START_PLOT_MAP = None

def minStartingDistanceModifier():
    return 15

def findStartingPlot(argsList):
    [playerID] = argsList
    global _START_PLOT_MAP

    if _START_PLOT_MAP is None:
        _START_PLOT_MAP = _assign_all_starting_plots()

    return _START_PLOT_MAP.get(playerID, -1)

def _is_real_coast(pPlot, min_water_size=5):
    """
    Checks if a land plot is adjacent to a water body of at least min_water_size.
    This prevents players from being 'Coastal' next to a 1-tile desert pond.
    """
    if pPlot.isWater(): return False
    map = CyMap()
    # Check all 8 directions (including diagonals) for ocean-sized water
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0: continue
            adj = map.plot(pPlot.getX() + dx, pPlot.getY() + dy)
            if adj and not adj.isNone():
                if adj.isWater():
                    area = adj.area()
                    if area and area.getNumTiles() >= min_water_size:
                        return True
    return False

def _synced_shuffle(dice, lst):
    result = lst[:]
    for i in range(len(result) - 1, 0, -1):
        j = dice.get(i + 1, "Synced Shuffle")
        result[i], result[j] = result[j], result[i]
    return result

def _find_plot_in_rect(rect, region_name, assigned_coords, min_landmass=4, bPreferCoast=False, bPreferRiver=False):
    """
    Return a plot index of a land tile inside the rectangle.
    rect format: (cX, cY, width, height)
    """
    map = CyMap()
    dice = CyGlobalContext().getGame().getMapRand()
    iW, iH = map.getGridWidth(), map.getGridHeight()

    cX, cY, width, height = rect
    west_x = max(0, int(iW * (cX - (width / 2.0))))
    east_x = min(iW - 1, int(iW * (cX + (width / 2.0))))
    south_y = max(0, int(iH * (cY - (height / 2.0))))
    north_y = min(iH - 1, int(iH * (cY + (height / 2.0))))

    # Determine dynamic minimum distance based on map size
    min_dist = 6
    if map.getWorldSize() >= WorldSizeTypes.WORLDSIZE_LARGE:
        min_dist = 9

    # Step 1: Find all valid land plots in the rectangle
    base_eligible = []
    for x in range(west_x, east_x + 1):
        for y in range(south_y, north_y + 1):
            pPlot = map.plot(x, y)
            if pPlot and not pPlot.isWater() and not pPlot.isPeak():
                area = pPlot.area()
                if area and area.getNumTiles() >= min_landmass:
                    base_eligible.append(pPlot)
    
    if not base_eligible: return -1

    # Step 2: Filter for Distance Safety (Best Effort)
    safe_eligible = []
    for pPlot in base_eligible:
        is_safe = True
        for (ax, ay) in assigned_coords:
            # plotDistance is the Civ4 standard for circular radius
            if plotDistance(pPlot.getX(), pPlot.getY(), ax, ay) < min_dist:
                is_safe = False
                break
        if is_safe:
            safe_eligible.append(pPlot)
            
    # If we found safe plots, they become our new candidates. 
    # If not, we use the original list (ignoring distance).
    if len(safe_eligible) > 0:
        candidates = safe_eligible
    else:
        candidates = base_eligible

    # Step 3: Apply Coast Preference
    if bPreferCoast:
        coastal_eligible = []
        for pPlot in candidates:
            if _is_real_coast(pPlot, 5):
                coastal_eligible.append(pPlot)
        if len(coastal_eligible) > 0:
            candidates = coastal_eligible

    # Step 4: Apply River Preference
    if bPreferRiver:
        river_eligible = []
        for pPlot in candidates:
            if pPlot.isRiver():
                river_eligible.append(pPlot)
        if len(river_eligible) > 0:
            candidates = river_eligible

    # Step 5: Final Selection
    idx = dice.get(len(candidates), "Historical start: %s" % region_name)
    target_plot = candidates[idx]
    return map.plotNum(target_plot.getX(), target_plot.getY())

def _fallback_start_placement(playerID, existing_coords):
    map = CyMap()
    gc = CyGlobalContext()
    dice = gc.getGame().getMapRand()
    player = gc.getPlayer(playerID)
    player.AI_updateFoundValues(True)

    COASTAL_START_BIAS = 1.35 # Increased slightly

    # Only consider the largest landmass for fallback players
    best_area = map.findBiggestArea(False)
    if not best_area: return -1

    iW, iH = map.getGridWidth(), map.getGridHeight()
    min_dist = 15
    if map.getWorldSize() >= WorldSizeTypes.WORLDSIZE_LARGE: min_dist = 20

    candidates = []
    for x in range(iW):
        for y in range(iH):
            pPlot = map.plot(x, y)
            
            # HARD CHECK: No Water, No Peaks, must be on Biggest Area
            if not pPlot or pPlot.isWater() or pPlot.isPeak(): continue
            if pPlot.getArea() != best_area.getID(): continue

            is_too_close = False
            for (ax, ay) in existing_coords:
                if (abs(x - ax) + abs(y - ay)) < min_dist:
                    is_too_close = True
                    break
            if is_too_close: continue

            val = pPlot.getFoundValue(playerID)
            if val > 0:
                # Use the new "Real Coast" check (adjacent to water body >= 5 tiles)
                if _is_real_coast(pPlot, 5):
                    val *= COASTAL_START_BIAS
                candidates.append((val, map.plotNum(x, y)))

    if not candidates:
        # Final emergency fallback if the logic above is too restrictive
        return CvMapGeneratorUtil.findStartingPlot(playerID)

    candidates.sort(key=lambda item: -item[0])
    num_best_choices = min(5, len(candidates))
    return candidates[dice.get(num_best_choices, "Fallback Start Choice")][1]

def _add_spawn_signs(spawn_dict):
    """Adds map signs to the center of each historical spawn region."""
    m = CyMap()
    engine = CyEngine()
    iW = m.getGridWidth()
    iH = m.getGridHeight()
    
    # In Python 2.4, iterating over keys is the safest method
    for name in spawn_dict.keys():
        data = spawn_dict[name]
        cx = data[0]
        cy = data[1]
        
        # Convert fractional center to plot coordinates
        iX = int(iW * cx)
        iY = int(iH * cy)
        
        pPlot = m.plot(iX, iY)
        if pPlot:
            if not pPlot.isNone():
                # -1 makes the sign visible to all players
                # engine.addSign(pPlot, -1, "Spawn: " + str(name))
                engine.addSign(pPlot, -1, str(name))

# Run Starting Plot Assignments
def _assign_all_starting_plots():
    print "PY: Assigning all starting plots..."
    map = CyMap()
    gc = CyGlobalContext()
    dice = gc.getGame().getMapRand()
    # Force a recalculation of areas to ensure 'isWater' and 'area size' are accurate
    map.recalculateAreas()
    
    start_option = map.getCustomMapOption(8)

    final_assignments = {} 
    assigned_coords = []   
    used_regions = set()
    unassigned_players = []

    # Format: (cX, cY, width, height, bPreferCoast, bPreferRiver)
    SPAWN_REGIONS = {
        # Primary
        "Zhou":    (0.463, 0.443, 0.152, 0.115, False,  False),
        "Qin":     (0.229, 0.495, 0.168, 0.08,  False, True),
        "Chu":     (0.436, 0.214, 0.2,   0.133, True,  True),
        "Jin":     (0.446, 0.609, 0.156, 0.147, False, False),
        "Qi":      (0.752, 0.662, 0.157, 0.127, True,  True),
        "Wei":     (0.863, 0.36,  0.185, 0.099, True,  True),
        # Secondary
        "Song":    (0.678, 0.476, 0.135, 0.095, False, True),
        "Yue":     (0.847, 0.163, 0.181, 0.12,  True, False),
        "Yan":     (0.771, 0.832, 0.226, 0.168, True,  False),
        "Shu":     (0.137, 0.238, 0.205, 0.202, False, True)
    }

    primary_regions = [
        "Zhou",
        "Qin",
        "Chu",
        "Jin",
        "Qi",
        "Wei",
        ]
    secondary_regions = ["Song", "Yue", "Yan", "Shu"]
    tertiary_regions  = []

    civ_mapping = {
        # "CIVILIZATION_CHINA":      "Qin",
    }

    all_players = []
    for i in range(gc.getMAX_CIV_PLAYERS()):
        player = gc.getPlayer(i)
        if player.isEverAlive():
            all_players.append(i)
    
    # --- PHASE 1: Fixed Assignments ---
    if start_option == 1:
        # Call this here to place Debug signs on the map
        _add_spawn_signs(SPAWN_REGIONS)
        
        for playerID in all_players:
            civ_str = gc.getCivilizationInfo(gc.getPlayer(playerID).getCivilizationType()).getType()
            region_name = civ_mapping.get(civ_str)
            
            if region_name and region_name not in used_regions:
                data = SPAWN_REGIONS[region_name]
                # Center-based rect: (cX, cY, w, h)
                rect = (data[0], data[1], data[2], data[3])
                plot_index = _find_plot_in_rect(rect, "Fixed: " + region_name, assigned_coords, 4, data[4], data[5])
                
                if plot_index != -1:
                    final_assignments[playerID] = plot_index
                    print "MAP DEBUG: Fixed Start - %s assigned to %s" % (civ_str, region_name)
                    p = map.plotByIndex(plot_index)
                    assigned_coords.append((p.getX(), p.getY()))
                    used_regions.add(region_name)
                    continue 
            unassigned_players.append(playerID)
    else:
        unassigned_players = all_players

    # --- PHASE 2: Prioritized Regional Shuffle ---
    if start_option == 1 and unassigned_players:
        print "MAP DEBUG: Attempting prioritized historical region assignment"
        unassigned_players = _synced_shuffle(dice, unassigned_players)
        
        p_avail = []
        for r in primary_regions:
            if r not in used_regions: p_avail.append(r)
        s_avail = []
        for r in secondary_regions:
            if r not in used_regions: s_avail.append(r)
            
        available_regions = _synced_shuffle(dice, p_avail) + _synced_shuffle(dice, s_avail)
        
        still_unassigned = []
        for playerID in unassigned_players:
            civ_str = gc.getCivilizationInfo(gc.getPlayer(playerID).getCivilizationType()).getType()
            if available_regions:
                fallback_region = available_regions.pop(0)
                data = SPAWN_REGIONS[fallback_region]
                rect = (data[0], data[1], data[2], data[3])
                plot_index = _find_plot_in_rect(rect, "Region-Shuffle: " + fallback_region, assigned_coords, 4, data[4], data[5])
                if plot_index != -1:
                    final_assignments[playerID] = plot_index
                    print "MAP DEBUG: Region-Shuffle - %s assigned to %s" % (civ_str, fallback_region)
                    p = map.plotByIndex(plot_index)
                    assigned_coords.append((p.getX(), p.getY()))
                else:
                    still_unassigned.append(playerID)
            else:
                still_unassigned.append(playerID)
        unassigned_players = still_unassigned

    # --- PHASE 3: Generic Fallback ---
    if unassigned_players:
        for playerID in unassigned_players:
            plot_index = _fallback_start_placement(playerID, assigned_coords)
            if plot_index != -1:
                final_assignments[playerID] = plot_index
                civ_str = gc.getCivilizationInfo(gc.getPlayer(playerID).getCivilizationType()).getType()
                p = map.plotByIndex(plot_index)
                print "MAP DEBUG: Generic Fallback - %s assigned to (%d, %d)" % (civ_str, p.getX(), p.getY())
                assigned_coords.append((p.getX(), p.getY()))
                
    return final_assignments


# -----------------------------------------------------------------------------
# Normalization overrides
# -----------------------------------------------------------------------------
def normalizeAddRiver():
    return None

def normalizeRemovePeaks():
    """
    Remove peaks only from the 1-tile radius of each player's starting plot.
    This overrides the default peak removal that could strip too many peaks.
    """
    map = CyMap()
    gc = CyGlobalContext()
    iW = map.getGridWidth()
    iH = map.getGridHeight()

    # Collect all starting plots
    starts = []
    for i in range(gc.getMAX_CIV_PLAYERS()):
        player = gc.getPlayer(i)
        if player.isEverAlive():
            start_plot = player.getStartingPlot()
            if start_plot:
                starts.append((start_plot.getX(), start_plot.getY()))

    # For each start, look at plots within Chebyshev distance <= 1 (3x3 area)
    for sx, sy in starts:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x = sx + dx
                y = sy + dy
                if 0 <= x < iW and 0 <= y < iH:
                    pPlot = map.plot(x, y)
                    if pPlot.getPlotType() == PlotTypes.PLOT_PEAK:
                        # Convert to hills
                        pPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)

def normalizeAddGoodTerrain():
    return None

def normalizeRemoveBadTerrain():
    return None

def normalizeRemoveBadFeatures():
    return None

def normalizeAddFoodBonuses():
    return None

def normalizeAddExtras():
    #CyPythonMgr().allowDefaultImpl() # disable default nomalizer
    addCustomResources() # custom Resource Generator

# -----------------------------------------------------------------------------
# Custom resource addition – Main entry point for all  resource handling
# -----------------------------------------------------------------------------

def addCustomResources():
    m = CyMap()
    gc = CyGlobalContext()
    dice = gc.getGame().getMapRand()
    iW = m.getGridWidth()
    iH = m.getGridHeight()
    rm = ResourceManager(m, gc, dice, iW, iH)
    
    # Custom Options
    food_count = m.getCustomMapOption(0) # 0, 1, or 2
    historical_resources = (m.getCustomMapOption(1) == 0)
    ivory_opt = m.getCustomMapOption(2)
    

    ivory_limit = 0.85 # Hebei
    if ivory_opt == 1: ivory_limit = 0.70 # Shandong
    if ivory_opt == 2: ivory_limit = 0.50 # Huai
    if ivory_opt == 3: ivory_limit = 0.35 # Yangtze
        
    
    # Region-specific resources
    region_specs = [
            {
                "name": "Ivory_Hebei",
                "rect": (0.736, 0.616, 0.383, 0.177),
                "bonuses": [
                    ("BONUS_IVORY", 1, False),
                ]
            },
            {
                "name": "Ivory_Huai",
                "rect": (0.74, 0.465, 0.33, 0.125),
                "bonuses": [
                    ("BONUS_IVORY", 1, False),
                ]
            },
            {
                "name": "Ivory_Yangtze-Mouth",
                "rect": (0.831, 0.199, 0.216, 0.289),
                "bonuses": [
                    ("BONUS_IVORY", 1, False),
                ]
            },
            {
                "name": "Ivory_Yangtze-Lakes",
                "rect": (0.457, 0.245, 0.235, 0.196),
                "bonuses": [
                    ("BONUS_IVORY", 1, False),
                ]
            },
            {
                "name": "Ivory_Sichuan",
                "rect": (0.157, 0.173, 0.216, 0.238),
                "bonuses": [
                    ("BONUS_IVORY", 1, False),
                ]
            },
        ]
    
    rm.add_region_specific(region_specs, force_placement=True)

    swap_rules = [
        ("BONUS_IVORY", None, ivory_limit), # Remove Ivory NORTH of limit
    ]
    if historical_resources:
        swap_rules.append(("BONUS_CORN", "BONUS_WHEAT")) # Swap corn for wheat

    rm.swap_resources(swap_rules)
    

    # 3. Strategic resources
    strategic_list = ["BONUS_COPPER", "BONUS_IRON", "BONUS_HORSE"]
    rm.place_bonus_in_radius(strategic_list, radius=5)

    # 4. Food resources
    food_list = ["BONUS_WHEAT", "BONUS_RICE", "BONUS_COW", "BONUS_SHEEP", "BONUS_PIG", "BONUS_DEER", "BONUS_BANANA", "BONUS_SUGAR"]
    rm.place_food_bonus_in_BFC(food_list, count=food_count, check_existence=True)

class ResourceManager:
    """Manages custom resource placement for the Mediterranean map script."""
    def __init__(self, map, gc, dice, iW, iH):
        self.map = map
        self.gc = gc
        self.dice = dice
        self.iW = iW
        self.iH = iH
        self._cache = {}   
        
        self.world_size = self.map.getWorldSize()
        self.size_multiplier = {
            WorldSizeTypes.WORLDSIZE_DUEL:     0.5,
            WorldSizeTypes.WORLDSIZE_TINY:     0.5,
            WorldSizeTypes.WORLDSIZE_SMALL:    1,
            WorldSizeTypes.WORLDSIZE_STANDARD: 1,
            WorldSizeTypes.WORLDSIZE_LARGE:    1.34,
            WorldSizeTypes.WORLDSIZE_HUGE:     1.5,
        }

    def _bonus_id(self, name):
        if name in self._cache: return self._cache[name]
        bid = self.gc.getInfoTypeForString(name)
        self._cache[name] = bid
        return bid

    def _is_bonus_appropriate_for_plot(self, bonus_id, pPlot):
        """
        Checks if the bonus is physically compatible with the plot's 
        terrain, topography, and feature, ignoring proximity and latitude.
        """
        info = self.gc.getBonusInfo(bonus_id)
        
        # 1. Check Topography (Hills vs Flat)
        if pPlot.isHills():
            if not info.isHills(): return False
        else:
            if not info.isFlatlands(): return False
            
        # 2. Check Terrain
        if not info.isTerrain(pPlot.getTerrainType()):
            return False
            
        # 3. Check Feature
        iFeature = pPlot.getFeatureType()
        if iFeature != -1:
            if not info.isFeature(iFeature):
                # Special case: If it's a feature we are willing to clear (Forest/Jungle)
                # and the bonus is valid on the underlying terrain, we count it as 'appropriate'
                # because our placement logic handles the clearing.
                iFloodplains = self.gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
                if iFeature == iFloodplains: return False # Floodplains usually strictly defined in XML
                
                # If the bonus can't exist with the feature AND we aren't allowed to clear it, return False
                # But for your script, we usually assume we can clear Forest/Jungle for a Tier 1 match.
                if not info.isTerrain(pPlot.getTerrainType()):
                    return False

        return True
    
    def place_food_bonus_in_BFC(self, bonus_list, count=1, check_existence=False):
        """
        Tiered placement logic for LAND starting resources.
        1. Natural Fit: Shuffles bonuses and finds a tile that matches terrain requirements.
        2. Emergency: Terraforms a foodless tile to Plains Flat and picks a valid bonus.
        """
        ids = []
        for b in bonus_list:
            ids.append(self._bonus_id(b))

        iPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
        iDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
        iFloodplains = self.gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")

        players = []
        for i in range(self.gc.getMAX_CIV_PLAYERS()):
            player = self.gc.getPlayer(i)
            if player.isEverAlive():
                pStart = player.getStartingPlot()
                if pStart and not pStart.isNone():
                    players.append((player.getID(), pStart.getX(), pStart.getY()))

        for (pid, sx, sy) in players:
            # 1. Define the Big Fat Cross (21 tiles)
            bfc_offsets = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0: continue 
                    if abs(dx) == 2 and abs(dy) == 2: continue 
                    bfc_offsets.append((dx, dy))

            # 2. Count existing resources from the list in the BFC (Exclude the center tile)
            existing_count = 0
            if check_existence:
                for dx, dy in bfc_offsets:
                    nx, ny = sx + dx, sy + dy
                    if 0 <= nx < self.iW and 0 <= ny < self.iH:
                        pPlot = self.map.plot(nx, ny)
                        if pPlot.isStartingPlot(): continue
                        if pPlot.getBonusType(-1) in ids:
                            existing_count += 1
            
            needed = count - existing_count
            
            # 3. Placement Loop: Run for every bonus still required
            for i in range(needed):
                # Shuffle the full list for every individual placement attempt
                shuffled_ids = _synced_shuffle(self.dice, ids[:])
                placed_successfully = False

                # --- TIER 1: NATURAL FIT ---
                # We iterate through the shuffled bonuses. If Bonus A doesn't fit 
                # anywhere in the BFC, we move to Bonus B.
                for chosen_id in shuffled_ids:
                    tier1_plots = []
                    for dx, dy in bfc_offsets:
                        nx, ny = sx + dx, sy + dy
                        if 0 <= nx < self.iW and 0 <= ny < self.iH:
                            pPlot = self.map.plot(nx, ny)
                            
                            # Filter: No starts, no existing bonuses, NO WATER, NO PEAKS
                            if pPlot.isStartingPlot() or pPlot.getBonusType(-1) != -1: continue
                            if pPlot.isWater() or pPlot.isPeak(): continue

                            # Use our manual check to see if the bonus fits this tile's terrain
                            if self._is_bonus_appropriate_for_plot(chosen_id, pPlot):
                                tier1_plots.append(pPlot)

                    if len(tier1_plots) > 0:
                        target_plot = tier1_plots[self.dice.get(len(tier1_plots), "T1 Plot")]
                        
                        # Handle feature clearing (Forest/Jungle), but keep Floodplains
                        current_feature = target_plot.getFeatureType()
                        if current_feature != -1 and current_feature != iFloodplains:
                            # Clear feature if the bonus can't naturally sit on it (e.g. Wheat in Forest)
                            if not target_plot.canHaveBonus(chosen_id, True):
                                target_plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)

                        target_plot.setBonusType(chosen_id)
                        placed_successfully = True
                        break # Successfully placed a Tier 1 bonus, move to next 'needed'

                # --- TIER 2: EMERGENCY TERRAFORM ---
                # Runs only if NO bonus in the list fits naturally anywhere in the BFC
                if not placed_successfully:
                    emergency_plots = []
                    for dx, dy in bfc_offsets:
                        nx, ny = sx + dx, sy + dy
                        if 0 <= nx < self.iW and 0 <= ny < self.iH:
                            pPlot = self.map.plot(nx, ny)
                            if pPlot.isStartingPlot() or pPlot.getBonusType(-1) != -1: continue
                            if pPlot.isWater() or pPlot.isPeak(): continue

                            # Target: Desert, Hills, or Floodplains (all considered 'foodless' candidates)
                            # calculateNatureYield(Yield, Team, bIgnoreFeature)
                            if pPlot.calculateNatureYield(YieldTypes.YIELD_FOOD, TeamTypes.NO_TEAM, False) == 0:
                                emergency_plots.append(pPlot)
                            elif pPlot.getFeatureType() == iFloodplains:
                                emergency_plots.append(pPlot)

                    if len(emergency_plots) > 0:
                        target_plot = emergency_plots[self.dice.get(len(emergency_plots), "Emergency Plot")]
                        
                        # 1. Terraform to Plains Flatland
                        target_plot.setPlotType(PlotTypes.PLOT_LAND, True, True)
                        target_plot.setTerrainType(iPlains, True, True)
                        target_plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)

                        # 2. Re-filter the shuffled list for the new Plains Flatland tile
                        for b_id in shuffled_ids:
                            if self._is_bonus_appropriate_for_plot(b_id, target_plot):
                                target_plot.setBonusType(b_id)
                                placed_successfully = True
                                break
                        
                        # 3. Brute Force: If for some reason nothing fit the manual check, force the first one
                        if not placed_successfully:
                            target_plot.setBonusType(shuffled_ids[0])

    def place_bonus_in_radius(self, bonus_list, radius=5):
        """
        Generic function to ensure a resource type exists within a radius.
        Uses plotDistance to ensure diagonal resources are correctly scanned.
        """
        ids = []
        for b in bonus_list:
            ids.append(self._bonus_id(b))

        players = []
        for i in range(self.gc.getMAX_CIV_PLAYERS()):
            player = self.gc.getPlayer(i)
            if player.isEverAlive():
                pStart = player.getStartingPlot()
                if pStart and not pStart.isNone():
                    players.append((player.getID(), pStart.getX(), pStart.getY()))

        for (pid, sx, sy) in players:
            # Step 1: Scan for existing bonuses from the list
            has_bonus = False
            found_x, found_y = -1, -1
            
            # Nested loop creates a square, plotDistance trims it to a circle
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = sx + dx, sy + dy
                    
                    # Boundary check
                    if 0 <= nx < self.iW and 0 <= ny < self.iH:
                        # plotDistance is the engine's standard for circular radii
                        if plotDistance(sx, sy, nx, ny) <= radius:
                            pPlot = self.map.plot(nx, ny)
                            # Use TeamTypes.NO_TEAM to see all placed bonuses
                            if pPlot.getBonusType(TeamTypes.NO_TEAM) in ids:
                                has_bonus = True
                                found_x, found_y = nx, ny
                                break
                if has_bonus: break
            
            if has_bonus:
                # DEBUG: Place a sign on the EXISTING resource that triggered the skip
                # This helps you verify that the Horse 3 tiles away was actually detected.
                # CyEngine().addSign(self.map.plot(found_x, found_y), -1, "DEBUG: Found existing for P%d" % pid)
                print "MAP DEBUG: Player %d skipped. Found existing bonus at (%d, %d)" % (pid, found_x, found_y)
                continue

            # Step 2: Placement (Same logic as before, but using plotDistance for consistency)
            shuffled_ids = _synced_shuffle(self.dice, ids[:])
            placed_successfully = False
            target_plot = None
            final_id = -1

            # TIER 1: Natural Fit
            for chosen_id in shuffled_ids:
                tier1_plots = []
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        nx, ny = sx + dx, sy + dy
                        if 0 <= nx < self.iW and 0 <= ny < self.iH:
                            if plotDistance(sx, sy, nx, ny) <= radius:
                                pPlot = self.map.plot(nx, ny)
                                if pPlot.isStartingPlot() or pPlot.getBonusType(-1) != -1: continue
                                if pPlot.isWater() or pPlot.isPeak(): continue

                                if self._is_bonus_appropriate_for_plot(chosen_id, pPlot):
                                    tier1_plots.append(pPlot)

                if len(tier1_plots) > 0:
                    target_plot = tier1_plots[self.dice.get(len(tier1_plots), "Radius T1")]
                    final_id = chosen_id
                    placed_successfully = True
                    break 

            # TIER 2: Emergency (Any Land)
            if not placed_successfully:
                emergency_plots = []
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        nx, ny = sx + dx, sy + dy
                        if 0 <= nx < self.iW and 0 <= ny < self.iH:
                            if plotDistance(sx, sy, nx, ny) <= radius:
                                pPlot = self.map.plot(nx, ny)
                                if not pPlot.isWater() and not pPlot.isPeak() and not pPlot.isStartingPlot():
                                    if pPlot.getBonusType(-1) == -1:
                                        emergency_plots.append(pPlot)

                if len(emergency_plots) > 0:
                    target_plot = emergency_plots[self.dice.get(len(emergency_plots), "Radius Emergency")]
                    final_id = shuffled_ids[0]
                    placed_successfully = True

            if placed_successfully and target_plot:
                target_plot.setBonusType(final_id)
                
                # Visual Marker for newly added resources
                bonus_name = self.gc.getBonusInfo(final_id).getType()
                # CyEngine().addSign(target_plot, -1, "DEBUG: Added " + bonus_name)
                print "MAP DEBUG: Placed %s for Player %d at (%d, %d)" % (bonus_name, pid, target_plot.getX(), target_plot.getY())


    def swap_resources(self, swap_rules, clear_feature=False):
        """
        Swaps resources globally. Now explicitly skips starting plots to 
        prevent accidental changes to the capital's immediate tile.
        """
        for rule in swap_rules:
            old_name = rule[0]
            new_name = rule[1]
            if len(rule) > 2:
                min_y_fraction = rule[2]
            else:
                min_y_fraction = 0.0
            
            old_id = self._bonus_id(old_name)
            y_thresh = int(self.iH * min_y_fraction)

            for i in range(self.map.numPlots()):
                pPlot = self.map.plotByIndex(i)
                # EXCLUDE starting plots from global swaps
                if pPlot.isStartingPlot(): continue
                
                if pPlot.getY() >= y_thresh and pPlot.getBonusType(-1) == old_id:
                    if new_name:
                        pPlot.setBonusType(self._bonus_id(new_name))
                    else:
                        pPlot.setBonusType(-1)
                    
                    if clear_feature:
                        pPlot.setFeatureType(FeatureTypes.NO_FEATURE, -1)

    def add_region_specific(self, region_specs, force_placement=True):
        """
        Place bonuses in specified regions using center-based coordinates. 
        region["rect"] format: (cX, cY, width, height)
        """
        multiplier = self.size_multiplier[self.world_size]
        
        for region in region_specs:
            # Unpack center-based coordinates
            cX, cY, width, height = region["rect"]
            
            # Calculate pixel-grid boundaries from center
            west_x = int(self.iW * (cX - (width / 2.0)))
            east_x = int(self.iW * (cX + (width / 2.0)))
            south_y = int(self.iH * (cY - (height / 2.0)))
            north_y = int(self.iH * (cY + (height / 2.0)))

            # Clamp to map edges
            iWest = max(0, west_x)
            iEast = min(self.iW - 1, east_x)
            iSouth = max(0, south_y)
            iNorth = min(self.iH - 1, north_y)

            for bonus_entry in region["bonuses"]:
                scaled_count = int(bonus_entry[1] * multiplier)
                if scaled_count == 0: 
                    continue
                    
                bonus_id = self._bonus_id(bonus_entry[0])
                
                # Manual check for optional 'clear_feature' argument (No Ternary)
                if len(bonus_entry) > 2:
                    clear_feat = bonus_entry[2]
                else:
                    clear_feat = False

                eligible = []
                fallback = []
                
                # Scan the calculated rectangle
                for x in range(iWest, iEast + 1):
                    for y in range(iSouth, iNorth + 1):
                        pPlot = self.map.plot(x, y)
                        
                        # EXCLUDE starting plots from region-specific placement
                        if pPlot.isStartingPlot(): 
                            continue
                        
                        if pPlot.getBonusType(-1) == -1:
                            if pPlot.canHaveBonus(bonus_id, True):
                                eligible.append((x, y))
                            elif force_placement:
                                if not pPlot.isWater() and pPlot.getPlotType() != PlotTypes.PLOT_PEAK:
                                    fallback.append((x, y))

                # Placement Loop
                placed = 0
                for _ in range(scaled_count):
                    choice = None
                    if eligible:
                        choice = eligible.pop(self.dice.get(len(eligible), "Region Bonus"))
                    elif fallback:
                        choice = fallback.pop(self.dice.get(len(fallback), "Fallback Bonus"))
                    
                    if choice:
                        p = self.map.plot(choice[0], choice[1])
                        p.setBonusType(bonus_id)
                        if clear_feat:
                            p.setFeatureType(FeatureTypes.NO_FEATURE, -1)
                        placed += 1