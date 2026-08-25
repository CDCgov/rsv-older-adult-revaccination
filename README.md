# Older adult RSV revaccination analytical code

## Purpose and scope

This folder is for older adult RSV revaccination analysis. It starts with draw-level results produced by the model, then:

1. combines result shards;
2. calculates absolute outcome summaries and paired relative differences; and
3. creates the combined outcome figure.


## Contents

```
cleaned_code/
|-- results/                 Included sample input shard (draws_0_4)
|-- scripts/                 Merge and summary-table scripts
|-- visualization/           Figure-generation script
|-- pyproject.toml           Python version and dependency specification
`-- README.md                This guide
```

### Folders and files

- `results/older_adult_vax/shards/draws_0_4/`
  - A small sample model-output shard used by the commands in this README.
  - `summary_draws.csv` is the required input to the merge step.
  - `manifest.json` records scenario settings and provenance; `posterior_draws_used.csv`, `summary_quantiles.csv`, and the weekly hospitalization time series are supplementary sample outputs.

- `scripts/merge_older_adult_vax_shards.py`
  - Reads `summary_draws.csv` from every immediate subfolder of `--shards-root`.
  - Retains the columns used by the subsequent analysis and writes one sorted, combined `summary_draws.csv` to `--outdir`.

- `scripts/summarize_older_adult_vax.py`
  - Reads the merged draw-level file.
  - Converts the four outcome rates to long format, uses the no-revaccination `K=0` rows as the comparator for each recovery curve, and calculates medians and central 95% intervals.
  - Writes three CSV analysis tables under `--results-dir/analysis_tables/`.

- `visualization/older_adult_vax_diagrams.py`
  - Reads the merged draw-level file and the paired relative-difference table.
  - Produces one publication-style PNG for the `vaccinated_primary` group showing hospitalizations, cases, and deaths for recovery Scenarios A--C and dose-2 intervals of one to five years.

## Requirements and installation

Use Python 3.10 or newer. The package requires NumPy, pandas, and matplotlib; their minimum versions are specified in `pyproject.toml`.

From the `cleaned_code` directory, install the dependencies:

```bash
python -m pip install numpy pandas matplotlib
```

Alternatively, install the project metadata and its dependencies:

```bash
python -m pip install .
```

## Run the included sample, step by step

Run these commands from the `cleaned_code` directory. They create a new `results/older_adult_vax/sample_run/` directory and leave the included sample shard unchanged.

### 1. Merge the sample shard

```bash
python scripts/merge_older_adult_vax_shards.py --shards-root results/older_adult_vax/shards --outdir results/older_adult_vax/sample_run
```

Expected result:

- `results/older_adult_vax/sample_run/summary_draws.csv`
- With the included `draws_0_4` sample, the script reports one shard and 320 draw-level rows.


### 2. Create summary tables

```bash
python scripts/summarize_older_adult_vax.py --results-dir results/older_adult_vax/sample_run
```

Expected result: a new `results/older_adult_vax/sample_run/analysis_tables/` directory containing:

- `absolute_outcome_summary.csv` -- median, lower 95%, and upper 95% outcome rates by scenario, interval, group, and outcome;
- `relative_difference_draws.csv` -- paired draw-level relative differences versus the no-revaccination baseline; and
- `relative_difference_summary.csv` -- median and 95% interval of those relative differences.

With the included sample, these files contain 288, 1,200, and 240 data rows, respectively.

### 3. Create the combined figure

```bash
python visualization/older_adult_vax_diagrams.py --results-dir results/older_adult_vax/sample_run --outdir results/older_adult_vax/sample_run/visualization
```

Expected result:

```
results/older_adult_vax/sample_run/visualization/
`-- older_adult_vax_combined_outcome_relative_difference_vaccinated_primary_per100k_per1000_py_alive.png
```

The PNG contains three outcome rows (hospitalizations, cases, deaths). It displays posterior medians, 50% and 95% credible intervals, the no-dose-2 reference, the dose-2 interval with the lowest posterior median, and paired relative differences.

## Expected input schema

The merge script expects each input shard to have a `summary_draws.csv` file. The required columns include draw identifiers; scenario and recovery-curve labels; dose-2 interval; population group; person-years alive; outcome counts; and outcome rates ending in `_per1000_py_alive` for infections, cases, hospitalizations, and deaths.

The merge step must precede summarization. Summarization must precede figure generation because the figure script requires both:

```
summary_draws.csv
analysis_tables/relative_difference_draws.csv
```


