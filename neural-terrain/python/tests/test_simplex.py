import sys
import os
import math
import time
import pytest

# Add parent directory to path so we can import simplex.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terrain'))

from simplex import SimplexNoise

class TestSimplexNoiseBasic:
    def test_instantiation(self):
        sn = SimplexNoise(seed=42)
        assert sn is not None

    def test_noise_range(self):
        sn = SimplexNoise(seed=42)
        for i in range(1000):
            x, y = i * 0.123, i * 0.456
            val = sn.noise(x, y)
            assert -1.0 <= val <= 1.0, f"Value {val} outside [-1, 1] at ({x}, {y})"

    def test_determinism(self):
        sn1 = SimplexNoise(seed=123)
        sn2 = SimplexNoise(seed=123)
        for i in range(100):
            x, y = i * 0.7, i * 0.9
            assert sn1.noise(x, y) == sn2.noise(x, y)

    def test_different_seeds(self):
        sn1 = SimplexNoise(seed=123)
        sn2 = SimplexNoise(seed=456)
        diffs = 0
        for i in range(100):
            if sn1.noise(i * 0.5, i * 0.5) != sn2.noise(i * 0.5, i * 0.5):
                diffs += 1
        assert diffs > 90

class TestSimplexNoiseProperties:
    def test_continuity(self):
        sn = SimplexNoise(seed=42)
        epsilon = 0.0001
        for i in range(100):
            x, y = i * 0.33, i * 0.44
            v1 = sn.noise(x, y)
            v2 = sn.noise(x + epsilon, y)
            assert abs(v2 - v1) < 0.01

    def test_not_zero_at_integers(self):
        """Simplex noise, unlike Perlin, is typically NOT zero at integers."""
        sn = SimplexNoise(seed=42)
        non_zero_count = 0
        for i in range(1, 11):
            if abs(sn.noise(float(i), float(i))) > 0.001:
                non_zero_count += 1
        assert non_zero_count > 0

    def test_grid_normalization(self):
        sn = SimplexNoise(seed=42)
        grid = sn.generate_grid(32, 32)
        flat_grid = [val for row in grid for val in row]
        assert min(flat_grid) <= 0.01
        assert max(flat_grid) >= 0.99
        assert all(0.0 <= v <= 1.0 for v in flat_grid)

class TestSimplexNoiseOctaves:
    def test_single_octave_matches_noise(self):
        sn = SimplexNoise(seed=42)
        x, y = 10.5, 20.5
        assert abs(sn.noise(x, y) - sn.octave_noise(x, y, octaves=1)) < 1e-10

    def test_octave_variance_growth(self):
        sn = SimplexNoise(seed=42)
        x, y = 5.5, 5.5
        val1 = sn.octave_noise(x, y, octaves=1)
        val2 = sn.octave_noise(x, y, octaves=4)
        # With persistence=0.5, val2 should generally be larger in magnitude or at least different
        assert val1 != val2

if __name__ == "__main__":
    pytest.main([__file__])
