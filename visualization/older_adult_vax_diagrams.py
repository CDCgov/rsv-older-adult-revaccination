import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


# These are the settings used for the combined figure.
GROUP = "vaccinated_primary"
OUTCOMES = ["hospitalizations", "cases", "deaths"]
CURVES = ["scenario_a", "scenario_b", "scenario_c"]
INTERVALS = [1, 2, 3, 4, 5]
SCALE = "per100k"
REFERENCE_CURVE = "no_revaccination"
RATE_METRIC = "per1000_py_alive"

SCENARIO_STYLES = {
    "scenario_a": ("Scenario A", "#0072B2"),
    "scenario_b": ("Scenario B", "#009E73"),
    "scenario_c": ("Scenario C", "#D55E00"),
}

OUTCOME_LABELS = {
    "hospitalizations": "Cumulative hospitalizations",
    "cases": "Cumulative cases",
    "deaths": "Cumulative deaths",
}

OUTCOME_COLUMNS = {
    "hospitalizations": "hospitalizations_per100k",
    "cases": "cases_per100k",
    "deaths": "deaths_per100k",
}

SCALE_LABEL = "per 100,000 person-years alive"

PUBLICATION_DPI = 600
FIG_WIDTH_PER_COLUMN = 3.85
FIG_LEFT_MARGIN = 1.8
FIG_HEIGHT_PER_OUTCOME = 4.2
FIG_LEGEND_HEIGHT = 1.35
TITLE_SIZE = 17.0
TICK_SIZE = 13.0
AXIS_LABEL_SIZE = 13.5
ROW_TITLE_SIZE = 15.0
ROW_UNIT_SIZE = 13.0
ROW_RELATIVE_SIZE = 13.0
LEGEND_SIZE = 13.0


def read_summary_draws(results_dir):
    """Load outcome counts and convert them to rates per 100,000 person-years alive."""
    path = results_dir / "summary_draws.csv"
    columns = [
        "group",
        "person_years_alive",
        "hospitalizations",
        "cases",
        "deaths",
        "boost_recovery_curve",
        "dose2_interval_years",
    ]
    draws = pd.read_csv(path, usecols=columns)

    for outcome in OUTCOMES:
        draws[OUTCOME_COLUMNS[outcome]] = (
            draws[outcome] * 100000 / draws["person_years_alive"]
        )

    return draws


def read_relative_difference_draws(results_dir):
    """Load relative differences for the per-1,000 person-years-alive metric."""
    path = results_dir / "analysis_tables" / "relative_difference_draws.csv"
    columns = [
        "boost_recovery_curve",
        "k_years",
        "group",
        "outcome",
        "rate_metric",
        "relative_difference_rate",
    ]
    draws = pd.read_csv(path, usecols=columns)
    draws = draws[draws["rate_metric"] == RATE_METRIC]
    draws = draws[draws["k_years"] > 0]
    return draws


def summarize(values):
    """Calculate the median, central 50% interval, and central 95% interval."""
    return {
        "median": np.median(values),
        "lo50": np.quantile(values, 0.25),
        "hi50": np.quantile(values, 0.75),
        "lo95": np.quantile(values, 0.025),
        "hi95": np.quantile(values, 0.975),
    }


def summarize_outcome(draws, curve, interval, outcome):
    """Summarize one absolute outcome for one curve and dose-2 interval."""
    subset = draws[
        (draws["boost_recovery_curve"] == curve)
        & (draws["dose2_interval_years"] == interval)
        & (draws["group"] == GROUP)
    ]
    values = subset[OUTCOME_COLUMNS[outcome]].to_numpy()
    return summarize(values)


def summarize_relative_difference(draws, curve, interval, outcome):
    """Summarize one relative difference for one curve and dose-2 interval."""
    subset = draws[
        (draws["boost_recovery_curve"] == curve)
        & (draws["k_years"] == interval)
        & (draws["group"] == GROUP)
        & (draws["outcome"] == outcome)
    ]
    values = 100 * subset["relative_difference_rate"].to_numpy()
    return summarize(values)


def summarize_reference(draws, outcome):
    """Summarize the no-revaccination reference for one outcome."""
    subset = draws[
        (draws["boost_recovery_curve"] == REFERENCE_CURVE)
        & (draws["dose2_interval_years"] == 0)
        & (draws["group"] == GROUP)
    ]
    values = subset[OUTCOME_COLUMNS[outcome]].to_numpy()
    return summarize(values)


def draw_interval(ax, x, stats, color, size):
    """Draw a 95% interval, 50% interval, and median point on an axis."""
    ax.vlines(x, stats["lo95"], stats["hi95"], color=color, alpha=0.55, linewidth=1.1)
    ax.vlines(x, stats["lo50"], stats["hi50"], color=color, linewidth=3.0)
    ax.scatter([x], [stats["median"]], color=color, edgecolor="white", linewidth=0.6, s=size)


