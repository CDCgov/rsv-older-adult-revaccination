"""Merge older-adult vaccination scenario shards into a draw-level file.

The script reads one ``summary_draws.csv`` file from each immediate shard
subfolder, retains the identifiers, scenario metadata, outcome counts, and
rate fields required by downstream analysis, and writes one sorted CSV file.
"""

import argparse
from pathlib import Path

import pandas as pd


# Keep the draw identifiers, scenario labels, denominators, outcome counts, and
# rate fields used by the summary script and the figure script. Selecting these
# columns also makes the merged file independent of shard-only metadata.
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


def merge_shards(shards_root: Path, outdir: Path) -> None:
    """Read each shard summary CSV and write one combined draw-level CSV."""
    shard_files = sorted(shards_root.glob("*/summary_draws.csv"))
    shard_tables = [
        pd.read_csv(path, usecols=SUMMARY_COLUMNS) for path in shard_files
    ]
    summary = pd.concat(shard_tables, ignore_index=True)
    summary = summary.sort_values(
        ["draw_row", "boost_recovery_curve", "k_years", "group"]
    )

    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / "summary_draws.csv"
    summary.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")
    print(f"Merged {len(shard_files)} shard files and {len(summary)} rows")


def main() -> None:
    """Read command-line paths and merge the scenario shard files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shards-root", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    merge_shards(args.shards_root, args.outdir)


if __name__ == "__main__":
    main()
