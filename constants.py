"""
constants.py — App-wide constants, special angle data, ASTC sign rules, and themes.
"""

import math

APP_NAME = "Trig Explorer"
APP_SUBTITLE = "Explore Trigonometric Ratios for Any Angle"
APP_VERSION = "1.0.0"

HISTORY_MAX = 50

# ── Themes ───────────────────────────────────────────────────────────────────

THEMES = {
    "Midnight": {
        "mode":     "dark",
        "bg":       "#0f1117",
        "surface":  "#1a1d27",
        "surface2": "#22263a",
        "border":   "#2e3150",
        "accent":   "#6c63ff",
        "accent2":  "#ff6584",
        "accent3":  "#43e97b",
        "text":     "#e8eaf6",
        "text_sub": "#8b92b8",
        "text_dim": "#555a80",
        "success":  "#43e97b",
        "warning":  "#ffd166",
        "error":    "#ef476f",
        "undefined":"#ef476f",
    },
    "Aurora": {
        "mode":     "dark",
        "bg":       "#0d1f1a",
        "surface":  "#122a22",
        "surface2": "#1a3a2e",
        "border":   "#1e4d3a",
        "accent":   "#00e5a0",
        "accent2":  "#00bcd4",
        "accent3":  "#f9c74f",
        "text":     "#d4f5ec",
        "text_sub": "#7abda0",
        "text_dim": "#3d6b58",
        "success":  "#00e5a0",
        "warning":  "#f9c74f",
        "error":    "#ff6b6b",
        "undefined":"#ff6b6b",
    },
    "Crimson": {
        "mode":     "dark",
        "bg":       "#150a0a",
        "surface":  "#1f1010",
        "surface2": "#2e1515",
        "border":   "#4a1e1e",
        "accent":   "#ff4d6d",
        "accent2":  "#ff9f43",
        "accent3":  "#ffd166",
        "text":     "#ffe0e6",
        "text_sub": "#bf7080",
        "text_dim": "#6b3040",
        "success":  "#51cf66",
        "warning":  "#ffd166",
        "error":    "#ff6b6b",
        "undefined":"#ff6b6b",
    },
    "Ocean": {
        "mode":     "dark",
        "bg":       "#070e1a",
        "surface":  "#0d1b2e",
        "surface2": "#122440",
        "border":   "#1a3355",
        "accent":   "#38bdf8",
        "accent2":  "#818cf8",
        "accent3":  "#34d399",
        "text":     "#cce8ff",
        "text_sub": "#6a9fc0",
        "text_dim": "#2a5070",
        "success":  "#34d399",
        "warning":  "#fbbf24",
        "error":    "#f87171",
        "undefined":"#f87171",
    },
    "Sunlight": {
        "mode":     "light",
        "bg":       "#fdf6e3",
        "surface":  "#ffffff",
        "surface2": "#f0e8d0",
        "border":   "#d4c5a0",
        "accent":   "#c07800",
        "accent2":  "#d64045",
        "accent3":  "#2d8a4e",
        "text":     "#2c2010",
        "text_sub": "#6b5530",
        "text_dim": "#a08860",
        "success":  "#2d8a4e",
        "warning":  "#c07800",
        "error":    "#d64045",
        "undefined":"#d64045",
    },
    "Arctic": {
        "mode":     "light",
        "bg":       "#eef4fb",
        "surface":  "#ffffff",
        "surface2": "#dce8f5",
        "border":   "#b0cceb",
        "accent":   "#1565c0",
        "accent2":  "#7b1fa2",
        "accent3":  "#00897b",
        "text":     "#0d1b2e",
        "text_sub": "#3a5a80",
        "text_dim": "#7090b0",
        "success":  "#00897b",
        "warning":  "#e65100",
        "error":    "#c62828",
        "undefined":"#c62828",
    },
}

THEME_NAMES = list(THEMES.keys())
DEFAULT_THEME = "Midnight"

# ── Trig Ratios ──────────────────────────────────────────────────────────────

RATIO_OPTIONS = ["Sin", "Cos", "Tan", "Cosec", "Sec", "Cot"]

