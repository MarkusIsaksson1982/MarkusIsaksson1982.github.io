"""
Test suite for Perlin noise implementation assessment.
Part of the Neural Terrain multi-model AI orchestration project.

Run with: pytest test_noise.py -v --tb=short
"""
import sys
import os
import math
import time
import pytest

# Add parent directory to path so we can import noise.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terrain'))

from noise import PerlinNoise


class TestPerlinNoiseBasic:
    """Basic functionality tests."""

    def test_instantiation_default(self):
        """Can create instance with default seed."""
        pn = PerlinNoise()
        assert pn is not None

    def test_instantiation_with_seed(self):
        """Can create instance with explicit seed."""
        pn = PerlinNoise(seed=42)
        assert pn is not None

    def test_noise_returns_float(self):
        """noise() returns a float."""
        pn = PerlinNoise(seed=0)
        result = pn.noise(0.5, 0.5)
        assert isinstance(result, float)

    def test_octave_noise_returns_float(self):
        """octave_noise() returns a float."""
        pn = PerlinNoise(seed=0)
        result = pn.octave_noise(0.5, 0.5)
        assert isinstance(result, float)

    def test_generate_grid_returns_nested_list(self):
        """generate_grid() returns a nested list of correct dimensions."""
        pn = PerlinNoise(seed=0)
        grid = pn.generate_grid(16, 16)
        assert len(grid) == 16
        assert all(len(row) == 16 for row in grid)

    def test_generate_grid_values_are_float(self):
        """Grid values are floats."""
        pn = PerlinNoise(seed=0)
        grid = pn.generate_grid(8, 8)
        assert all(isinstance(grid[y][x], float) for y in range(8) for x in range(8))


class TestPerlinNoiseRange:
    """Value range tests."""

    def test_noise_range_single_values(self):
        """noise() returns values in [-1, 1]."""
        pn = PerlinNoise(seed=42)
        for i in range(500):
            x = (i * 0.137) % 100
            y = (i * 0.291) % 100
            val = pn.noise(x, y)
            assert -1.0 <= val <= 1.0, f"noise({x}, {y}) = {val}, outside [-1, 1]"

    def test_noise_range_negative_coords(self):
        """noise() works with negative coordinates."""
        pn = PerlinNoise(seed=42)
        for i in range(100):
            x = -50 + i * 0.73
            y = -50 + i * 0.31
            val = pn.noise(x, y)
            assert -1.0 <= val <= 1.0, f"noise({x}, {y}) = {val}, outside [-1, 1]"

    def test_grid_range(self):
        """generate_grid() returns values in [0, 1]."""
        pn = PerlinNoise(seed=42)
        grid = pn.generate_grid(64, 64)
        for y in range(64):
            for x in range(64):
                assert 0.0 <= grid[y][x] <= 1.0, (
                    f"grid[{y}][{x}] = {grid[y][x]}, outside [0, 1]"
                )

    def test_noise_uses_full_range(self):
        """noise() actually uses a reasonable portion of [-1, 1], not just near 0."""
        pn = PerlinNoise(seed=42)
        values = [pn.noise(i * 0.1, i * 0.07) for i in range(1000)]
        assert max(values) > 0.3, f"Max value {max(values)} is suspiciously low"
        assert min(values) < -0.3, f"Min value {min(values)} is suspiciously high"


class TestPerlinNoiseDeterminism:
    """Determinism and reproducibility tests."""

    def test_same_seed_same_output(self):
        """Same seed produces identical results."""
        pn1 = PerlinNoise(seed=42)
        pn2 = PerlinNoise(seed=42)
        for i in range(100):
            x, y = i * 0.5, i * 0.3
            assert pn1.noise(x, y) == pn2.noise(x, y)

    def test_different_seed_different_output(self):
        """Different seeds produce different results."""
        pn1 = PerlinNoise(seed=42)
        pn2 = PerlinNoise(seed=99)
        differences = sum(
            1 for i in range(100)
            if pn1.noise(i * 0.5, i * 0.3) != pn2.noise(i * 0.5, i * 0.3)
        )
        assert differences > 80, f"Only {differences}/100 values differ between seeds"

    def test_grid_determinism(self):
        """Same parameters produce identical grids."""
        pn1 = PerlinNoise(seed=42)
        pn2 = PerlinNoise(seed=42)
        g1 = pn1.generate_grid(32, 32, scale=25.0, octaves=4)
        g2 = pn2.generate_grid(32, 32, scale=25.0, octaves=4)
        for y in range(32):
            for x in range(32):
                assert g1[y][x] == g2[y][x], f"Grids differ at [{y}][{x}]"


