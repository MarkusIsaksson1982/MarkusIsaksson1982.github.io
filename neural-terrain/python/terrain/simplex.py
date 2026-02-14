import math
import random
from typing import List

class SimplexNoise:
    """2D Simplex noise generator using the simplex (triangular) grid approach."""
    
    # Skewing and unskewing factors for 2D
    F2 = (math.sqrt(3.0) - 1.0) / 2.0
    G2 = (3.0 - math.sqrt(3.0)) / 6.0
    
    # 12 gradient vectors for 2D Simplex noise
    # These are directions to the midpoints of the edges of a cube (in 3D), 
    # but for 2D we use a set of vectors that provide good coverage.
    GRADIENTS = [
        (1, 1), (-1, 1), (1, -1), (-1, -1),
        (1, 0), (-1, 0), (1, 0), (-1, 0), # Duplicates or variations for 12
        (0, 1), (0, -1), (0, 1), (0, -1)
    ]

    def __init__(self, seed: int = 0):
        """Initialize with a seed for reproducibility."""
        self.p = list(range(256))
        rng = random.Random(seed)
        rng.shuffle(self.p)
        # Double the permutation table to avoid overflow
        self.perm = self.p * 2

    def _dot(self, g: tuple, x: float, y: float) -> float:
        """Calculate dot product of gradient vector and distance vector."""
        return g[0] * x + g[1] * y

    def noise(self, x: float, y: float) -> float:
        """
        Generate Simplex noise value at (x, y).
        Returns a float in the range [-1, 1].
        """
        # Skew the input space to determine which simplex cell we're in
        s = (x + y) * self.F2
        i = math.floor(x + s)
        j = math.floor(y + s)
        
        # Unskew the cell origin back to (x, y) space
        t = (i + j) * self.G2
        X0 = i - t
        Y0 = j - t
        
        # The distance from the cell origin
        x0 = x - X0
        y0 = y - Y0
        
        # For 2D, the simplex shape is an equilateral triangle.
        # Determine which side of the internal traversal we are on.
        if x0 > y0:
            i1, j1 = 1, 0 # Lower triangle
        else:
            i1, j1 = 0, 1 # Upper triangle
            
        # Offsets for the middle corner
        x1 = x0 - i1 + self.G2
        y1 = y0 - j1 + self.G2
        
        # Offsets for the last corner
        x2 = x0 - 1.0 + 2.0 * self.G2
        y2 = y0 - 1.0 + 2.0 * self.G2
        
        # Wrap the integer indices to [0, 255]
        ii = i & 255
        jj = j & 255
        
        # Calculate the contribution from the three corners
        n0, n1, n2 = 0.0, 0.0, 0.0
        
        # Corner 0
        t0 = 0.5 - x0*x0 - y0*y0
        if t0 > 0:
            t0 *= t0
            gi0 = self.perm[ii + self.perm[jj]] % 12
            n0 = t0 * t0 * self._dot(self.GRADIENTS[gi0], x0, y0)
            
        # Corner 1
        t1 = 0.5 - x1*x1 - y1*y1
        if t1 > 0:
            t1 *= t1
            gi1 = self.perm[ii + i1 + self.perm[jj + j1]] % 12
            n1 = t1 * t1 * self._dot(self.GRADIENTS[gi1], x1, y1)
            
        # Corner 2
        t2 = 0.5 - x2*x2 - y2*y2
        if t2 > 0:
            t2 *= t2
            gi2 = self.perm[ii + 1 + self.perm[jj + 1]] % 12
            n2 = t2 * t2 * self._dot(self.GRADIENTS[gi2], x2, y2)
            
        # Add contributions from each corner and scale the result to [-1, 1]
        # The maximum value is approximately 0.014... So we scale by 70.
        return 70.0 * (n0 + n1 + n2)

    def octave_noise(self, x: float, y: float, octaves: int = 6,
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """
        Generate fractal Brownian motion (fBm) using multiple octaves of simplex noise.
        Returns a float approximately in [-1, 1].
        """
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            amplitude *= persistence
            frequency *= lacunarity
            
        return total

    def generate_grid(self, width: int, height: int, scale: float = 50.0,
                      octaves: int = 6, persistence: float = 0.5,
                      lacunarity: float = 2.0) -> List[List[float]]:
        """
        Generate a 2D grid of simplex noise values.
        Returns a height×width nested list of floats, normalized to [0, 1].
        """
        temp_grid = [[0.0 for _ in range(width)] for _ in range(height)]
        min_val = float('inf')
        max_val = float('-inf')
        
        for y in range(height):
            for x in range(width):
                val = self.octave_noise(x / scale, y / scale, octaves, persistence, lacunarity)
                temp_grid[y][x] = val
                if val < min_val: min_val = val
                if val > max_val: max_val = val
                
        # Normalize to [0, 1]
        range_val = max_val - min_val
        if range_val < 1e-10:
            return [[0.5 for _ in range(width)] for _ in range(height)]
            
        grid = [[(temp_grid[y][x] - min_val) / range_val for x in range(width)] for y in range(height)]
        return grid

if __name__ == "__main__":
    sn = SimplexNoise(seed=42)
    # Generate and print a 10x10 grid as required
    grid = sn.generate_grid(10, 10, scale=5.0)
    for row in grid:
        print(" ".join(f"{v:6.3f}" for v in row))
