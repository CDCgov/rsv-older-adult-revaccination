"""Combine older-adult vaccination scenario shards into one draw-level file."""

import argparse
from pathlib import Path

import pandas as pd


# These columns are used by the summary and figure scripts.
SUMMARY_COLUMNS = [
    "draw_row",
    "posterior_draw_id",
    "pre_posterior_draw_id",
    "posterior_source_row",
    "posterior_source_wave",
    "posterior_source_task_id",
    "posterior_source_sample_in_task",
    "scenario",
    "boost_scenario",
    "boost_recovery_curve",
    "k_years",
    "dose2_interval_years",
    "is_no_revaccination",
    "group",
    "person_years_alive",
    "infections",
    "cases",
    "hospitalizations",
    "deaths",
    "infections_per1000_py_alive",
    "cases_per1000_py_alive",
    "hospitalizations_per1000_py_alive",
    "deaths_per1000_py_alive",
]


def merge_shards(shards_root, outdir):
    """Read one summary CSV from each shard and combine them into one file."""
    shard_files = sorted(shards_root.glob("*/summary_draws.csv"))
    shard_tables = [pd.read_csv(path, usecols=SUMMARY_COLUMNS) for path in shard_files]
    summary = pd.concat(shard_tables, ignore_index=True)
    summary = summary.sort_values(
        ["draw_row", "boost_recovery_curve", "k_years", "group"]
    )

    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / "summary_draws.csv"
    summary.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")
    print(f"Merged {len(shard_files)} shard files and {len(summary)} rows")


def main():
    """Read command-line paths and merge the scenario shard files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shards-root", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    merge_shards(args.shards_root, args.outdir)


if __name__ == "__main__":
    main()
