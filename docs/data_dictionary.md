# Data Dictionary

`configs/datasets.toml` is the authoritative pilot registry. Each entry follows `schemas/dataset_registry.schema.json` and is validated by `DatasetSpec` and the loader. `openml_id` and `version` identify the pinned source; `family` groups related datasets for evaluation; `clinical` marks clinical holdouts. Feature-role lists partition predictors and excluded columns. `positive_class` maps to target value 1.

Run-log and meta-dataset schemas are provisional for the future runner. Their string `dataset_id` will identify a registry entry by its unique `name`; it is not a replacement for the source OpenML ID.
