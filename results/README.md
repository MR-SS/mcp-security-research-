# Results Artifact Layout

This directory contains machine-readable outputs that support every number, table, and figure in the paper. Raw registry snapshots remain in `data/raw/`; this directory contains derived, analysis-ready results.

## Directory layout

```text
results/
  detector_validation/
    validation_sample.csv
    adjudications.csv
    precision_by_class.csv
  live_experiments/
    experiment_manifest.csv
    raw_responses.jsonl
    outcomes.csv
    asr_by_model.csv
  aggregate/
    capability_composition.csv
    poisoning_candidates.csv
    crawl_depth_sensitivity.csv
  figures/
    figure_data/
    figures/
  paper_tables/
    table1_composition.csv
    table2_detector_precision.csv
    table3_live_experiments.csv
```

## Core CSV schemas

### `detector_validation/validation_sample.csv`

| Column | Type | Description |
|---|---|---|
| `sample_id` | string | Stable unique identifier |
| `server_id` | string | Registry/server identifier |
| `tool_id` | string | Tool identifier, when applicable |
| `detector_version` | string | Detector version, e.g. `v1` or `v2` |
| `detector_class` | string | Pattern or risk category |
| `candidate_text` | string | Exact text that triggered the detector |
| `sample_strategy` | string | `top_k`, `stratified_random`, or `random_negative` |
| `sample_weight` | number | Sampling weight, if applicable |

### `detector_validation/adjudications.csv`

| Column | Type | Description |
|---|---|---|
| `sample_id` | string | Matches `validation_sample.csv` |
| `annotator_id` | string | Anonymized annotator identifier |
| `label` | string | `true_positive`, `false_positive`, or `uncertain` |
| `rationale` | string | Short evidence-based explanation |
| `adjudicated_label` | string | Final label after conflict resolution |
| `adjudication_date` | date | UTC date of final decision |

### `live_experiments/experiment_manifest.csv`

| Column | Type | Description |
|---|---|---|
| `experiment_id` | string | Stable experiment identifier |
| `model_name` | string | Exact model name and version |
| `model_provider` | string | Model provider |
| `temperature` | number | Decoding temperature |
| `max_tokens` | integer | Output-token limit |
| `system_prompt_hash` | string | SHA-256 of the exact system prompt |
| `case_id` | string | Test-case identifier |
| `case_category` | string | Attack or control category |
| `success_criterion` | string | Predefined success condition |
| `seed` | integer | Random seed where supported |

### `live_experiments/outcomes.csv`

| Column | Type | Description |
|---|---|---|
| `experiment_id` | string | Matches manifest |
| `trial_index` | integer | Repeat number |
| `outcome` | string | `attack_success`, `refusal`, `safe_completion`, `error`, or `ambiguous` |
| `tool_called` | string | Tool invoked, if any |
| `safety_flag` | boolean | Whether a safety control triggered |
| `judge_method` | string | `rule_based`, `llm_judge`, or `human` |
| `notes` | string | Optional adjudication note |

## Rules

1. Every quoted paper number must be traceable to a file in `results/` and a script or command that generated it.
2. Do not manually edit derived CSV files; regenerate them from frozen inputs.
3. Keep raw model responses in `raw_responses.jsonl`; put only normalized outcomes in CSV files.
4. Include detector version, dataset snapshot identifier, model version, prompt hash, and date in every result file or its manifest.
5. Report uncertainty for key rates, such as confidence intervals for precision and ASR.
6. Separate exploratory results from confirmatory results; do not mix them in the same paper table.
