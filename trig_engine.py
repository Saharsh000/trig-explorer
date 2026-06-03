"""
trig_engine.py — Core trigonometric computation engine.

All calculations use Python's math module.  Undefined results (division by
zero or near-zero denominators) are returned as the sentinel string
"Undefined" rather than raising exceptions.
"""

import math
from dataclasses import dataclass, field

from conversions import (
    to_degrees,
    all_units,
    normalise_degrees,
    get_quadrant,
    reference_angle_deg,
    deg_to_rad,
    deg_to_grad,
)
from constants import EXACT_VALUES, ASTC, ASTC_LABELS, PERIODICITY, RATIO_OPTIONS

# Threshold below which sin/cos is treated as zero (avoids near-inf results).
_NEAR_ZERO = 1e-12
# Precision for decimal display.
DECIMAL_PLACES = 12


@dataclass
class TrigResult:
    """Full result bundle returned by :func:`compute`."""

    # ── Raw input ─────────────────────────────────────────────────────────────
    ratio: str
    input_value: float
    input_unit: str

    # ── Converted angles ──────────────────────────────────────────────────────
    degrees: float
    radians: float
    gradians: float

    # ── Main result ───────────────────────────────────────────────────────────
    value: str          # decimal string or "Undefined"
    value_float: float | None  # raw float, or None when undefined

    # ── Derived info ──────────────────────────────────────────────────────────
    quadrant: int | None        # 1-4, or None for on-axis
    reference_deg: float
    reference_rad: float
    reference_grad: float
    normalised_deg: float       # unit-circle equivalent in [0, 360)

    # ── Sign analysis (all six ratios for current quadrant) ───────────────────
    sign_map: dict[str, str] = field(default_factory=dict)

    # ── Exact special value ───────────────────────────────────────────────────
    exact_value: str | None = None   # e.g. "√3/2", or None if not special

    # ── Periodicity ──────────────────────────────────────────────────────────
    period_deg: int = 360


# ── Internal helpers ──────────────────────────────────────────────────────────

def _fmt(value: float) -> str:
    """Format a float to DECIMAL_PLACES significant decimal digits."""
    return f"{value:.{DECIMAL_PLACES}f}"


def _is_undef(x: float) -> bool:
    return abs(x) < _NEAR_ZERO


def _safe_reciprocal(x: float) -> float | None:
    """Return 1/x, or None if x is effectively zero."""
    if _is_undef(x):
        return None
    return 1.0 / x


def _calc(ratio: str, rad: float) -> tuple[str, float | None]:
    """
    Compute the requested *ratio* for the given radian value.

    Returns
    -------
    (display_string, float_or_None)
    """
    try:
        if ratio == "Sin":
            v = math.sin(rad)
            return _fmt(v), v

        if ratio == "Cos":
            v = math.cos(rad)
            return _fmt(v), v

        if ratio == "Tan":
            cos_v = math.cos(rad)
            if _is_undef(cos_v):
                return "Undefined", None
            v = math.tan(rad)
            return _fmt(v), v

        if ratio == "Cosec":
            sin_v = math.sin(rad)
            r = _safe_reciprocal(sin_v)
            if r is None:
                return "Undefined", None
            return _fmt(r), r

        if ratio == "Sec":
            cos_v = math.cos(rad)
            r = _safe_reciprocal(cos_v)
            if r is None:
                return "Undefined", None
            return _fmt(r), r

        if ratio == "Cot":
            sin_v = math.sin(rad)
            if _is_undef(sin_v):
                return "Undefined", None
            cos_v = math.cos(rad)
            v = cos_v / sin_v
            return _fmt(v), v

    except (ValueError, ZeroDivisionError, OverflowError):
        pass

    return "Undefined", None


def _sign_map(quadrant: int | None) -> dict[str, str]:
    """
    Return sign ("Positive" / "Negative") for every ratio given *quadrant*.
    When on-axis, each function is either 0, ±1, or undefined – mark as "Axis".
    """
    if quadrant is None:
        return {r: "Axis" for r in RATIO_OPTIONS}

    positive = set(ASTC.get(quadrant, []))
    return {
        r: ("Positive" if r in positive else "Negative")
        for r in RATIO_OPTIONS
    }


def _exact(ratio: str, normalised: float) -> str | None:
    """Look up exact form if *normalised* matches a known special angle."""
    rounded = round(normalised, 6)
    for special_deg, table in EXACT_VALUES.items():
        if abs(rounded - special_deg) < 0.001:
            return table.get(ratio)
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def compute(ratio: str, input_value: float, input_unit: str) -> TrigResult:
    """
    Full trig computation for *ratio* at *input_value* in *input_unit*.

    Parameters
    ----------
    ratio      : str   — One of RATIO_OPTIONS.
    input_value: float — Angle value as entered by the user.
    input_unit : str   — "Degrees", "Radians", or "Gradians".

    Returns
    -------
    TrigResult dataclass.
    """
    deg = to_degrees(input_value, input_unit)
    rad = deg_to_rad(deg)
    grad = deg_to_grad(deg)

    value_str, value_float = _calc(ratio, rad)

    norm = normalise_degrees(deg)
    quad = get_quadrant(deg)
    ref_deg = reference_angle_deg(deg)
    ref_rad = deg_to_rad(ref_deg)
    ref_grad = deg_to_grad(ref_deg)

    return TrigResult(
        ratio=ratio,
        input_value=input_value,
        input_unit=input_unit,
        degrees=deg,
        radians=rad,
        gradians=grad,
        value=value_str,
        value_float=value_float,
        quadrant=quad,
        reference_deg=ref_deg,
        reference_rad=ref_rad,
        reference_grad=ref_grad,
        normalised_deg=norm,
        sign_map=_sign_map(quad),
        exact_value=_exact(ratio, norm),
        period_deg=PERIODICITY.get(ratio, 360),
    )


def quadrant_label(quad: int | None) -> str:
    """Human-readable quadrant string."""
    if quad is None:
        return "On Axis"
    return f"Quadrant {['', 'I', 'II', 'III', 'IV'][quad]}"


def astc_label(quad: int | None) -> str:
    """Return the ASTC memory-aid word for the quadrant."""
    if quad is None:
        return "—"
    words = {1: "All (+)", 2: "Sin (+)", 3: "Tan (+)", 4: "Cos (+)"}
    return words.get(quad, "—")
