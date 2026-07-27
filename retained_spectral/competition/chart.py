#!/usr/bin/env python3
"""Render the Retained Spectral competition charts from the results JSON.

Dark-theme figures drawn only from measured numbers in the JSON record:

* ``retained_spectral_hero.png`` — one clear comparison: median solve time
  (milliseconds, log scale, lower is faster) on one identical operator, native
  Retained Multilevel Sturm against every standard eigensolver in the audit
  (SciPy ``eigh_tridiagonal``/``eigh``, NumPy ``eigvalsh``, SciPy ``eigsh``/ARPACK,
  JAX ``eigvalsh``); the fastest measured bar is highlighted ★ — computed from the data, so it
  moves to whichever solver actually won on the host that produced the JSON.
* ``retained_spectral_detail.png`` — two credibility panels: a forest plot of the per-case
  end-to-end speedup with its 95% bootstrap confidence interval (colour = the recorded
  native_faster/tie/competitor_faster verdict, parity line at 1×), and the raw per-call samples
  (every timed repeat, not just a median) for native vs the independent SciPy pipeline.

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

    # spread whisker on each bar: the 25th–75th percentile of that solver's per-case times, so the
    # bar's consistency across the 7 problems is visible, not just the aggregate geomean point.
    for xi, entry in zip(x, ranking):
        key = entry[3]
        per = per_case["native"] if key == "native" else per_case.get(key, {})
        pts = sorted(per[n] * 1e3 for n in common if n in per)
        if len(pts) >= 2:
            q1, q3 = float(np.percentile(pts, 25)), float(np.percentile(pts, 75))
            if q3 > q1:
                ax.plot([xi, xi], [q1, q3], color=BG, lw=2.6, zorder=4, solid_capstyle="round")
                ax.plot([xi, xi], [q1, q3], color=TEXT, lw=1.3, zorder=5, alpha=0.55,
                        solid_capstyle="round")

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
        f"(95% bootstrap CI recorded in the JSON)  ·  {agg_note}\n"
        f"this host: numpy {env['numpy']}, scipy {env['scipy']}, jax {env['jax']}, numba {env['numba']}"
        f"  ·  dense-route time depends on the linked BLAS/LAPACK",
        ha="left", fontsize=8.5, color=MUTED,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def render_detail(data: dict, output_path: Path) -> Path:
    """Two credibility panels drawn only from the measured record:

    * LEFT — a forest plot of the per-case end-to-end speedup (SciPy time / native time) with the
      95% bootstrap confidence interval as a whisker, a dot at the bootstrap median, and a colour
      set by the recorded verdict (native_faster / tie / competitor_faster). The parity line at 1×
      is where the interval must clear to claim a win. The winner is read from the data, per case.
    * RIGHT — the raw per-call samples (every timed repeat, not just a median) for native vs the
      independent SciPy pipeline, so the actual measurement spread is visible behind each median.
    """

    import matplotlib

    matplotlib.use("Agg")
    _apply_theme(matplotlib)
    import matplotlib.pyplot as plt

    e2e = data["end_to_end"]["cases"]
    names = list(e2e.keys())
    labels = [_SHORT.get(n, n) for n in names]
    summ = data["end_to_end"]["summary"]

    verdict_color = {"native_faster": NATIVE, "tie": GOLD, "competitor_faster": SCIPY}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.4, 5.8))
    fig.subplots_adjust(left=0.13, right=0.975, top=0.80, bottom=0.16, wspace=0.32)
    fig.suptitle(
        "Per-case detail — confidence intervals and raw measurements",
        x=0.055, y=0.95, ha="left", fontsize=15, fontweight="bold", color=TEXT,
    )

    # ---- LEFT: forest plot of the per-case speedup with its 95% bootstrap CI ----
    y = np.arange(len(names))[::-1]                     # top case at the top of the panel
    any_ci = False
    for yi, n in zip(y, names):
        ci = e2e[n].get("scipy_speedup_over_native", {})
        lo, hi = ci.get("ci95_low"), ci.get("ci95_high")
        med = ci.get("ratio_median", e2e[n].get("scipy_to_native_time_ratio"))
        col = verdict_color.get(ci.get("verdict"), MUTED)
        if lo is not None and hi is not None and hi >= lo:
            any_ci = True
            ax1.plot([lo, hi], [yi, yi], color=col, lw=3.0, solid_capstyle="round", zorder=3)
            ax1.plot([lo, lo], [yi - 0.16, yi + 0.16], color=col, lw=1.6, zorder=3)
            ax1.plot([hi, hi], [yi - 0.16, yi + 0.16], color=col, lw=1.6, zorder=3)
        if med is not None:
            ax1.scatter([med], [yi], s=46, color=col, edgecolor=BG, linewidth=1.0, zorder=4)
            ax1.text(med, yi + 0.30, f"{med:.1f}×", ha="center", va="bottom",
                     fontsize=9, color=TEXT)
    ax1.axvline(1.0, color=MUTED, lw=1.6, ls="--", zorder=2)
    ax1.text(1.0, len(names) - 0.35, "parity 1×", ha="center", va="bottom",
             color=MUTED, fontsize=9)
    ax1.set_xscale("log")
    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=10, color=TEXT)
    ax1.set_ylim(-0.6, len(names) - 0.2)
    ax1.set_xlabel("end-to-end speedup  =  SciPy time / native time   (log, right is a native win)",
                   fontsize=10)
    ax1.set_title("Speedup with 95% bootstrap CI  ·  colour = recorded verdict",
                  loc="left", fontsize=12, color=TEXT, fontweight="bold")

    # ---- RIGHT: raw per-call samples for native vs the independent SciPy pipeline ----
    rng = np.random.default_rng(0)                     # deterministic horizontal jitter only
    yb = np.arange(len(names))[::-1]
    for yi, n in zip(yb, names):
        for stats_key, colour, off in (("native_stats", NATIVE, -0.15),
                                        ("scipy_stats", SCIPY, 0.15)):
            samples = e2e[n].get(stats_key, {}).get("samples_ms", [])
            if not samples:
                continue
            jit = (rng.random(len(samples)) - 0.5) * 0.18
            ax2.scatter(samples, np.full(len(samples), yi + off) + jit,
                        s=26, color=colour, alpha=0.75, edgecolor="none", zorder=3)
            med = float(np.median(samples))
            ax2.plot([med, med], [yi + off - 0.14, yi + off + 0.14],
                     color=colour, lw=2.2, zorder=4)
    ax2.set_xscale("log")
    ax2.set_yticks(yb)
    ax2.set_yticklabels(labels, fontsize=10, color=TEXT)
    ax2.set_ylim(-0.6, len(names) - 0.2)
    ax2.set_xlabel("per-call solve time, ms  (log — every timed repeat, not a median)", fontsize=10)
    ax2.set_title("Raw per-call samples  ·  native vs SciPy",
                  loc="left", fontsize=12, color=TEXT, fontweight="bold")

    for ax in (ax1, ax2):
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)

    # read the resample count + seed from the record itself, so the caption never drifts from what
    # actually produced the intervals.
    _ci_meta = next((e2e[n].get("scipy_speedup_over_native", {}) for n in names
                     if e2e[n].get("scipy_speedup_over_native", {}).get("resamples")), {})
    _res, _seed = _ci_meta.get("resamples"), _ci_meta.get("seed")
    ci_note = (f"95% bootstrap CI, {_res:,} resamples, seed {_seed}" if any_ci and _res
               else "95% bootstrap CI" if any_ci else "CI unavailable (need ≥2 repeats)")
    fig.text(
        0.055, 0.03,
        f"Left: {ci_note} — a native win needs the whole interval right of 1×.  "
        f"Right: the SciPy pipeline is our own construction, shown in full for disclosure.",
        ha="left", fontsize=8.5, color=MUTED,
    )
    fig.text(
        0.055, 0.005,
        f"Native {summ['speedup_geomean']:.2f}× geomean over {summ['cases']} end-to-end cases.",
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
