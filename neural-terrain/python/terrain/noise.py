import random
import math
from typing import List

class PerlinNoise:
    """2D Perlin noise generator using Ken Perlin's 2002 improved noise algorithm."""
    
    def __init__(self, seed: int = 0):
        """
        Initialize with a seed for reproducibility.
        
        Args:
            seed (int): The seed used to shuffle the permutation table.
        """
        self.p = list(range(256))
        # Use a local Random instance to avoid affecting global state
        rng = random.Random(seed)
        rng.shuffle(self.p)
        # Double the permutation table to avoid overflow and simplify indexing
        self.p = self.p * 2

    def _fade(self, t: float) -> float:
        """Fade function: f(t) = 6t^5 - 15t^4 + 10t^3."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, t: float, a: float, b: float) -> float:
        """Linear interpolation."""
        return a + t * (b - a)

    def _grad(self, hash: int, x: float, y: float) -> float:
        """
        Calculate the dot product of a randomly chosen gradient vector and the distance vector.
        Using the 2002 improved noise gradient selection logic (adapted for 2D).
        """
        h = hash & 15
        # Convert low 4 bits of hash code into 8 gradient directions:
        # (1,1), (-1,1), (1,-1), (-1,-1), (1,0), (-1,0), (0,1), (0,-1)
        if h == 0: return x + y
        if h == 1: return -x + y
        if h == 2: return x - y
        if h == 3: return -x - y
        if h == 4: return x + 0.0 # x direction
        if h == 5: return -x + 0.0
        if h == 6: return 0.0 + y # y direction
        if h == 7: return 0.0 - y
        # Duplicate for 8-15
        if h == 8: return x + y
        if h == 9: return -x + y
        if h == 10: return x - y
        if h == 11: return -x - y
        if h == 12: return x
        if h == 13: return -x
        if h == 14: return y
        return -y

    def noise(self, x: float, y: float) -> float:
        """
        Generate Perlin noise value at (x, y).
        Returns a float in the range [-1, 1].
        """
        # Find unit square containing point
        ix = int(math.floor(x))
        iy = int(math.floor(y))
        
        # Relative x, y in unit square
        xf = x - ix
        yf = y - iy
        
        # Wrapped coordinates for permutation table
        X = ix & 255
        Y = iy & 255
        
        # Compute fade curves for x, y
        u = self._fade(xf)
        v = self._fade(yf)
        
        # Hash coordinates of the 4 square corners
        p = self.p
        A = p[X] + Y
        B = p[X + 1] + Y
        
        # Add blended results from 4 corners of the square
        # We scale by ~1.0 to fit roughly in [-1, 1]
        # In 2D with these gradients, the max value is 0.5 * sqrt(2) approx?
        # Actually, let's use a scale factor to ensure it reaches the range.
        res = self._lerp(v, 
                         self._lerp(u, self._grad(p[A], xf, yf), 
                                       self._grad(p[B], xf - 1, yf)),
                         self._lerp(u, self._grad(p[A + 1], xf, yf - 1), 
                                       self._grad(p[B + 1], xf - 1, yf - 1)))
        
        # Perlin noise typically needs a scale factor. 
        # For 2D with 8 gradients, 1.0 is usually sufficient to stay within [-1, 1]
        # but we want to use more of the range.
        return res

    def octave_noise(self, x: float, y: float, octaves: int = 6, 
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """
        Generate fractal Brownian motion (fBm) using multiple octaves.
        Returns a float approximately in [-1, 1].
        """
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            amplitude *= persistence
            frequency *= lacunarity
            
        # The prompt says: "Returns a float approximately in [-1, 1] (may slightly exceed due to octave stacking)."
        # So we don't divide by the sum of amplitudes here.
        return total

    def generate_grid(self, width: int, height: int, scale: float = 50.0,
                      octaves: int = 6, persistence: float = 0.5,
                      lacunarity: float = 2.0) -> List[List[float]]:
        """
        Generate a 2D grid of noise values.
        Returns a width×height nested list of floats, normalized to [0, 1].
        """
        # First pass: calculate values and find min/max for normalization
        temp_grid = [[0.0 for _ in range(width)] for _ in range(height)]
        min_val = float('inf')
        max_val = float('-inf')
        
        for y in range(height):
            for x in range(width):
                val = self.octave_noise(x / scale, y / scale, octaves, persistence, lacunarity)
                temp_grid[y][x] = val
                if val < min_val: min_val = val
                if val > max_val: max_val = val
        
        # Second pass: normalize to [0, 1]
        # If all values are the same, return 0.5
        range_val = max_val - min_val
        if range_val < 1e-10:
            return [[0.5 for _ in range(width)] for _ in range(height)]
            
        grid = [[(temp_grid[y][x] - min_val) / range_val for x in range(width)] for y in range(height)]
        return grid

if __name__ == "__main__":
    pn = PerlinNoise(seed=42)
    grid = pn.generate_grid(10, 10, scale=5.0)
    for row in grid:
        print(" ".join(f"{v:6.3f}" for v in row))
