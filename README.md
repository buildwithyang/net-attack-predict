# IoT Network Attack Detection Using Neural Networks

A small PyTorch MLP that reads IoT network flow features (RT-IoT2022) and says
**normal** or **attack**. This is a learning project: the goal is to master the whole training
process of an MLP, end to end: data -> model -> train -> validate -> test.

## Project layout

The standard "src layout" used by most Python ML projects:

```
.
├── README.md            this file
├── pyproject.toml       package name, dependencies, pytest settings
├── configs/             one YAML file = one experiment (no code changes needed)
│   ├── baseline.yaml
│   ├── training/        main experiments: scaling, learning rate, network size, overfitting
│   └── imbalance/       extra experiments: class imbalance (not the main story)
├── data/
│   └── raw/             original data, never edited (the .csv is unzipped from the .zip)
├── src/iotids/          the library: reusable code, imported as `iotids`
│   ├── data.py          CSV -> train/val/test number arrays     (Seams in transforms.py)
│   ├── transforms.py    feature selection / scaling / sampling variants
│   ├── model.py         builds the MLP from the config
│   ├── train.py         the training loop (forward, loss, backward, step) + early stopping
│   ├── decision.py      picks the attack threshold on the validation set (Seam)
│   ├── evaluate.py      test numbers: detection rate, false alarm rate, per type
│   ├── plots.py         the charts
│   └── experiment.py    train -> validate -> test -> save (the only module that writes files)
├── scripts/             command-line entry points: thin, they only call src/
│   ├── train.py         run one or more configs
│   ├── compare.py       put several finished runs in one chart + table
│   └── start.py         beginner menu behind start.command / start.bat
├── tests/               checks each module through its interface
└── runs/                outputs, one folder per experiment (generated, safe to delete)
```

`src/` is code you import; `scripts/` is code you run. `data/raw/` and
`configs/` are inputs; `runs/` is output. Anything in `.gitignore` can be rebuilt.

## Easiest way: the launcher (no programming needed)

1. Install Python 3.12 from <https://www.python.org/downloads/> (Windows: tick "Add python.exe to PATH").
2. Double-click **`start.command`** (macOS) or **`start.bat`** (Windows) in this folder.
   On macOS, if it says "cannot be opened", right-click it → Open. Or in Terminal: `bash start.command`.
3. The first time, it creates a private Python environment in `.venv/` and installs the
   packages (a few hundred MB, 1–10 minutes). After that it starts in seconds.
4. Pick from the menu: run the baseline, pick experiments, compare runs, open the results.

To start over, delete the `.venv` folder and double-click again. The launcher code is in `scripts/start.py`.

## Run it

From the project root:

```bash
pip install -e ".[dev]"                     # once; -e = use src/ directly, edits apply at once
unzip data/raw/rt-iot2022.zip -d data/raw/  # once
pytest                                      # 13 checks, about 5 s
python scripts/train.py configs/baseline.yaml   # about 30 s on a laptop CPU

# run all training experiments, then compare one group (reference first)
python scripts/train.py configs/training/*.yaml
python scripts/compare.py runs/baseline runs/lr_high runs/lr_low --title "Learning rate" --out runs/compare_lr
```

`compare.py` writes `<out>.png` (loss curves + false alarms + missed attacks)
and `<out>.md` (table). Up to 4 runs; it refuses runs with different test sets.

Each run writes `runs/<name>/`:

| File | What it shows |
| --- | --- |
| `summary.png` | One page for the slides: headline numbers + the four charts below |
| `training_curves.png` | Train and validation loss per epoch; the kept epoch |
| `confusion_matrix.png` | Test set: normal/attack, true vs predicted, counts and row % |
| `per_type.png` | Test set: % flagged as attack for each original traffic type |
| `score_distribution.png` | Test set: model scores for normal vs attack, with the threshold |
| `metrics.json` | All numbers, including `test_fingerprint` (same value = same test set) |
| `history.csv` | Loss per epoch |
| `config.yaml` | The exact config used |

Same config + same seed gives exactly the same numbers.

## How the code is split

Each module only talks to the next one through a small interface:

```
load_splits(data_cfg, seed)           -> Splits (train / val / test: X, y, attack_type)
build_model(model_cfg, n_features, seed) -> torch MLP (outputs one logit per row)
fit(model, train, val, train_cfg, seed) -> History (losses per epoch)
predict_proba(model, X)               -> attack probability per row
choose_threshold(val_scores, val_y, decision_cfg) -> threshold
evaluate(test_scores, test, threshold) -> Report
```

The model only sees number arrays `X` and labels `y`. It never sees the CSV.

## Improving one module without breaking the others

Every experiment is a copy of `configs/baseline.yaml` with **one section
changed**. Keep `seed` and `data.split` unchanged so the test set stays the
same; check `test_fingerprint` in `metrics.json`.

| To try | Change | Options now |
| --- | --- | --- |
| Remove noisy features | `data.features` | `all`, `drop_constant`, `{name: drop, columns: [...]}` |
| Another normalisation | `data.scaler` | `none`, `standard`, `minmax`, `robust`, `log_standard` |
| Fix class imbalance in data | `data.sampler` | `none`, `{name: undersample, ratio: 1.0}` |
| Network size / shape | `model.*` | `hidden`, `activation`, `dropout` |
| Training settings | `train.*` | `epochs`, `batch_size`, `optimizer`, `lr`, `early_stopping` |
| Fix class imbalance in loss | `train.class_weight` | `none`, `balanced`, a number |
| Trade false alarms vs missed attacks | `decision` | `fixed {value}`, `max_fpr {fpr}` |

### Adding a new variant (Adapter) to a Seam

The data Seams are documented at the top of `src/iotids/transforms.py`. In short:

1. Write a class with the same methods as the Port (`FeatureSelector`, `Scaler` or `Sampler`).
2. Add it to the registry dict in the same file with a short name.
3. Use the name in a config.
4. Run `pytest`. The data tests check that the test set does
   not change and nothing is fitted on val/test.

Threshold rules work the same way in `decision.py` (`RULES`).

## Data notes

- Source: <https://www.kaggle.com/datasets/supplejade/rt-iot2022real-time-internet-of-things>, file `data/raw/rt-iot2022.zip` -> `RT_IOT2022.csv` (123,117 rows, 85 columns).
- `Attack_type` values end with `\r` in the file; the loader strips it.
- Column `no` restarts at 0 for every attack type, so it is not an id. It is dropped; the row position in the CSV is used as id.
- 5,195 duplicate rows are removed before splitting (otherwise the same row can be in train and test). 117,922 rows remain.
- Split: 70 / 15 / 15, stratified by `Attack_type`.
- **Assumption**: `Thing_Speak`, `MQTT_Publish`, `Wipro_bulb` are normal traffic; all other types are attacks (see `NORMAL_TYPES` in `data.py`). Not yet checked against the dataset paper.
- About 90% of rows are attacks, so accuracy alone is misleading. Look at the false alarm rate and the per-type chart.
