"""Swappable data steps (the Seams of the data module).

The data pipeline in `data.py` has a fixed order. Three steps in that order
are Seams: you can swap their behaviour from the config file without touching
any caller.

    step              config key        Port (Interface)   fitted on
    ----------------  ----------------  -----------------  -----------
    feature selection data.features     FeatureSelector    train only
    scaling           data.scaler       Scaler             train only
    sampling          data.sampler      Sampler            train only (val/test never sampled)

How to add a new variant (an Adapter):

1. Write a class that follows the Port below (same method names and shapes).
2. Register it in the matching `*_REGISTRY` dict with a short name.
3. Use it from a config, e.g. `scaler: {name: robust}`.

Nothing else changes: `data.load_splits` and every later module stay the same.

A config spec is either a name (`"standard"`) or a mapping with a `name` key
plus keyword arguments for the class (`{name: drop, columns: [proto]}`).
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol

import numpy as np
import pandas as pd
from sklearn import preprocessing


# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------


class FeatureSelector(Protocol):
    """Chooses which raw feature columns the model will see.

    Works on raw column names (before one-hot encoding and scaling), so a
    config can say "drop proto" in plain words.

    - `fit` sees the training rows only. It may look at labels (`y`), for
      example to rank features, but must not look at val/test.
    - `transform` returns a DataFrame with a subset of the input columns and
      the same rows in the same order. It must not create new rows.
    """

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "FeatureSelector": ...

    def transform(self, X: pd.DataFrame) -> pd.DataFrame: ...


class Scaler(Protocol):
    """Rescales the numeric feature columns.

    - `fit` sees the training rows only (otherwise test information leaks
      into training).
    - `transform` keeps the shape (n_rows, n_numeric_features) and returns
      finite float values.
    - One-hot columns are not scaled; they are already 0/1.
    """

    def fit(self, X: np.ndarray) -> "Scaler": ...

    def transform(self, X: np.ndarray) -> np.ndarray: ...


class Sampler(Protocol):
    """Changes the class balance of the training set.

    Called on the training set only. Val and test keep the real class
    balance, so their numbers stay comparable between experiments.

    Returns row positions (indices into the training arrays), so features,
    labels and attack types always move together. Positions may repeat
    (oversampling) or be left out (undersampling).
    """

    def sample(self, y: np.ndarray, attack_type: np.ndarray, seed: int) -> np.ndarray: ...


# ---------------------------------------------------------------------------
# Feature selection adapters
# ---------------------------------------------------------------------------


class AllFeatures:
    """Keep every feature column (baseline)."""

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "AllFeatures":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return X


class DropColumns:
    """Drop the named columns, e.g. features you think are noise or leakage."""

    def __init__(self, columns: list[str]):
        self.columns = list(columns)

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "DropColumns":
        unknown = sorted(set(self.columns) - set(X.columns))
        if unknown:
            raise ValueError(f"DropColumns: unknown columns {unknown}")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.drop(columns=self.columns)


class DropConstant:
    """Drop columns that have a single value in the training set."""

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "DropConstant":
        self.columns = [c for c in X.columns if X[c].nunique(dropna=False) <= 1]
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.drop(columns=self.columns)


# ---------------------------------------------------------------------------
# Scaler adapters
# ---------------------------------------------------------------------------


class NoScaling:
    """Leave values as they are (useful to show why scaling matters)."""

    def fit(self, X: np.ndarray) -> "NoScaling":
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return X


class SklearnScaler:
    """Wraps a scikit-learn scaler so it follows the Scaler Port."""

    def __init__(self, scaler: Any):
        self._scaler = scaler

    def fit(self, X: np.ndarray) -> "SklearnScaler":
        self._scaler.fit(X)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return self._scaler.transform(X)


class LogStandard:
    """sign(x) * log1p(|x|), then standardise.

    Some RT-IoT2022 features reach ~2e10, so plain standardisation squeezes
    most rows into a tiny range. The log step spreads them out first.
    """

    def __init__(self) -> None:
        self._scaler = preprocessing.StandardScaler()

    def fit(self, X: np.ndarray) -> "LogStandard":
        self._scaler.fit(self._log(X))
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return self._scaler.transform(self._log(X))

    @staticmethod
    def _log(X: np.ndarray) -> np.ndarray:
        return np.sign(X) * np.log1p(np.abs(X))


# ---------------------------------------------------------------------------
# Sampler adapters
# ---------------------------------------------------------------------------


class NoSampling:
    """Use the training set as it is (baseline)."""

    def sample(self, y: np.ndarray, attack_type: np.ndarray, seed: int) -> np.ndarray:
        return np.arange(len(y))


class UndersampleAttack:
    """Randomly drop attack rows until attack:normal is at most `ratio`:1.

    Attack rows are dropped proportionally inside each attack type, so rare
    attack types are not wiped out.
    """

    def __init__(self, ratio: float = 1.0):
        if ratio <= 0:
            raise ValueError("UndersampleAttack: ratio must be > 0")
        self.ratio = ratio

    def sample(self, y: np.ndarray, attack_type: np.ndarray, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        normal_idx = np.flatnonzero(y == 0)
        attack_idx = np.flatnonzero(y == 1)
        target = int(len(normal_idx) * self.ratio)
        if target >= len(attack_idx):
            return np.arange(len(y))

        keep_share = target / len(attack_idx)
        kept = []
        for kind in np.unique(attack_type[attack_idx]):
            rows = attack_idx[attack_type[attack_idx] == kind]
            n_keep = max(1, round(len(rows) * keep_share))
            kept.append(rng.choice(rows, size=n_keep, replace=False))
        return np.sort(np.concatenate([normal_idx, *kept]))


# ---------------------------------------------------------------------------
# Registries and builders
# ---------------------------------------------------------------------------

FEATURE_SELECTORS: dict[str, Callable[..., FeatureSelector]] = {
    "all": AllFeatures,
    "drop": DropColumns,
    "drop_constant": DropConstant,
}

SCALERS: dict[str, Callable[..., Scaler]] = {
    "none": NoScaling,
    "standard": lambda: SklearnScaler(preprocessing.StandardScaler()),
    "minmax": lambda: SklearnScaler(preprocessing.MinMaxScaler()),
    "robust": lambda: SklearnScaler(preprocessing.RobustScaler()),
    "log_standard": LogStandard,
}

SAMPLERS: dict[str, Callable[..., Sampler]] = {
    "none": NoSampling,
    "undersample": UndersampleAttack,
}


def build_feature_selector(spec: str | Mapping[str, Any]) -> FeatureSelector:
    return _build(spec, FEATURE_SELECTORS, "data.features")


def build_scaler(spec: str | Mapping[str, Any]) -> Scaler:
    return _build(spec, SCALERS, "data.scaler")


def build_sampler(spec: str | Mapping[str, Any]) -> Sampler:
    return _build(spec, SAMPLERS, "data.sampler")


def _build(spec: str | Mapping[str, Any], registry: Mapping[str, Callable[..., Any]], key: str) -> Any:
    if isinstance(spec, str):
        name, params = spec, {}
    else:
        params = dict(spec)
        name = params.pop("name", None)
    if name not in registry:
        raise ValueError(f"{key}: unknown name {name!r}; choose one of {sorted(registry)}")
    return registry[name](**params)
