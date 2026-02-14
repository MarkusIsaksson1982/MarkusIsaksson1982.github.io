"""Particle-based hydraulic erosion for 2D heightmaps."""

from __future__ import annotations

import math
from random import Random
from typing import List, Sequence, Tuple


class HydraulicErosion:
    """Particle-based hydraulic erosion simulation for 2D heightmaps."""

    def __init__(self, seed: int = 0):
        """Initialize with a seed for reproducible droplet paths."""
        self.seed = seed
        self._rng = Random(seed)

    def compute_gradient(
        self, heightmap: list[list[float]], x: float, y: float
    ) -> tuple[float, float, float]:
        """
        Compute interpolated gradient and height at a fractional position.
        Uses bilinear interpolation of the 4 surrounding cells.

        Returns:
            (gradient_x, gradient_y, height) -- gradient points downhill.
        """
        height = len(heightmap)
        width = len(heightmap[0])

        x = min(max(x, 0.0), width - 1.000001)
        y = min(max(y, 0.0), height - 1.000001)

        cell_x = int(x)
        cell_y = int(y)

        x_frac = x - cell_x
        y_frac = y - cell_y

        h00 = heightmap[cell_y][cell_x]
        h10 = heightmap[cell_y][cell_x + 1]
        h01 = heightmap[cell_y + 1][cell_x]
        h11 = heightmap[cell_y + 1][cell_x + 1]

        gradient_x = (h10 - h00) * (1.0 - y_frac) + (h11 - h01) * y_frac
        gradient_y = (h01 - h00) * (1.0 - x_frac) + (h11 - h10) * x_frac

        interpolated_height = (
            h00 * (1.0 - x_frac) * (1.0 - y_frac)
            + h10 * x_frac * (1.0 - y_frac)
            + h01 * (1.0 - x_frac) * y_frac
            + h11 * x_frac * y_frac
        )

        return gradient_x, gradient_y, interpolated_height

    def erode(
        self,
        heightmap: list[list[float]],
        iterations: int = 5000,
        max_lifetime: int = 64,
        inertia: float = 0.05,
        sediment_capacity_factor: float = 4.0,
        min_sediment_capacity: float = 0.01,
        deposit_speed: float = 0.3,
        erode_speed: float = 0.3,
        evaporate_speed: float = 0.01,
        gravity: float = 4.0,
        erosion_radius: int = 3,
    ) -> list[list[float]]:
        """
        Apply hydraulic erosion to a heightmap.

        Args:
            heightmap: 2D nested list of floats (will NOT be modified -- returns a new copy).
            iterations: Number of water droplets to simulate.
            max_lifetime: Maximum steps per droplet before evaporation.
            inertia: How much the droplet's direction persists vs following gradient (0-1).
            sediment_capacity_factor: Multiplier for sediment carrying capacity.
            min_sediment_capacity: Minimum sediment a droplet can carry.
            deposit_speed: Fraction of excess sediment deposited per step (0-1).
            erode_speed: Fraction of capacity deficit eroded per step (0-1).
            evaporate_speed: Fraction of water lost per step (0-1).
            gravity: Affects speed calculation from height difference.
            erosion_radius: Radius of erosion brush (cells affected per erosion event).

        Returns:
            A new 2D nested list of floats -- the eroded heightmap.
            Same dimensions as input. Values may extend slightly outside [0,1].
        """
        if not heightmap or not heightmap[0]:
            return []

        map_h = len(heightmap)
        map_w = len(heightmap[0])
        if map_w < 2 or map_h < 2:
            return [row[:] for row in heightmap]
        if any(len(row) != map_w for row in heightmap):
            raise ValueError("heightmap must be rectangular")
        if iterations <= 0:
            return [row[:] for row in heightmap]

        # Never mutate caller input.
        out_map = [row[:] for row in heightmap]

        brush_offsets, brush_weights = self._build_brush(erosion_radius)

        for _ in range(iterations):
            x = self._rng.uniform(0.0, map_w - 1.000001)
            y = self._rng.uniform(0.0, map_h - 1.000001)
            direction_x = 0.0
            direction_y = 0.0
            speed = 1.0
            water = 1.0
            sediment = 0.0

            for _step in range(max_lifetime):
                cell_x = int(x)
                cell_y = int(y)

                grad_x, grad_y, old_height = self.compute_gradient(out_map, x, y)

                # Move downhill: direction follows negative gradient.
                direction_x = direction_x * inertia - grad_x * (1.0 - inertia)
                direction_y = direction_y * inertia - grad_y * (1.0 - inertia)

                dir_len = math.hypot(direction_x, direction_y)
                if dir_len < 1e-12:
                    break
                direction_x /= dir_len
                direction_y /= dir_len

                new_x = x + direction_x
                new_y = y + direction_y
                if (
                    new_x < 0.0
                    or new_x >= map_w - 1
                    or new_y < 0.0
                    or new_y >= map_h - 1
                ):
                    break

                _, _, new_height = self.compute_gradient(out_map, new_x, new_y)
                delta_h = new_height - old_height

                sediment_capacity = max(
                    min_sediment_capacity,
                    -delta_h * speed * water * sediment_capacity_factor,
                )

                if sediment > sediment_capacity or delta_h > 0.0:
                    if delta_h > 0.0:
                        amount_to_deposit = min(delta_h, sediment)
                    else:
                        amount_to_deposit = (sediment - sediment_capacity) * deposit_speed
                    sediment -= amount_to_deposit
                    self._deposit_bilinear(out_map, x, y, amount_to_deposit)
                elif delta_h < 0.0:
                    amount_to_erode = min(
                        (sediment_capacity - sediment) * erode_speed,
                        -delta_h,
                    )
                    eroded = self._erode_brush(
                        out_map,
                        cell_x,
                        cell_y,
                        new_height,
                        amount_to_erode,
                        brush_offsets,
                        brush_weights,
                    )
                    sediment += eroded

                speed = math.sqrt(max(speed * speed + delta_h * gravity, 0.0))
                water *= 1.0 - evaporate_speed
                x = new_x
                y = new_y

                if water <= 1e-5 or speed < 1e-10:
                    break

        return out_map

    @staticmethod
    def _build_brush(radius: int) -> Tuple[List[Tuple[int, int]], List[float]]:
        if radius <= 0:
            return [(0, 0)], [1.0]

        offsets: List[Tuple[int, int]] = []
        raw_weights: List[float] = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                weight = max(0.0, radius - dist)
                if weight > 0.0:
                    offsets.append((dx, dy))
                    raw_weights.append(weight)

        total = sum(raw_weights)
        if total == 0.0:
            return [(0, 0)], [1.0]
        return offsets, [w / total for w in raw_weights]

    @staticmethod
    def _deposit_bilinear(heightmap: list[list[float]], x: float, y: float, amount: float) -> None:
        if amount <= 0.0:
            return
        map_h = len(heightmap)
        map_w = len(heightmap[0])
        if x < 0.0 or x >= map_w - 1 or y < 0.0 or y >= map_h - 1:
            return

        cell_x = int(x)
        cell_y = int(y)
        x_frac = x - cell_x
        y_frac = y - cell_y

        w00 = (1.0 - x_frac) * (1.0 - y_frac)
        w10 = x_frac * (1.0 - y_frac)
        w01 = (1.0 - x_frac) * y_frac
        w11 = x_frac * y_frac

        heightmap[cell_y][cell_x] += amount * w00
        heightmap[cell_y][cell_x + 1] += amount * w10
        heightmap[cell_y + 1][cell_x] += amount * w01
        heightmap[cell_y + 1][cell_x + 1] += amount * w11

    @staticmethod
    def _erode_brush(
        heightmap: list[list[float]],
        center_x: int,
        center_y: int,
        min_target_height: float,
        amount: float,
        offsets: Sequence[Tuple[int, int]],
        weights: Sequence[float],
    ) -> float:
        if amount <= 0.0:
            return 0.0

        map_h = len(heightmap)
        map_w = len(heightmap[0])

        removable: List[float] = []
        active_indices: List[Tuple[int, int]] = []
        active_weights: List[float] = []

        for (dx, dy), weight in zip(offsets, weights):
            px = center_x + dx
            py = center_y + dy
            if px < 0 or px >= map_w or py < 0 or py >= map_h:
                continue
            max_remove_here = max(0.0, heightmap[py][px] - min_target_height)
            if max_remove_here > 0.0 and weight > 0.0:
                active_indices.append((px, py))
                active_weights.append(weight)
                removable.append(max_remove_here)

        if not active_indices:
            return 0.0

        weight_sum = sum(active_weights)
        if weight_sum <= 0.0:
            return 0.0

        actual_eroded = 0.0
        for (px, py), weight, max_remove in zip(active_indices, active_weights, removable):
            planned = amount * (weight / weight_sum)
            taken = min(planned, max_remove)
            if taken > 0.0:
                heightmap[py][px] -= taken
                actual_eroded += taken

        return actual_eroded