PERIODICITY = {
    "Sin":   360,
    "Cos":   360,
    "Tan":   180,
    "Cosec": 360,
    "Sec":   360,
    "Cot":   180,
}

# ── Special (Exact) Values ────────────────────────────────────────────────────

EXACT_VALUES: dict[float, dict[str, str]] = {
    0: {
        "Sin": "0", "Cos": "1", "Tan": "0",
        "Cosec": "Undefined", "Sec": "1", "Cot": "Undefined",
    },
    30: {
        "Sin": "1/2", "Cos": "√3/2", "Tan": "1/√3",
        "Cosec": "2", "Sec": "2/√3", "Cot": "√3",
    },
    45: {
        "Sin": "1/√2", "Cos": "1/√2", "Tan": "1",
        "Cosec": "√2", "Sec": "√2", "Cot": "1",
    },
    60: {
        "Sin": "√3/2", "Cos": "1/2", "Tan": "√3",
        "Cosec": "2/√3", "Sec": "2", "Cot": "1/√3",
    },
    90: {
        "Sin": "1", "Cos": "0", "Tan": "Undefined",
        "Cosec": "1", "Sec": "Undefined", "Cot": "0",
    },
    120: {
        "Sin": "√3/2", "Cos": "-1/2", "Tan": "-√3",
        "Cosec": "2/√3", "Sec": "-2", "Cot": "-1/√3",
    },
    135: {
        "Sin": "1/√2", "Cos": "-1/√2", "Tan": "-1",
        "Cosec": "√2", "Sec": "-√2", "Cot": "-1",
    },
    150: {
        "Sin": "1/2", "Cos": "-√3/2", "Tan": "-1/√3",
        "Cosec": "2", "Sec": "-2/√3", "Cot": "-√3",
    },
    180: {
        "Sin": "0", "Cos": "-1", "Tan": "0",
        "Cosec": "Undefined", "Sec": "-1", "Cot": "Undefined",
    },
    210: {
        "Sin": "-1/2", "Cos": "-√3/2", "Tan": "1/√3",
        "Cosec": "-2", "Sec": "-2/√3", "Cot": "√3",
    },
    225: {
        "Sin": "-1/√2", "Cos": "-1/√2", "Tan": "1",
        "Cosec": "-√2", "Sec": "-√2", "Cot": "1",
    },
    240: {
        "Sin": "-√3/2", "Cos": "-1/2", "Tan": "√3",
        "Cosec": "-2/√3", "Sec": "-2", "Cot": "1/√3",
    },
    270: {
        "Sin": "-1", "Cos": "0", "Tan": "Undefined",
        "Cosec": "-1", "Sec": "Undefined", "Cot": "0",
    },
    300: {
        "Sin": "-√3/2", "Cos": "1/2", "Tan": "-√3",
        "Cosec": "-2/√3", "Sec": "2", "Cot": "-1/√3",
    },
    315: {
        "Sin": "-1/√2", "Cos": "1/√2", "Tan": "-1",
        "Cosec": "-√2", "Sec": "√2", "Cot": "-1",
    },
    330: {
        "Sin": "-1/2", "Cos": "√3/2", "Tan": "-1/√3",
        "Cosec": "-2", "Sec": "2/√3", "Cot": "-√3",
    },
    360: {
        "Sin": "0", "Cos": "1", "Tan": "0",
        "Cosec": "Undefined", "Sec": "1", "Cot": "Undefined",
    },
}

# ── ASTC ──────────────────────────────────────────────────────────────────────

ASTC: dict[int, list[str]] = {
    1: ["Sin", "Cos", "Tan", "Cosec", "Sec", "Cot"],
    2: ["Sin", "Cosec"],
    3: ["Tan", "Cot"],
    4: ["Cos", "Sec"],
}

ASTC_LABELS = {1: "All", 2: "Sin", 3: "Tan", 4: "Cos"}

# Keep these for backwards compat
DARK_THEME  = THEMES["Midnight"]
LIGHT_THEME = THEMES["Arctic"]
