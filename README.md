# Older-adult RSV revaccination analysis

## Citation

Xinmeng Zhao, PhD, Michael Melgar, MD, Diya Surie, MD, Jefferson Jones, MD MPH, Emily D. Carter, PhD, Amadea Britton, MD, Ismael R. Ortega-Sanchez, PhD, Heidi Moline, MD, Brian Gurbaxani, PhD, Phillip P. Salvatore, PhD SM. *Optimal Timing of Revaccination against Respiratory Syncytial Virus among Older Adults in the U.S. – a Transmission Modeling Study.*

## Disclaimer

The findings and conclusions in this report are those of the authors and do not necessarily represent the official position of the Centers for Disease Control and Prevention.

## Disclosure of generative AI use

ChatGPT 5.6 was used to clean, debug, and comment the code. The first author reviewed, tested, and validated all code and takes full responsibility for its content.

## Purpose and scope

This package post-processes draw-level output from the older-adult RSV revaccination transmission model. It:

1. merges draw-level model-output shards;
2. calculates absolute outcome summaries and paired relative differences; and
3. creates a combined outcome figure.

The included data are a small sample shard for demonstrating the workflow. They are not the complete model-output dataset required to reproduce every analysis result.

## System requirements

- Operating system: Windows 10 Enterprise 24H2 (build 26100.9168) was tested. macOS and Linux compatibility were not tested.
- Python: 3.10 or newer; the tested version was Python 3.12.5.
- Python packages: NumPy, pandas, and matplotlib. Tested versions were NumPy 2.1.0, pandas 2.2.2, and matplotlib 3.10.0. Minimum supported versions are specified in `pyproject.toml`.
- Hardware: no non-standard hardware is required. The workflow is CPU-based and should run on a normal desktop computer with sufficient storage for the input and output CSV files.
- Installation time: typically less than 5 minutes when Python is already installed; network speed and whether packages are already cached determine the actual time.

## Installation

Open a terminal in this `cleaned_code` directory. Install the dependencies with:

```bash
python -m pip install numpy pandas matplotlib
```

Alternatively, install this project and the dependency versions allowed by `pyproject.toml`:

```bash
python -m pip install .
```

To confirm that the command-line interfaces are available, run:

```bash
python scripts/merge_older_adult_vax_shards.py --help
python scripts/summarize_older_adult_vax.py --help
python visualization/older_adult_vax_diagrams.py --help
```

## Contents

