#!/usr/bin/env python3
"""Render the Retained Spectral competition charts from the results JSON.

Dark-theme figures drawn only from measured numbers in the JSON record:

* ``retained_spectral_hero.png`` — one clear comparison: median solve time
  (milliseconds, log scale, lower is faster) on one identical operator, native
  Retained Multilevel Sturm against every standard eigensolver in the audit
  (SciPy ``eigh_tridiagonal``/``eigh``, NumPy ``eigvalsh``, SciPy ``eigsh``/ARPACK,
  JAX ``eigvalsh``); the fastest measured bar is highlighted ★ — computed from the data, so it
  moves to whichever solver actually won on the host that produced the JSON.
* ``retained_spectral_detail.png`` — per-case breakdown: every solver's
  times-slower-than-native and the end-to-end wall-clock.

Usage::

    PYTHONPATH=. python3 -m retained_spectral.competition.chart
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve()
DEFAULT_RESULTS = _HERE.parent.parent / "results" / "competition_results.json"
ASSETS = _HERE.parents[2] / "assets"

# Dark theme, tuned to sit on a GitHub dark-canvas README.
BG = "#0D1117"
PANEL = "#0D1117"
TEXT = "#E6EDF3"
MUTED = "#8B949E"
GRID = "#21262D"
NATIVE = "#F0776C"  # coral — the highlighted hero bar (ours)
SCIPY = "#58A6FF"  # blue
JAX = "#BC8CFF"  # purple
GOLD = "#F2CC60"  # star / accents

_SHORT = {
    "harmonic_low4": "harmonic",
    "displaced_harmonic_low4": "displaced",
    "squeezed_harmonic_omega16_low4": "squeezed ω16",
    "poschl_teller_lambda3_all_bound": "Pöschl–Teller",
    "morse_lambda5_all_bound": "Morse",
    "factorized_sextic_ground": "sextic",
    "pure_quartic_ground": "quartic",
}


def _geomean(values) -> float:
    values = [v for v in values if v and v > 0]
    return float(np.exp(np.mean(np.log(values)))) if values else float("nan")


def _apply_theme(matplotlib) -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "figure.facecolor": BG,
            "savefig.facecolor": BG,
            "axes.facecolor": PANEL,
            "axes.edgecolor": GRID,
            "axes.linewidth": 1.0,
            "text.color": TEXT,
            "axes.labelcolor": MUTED,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.size": 11,
        }
    )


def render_banner(
    output_path: Path,
    *,
    lines: tuple[str, ...] = ("RETAINED", "SPECTRAL"),
    subtitle: str = "readout-first Schrödinger spectrum solver",
    tagline: str = "every readout is a finite discrete rational number  ·  finite_diagnostic tier",
    accent: str = "v0.1.0",
) -> Path:
    """Dark title banner with a pink→purple→blue gradient stacked wordmark."""

    import matplotlib

    matplotlib.use("Agg")
    _apply_theme(matplotlib)
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.font_manager import FontProperties
    from matplotlib.patches import PathPatch
    from matplotlib.textpath import TextPath

    prop = FontProperties(family="DejaVu Sans", weight="bold")
    cmap = LinearSegmentedColormap.from_list(
        "spectral_wordmark", ["#F778BA", "#BC8CFF", "#58A6FF"]
    )

    # Lay out each word as a unit-height glyph path, centred, stacked top-down.
    paths = []
    widths = []
    for word in lines:
        tp = TextPath((0, 0), word, size=1.0, prop=prop)
        e = tp.get_extents()
        tp0 = TextPath((-e.x0, -e.y0), word, size=1.0, prop=prop)
        paths.append(tp0)
        widths.append(tp0.get_extents().width)
    max_w = max(widths)
    line_h = 1.0
    gap = 0.24 * line_h
    n = len(lines)

    fig_w = 12.0
    fig = plt.figure(figsize=(fig_w, 2.0 + 1.55 * n))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_facecolor(BG)
    gradient = np.linspace(0, 1, 512).reshape(1, -1)

    top_y = n * line_h + (n - 1) * gap
    for i, (tp0, wdt) in enumerate(zip(paths, widths)):
        x0 = (max_w - wdt) / 2.0
        y0 = top_y - (i + 1) * line_h - i * gap
        from matplotlib.transforms import Affine2D

        placed = tp0.transformed(Affine2D().translate(x0, y0))
        patch = PathPatch(placed, facecolor="none", edgecolor="none")
        ax.add_patch(patch)
        im = ax.imshow(
            gradient,
            extent=(0, max_w, y0, y0 + line_h),
            aspect="auto",
            cmap=cmap,
            zorder=2,
        )
        im.set_clip_path(patch)

    cx = max_w / 2.0
    pad_x = 0.05 * max_w
    ax.set_xlim(-pad_x, max_w + pad_x)
    ax.set_ylim(-1.15 * line_h, top_y + 0.22 * line_h)

    ax.text(cx, -0.14 * line_h, subtitle, ha="center", va="top",
            fontsize=16, color=TEXT, fontweight="bold")
    ax.text(cx, -0.44 * line_h, tagline, ha="center", va="top",
            fontsize=10.5, color=MUTED)
    if accent:
        ax.text(cx, -0.78 * line_h, accent, ha="center", va="top",
                fontsize=10, color=GOLD, fontweight="bold")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def render_hero(data: dict, output_path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    _apply_theme(matplotlib)
    import matplotlib.pyplot as plt

    audit = data["executor_audit"]["cases"]
    names = list(audit.keys())
    solver_names = list(audit[names[0]]["solvers"].keys())

    palette = {
        "SciPy eigh_tridiagonal": "#58A6FF",
        "SciPy eigsh (ARPACK)": "#3FB0AC",
        "SciPy eigh (dense)": "#BC8CFF",
        "NumPy eigvalsh (dense)": "#E3A857",
        "JAX eigvalsh (dense)": "#F778BA",
    }
    short = {
        "SciPy eigh_tridiagonal": "SciPy\neigh_tridiagonal",
        "SciPy eigsh (ARPACK)": "SciPy eigsh\n(ARPACK)",
        "SciPy eigh (dense)": "SciPy eigh\n(dense)",
        "NumPy eigvalsh (dense)": "NumPy\neigvalsh",
        "JAX eigvalsh (dense)": "JAX\neigvalsh",
    }

    # per-solver {case: median seconds}, present only where the solver actually ran
    per_case = {"native": {n: audit[n]["native_hot_median_seconds"] for n in names}}
    for s in solver_names:
        got = {n: audit[n]["solvers"][s].get("hot_median_seconds") for n in names
               if audit[n]["solvers"][s].get("hot_median_seconds") is not None}
        if got:
            per_case[s] = got
    # aggregate ONLY over the case set every scored solver completed (no silently-dropped cases)
    common = set(names)
    for t in per_case.values():
        common &= set(t)
    common = sorted(common)

    def gm(times):
        return _geomean([times[n] for n in common]) * 1e3

    # rank ALL solvers by measured time — native is NOT assumed first; the ★ lands on the true minimum,
    # and if a competitor is fastest the chart says so without any source edit.
    ranking = [("Retained\nMultilevel Sturm", gm(per_case["native"]), NATIVE, "native")]
    for s in solver_names:
        if s in per_case:
            ranking.append((short.get(s, s), gm(per_case[s]), palette.get(s, MUTED), s))
    ranking.sort(key=lambda e: e[1])

    labels = [e[0] for e in ranking]
    values = [e[1] for e in ranking]
    colors = [e[2] for e in ranking]
    native_ms = gm(per_case["native"])
    fastest_ms = values[0]
    incomplete = len(common) < len(names)

    fig, ax = plt.subplots(figsize=(12.4, 6.6))
    fig.subplots_adjust(left=0.09, right=0.975, top=0.70, bottom=0.17)
    x = np.arange(len(ranking))
    bars = ax.bar(x, values, width=0.66, color=colors, zorder=3)

    ax.set_yscale("log")
    ax.set_ylabel("median solve time, ms   (log — lower is faster ↓)", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10.5, color=TEXT)
    ax.grid(axis="y", color=GRID, lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)

    hi = max(values)
    for i, (bar, val) in enumerate(zip(bars, values)):
        cx = bar.get_x() + bar.get_width() / 2
        label = f"{val:.2f} ms" if val < 10 else f"{val:,.0f} ms"
        ax.text(cx, val * 1.4, label, ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=TEXT)
        if i == 0:
            ax.text(cx, val * 5.5, "★ fastest", ha="center", va="bottom",
                    fontsize=13, fontweight="bold", color=GOLD)
        else:
            factor = val / values[0]
            tag = f"{factor:,.0f}× slower" if factor >= 10 else f"{factor:.1f}× slower"
            ax.text(cx, val * 5.5, tag, ha="center", va="bottom",
                    fontsize=10.5, color=MUTED)
    ax.set_ylim(top=hi * 30.0)

    env = data["environment"]
    fig.suptitle(
        "Same operator — median solve time (lower is faster)",
        x=0.09, y=0.955, ha="left", fontsize=18, fontweight="bold", color=TEXT,
    )
    # subtitle computed from the data — flips automatically if a competitor is fastest
    winner = ranking[0][0].replace("\n", " ")
    if ranking[0][3] == "native":
        line1 = f"Native Retained Multilevel Sturm was the fastest measured on this host — {native_ms:.2f} ms (median)."
    else:
        line1 = (f"On this host the fastest was {winner} ({fastest_ms:.2f} ms, median); "
                 f"native {native_ms:.2f} ms = {native_ms / fastest_ms:.2f}× slower.")
    tri = gm(per_case["SciPy eigh_tridiagonal"]) if "SciPy eigh_tridiagonal" in per_case else None
    if tri is not None:
        rel = (f"{tri / native_ms:.1f}× faster" if tri > native_ms
               else f"{native_ms / tri:.1f}× slower")
        line2 = f"vs SciPy eigh_tridiagonal (the requested-only peer): native {rel}."
    else:
        line2 = ""
    fig.text(0.09, 0.850, line1, ha="left", fontsize=10.5, color=MUTED)
    fig.text(0.09, 0.808, line2, ha="left", fontsize=10.5, color=MUTED)
    summ = data.get("end_to_end", {}).get("summary", {})
    nc, tc = summ.get("native_correct", "?"), summ.get("cases", len(names))
    agg_note = f"geomean over {len(common)}/{len(names)} common cases" if incomplete \
        else f"geomean over all {len(names)} cases"
    fig.text(
        0.09, 0.02,
        f"{nc}/{tc} within declared tolerance  ·  finite_diagnostic tier  ·  median of hot calls "
        f"(95% CI is future work)  ·  {agg_note}\n"
        f"this host: numpy {env['numpy']}, scipy {env['scipy']}, jax {env['jax']}, numba {env['numba']}"
        f"  ·  dense-route time depends on the linked BLAS/LAPACK",
        ha="left", fontsize=8.5, color=MUTED,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def render_detail(data: dict, output_path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    _apply_theme(matplotlib)
    import matplotlib.pyplot as plt

    audit = data["executor_audit"]["cases"]
    e2e = data["end_to_end"]["cases"]
    names = list(e2e.keys())
    labels = [_SHORT.get(n, n) for n in names]
    x = np.arange(len(names))

    # every competitor's per-case ×slower-than-native factor
    palette = {
        "SciPy eigh_tridiagonal": "#58A6FF",
        "SciPy eigsh (ARPACK)": "#3FB0AC",
        "SciPy eigh (dense)": "#BC8CFF",
        "NumPy eigvalsh (dense)": "#E3A857",
        "JAX eigvalsh (dense)": "#F778BA",
    }
    solver_names = [s for s in audit[names[0]]["solvers"] if s in palette]
    native_ms = [e2e[n]["native"]["hot_median_seconds"] * 1e3 for n in names]
    scipy_ms = [e2e[n]["scipy"]["hot_median_seconds"] * 1e3 for n in names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.4, 5.6))
    fig.subplots_adjust(left=0.055, right=0.985, top=0.82, bottom=0.22, wspace=0.17)
    summ = data["end_to_end"]["summary"]

    fig.suptitle(
        "Per-case detail",
        x=0.055, y=0.95, ha="left", fontsize=15, fontweight="bold", color=TEXT,
    )

    m = len(solver_names)
    bw = 0.8 / m
    for j, s in enumerate(solver_names):
        ratios = [audit[n]["solvers"][s].get("to_native_time_ratio", np.nan) for n in names]
        ax1.bar(x + (j - (m - 1) / 2) * bw, ratios, bw, color=palette[s],
                label=s, zorder=3)
    ax1.axhline(1.0, color=NATIVE, lw=2.2, zorder=2)
    ax1.text(len(names) - 0.5, 1.08, "native = 1×", va="bottom", ha="right",
             color=NATIVE, fontsize=9.5, fontweight="bold")
    ax1.set_yscale("log")
    ax1.set_ylabel("times slower than native  (log)", fontsize=10)
    ax1.set_title("Same-operator executor audit — all solvers", loc="left",
                  fontsize=12, color=TEXT, fontweight="bold")

    w2 = 0.4
    ax2.bar(x - w2 / 2, native_ms, w2, color=NATIVE, label="native RMS", zorder=3)
    ax2.bar(x + w2 / 2, scipy_ms, w2, color=SCIPY, label="independent SciPy pipeline (ours)", zorder=3)
    ax2.set_yscale("log")
    ax2.set_ylabel("wall-clock per solve, ms  (log)", fontsize=10)
    ax2.set_title(
        f"End-to-end from raw input  ·  native {summ['speedup_geomean']:.2f}× geomean",
        loc="left", fontsize=12, color=TEXT, fontweight="bold",
    )

    for ax in (ax1, ax2):
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=32, ha="right", fontsize=9.5)
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
        ax.legend(frameon=False, fontsize=9, loc="upper left", labelcolor=TEXT)

    fig.text(
        0.06, 0.02,
        "Left panel is the credible comparison (identical operator, standard library APIs). "
        "Right panel's SciPy competitor is our own construction, shown for full disclosure.",
        ha="left", fontsize=8.5, color=MUTED,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--assets", type=Path, default=ASSETS)
    args = parser.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    render_banner(
        args.assets / "idm_banner.png",
        lines=("INFORMATION", "DISCRETE MATH"),
        subtitle="the continuum, computed as a readout of the discrete",
        tagline="258 solver kinds  ·  120 axiom-free Coq theorems  ·  tier-honest finite readouts",
        accent="by Yaoharee Lahtee",
    )
    banner = render_banner(args.assets / "retained_spectral_banner.png")
    hero = render_hero(data, args.assets / "retained_spectral_hero.png")
    detail = render_detail(data, args.assets / "retained_spectral_detail.png")
    print("banner:", banner)
    print("hero:", hero)
    print("detail:", detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