def style_outcome_axis(ax):
    """Apply the common formatting used by absolute-outcome panels."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.9)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.grid(axis="y", color="#E6E6E6", linewidth=0.6)
    ax.tick_params(axis="both", labelsize=TICK_SIZE, width=0.9, length=3.2)
    ax.tick_params(axis="x", labelbottom=False)


def style_relative_axis(ax, show_x_labels):
    """Apply the common formatting used by relative-difference panels."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.9)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.axhline(0, color="#A6A6A6", linestyle="--", linewidth=0.8, zorder=0)
    ax.grid(axis="y", color="#E6E6E6", linewidth=0.6)
    ax.tick_params(axis="both", labelsize=8.5, width=0.9, length=3.5)
    ax.set_xlim(-0.45, 5.45)
    ax.set_xticks([0, *INTERVALS])
    ax.set_xticklabels(["No\ndose 2", *[str(interval) for interval in INTERVALS]])
    if not show_x_labels:
        ax.tick_params(axis="x", labelbottom=False)


def add_panel_label(ax, label):
    """Add a lettered panel label to an axis."""
    ax.text(
        -0.19,
        1.13,
        label,
        transform=ax.transAxes,
        fontsize=16.0,
        fontweight="bold",
        va="top",
        ha="left",
    )


def plot_figure(results_dir, outdir):
    """Read the result tables, draw the multi-panel figure, and save it."""
    outcome_draws = read_summary_draws(results_dir)
    relative_draws = read_relative_difference_draws(results_dir)

    number_of_outcomes = len(OUTCOMES)
    number_of_curves = len(CURVES)
    figure = plt.figure(
        figsize=(
            FIG_WIDTH_PER_COLUMN * number_of_curves + FIG_LEFT_MARGIN,
            FIG_HEIGHT_PER_OUTCOME * number_of_outcomes + FIG_LEGEND_HEIGHT,
        )
    )
    grid = GridSpec(
        number_of_outcomes * 2,
        number_of_curves,
        figure=figure,
        height_ratios=[1.25, 0.9] * number_of_outcomes,
        hspace=0.36,
        wspace=0.38,
    )

    axes = np.empty((number_of_outcomes * 2, number_of_curves), dtype=object)
    for row in range(number_of_outcomes * 2):
        for column in range(number_of_curves):
            axes[row, column] = figure.add_subplot(grid[row, column])
            panel_number = column * (number_of_outcomes * 2) + row
            add_panel_label(axes[row, column], f"({chr(ord('a') + panel_number)})")

    for column, curve in enumerate(CURVES):
        title, color = SCENARIO_STYLES[curve]
        axes[0, column].set_title(
            title, color="#1A1A1A", fontsize=TITLE_SIZE, fontweight="bold", pad=10
        )

    for outcome_number, outcome in enumerate(OUTCOMES):
        outcome_row = 2 * outcome_number
        relative_row = outcome_row + 1
        outcome_values = []
        relative_values = [0]

        for curve in CURVES:
            for interval in INTERVALS:
                outcome_stats = summarize_outcome(outcome_draws, curve, interval, outcome)
                relative_stats = summarize_relative_difference(
                    relative_draws, curve, interval, outcome
                )
                outcome_values.extend(
                    [outcome_stats["lo95"], outcome_stats["hi95"], outcome_stats["median"]]
                )
                relative_values.extend(
                    [relative_stats["lo95"], relative_stats["hi95"], relative_stats["median"]]
                )

            reference_stats = summarize_reference(outcome_draws, outcome)
            outcome_values.extend(
                [reference_stats["lo95"], reference_stats["hi95"], reference_stats["median"]]
            )

        outcome_min = min(0, min(outcome_values))
        outcome_max = max(outcome_values)
        outcome_padding = max((outcome_max - outcome_min) * 0.12, outcome_max * 0.04, 1.0)
        outcome_limits = (
            outcome_min - 0.05 * outcome_padding,
            outcome_max + outcome_padding,
        )

        relative_min = min(0, min(relative_values))
        relative_max = max(0, max(relative_values))
        relative_span = max(relative_max - relative_min, 0.001)
        relative_padding = relative_span * 0.12
        relative_limits = (
            relative_min - relative_padding,
            relative_max + relative_padding,
        )

        for column, curve in enumerate(CURVES):
            title, color = SCENARIO_STYLES[curve]
            outcome_axis = axes[outcome_row, column]
            relative_axis = axes[relative_row, column]

            outcome_stats = [
                summarize_outcome(outcome_draws, curve, interval, outcome)
                for interval in INTERVALS
            ]
            relative_stats = [
                summarize_relative_difference(relative_draws, curve, interval, outcome)
                for interval in INTERVALS
            ]
            outcome_medians = np.array([stats["median"] for stats in outcome_stats])
            relative_medians = np.array([stats["median"] for stats in relative_stats])
            reference_stats = summarize_reference(outcome_draws, outcome)

            draw_interval(outcome_axis, 0, reference_stats, "#1A1A1A", 34)
            for interval, stats in zip(INTERVALS, outcome_stats):
                draw_interval(outcome_axis, interval, stats, color, 38)
            best_outcome = np.argmin(outcome_medians)
            outcome_axis.scatter(
                [INTERVALS[best_outcome]],
                [outcome_medians[best_outcome]],
                marker="*",
                s=190,
                facecolor="white",
                edgecolor=color,
                linewidth=1.6,
            )

            relative_axis.scatter([0], [0], color="#1A1A1A", s=32)
            for interval, stats in zip(INTERVALS, relative_stats):
                draw_interval(relative_axis, interval, stats, color, 38)
            best_relative = np.argmin(relative_medians)
            relative_axis.scatter(
                [INTERVALS[best_relative]],
                [relative_medians[best_relative]],
                marker="*",
                s=190,
                facecolor="white",
                edgecolor=color,
                linewidth=1.6,
            )

            outcome_axis.set_ylim(*outcome_limits)
            style_outcome_axis(outcome_axis)
            relative_axis.set_ylim(*relative_limits)
            style_relative_axis(relative_axis, outcome_number == number_of_outcomes - 1)

            if outcome_number == number_of_outcomes - 1:
                relative_axis.set_xlabel(
                    "Second-dose timing, K (years)", fontsize=AXIS_LABEL_SIZE
                )

    figure.subplots_adjust(left=0.158, right=0.985, top=0.925, bottom=0.175)

    for outcome_number, outcome in enumerate(OUTCOMES):
        outcome_position = axes[2 * outcome_number, 0].get_position()
        relative_position = axes[2 * outcome_number + 1, 0].get_position()
        outcome_center = (outcome_position.y0 + outcome_position.y1) / 2
        relative_center = (relative_position.y0 + relative_position.y1) / 2
        figure.text(
            0.11,
            outcome_center + 0.015,
            OUTCOME_LABELS[outcome],
            ha="right",
            va="center",
            fontsize=ROW_TITLE_SIZE,
            fontweight="bold",
        )
        figure.text(
            0.11,
            outcome_center - 0.020,
            f"({SCALE_LABEL})",
            ha="right",
            va="center",
            fontsize=ROW_UNIT_SIZE,
        )
        figure.text(
            0.11,
            relative_center,
            "Relative difference (%)",
            ha="right",
            va="center",
            fontsize=ROW_RELATIVE_SIZE,
        )

    for outcome_number in range(1, number_of_outcomes):
        upper = axes[2 * outcome_number - 1, 0].get_position()
        lower = axes[2 * outcome_number, 0].get_position()
        y = (upper.y0 + lower.y1) / 2
        figure.add_artist(
            Line2D(
                [0.02, 0.995],
                [y, y],
                transform=figure.transFigure,
                color="#C8C8C8",
                linewidth=0.75,
                linestyle=(0, (4, 4)),
                zorder=0,
            )
        )

    legend_items = [
        Line2D([0], [0], color="#1A1A1A", marker="o", linestyle="none", markersize=8.0, label="No dose 2 reference"),
        Line2D([0], [0], color="#666666", marker="o", linestyle="none", markersize=8.0, label="Posterior median"),
        Line2D([0], [0], color="#666666", linewidth=4.0, label="50% credible interval"),
        Line2D([0], [0], color="#666666", linewidth=1.8, alpha=0.55, label="95% credible interval"),
        Line2D([0], [0], color="#666666", marker="*", linestyle="none", markerfacecolor="white", markeredgewidth=1.5, markersize=14, label="K with lowest posterior median"),
    ]
    figure.legend(
        handles=legend_items,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.02),
        ncol=5,
        frameon=False,
        fontsize=LEGEND_SIZE,
    )

    outdir.mkdir(parents=True, exist_ok=True)
    output_stem = outdir / (
        "older_adult_vax_combined_outcome_relative_difference_"
        f"{GROUP}_{SCALE}_{RATE_METRIC}"
    )
    figure.savefig(
        output_stem.with_suffix(".png"),
        dpi=PUBLICATION_DPI,
        bbox_inches="tight",
        facecolor="white",
    )
    
    plt.close(figure)

    print(f"Wrote {output_stem}.png")



def main():
    """Read command-line paths and create the combined figure."""
    parser = argparse.ArgumentParser(
        description="Create the combined older-adult vaccination outcome figure."
    )
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    plot_figure(args.results_dir, args.outdir)


if __name__ == "__main__":
    main()