class TestPerlinNoiseContinuity:
    """Continuity and smoothness tests."""

    def test_continuity_small_step(self):
        """Small input changes produce small output changes (Lipschitz-like)."""
        pn = PerlinNoise(seed=42)
        epsilon = 0.001
        max_delta = 0
        for i in range(200):
            x = i * 0.37
            y = i * 0.23
            v1 = pn.noise(x, y)
            v2 = pn.noise(x + epsilon, y)
            v3 = pn.noise(x, y + epsilon)
            delta_x = abs(v2 - v1)
            delta_y = abs(v3 - v1)
            max_delta = max(max_delta, delta_x, delta_y)
        # For well-implemented Perlin noise, gradient magnitudes stay bounded
        assert max_delta < 0.01, (
            f"Max delta {max_delta} for epsilon {epsilon} — noise is discontinuous"
        )

    def test_no_grid_artifacts(self):
        """No sudden jumps at integer boundaries."""
        pn = PerlinNoise(seed=42)
        for boundary in range(1, 10):
            before = pn.noise(boundary - 0.001, 3.7)
            after = pn.noise(boundary + 0.001, 3.7)
            delta = abs(after - before)
            assert delta < 0.01, (
                f"Jump of {delta} at x={boundary} boundary — grid artifacts present"
            )

    def test_integer_coordinates_near_zero(self):
        """At integer coordinates, Perlin noise should be 0 or very near 0."""
        pn = PerlinNoise(seed=42)
        for ix in range(10):
            for iy in range(10):
                val = pn.noise(float(ix), float(iy))
                assert abs(val) < 1e-10, (
                    f"noise({ix}, {iy}) = {val}, expected ~0 at integer coords"
                )


class TestPerlinNoiseOctaves:
    """Octave/fBm tests."""

    def test_single_octave_matches_noise(self):
        """1 octave of octave_noise should match base noise."""
        pn = PerlinNoise(seed=42)
        for i in range(50):
            x, y = i * 0.3, i * 0.7
            single = pn.noise(x, y)
            octaved = pn.octave_noise(x, y, octaves=1)
            assert abs(single - octaved) < 1e-10, (
                f"1-octave fBm differs from base noise at ({x},{y})"
            )

    def test_more_octaves_more_detail(self):
        """More octaves should increase variance (more detail)."""
        pn = PerlinNoise(seed=42)
        coords = [(i * 0.1, i * 0.07) for i in range(500)]
        var_1 = self._variance([pn.octave_noise(x, y, octaves=1) for x, y in coords])
        var_4 = self._variance([pn.octave_noise(x, y, octaves=4) for x, y in coords])
        assert var_4 >= var_1 * 0.9, (
            f"4-octave variance ({var_4}) much less than 1-octave ({var_1})"
        )

    def test_persistence_effect(self):
        """Lower persistence should reduce high-frequency contribution."""
        pn = PerlinNoise(seed=42)
        coords = [(i * 0.1, i * 0.07) for i in range(500)]
        var_high = self._variance(
            [pn.octave_noise(x, y, octaves=6, persistence=0.8) for x, y in coords]
        )
        var_low = self._variance(
            [pn.octave_noise(x, y, octaves=6, persistence=0.2) for x, y in coords]
        )
        assert var_high > var_low, "Higher persistence should produce more variance"

    @staticmethod
    def _variance(values):
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)


class TestPerlinNoisePerformance:
    """Performance tests."""

    def test_grid_generation_speed(self):
        """512x512 grid should generate in under 10 seconds (generous for pure Python)."""
        pn = PerlinNoise(seed=42)
        start = time.time()
        grid = pn.generate_grid(512, 512, octaves=4)
        elapsed = time.time() - start
        assert elapsed < 10.0, f"512x512 grid took {elapsed:.1f}s (limit: 10s)"
        assert len(grid) == 512
        assert len(grid[0]) == 512


class TestPerlinNoiseEdgeCases:
    """Edge cases and robustness."""

    def test_zero_coordinates(self):
        """noise(0, 0) should return 0."""
        pn = PerlinNoise(seed=42)
        assert abs(pn.noise(0.0, 0.0)) < 1e-10

    def test_large_coordinates(self):
        """Works with large coordinate values."""
        pn = PerlinNoise(seed=42)
        val = pn.noise(10000.5, 20000.5)
        assert isinstance(val, float)
        assert -1.0 <= val <= 1.0

    def test_very_small_coordinates(self):
        """Works with very small fractional coordinates."""
        pn = PerlinNoise(seed=42)
        val = pn.noise(0.0001, 0.0001)
        assert isinstance(val, float)
        assert -1.0 <= val <= 1.0

    def test_grid_small(self):
        """Can generate a 1x1 grid."""
        pn = PerlinNoise(seed=42)
        grid = pn.generate_grid(1, 1)
        assert len(grid) == 1
        assert len(grid[0]) == 1

    def test_different_scale(self):
        """Different scales produce different-looking grids."""
        pn = PerlinNoise(seed=42)
        g1 = pn.generate_grid(32, 32, scale=10.0)
        g2 = pn.generate_grid(32, 32, scale=100.0)
        diffs = sum(
            1 for y in range(32) for x in range(32)
            if abs(g1[y][x] - g2[y][x]) > 0.01
        )
        assert diffs > 100, "Different scales should produce noticeably different grids"