def _basic_heightmap(width: int, height: int) -> list[list[float]]:
    grid: list[list[float]] = []
    for y in range(height):
        row: list[float] = []
        for x in range(width):
            # Cheap deterministic pseudo-noise for quick demo.
            v = (
                0.5
                + 0.25 * math.sin(x * 0.075)
                + 0.2 * math.cos(y * 0.065)
                + 0.1 * math.sin((x + y) * 0.035)
            )
            row.append(v)
        grid.append(row)
    return grid


def _stats(heightmap: list[list[float]]) -> tuple[float, float, float, float]:
    vals = [v for row in heightmap for v in row]
    n = len(vals)
    mean = sum(vals) / n
    variance = sum((v - mean) ** 2 for v in vals) / n
    return min(vals), max(vals), mean, math.sqrt(variance)


if __name__ == "__main__":
    hm_before = _basic_heightmap(128, 128)
    eroder = HydraulicErosion(seed=42)
    hm_after = eroder.erode(hm_before, iterations=5000)

    b_min, b_max, b_mean, b_std = _stats(hm_before)
    a_min, a_max, a_mean, a_std = _stats(hm_after)

    print("Before:")
    print(f"  min={b_min:.5f} max={b_max:.5f} mean={b_mean:.5f} std={b_std:.5f}")
    print("After:")
    print(f"  min={a_min:.5f} max={a_max:.5f} mean={a_mean:.5f} std={a_std:.5f}")
