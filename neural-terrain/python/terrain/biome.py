from enum import Enum
from typing import List, Tuple

class Biome(Enum):
    """Terrain biome types."""
    DEEP_OCEAN = "deep_ocean"
    OCEAN = "ocean"
    BEACH = "beach"
    SCORCHED = "scorched"
    BARE = "bare"
    TUNDRA = "tundra"
    SNOW = "snow"
    TEMPERATE_DESERT = "temperate_desert"
    SHRUBLAND = "shrubland"
    GRASSLAND = "grassland"
    TEMPERATE_FOREST = "temperate_forest"
    TEMPERATE_RAINFOREST = "temperate_rainforest"
    SUBTROPICAL_DESERT = "subtropical_desert"
    TROPICAL_SAVANNA = "tropical_savanna"
    TROPICAL_FOREST = "tropical_forest"
    TROPICAL_RAINFOREST = "tropical_rainforest"

# Color palette for rendering (RGB tuples)
BIOME_COLORS: dict[Biome, tuple[int, int, int]] = {
    Biome.DEEP_OCEAN: (30, 50, 100),
    Biome.OCEAN: (50, 80, 140),
    Biome.BEACH: (210, 200, 150),
    Biome.SCORCHED: (100, 90, 80),
    Biome.BARE: (140, 135, 125),
    Biome.TUNDRA: (180, 190, 185),
    Biome.SNOW: (240, 245, 250),
    Biome.TEMPERATE_DESERT: (200, 190, 130),
    Biome.SHRUBLAND: (140, 165, 110),
    Biome.GRASSLAND: (120, 170, 70),
    Biome.TEMPERATE_FOREST: (70, 130, 50),
    Biome.TEMPERATE_RAINFOREST: (40, 100, 50),
    Biome.SUBTROPICAL_DESERT: (215, 185, 110),
    Biome.TROPICAL_SAVANNA: (170, 180, 60),
    Biome.TROPICAL_FOREST: (50, 120, 40),
    Biome.TROPICAL_RAINFOREST: (30, 90, 45),
}

