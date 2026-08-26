# Cite 
Xinmeng Zhao, PhD, Michael Melgar, MD, Diya Surie, MD, Jefferson Jones, MD MPH, Emily D. Carter, PhD, Amadea Britton, MD, Ismael R. Ortega-Sanchez, PhD, Heidi Moline, MD, Brian Gurbaxani, PhD, Phillip P. Salvatore, PhD SM.Optimal Timing of Revaccination against Respiratory Syncytial Virus among Older Adults in the U.S. – a Transmission Modeling Study (Submission to the journal)

# Disclaimer
The findings and conclusions in this report are those of the authors and do not necessarily represent the official position of the Centers for Disease Control and Prevention. 

# Disclosure of Generative AI Use
ChatGPT 5.6 was used to clean, debug and comment the code. The first author reviewed, tested and validated all code and take full responsibility of all content.

# Code Overview

## Purpose and scope

This folder contains the analytical stage of the older-adult RSV revaccination analysis. It begins with draw-level model-output shards and then:

1. merges the shards into one draw-level file;
2. calculates absolute outcome summaries and paired relative differences; and
3. creates the combined outcome figure.


## Contents

```
cleaned_code/
|-- results/                      Included input shard and generated outputs
|   `-- older_adult_vax/
|       |-- shards/draws_0_4/     Included sample input shard
|       `-- sample_run/           Created when the commands below are run
|-- scripts/                      Merge and summary-table scripts
|-- visualization/                Figure-generation script
|-- pyproject.toml                Python dependency specification
`-- README.md                     This guide
```

The included `results/older_adult_vax/shards/draws_0_4/` folder is the only input shard included in this package. The `results/older_adult_vax/sample_run/`, `analysis_tables/`, and `visualization/` folders do not exist until the corresponding execution steps create them.

## Folders and files

### `results/older_adult_vax/shards/draws_0_4/`: included sample model-output shard

- `summary_draws.csv`: required input to the merge step; contains draw identifiers, scenario metadata, outcome counts, person-years alive, and outcome rates.
- `summary_quantiles.csv`: shard-level quantile summary produced by the upstream model run; it is included for reference and is not read by the analytical scripts.
- `posterior_draws_used.csv`: identifies the posterior draws used by the upstream model run; included for provenance and not read by the analytical scripts.
- `manifest.json`: records the scenario settings and provenance of the sample shard.
- `hospitalizations_timeseries_vaccinated_weekly.npz`: weekly hospitalization time series for the vaccinated primary group; included for reference and not read by the analytical scripts.

### `scripts/`: analytical data-processing scripts

- `merge_older_adult_vax_shards.py`: reads one `summary_draws.csv` file from each shard subfolder and writes a sorted, merged draw-level CSV.
- `summarize_older_adult_vax.py`: reads the merged CSV and writes absolute-outcome and paired relative-difference summary tables.

### `visualization/`: figure-generation script

- `older_adult_vax_diagrams.py`: reads the merged CSV and paired relative-difference table, then creates the combined outcome figure.

### Top-level files

- `pyproject.toml`: specifies the supported Python version and required package versions.
- `README.md`: explains the package, inputs, execution steps, and expected outputs.

## Requirements, installation, and tested platform

Use Python 3.10 or newer. The required packages are NumPy, pandas, and matplotlib; their minimum versions are specified in `pyproject.toml`.

The package was smoke-tested on Windows 10 Enterprise 24H2 (build 26100.9168) with Python 3.12.5, NumPy 2.1.0, pandas 2.2.2, and matplotlib 3.10.0. macOS compatibility has not been tested.

From the `cleaned_code` directory, install the dependencies:

```bash
python -m pip install numpy pandas matplotlib
```

Alternatively, install the project metadata and its dependencies:

```bash
python -m pip install .
```

## Expected input schema and workflow order

Each immediate subfolder of the directory passed to `--shards-root` must contain a `summary_draws.csv` file. It must include draw identifiers; scenario and recovery-curve labels; dose-2 interval; population group; person-years alive; outcome counts; and outcome-rate columns ending in `_per1000_py_alive` for infections, cases, hospitalizations, and deaths.

Run the scripts in this order:

1. Merge input shards into `summary_draws.csv`.
2. Create summary tables from that merged file.
3. Create the figure from the merged file and `relative_difference_draws.csv`.

## Run the included sample

Run the following commands from the `cleaned_code` directory. They create `results/older_adult_vax/sample_run/` and do not modify the included `draws_0_4` sample shard.

### 1. Merge the sample shard

```bash
python scripts/merge_older_adult_vax_shards.py --shards-root results/older_adult_vax/shards --outdir results/older_adult_vax/sample_run
```

Expected result:

- `results/older_adult_vax/sample_run/summary_draws.csv`: merged draw-level analytical input.
- Console message reporting one shard and 320 draw-level rows for the included sample.

### 2. Create summary tables

```bash
python scripts/summarize_older_adult_vax.py --results-dir results/older_adult_vax/sample_run
```

Expected result:

- `results/older_adult_vax/sample_run/analysis_tables/absolute_outcome_summary.csv`: median, lower 95%, and upper 95% outcome rates by scenario, interval, group, and outcome.
- `results/older_adult_vax/sample_run/analysis_tables/relative_difference_draws.csv`: paired draw-level relative differences versus the no-revaccination baseline.
- `results/older_adult_vax/sample_run/analysis_tables/relative_difference_summary.csv`: median and 95% interval of the paired relative differences.
- For the included sample, these three files contain 288, 1,200, and 240 data rows, respectively.

### 3. Create the combined figure

```bash
python visualization/older_adult_vax_diagrams.py --results-dir results/older_adult_vax/sample_run --outdir results/older_adult_vax/sample_run/visualization
```

Expected result:

- `results/older_adult_vax/sample_run/visualization/older_adult_vax_combined_outcome_relative_difference_vaccinated_primary_per100k_per1000_py_alive.png`: combined figure for hospitalizations, cases, and deaths.
- The figure shows posterior medians, 50% and 95% credible intervals, the no-dose-2 reference, the dose-2 interval with the lowest posterior median, and paired relative differences for Scenarios A--C.

## Help

To view the arguments for any script, run it with `--help`. For example:

```bash
python scripts/summarize_older_adult_vax.py --help
```
