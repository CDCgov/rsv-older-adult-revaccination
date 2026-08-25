"""Create summary tables from older-adult vaccination draw results."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


OUTCOMES = ["infections", "cases", "hospitalizations", "deaths"]
RATE_COLUMNS = [f"{outcome}_per1000_py_alive" for outcome in OUTCOMES]
SCENARIO_CURVES = ["scenario_a", "scenario_b", "scenario_c"]
NO_REVACCINATION_CURVE = "no_revaccination"


def read_draws(results_dir):
    """Load the merged draw-level CSV file from a results directory."""
    return pd.read_csv(results_dir / "summary_draws.csv")


def make_long_table(draws):
    """Reshape four rate columns into one row per draw and outcome."""
    id_columns = [
        "draw_row",
        "scenario",
        "boost_scenario",
        "boost_recovery_curve",
        "k_years",
        "dose2_interval_years",
        "is_no_revaccination",
        "group",
    ]
    long_table = draws.melt(
        id_vars=id_columns,
        value_vars=RATE_COLUMNS,
        var_name="outcome",
        value_name="value_rate",
    )
    long_table["outcome"] = long_table["outcome"].str.replace(
        "_per1000_py_alive", "", regex=False
    )
    long_table["rate_metric"] = "per1000_py_alive"
    return long_table


def add_baseline_for_each_curve(long_table):
    """Copy the no-revaccination rows so every curve has a K=0 comparator."""
    baseline = long_table[
        (long_table["k_years"] == 0)
        & (long_table["boost_recovery_curve"] == NO_REVACCINATION_CURVE)
    ]
    comparisons = long_table[long_table["k_years"] > 0]

    baseline_copies = []
    for curve in SCENARIO_CURVES:
        copy = baseline.copy()
        copy["boost_recovery_curve"] = curve
        copy["boost_scenario"] = curve
        baseline_copies.append(copy)

    return pd.concat([comparisons, *baseline_copies], ignore_index=True)


def interval_summary(values):
    """Calculate the median and central 95% interval for an array of values."""
    return {
        "median": float(np.median(values)),
        "lo95": float(np.quantile(values, 0.025)),
        "hi95": float(np.quantile(values, 0.975)),
    }


def absolute_summary(long_table):
    """Calculate outcome medians and 95% intervals for each scenario group."""
    group_columns = [
        "boost_recovery_curve",
        "boost_scenario",
        "k_years",
        "group",
        "outcome",
        "rate_metric",
    ]
    rows = []
    for keys, subset in long_table.groupby(group_columns):
        row = dict(zip(group_columns, keys))
        row["n_draws"] = len(subset)
        stats = interval_summary(subset["value_rate"].to_numpy())
        row["value_rate_median"] = stats["median"]
        row["value_rate_lo95"] = stats["lo95"]
        row["value_rate_hi95"] = stats["hi95"]
        rows.append(row)
    return pd.DataFrame(rows)


def relative_difference_draws(long_table):
    """Compare each positive-K draw with its matching K=0 draw."""
    key_columns = ["draw_row", "boost_recovery_curve", "group", "outcome"]
    baseline = long_table[long_table["k_years"] == 0][
        key_columns + ["value_rate"]
    ].rename(columns={"value_rate": "value_rate_k0"})
    comparisons = long_table[long_table["k_years"] > 0]

    relative = comparisons.merge(baseline, on=key_columns)
    relative["relative_difference_rate"] = (
        (relative["value_rate"] - relative["value_rate_k0"])
        / relative["value_rate_k0"]
    )
    return relative


def relative_difference_summary(relative_draws):
    """Calculate medians and 95% intervals for relative differences."""
    group_columns = [
        "boost_recovery_curve",
        "boost_scenario",
        "k_years",
        "group",
        "outcome",
        "rate_metric",
    ]
    rows = []
    for keys, subset in relative_draws.groupby(group_columns):
        row = dict(zip(group_columns, keys))
        row["n_draws"] = len(subset)
        stats = interval_summary(subset["relative_difference_rate"].to_numpy())
        row["relative_difference_rate_median"] = stats["median"]
        row["relative_difference_rate_lo95"] = stats["lo95"]
        row["relative_difference_rate_hi95"] = stats["hi95"]
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    """Read the results directory and write the three summary tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    analysis_dir = args.results_dir / "analysis_tables"
    draws = read_draws(args.results_dir)
    long_table = add_baseline_for_each_curve(make_long_table(draws))
    relative_draws = relative_difference_draws(long_table)

    analysis_dir.mkdir(parents=True, exist_ok=True)
    absolute_summary(long_table).to_csv(
        analysis_dir / "absolute_outcome_summary.csv", index=False
    )
    relative_draws.to_csv(
        analysis_dir / "relative_difference_draws.csv", index=False
    )
    relative_difference_summary(relative_draws).to_csv(
        analysis_dir / "relative_difference_summary.csv", index=False
    )

    print(f"Wrote summary tables to {analysis_dir}")


if __name__ == "__main__":
    main()
