"""Data module: from the raw RT-IoT2022 CSV to model-ready number arrays.

Interface (all a caller needs):

    splits = load_splits(data_cfg, seed)
    splits.train.X, splits.train.y, splits.train.attack_type   # same for .val and .test

The model only ever sees `X` (float32 numbers) and `y` (0 = normal, 1 = attack).
It never sees the CSV, column names or text labels.

Pipeline (fixed order; steps marked [Seam] are chosen in the config, see
`transforms.py`):

    1. read CSV, drop the row-number column `no`, clean the label text
    2. map Attack_type -> y (0 normal / 1 attack)
    3. remove duplicate rows
    4. split train / val / test, stratified by Attack_type      <- depends only on seed + ratios
        train: its used to update the weights of the model while training.
        val: its used to evaluate the model during training, to choose the best weights.
        test: its used to evaluate the final model after training, to report the final results.
    5. [Seam] feature selection        data.features   (fit on train)
    6. one-hot encode proto / service                  (fit on train; unseen values -> all zeros)
    7. [Seam] scale numeric columns    data.scaler     (fit on train)
    8. [Seam] resample training rows   data.sampler    (train only)

Guarantees (tests check these):

- The test set is the same rows for every experiment with the same seed and
  split ratios, whatever features / scaler / sampler you pick. Steps 5-8 run
  after the split, so they cannot change it. `test_fingerprint` lets you check.
- Nothing is fitted on val or test.
- Val and test keep the real class balance (no sampling).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

from .transforms import build_feature_selector, build_sampler, build_scaler

LABEL_COLUMN = "Attack_type"
ID_COLUMN = "no"
CATEGORICAL_COLUMNS = ("proto", "service")

# Assumption, not yet checked against the dataset paper: these three types are
# normal IoT device traffic; every other type is an attack.
NORMAL_TYPES = frozenset({"Thing_Speak", "MQTT_Publish", "Wipro_bulb"})


@dataclass(frozen=True)
class Split:
    """One part of the data (train, val or test)."""

    X: np.ndarray  # float32, shape (n_rows, n_features)
    y: np.ndarray  # float32, shape (n_rows,); 0 = normal, 1 = attack
    attack_type: (
        np.ndarray
    )  # str, shape (n_rows,); original label, for per-type results
    row_ids: np.ndarray  # int, shape (n_rows,); 0-based data row position in the CSV


@dataclass(frozen=True)
class Splits:
    train: Split
    val: Split
    test: Split
    feature_names: list[str]  # names of the columns of X, after one-hot encoding

    @property
    def n_features(self) -> int:
        return len(self.feature_names)

    @property
    def test_fingerprint(self) -> str:
        """Short hash of the test row ids. Equal fingerprint = same test set."""
        ids = np.sort(self.test.row_ids).astype(np.int64).tobytes()
        return hashlib.sha256(ids).hexdigest()[:12]


def load_splits(cfg: Mapping[str, Any], seed: int) -> Splits:
    """Build train / val / test arrays as described in the module docstring.

    cfg keys: path, split ([train, val, test] ratios), features, scaler, sampler.
    """
    raw = load_raw(cfg["path"])
    train_df, val_df, test_df = split_rows(raw, cfg["split"], seed)

    feature_cols = [c for c in raw.columns if c != LABEL_COLUMN]
    selector = build_feature_selector(cfg["features"]).fit(
        train_df[feature_cols], _labels(train_df)
    )
    kept = list(selector.transform(train_df[feature_cols].head(0)).columns)
    categorical = [c for c in kept if c in CATEGORICAL_COLUMNS]
    numeric = [c for c in kept if c not in CATEGORICAL_COLUMNS]
    if not kept:
        raise ValueError("data.features removed every column")

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    if categorical:
        encoder.fit(train_df[categorical])
    scaler = build_scaler(cfg["scaler"]).fit(train_df[numeric].to_numpy(np.float64))

    def to_split(df: pd.DataFrame) -> Split:
        parts = [scaler.transform(df[numeric].to_numpy(np.float64))]
        if categorical:
            parts.append(encoder.transform(df[categorical]))
        return Split(
            X=np.hstack(parts).astype(np.float32),
            y=_labels(df),
            attack_type=df[LABEL_COLUMN].to_numpy(),
            row_ids=df.index.to_numpy(),
        )

    train = to_split(train_df)
    keep = build_sampler(cfg["sampler"]).sample(train.y, train.attack_type, seed)
    train = Split(
        train.X[keep], train.y[keep], train.attack_type[keep], train.row_ids[keep]
    )

    onehot_names = (
        list(encoder.get_feature_names_out(categorical)) if categorical else []
    )
    return Splits(train, to_split(val_df), to_split(test_df), numeric + onehot_names)


def load_raw(path: str | Path) -> pd.DataFrame:
    """Steps 1-3: read, clean labels, remove duplicate rows.

    Returns features + Attack_type. The index is the row position in the CSV
    (used as row id). `no` is dropped: it restarts from 0 for every attack
    type, so it is not a unique id and carries no traffic information.
    A few rows have identical features but different labels; they are kept.
    """
    df = pd.read_csv(path).drop(columns=[ID_COLUMN])
    df[LABEL_COLUMN] = (
        df[LABEL_COLUMN].astype(str).str.strip()
    )  # labels end with "\r" in the file
    return df.drop_duplicates()


def split_rows(
    df: pd.DataFrame, ratios: list[float], seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Step 4: stratified train / val / test split by Attack_type."""
    if len(ratios) != 3 or not np.isclose(sum(ratios), 1.0):
        raise ValueError(
            f"data.split must be three ratios that add up to 1, got {ratios}"
        )
    train_r, val_r, test_r = ratios
    train_df, rest = train_test_split(
        df, train_size=train_r, stratify=df[LABEL_COLUMN], random_state=seed
    )
    val_df, test_df = train_test_split(
        rest,
        test_size=test_r / (val_r + test_r),
        stratify=rest[LABEL_COLUMN],
        random_state=seed,
    )
    return train_df, val_df, test_df


def _labels(df: pd.DataFrame) -> np.ndarray:
    return (~df[LABEL_COLUMN].isin(NORMAL_TYPES)).to_numpy(np.float32)