class BiomeClassifier:
    """Classifies terrain cells into biomes based on elevation, temperature, and moisture."""
    
    def __init__(self, sea_level: float = 0.35):
        """
        Initialize the classifier.
        
        Args:
            sea_level: Elevation threshold below which terrain is water (0-1 scale).
        """
        self.sea_level = sea_level
    
    def classify(self, elevation: float, moisture: float, temperature: float) -> Biome:
        """
        Classify a single cell into a biome.
        
        Args:
            elevation: Normalized elevation value in [0, 1]. 0 = lowest, 1 = highest.
            moisture: Normalized moisture value in [0, 1]. 0 = driest, 1 = wettest.
            temperature: Normalized temperature value in [0, 1]. 0 = coldest, 1 = hottest.
            
        Returns:
            A Biome enum value.
        """
        # Clamp inputs to [0, 1]
        elevation = max(0.0, min(1.0, elevation))
        moisture = max(0.0, min(1.0, moisture))
        temperature = max(0.0, min(1.0, temperature))
        
        beach_threshold = self.sea_level + 0.05
        
        if elevation < self.sea_level:
            if elevation < self.sea_level * 0.5:
                return Biome.DEEP_OCEAN
            else:
                return Biome.OCEAN
        elif elevation < beach_threshold:
            return Biome.BEACH
        else:
            # Above sea level
            if elevation > 0.85:
                # High elevation
                if temperature < 0.2:
                    return Biome.SNOW
                elif temperature < 0.4:
                    return Biome.TUNDRA
                elif moisture < 0.2:
                    return Biome.BARE
                else:
                    return Biome.SCORCHED
            elif elevation > 0.6:
                # Medium-high elevation
                if temperature < 0.3:
                    if moisture > 0.5:
                        return Biome.TUNDRA
                    else:
                        return Biome.BARE
                elif moisture < 0.2:
                    return Biome.TEMPERATE_DESERT
                elif moisture < 0.5:
                    return Biome.SHRUBLAND
                else:
                    return Biome.TEMPERATE_FOREST
            else:
                # Medium elevation
                if temperature > 0.7:
                    # Hot
                    if moisture < 0.2:
                        return Biome.SUBTROPICAL_DESERT
                    elif moisture < 0.5:
                        return Biome.TROPICAL_SAVANNA
                    elif moisture < 0.75:
                        return Biome.TROPICAL_FOREST
                    else:
                        return Biome.TROPICAL_RAINFOREST
                elif temperature > 0.4:
                    # Warm
                    if moisture < 0.2:
                        return Biome.TEMPERATE_DESERT
                    elif moisture < 0.5:
                        return Biome.GRASSLAND
                    elif moisture < 0.75:
                        return Biome.TEMPERATE_FOREST
                    else:
                        return Biome.TEMPERATE_RAINFOREST
                else:
                    # Cold
                    if moisture < 0.3:
                        return Biome.BARE
                    elif moisture < 0.6:
                        return Biome.SHRUBLAND
                    else:
                        return Biome.TUNDRA
    
    def classify_grid(self, elevation_map: List[List[float]],
                      moisture_map: List[List[float]],
                      temperature_map: List[List[float]]) -> List[List[Biome]]:
        """
        Classify an entire grid of terrain cells.
        
        Args:
            elevation_map: 2D grid of elevation values in [0, 1].
            moisture_map: 2D grid of moisture values in [0, 1].
            temperature_map: 2D grid of temperature values in [0, 1].
            All three grids must have the same dimensions.
            
        Returns:
            2D grid of Biome enum values, same dimensions as input.
        """
        if not elevation_map or not all(len(row) == len(elevation_map[0]) for row in elevation_map):
            raise ValueError("Elevation map must be a non-empty rectangular grid")
        
        height = len(elevation_map)
        width = len(elevation_map[0])
        
        if (len(moisture_map) != height or any(len(row) != width for row in moisture_map) or
            len(temperature_map) != height or any(len(row) != width for row in temperature_map)):
            raise ValueError("All input maps must have the same dimensions")
        
        biome_grid: List[List[Biome]] = []
        for y in range(height):
            row: List[Biome] = []
            for x in range(width):
                biome = self.classify(elevation_map[y][x], moisture_map[y][x], temperature_map[y][x])
                row.append(biome)
            biome_grid.append(row)
        return biome_grid
    
    def generate_temperature_map(self, elevation_map: List[List[float]],
                                 base_temperature: float = 0.7,
                                 elevation_cooling: float = 0.6) -> List[List[float]]:
        """
        Generate a temperature map from elevation.
        Higher elevation = colder. Temperature decreases linearly with elevation above sea level.
        Below sea level, temperature equals base_temperature.
        
        Args:
            elevation_map: 2D grid of elevation values in [0, 1].
            base_temperature: Temperature at sea level (0-1 scale).
            elevation_cooling: How much temperature drops from sea level to peak (0-1 scale).
            
        Returns:
            2D grid of temperature values in [0, 1].
        """
        if not elevation_map or not all(len(row) == len(elevation_map[0]) for row in elevation_map):
            raise ValueError("Elevation map must be a non-empty rectangular grid")
        
        height = len(elevation_map)
        width = len(elevation_map[0])
        
        temp_map: List[List[float]] = []
        land_elevation_range = max(1e-6, 1.0 - self.sea_level)  # Avoid division by zero
        
        for y in range(height):
            row: List[float] = []
            for x in range(width):
                elev = max(0.0, min(1.0, elevation_map[y][x]))
                if elev <= self.sea_level:
                    temp = base_temperature
                else:
                    normalized_height = (elev - self.sea_level) / land_elevation_range
                    temp = base_temperature - elevation_cooling * normalized_height
                temp = max(0.0, min(1.0, temp))  # Clamp to [0,1]
                row.append(temp)
            temp_map.append(row)
        return temp_map
    
    def get_color(self, biome: Biome) -> Tuple[int, int, int]:
        """Return the RGB color tuple for a given biome."""
        return BIOME_COLORS[biome]
    
    def colorize_grid(self, biome_grid: List[List[Biome]]) -> List[List[Tuple[int, int, int]]]:
        """
        Convert a biome grid to an RGB color grid for rendering.
        
        Returns:
            2D grid of (R, G, B) tuples.
        """
        if not biome_grid or not all(len(row) == len(biome_grid[0]) for row in biome_grid):
            raise ValueError("Biome grid must be a non-empty rectangular grid")
        
        return [[self.get_color(biome) for biome in row] for row in biome_grid]

if __name__ == "__main__":
    # Sample demo
    bc = BiomeClassifier()
    samples = [
        (0.2, 0.5, 0.5),  # Below sea level -> OCEAN or DEEP_OCEAN
        (0.36, 0.5, 0.5),  # Beach
        (0.9, 0.1, 0.1),   # High elevation, cold, dry -> SNOW
        (0.7, 0.6, 0.2),   # Medium-high, cold, moist -> TUNDRA
        (0.5, 0.8, 0.8),   # Medium, hot, wet -> TROPICAL_RAINFOREST
    ]
    for elev, moist, temp in samples:
        biome = bc.classify(elev, moist, temp)
        print(f"Elevation: {elev:.2f}, Moisture: {moist:.2f}, Temperature: {temp:.2f} -> {biome.value}")