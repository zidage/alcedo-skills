#!/usr/bin/env python3
"""Measures an Alcedo Studio preview PNG for photo corrections.

Run it on the file that `render.preview` writes (`<stem>_current.png`). The preview is the
display-referred image that the user sees, so the numbers describe what the photo looks like,
not the internal pipeline state.

    python analyze_preview.py <preview.png> [--json]

It reports:

- tone: L* percentiles (0 = black, 100 = white), clipped highlights and shadows, and a
  suggested exposure change in stops;
- color: the median a* (green-/magenta+) and b* (blue-/yellow+) of the most neutral pixels, the
  cast that they show, and how reliable that is;
- saturation: the average chroma and the share of very saturated pixels;
- tilt: the angle of the strongest straight horizontal or vertical lines, counterclockwise
  positive. Add it to `crop_rotate.angle_degrees` to level the photo.

This script is optional. The agent judges a photo by looking at the preview; use the script
only when the user asks for measurements. The numbers describe the image, not whether it looks
good: a dark night photo or a warm sunset can be right as it is.

Needs Python 3.9 or later with numpy and Pillow (`pip install numpy pillow`).
"""

from __future__ import annotations

import argparse
import json
import math
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError as error:  # pragma: no cover - depends on the machine
    sys.stderr.write(f"analyze_preview.py needs numpy and Pillow: {error}\n"
                     "Install them with: python -m pip install numpy pillow\n")
    sys.exit(2)

ANALYSIS_LONG_EDGE = 1024
# L* of middle grey. A typical daylight scene has its median near it.
TARGET_MEDIAN_L = 50.0
# A neutral candidate: not too dark or bright, and little chroma (C*ab).
NEUTRAL_L_RANGE = (25.0, 90.0)
STRICT_NEUTRAL_CHROMA = 8.0
NEUTRAL_MAX_CHROMA = 18.0
# The share of the image that the neutral estimate needs.
MIN_NEUTRAL_SHARE = 0.03
# A median a* or b* beyond this is a cast.
CAST_THRESHOLD = 3.0
# Tilt search range in degrees, and the bin size.
TILT_RANGE = 12.0
TILT_BIN = 0.1