```
cleaned_code/
|-- results/                      Included input shard and generated outputs
|   `-- older_adult_vax/
|       |-- shards/draws_0_4/     Included sample input shard
|       `-- sample_run/           Created by the demo commands
|-- scripts/                      Merge and summary-table scripts
|-- visualization/                Figure-generation script
|-- pyproject.toml                Python dependency specification
`-- README.md                     This guide
```

### Included sample shard

`results/older_adult_vax/shards/draws_0_4/` contains:

- `summary_draws.csv`: draw-level outcomes, scenario metadata, person-years alive, counts, and rates; this is the required input to the merge step.
- `summary_quantiles.csv`: upstream shard-level quantile summary, included for reference and not read by these scripts.
- `posterior_draws_used.csv`: provenance for the upstream posterior draws, included for reference and not read by these scripts.
- `manifest.json`: scenario settings and provenance for the sample shard.
- `hospitalizations_timeseries_vaccinated_weekly.npz`: weekly hospitalization time series, included for reference and not read by these scripts.

### Scripts

- `scripts/merge_older_adult_vax_shards.py`: reads one `summary_draws.csv` from each immediate shard subfolder and writes a sorted merged draw-level CSV.
- `scripts/summarize_older_adult_vax.py`: writes absolute-outcome summaries, paired relative-difference draws, and relative-difference summaries.
- `visualization/older_adult_vax_diagrams.py`: creates the combined figure for hospitalizations, cases, and deaths.

## Demo

Run these commands from the `cleaned_code` directory. They create `results/older_adult_vax/sample_run/` and do not modify the included input shard.

### 1. Merge the sample shard

```bash
python scripts/merge_older_adult_vax_shards.py --shards-root results/older_adult_vax/shards --outdir results/older_adult_vax/sample_run
```

Expected output: `results/older_adult_vax/sample_run/summary_draws.csv`, containing one merged shard and 320 draw-level rows.

### 2. Create summary tables

```bash
python scripts/summarize_older_adult_vax.py --results-dir results/older_adult_vax/sample_run
```

Expected files in `results/older_adult_vax/sample_run/analysis_tables/`:

- `absolute_outcome_summary.csv`: medians and central 95% intervals for outcome rates.
- `relative_difference_draws.csv`: paired draw-level relative differences versus the no-revaccination baseline.
- `relative_difference_summary.csv`: medians and central 95% intervals for paired relative differences.

For the included sample, these files contain 288, 1,200, and 240 data rows, respectively.

### 3. Create the figure

```bash
python visualization/older_adult_vax_diagrams.py --results-dir results/older_adult_vax/sample_run --outdir results/older_adult_vax/sample_run/visualization
```

Expected output:

`results/older_adult_vax/sample_run/visualization/older_adult_vax_combined_outcome_relative_difference_vaccinated_primary_per100k_per1000_py_alive.png`

The figure shows posterior medians, 50% and 95% credible intervals, the no-dose-2 reference, the dose-2 interval with the lowest posterior median, and paired relative differences for Scenarios A–C.

### Demo runtime

On the tested Windows desktop, the complete three-step demo took approximately 13 seconds. Runtime will vary with hardware, input size, and the number of shards. No special hardware or long-running computation is required for this post-processing demo.

## Instructions for use with your own data

1. Place one model-output shard in each immediate subfolder of a directory passed to `--shards-root`.
2. Ensure every shard contains a file named `summary_draws.csv` with the required columns below.
3. Run the merge, summary, and visualization commands in that order, replacing the sample paths with your own paths.

Each `summary_draws.csv` must contain these columns:

```text
draw_row, posterior_draw_id, pre_posterior_draw_id,
posterior_source_row, posterior_source_wave, posterior_source_task_id,
posterior_source_sample_in_task, scenario, boost_scenario,
boost_recovery_curve, k_years, dose2_interval_years,
is_no_revaccination, group, person_years_alive, infections, cases,
hospitalizations, deaths, infections_per1000_py_alive,
cases_per1000_py_alive, hospitalizations_per1000_py_alive,
deaths_per1000_py_alive
```

The rate columns are outcomes per 1,000 person-years alive. The summary script compares each positive-`k_years` result with the matching draw-level `k_years = 0` no-revaccination baseline. Relative differences are calculated as `(revaccination rate - baseline rate) / baseline rate`.

The supplied summary and visualization scripts expect the recovery-curve labels `no_revaccination`, `scenario_a`, `scenario_b`, and `scenario_c`. If your data use different labels or a different schema, update the scripts consistently before running the workflow.

## Reproduction instructions

The package reproduces the included post-processing demonstration. Reproducing the complete quantitative results requires the complete upstream model-output shards and their associated provenance. The upstream transmission-model code, model inputs, and full posterior-draw outputs are not included here.

For a complete reproduction:

1. obtain the complete upstream shard set and confirm its provenance;
2. place the shards under a common directory using the immediate-subfolder layout described above;
3. run the three workflow steps in order; and
4. retain the generated merged CSV, analysis tables, and figure together with the software versions used.

## Units and interpretation

- Absolute outcome rates are reported per 1,000 person-years alive in the analytical tables.
- The figure displays the corresponding outcome rates per 100,000 person-years alive for the vaccinated primary group.
- “Relative difference” is a paired draw-level comparison with the no-revaccination baseline; it is not calculated by subtracting summary medians or quantiles.
- The reported intervals are central 95% intervals calculated from the draw-level values.

## Help

To view the arguments for any script, run it with `--help`; for example:

```bash
python scripts/summarize_older_adult_vax.py --help
```
