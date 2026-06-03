"""
conversions.py — Unit conversion helpers (degrees ↔ radians ↔ gradians).
"""

import math


def deg_to_rad(deg: float) -> float:
    """Convert degrees to radians."""
    return math.radians(deg)


def rad_to_deg(rad: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(rad)


def grad_to_deg(grad: float) -> float:
    """Convert gradians (gons) to degrees."""
    return grad * (360.0 / 400.0)


def deg_to_grad(deg: float) -> float:
    """Convert degrees to gradians (gons)."""
    return deg * (400.0 / 360.0)


def to_degrees(value: float, unit: str) -> float:
    """
    Convert *value* in the given *unit* to degrees.

    Parameters
    ----------
    value : float
        Numeric angle value.
    unit  : str
        One of "Degrees", "Radians", "Gradians".

    Returns
    -------
    float – angle in degrees.
    """
    if unit == "Radians":
        return rad_to_deg(value)
    if unit == "Gradians":
        return grad_to_deg(value)
    return value  # already degrees


def all_units(degrees: float) -> tuple[float, float, float]:
    """
    Given an angle in degrees return (degrees, radians, gradians).
    """
    return degrees, deg_to_rad(degrees), deg_to_grad(degrees)


def normalise_degrees(deg: float) -> float:
    """
    Normalise *deg* into the [0, 360) range for quadrant / reference-angle
    calculations. Handles negative angles and values > 360.
    """
    return deg % 360.0


def get_quadrant(deg: float) -> int | None:
    """
    Return the quadrant (1–4) for the normalised degree value, or
    *None* when the angle lies exactly on an axis.
    """
    n = normalise_degrees(deg)
    if n in (0.0, 90.0, 180.0, 270.0):
        return None  # on axis
    if 0 < n < 90:
        return 1
    if 90 < n < 180:
        return 2
    if 180 < n < 270:
        return 3
    return 4


def reference_angle_deg(deg: float) -> float:
    """
    Return the reference angle in degrees for *deg* (always in [0, 90]).
    """
    n = normalise_degrees(deg)
    if 0 <= n <= 90:
        return n
    if 90 < n <= 180:
        return 180.0 - n
    if 180 < n <= 270:
        return n - 180.0
    return 360.0 - n