def load_rgb(path: str) -> np.ndarray:
    """Returns the image as float RGB in 0..1, scaled to ANALYSIS_LONG_EDGE at most."""
    image = Image.open(path).convert("RGB")
    scale = ANALYSIS_LONG_EDGE / max(image.size)
    if scale < 1:
        image = image.resize((max(1, round(image.width * scale)),
                              max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
    return np.asarray(image, dtype=np.float64) / 255.0


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_to_lab(linear: np.ndarray) -> np.ndarray:
    """sRGB (D65) linear RGB to CIE L*a*b* (D65 white)."""
    matrix = np.array([[0.4124564, 0.3575761, 0.1804375],
                       [0.2126729, 0.7151522, 0.0721750],
                       [0.0193339, 0.1191920, 0.9503041]])
    xyz = linear @ matrix.T
    white = np.array([0.95047, 1.0, 1.08883])
    ratio = xyz / white
    epsilon, kappa = 216 / 24389, 24389 / 27
    f = np.where(ratio > epsilon, np.cbrt(ratio), (kappa * ratio + 16) / 116)
    lightness = 116 * f[..., 1] - 16
    a_star = 500 * (f[..., 0] - f[..., 1])
    b_star = 200 * (f[..., 1] - f[..., 2])
    return np.stack([lightness, a_star, b_star], axis=-1)


def l_to_y(lightness: float) -> float:
    """CIE L* to relative luminance Y."""
    if lightness > 8:
        return ((lightness + 16) / 116) ** 3
    return lightness / (24389 / 27)


def analyze_tone(rgb: np.ndarray, lab: np.ndarray) -> dict:
    lightness = lab[..., 0].ravel()
    percentiles = {f"p{p}": round(float(np.percentile(lightness, p)), 1)
                   for p in (1, 5, 25, 50, 75, 95, 99)}
    clipped_high = float(np.mean(np.max(rgb, axis=-1) >= 254 / 255))
    clipped_low = float(np.mean(np.max(rgb, axis=-1) <= 2 / 255))

    median_l = percentiles["p50"]
    suggested = math.log2(l_to_y(TARGET_MEDIAN_L) / max(l_to_y(median_l), 1e-4))
    # The display transform rolls off the highlights, so the 99th percentile rarely reaches
    # white and gives no useful headroom. Only clipped highlights stop an exposure increase.
    if clipped_high > 0.01 and suggested > 0:
        suggested = 0.0
    suggested = max(-2.0, min(2.0, suggested))

    if median_l < 30:
        key = "dark"
    elif median_l > 70:
        key = "bright"
    else:
        key = "normal"
    return {
        "lightness": percentiles,
        "mean_lightness": round(float(lightness.mean()), 1),
        "contrast_p5_p95": round(percentiles["p95"] - percentiles["p5"], 1),
        "clipped_highlights": round(clipped_high, 4),
        "clipped_shadows": round(clipped_low, 4),
        "key": key,
        "suggested_exposure_change_ev": round(suggested, 2),
    }


def analyze_color(lab: np.ndarray) -> dict:
    """Estimates a color cast from the pixels that should be neutral (grey or white).

    It uses the median a* and b* of the most neutral pixels. The reliability says how much to
    trust it: "high" when the photo has enough nearly grey pixels; "low" when only muted colors
    (for example foliage or skin) or all mid tones are left. A low reliability often means that
    the "cast" is the color of the scene, not of the light.
    """
    lightness, a_star, b_star = lab[..., 0], lab[..., 1], lab[..., 2]
    chroma = np.hypot(a_star, b_star)
    mid = (lightness >= NEUTRAL_L_RANGE[0]) & (lightness <= NEUTRAL_L_RANGE[1])
    candidates = (
        (mid & (chroma <= STRICT_NEUTRAL_CHROMA), "nearly grey pixels", "high"),
        (mid & (chroma <= NEUTRAL_MAX_CHROMA), "muted pixels (few grey pixels)", "low"),
        (mid, "all mid-tone pixels (no grey pixels)", "low"),
    )
    for neutral, source, reliability in candidates:
        if neutral.mean() >= MIN_NEUTRAL_SHARE:
            break
    else:
        return {"source": "none", "reliability": "none", "cast": "unknown"}

    neutral_a = float(np.median(a_star[neutral]))
    neutral_b = float(np.median(b_star[neutral]))
    words = []
    if neutral_b > CAST_THRESHOLD:
        words.append("warm (yellow)")
    elif neutral_b < -CAST_THRESHOLD:
        words.append("cool (blue)")
    if neutral_a > CAST_THRESHOLD:
        words.append("magenta")
    elif neutral_a < -CAST_THRESHOLD:
        words.append("green")
    return {
        "source": source,
        "reliability": reliability,
        "neutral_share": round(float(neutral.mean()), 3),
        "neutral_a": round(neutral_a, 2),
        "neutral_b": round(neutral_b, 2),
        "cast": " and ".join(words) if words else "neutral",
        "mean_chroma": round(float(chroma[mid].mean()) if mid.any() else 0.0, 1),
        "saturated_share": round(float(np.mean(chroma > 60)), 4),
    }


def sobel(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sobel gradients (x to the right, y down) of a 2-D image, with edge padding."""
    padded = np.pad(image, 1, mode="edge")
    gx = ((padded[:-2, 2:] + 2 * padded[1:-1, 2:] + padded[2:, 2:]) -
          (padded[:-2, :-2] + 2 * padded[1:-1, :-2] + padded[2:, :-2]))
    gy = ((padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:]) -
          (padded[:-2, :-2] + 2 * padded[:-2, 1:-1] + padded[:-2, 2:]))
    return gx, gy


def line_scores(xs: np.ndarray, ys: np.ndarray, weights: np.ndarray, normal_angles: np.ndarray,
                angles: np.ndarray, vertical: bool, diagonal: float) -> np.ndarray:
    """Hough scores of straight lines at each angle of @p angles.

    The score of an angle is the summed weight of the three strongest lines (rho bins of
    2 pixels) at that angle. Only edge pixels whose gradient is near the normal of the angle
    vote, so texture adds little and a long straight edge forms a clear peak.
    """
    scores = np.zeros(angles.size)
    bins = int(diagonal) + 2
    for index, angle in enumerate(angles):
        theta = math.radians(angle)
        # Line direction (counterclockwise from the x axis, y up): (cos, sin) for a horizontal
        # line, rotated by 90 degrees for a vertical line. Image y points down.
        if vertical:
            normal = (-math.cos(theta), math.sin(theta))
            normal_angle = math.degrees(math.atan2(-normal[1], normal[0]))
        else:
            normal = (-math.sin(theta), -math.cos(theta))
            normal_angle = math.degrees(math.atan2(-normal[1], normal[0]))
        difference = np.abs((normal_angles - normal_angle + 90.0) % 180.0 - 90.0)
        voters = difference <= 15.0
        if not voters.any():
            continue
        rho = xs[voters] * normal[0] + ys[voters] * normal[1]
        accumulator = np.bincount(((rho + diagonal) / 2).astype(np.int64),
                                  weights=weights[voters], minlength=bins)
        scores[index] = np.sort(accumulator)[-3:].sum()
    return scores


def analyze_tilt(lab: np.ndarray) -> dict:
    """Finds the tilt of the strongest straight horizontal or vertical lines (Hough transform).

    The tilt is in degrees, counterclockwise positive: a horizon that rises to the right has a
    positive tilt. To level the photo, add the tilt to `crop_rotate.angle_degrees`.
    """
    lightness = lab[..., 0]
    gx, gy = sobel(lightness)
    magnitude = np.hypot(gx, gy)
    threshold = np.percentile(magnitude, 92)
    ys, xs = np.nonzero(magnitude > threshold)
    if xs.size < 200:
        return {"tilt_degrees": 0.0, "confidence": 0.0, "lines": "none",
                "basis": "too few edges"}
    weights = magnitude[ys, xs]
    # Gradient direction with y up, folded to -90..90.
    normal_angles = np.degrees(np.arctan2(-gy[ys, xs], gx[ys, xs]))
    xs = xs.astype(np.float64)
    ys = ys.astype(np.float64)
    diagonal = math.hypot(*lightness.shape)

    angles = np.arange(-TILT_RANGE, TILT_RANGE + TILT_BIN / 2, TILT_BIN)
    results = {}
    for name, vertical in (("horizontal", False), ("vertical", True)):
        scores = line_scores(xs, ys, weights, normal_angles, angles, vertical, diagonal)
        peak = int(np.argmax(scores))
        baseline = float(np.median(scores)) + 1e-9
        results[name] = (float(angles[peak]), float(scores[peak]), scores[peak] / baseline)

    name = max(results, key=lambda key: results[key][2])
    tilt, _, prominence = results[name]
    # A peak 1.5 times the median score is weak; 3 times or more is a clear straight line.
    confidence = max(0.0, min(1.0, (prominence - 1.5) / 1.5))
    return {
        "tilt_degrees": round(tilt, 1) + 0.0,
        "confidence": round(confidence, 2),
        "lines": name,
        "horizontal_tilt": round(results["horizontal"][0], 1) + 0.0,
        "horizontal_prominence": round(results["horizontal"][2], 2),
        "vertical_tilt": round(results["vertical"][0], 1) + 0.0,
        "vertical_prominence": round(results["vertical"][2], 2),
        "basis": f"{xs.size} edge pixels",
    }


def describe(result: dict) -> str:
    tone, color, tilt = result["tone"], result["color"], result["tilt"]
    lines = [
        f"File: {result['file']} ({result['width']}x{result['height']})",
        "Tone:",
        f"  L* p1/p5/p50/p95/p99: {tone['lightness']['p1']} / {tone['lightness']['p5']} / "
        f"{tone['lightness']['p50']} / {tone['lightness']['p95']} / {tone['lightness']['p99']}"
        f"  (key: {tone['key']})",
        f"  clipped highlights {tone['clipped_highlights'] * 100:.2f}%, "
        f"clipped shadows {tone['clipped_shadows'] * 100:.2f}%",
        f"  suggested exposure change {tone['suggested_exposure_change_ev']:+.2f} EV",
        "Color:",
        f"  {color.get('source')}: a* {color.get('neutral_a')}, b* {color.get('neutral_b')} "
        f"-> cast: {color.get('cast')} (reliability {color.get('reliability')})",
        f"  mean chroma {color.get('mean_chroma')}, very saturated "
        f"{color.get('saturated_share', 0) * 100:.2f}%",
        "Tilt:",
        f"  {tilt['tilt_degrees']:+.1f} degrees from {tilt['lines']} lines "
        f"(counterclockwise positive), confidence {tilt['confidence']} ({tilt['basis']})",
        f"  horizontal lines {tilt.get('horizontal_tilt', 0):+.1f} (prominence "
        f"{tilt.get('horizontal_prominence', 0)}), vertical lines "
        f"{tilt.get('vertical_tilt', 0):+.1f} (prominence {tilt.get('vertical_prominence', 0)})",
        "  To level the photo, add the tilt to crop_rotate.angle_degrees.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("png", help="A preview PNG from render.preview.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    arguments = parser.parse_args()

    try:
        rgb = load_rgb(arguments.png)
    except OSError as error:
        sys.stderr.write(f"cannot read {arguments.png}: {error}\n")
        return 1
    lab = linear_to_lab(srgb_to_linear(rgb))
    result = {
        "file": arguments.png,
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "tone": analyze_tone(rgb, lab),
        "color": analyze_color(lab),
        "tilt": analyze_tilt(lab),
    }
    print(json.dumps(result, indent=2) if arguments.json else describe(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
