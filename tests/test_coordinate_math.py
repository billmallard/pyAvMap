"""
Unit tests for pyavmap coordinate math functions.

These functions are pure math with no Qt dependency and can be tested
without a display or chart data.

Run from the repo root:
    python -m pytest tests/test_coordinate_math.py -v
"""
import math
import unittest

# Qt and avchart_proj stubs are installed by conftest.py before collection.
from pyavmap import (
    Distance,
    GetRelLng,
    Heading,
    adjusted_polar_deltas,
    METERS_PER_NM,
)

NM_TO_M = 1852
DEG_TO_RAD = math.pi / 180.0


class TestConstants(unittest.TestCase):
    def test_meters_per_nm(self):
        self.assertEqual(METERS_PER_NM, 1852)


class TestGetRelLng(unittest.TestCase):
    """GetRelLng(lat_radians) returns cos(lat) — longitude compression factor."""

    def test_equator(self):
        self.assertAlmostEqual(GetRelLng(0.0), 1.0, places=10)

    def test_60_degrees(self):
        # cos(60°) = 0.5
        self.assertAlmostEqual(GetRelLng(60 * DEG_TO_RAD), 0.5, places=10)

    def test_45_degrees(self):
        self.assertAlmostEqual(GetRelLng(45 * DEG_TO_RAD), math.sqrt(2) / 2, places=10)

    def test_90_degrees(self):
        # cos(90°) = 0 — longitude has no length at the pole
        self.assertAlmostEqual(GetRelLng(90 * DEG_TO_RAD), 0.0, places=10)


class TestAdjustedPolarDeltas(unittest.TestCase):
    """adjusted_polar_deltas applies longitude compression to the longitude delta."""

    def test_due_north_at_equator(self):
        course = ((0, 0), (0, 1))  # (lon, lat) pairs
        dlng, dlat = adjusted_polar_deltas(course)
        self.assertAlmostEqual(dlng, 0.0, places=10)
        self.assertAlmostEqual(dlat, 1.0, places=10)

    def test_due_east_at_equator(self):
        # cos(0) = 1.0 → dlng unchanged
        course = ((0, 0), (1, 0))
        dlng, dlat = adjusted_polar_deltas(course)
        self.assertAlmostEqual(dlng, 1.0, places=10)
        self.assertAlmostEqual(dlat, 0.0, places=10)

    def test_due_east_at_60_degrees(self):
        # cos(60°) = 0.5 → dlng halved
        course = ((0, 60), (1, 60))
        dlng, dlat = adjusted_polar_deltas(course)
        self.assertAlmostEqual(dlng, 0.5, places=5)
        self.assertAlmostEqual(dlat, 0.0, places=10)

    def test_explicit_rel_lng_overrides_computed(self):
        course = ((0, 60), (1, 60))  # would compute cos(60°)=0.5 otherwise
        dlng, dlat = adjusted_polar_deltas(course, rel_lng=0.25)
        self.assertAlmostEqual(dlng, 0.25, places=10)

    def test_diagonal_at_equator(self):
        course = ((0, 0), (3, 4))  # dlng=3, dlat=4; rel_lng=cos(0)=1
        dlng, dlat = adjusted_polar_deltas(course)
        self.assertAlmostEqual(dlng, 3.0, places=10)
        self.assertAlmostEqual(dlat, 4.0, places=10)


class TestDistance(unittest.TestCase):
    """Distance returns meters; each degree = 60 NM in the spherical approximation."""

    def test_same_point(self):
        course = ((0, 0), (0, 0))
        self.assertAlmostEqual(Distance(course), 0.0, places=5)

    def test_one_degree_north_from_equator(self):
        # 1° lat = 60 NM = 111120 m
        course = ((0, 0), (0, 1))
        self.assertAlmostEqual(Distance(course), 60 * NM_TO_M, places=2)

    def test_one_degree_east_at_equator(self):
        # At equator, 1° lon = 60 NM (cos(0)=1)
        course = ((0, 0), (1, 0))
        self.assertAlmostEqual(Distance(course), 60 * NM_TO_M, places=2)

    def test_one_degree_east_at_60_degrees(self):
        # At 60° lat, 1° lon = 30 NM (cos(60°)=0.5)
        course = ((0, 60), (1, 60))
        self.assertAlmostEqual(Distance(course), 30 * NM_TO_M, places=0)

    def test_pythagorean_3_4_5_triangle(self):
        # 3° lng and 4° lat at equator → hypotenuse = 5° = 300 NM
        course = ((0, 0), (3, 4))
        self.assertAlmostEqual(Distance(course), 300 * NM_TO_M, places=2)

    def test_distance_asymmetry_with_latitude(self):
        # Distance uses the start point's latitude for longitude compression, so
        # reversing a course that crosses latitudes gives a slightly different result.
        # Both results should be within ~1% of each other for small lat changes.
        c_fwd = ((0, 0), (1, 1))
        c_rev = ((1, 1), (0, 0))
        ratio = Distance(c_fwd) / Distance(c_rev)
        self.assertAlmostEqual(ratio, 1.0, delta=0.01)

    def test_distance_always_nonnegative(self):
        for course in [((0, 0), (1, -1)), ((5, 5), (3, 2)), ((0, 45), (0, 45))]:
            self.assertGreaterEqual(Distance(course), 0.0)


class TestHeading(unittest.TestCase):
    """Heading returns degrees true; atan2(dlng, dlat) convention."""

    def test_due_north(self):
        course = ((0, 0), (0, 1))
        self.assertAlmostEqual(Heading(course), 0.0, places=5)

    def test_due_east_at_equator(self):
        course = ((0, 0), (1, 0))
        self.assertAlmostEqual(Heading(course), 90.0, places=5)

    def test_due_south(self):
        course = ((0, 0), (0, -1))
        # atan2(0, -1) = 180° or -180° — both are correct representations
        h = Heading(course)
        self.assertAlmostEqual(abs(h), 180.0, places=5)

    def test_due_west_at_equator(self):
        course = ((0, 0), (-1, 0))
        self.assertAlmostEqual(Heading(course), -90.0, places=5)

    def test_northeast_45_degrees(self):
        # Equal north and east components at equator → NE = 45°
        course = ((0, 0), (1, 1))
        self.assertAlmostEqual(Heading(course), 45.0, places=5)

    def test_northwest_minus_45_degrees(self):
        course = ((0, 0), (-1, 1))
        self.assertAlmostEqual(Heading(course), -45.0, places=5)

    def test_heading_changes_with_latitude(self):
        # At 60° lat, 1° lon is compressed to 0.5°; due east will still be 90°
        # because dlat=0 and dlng>0 regardless of compression
        course = ((0, 60), (1, 60))
        self.assertAlmostEqual(Heading(course), 90.0, places=5)

    def test_northeast_at_60_degrees_skews(self):
        # Equal raw lon/lat deltas at 60° lat; lon is compressed by 0.5
        # → effective dlng=0.5, dlat=1 → atan2(0.5, 1) ≈ 26.57°
        course = ((0, 60), (1, 61))
        expected = math.atan2(0.5, 1.0) * 180 / math.pi
        self.assertAlmostEqual(Heading(course), expected, places=3)


if __name__ == "__main__":
    unittest.main()
