"""Data module: checks the guarantees listed in data.py, through load_splits only."""

import numpy as np
import pytest
from conftest import DATA_PATH

from iotids.data import NORMAL_TYPES, load_splits

BASE = {"path": DATA_PATH, "split": [0.7, 0.15, 0.15], "features": "all", "scaler": "standard", "sampler": "none"}


@pytest.fixture(scope="module")
def base():
    return load_splits(BASE, seed=42)


def test_parts_are_disjoint_and_duplicates_removed(base):
    ids = [set(s.row_ids) for s in (base.train, base.val, base.test)]
    assert not (ids[0] & ids[1] or ids[0] & ids[2] or ids[1] & ids[2])
    assert sum(len(i) for i in ids) == 117_922  # 123,117 rows minus 5,195 duplicates


def test_labels_follow_attack_type(base):
    for split in (base.train, base.val, base.test):
        assert not any("\r" in t for t in split.attack_type)
        assert np.array_equal(split.y == 0, np.isin(split.attack_type, list(NORMAL_TYPES)))


def test_test_set_does_not_depend_on_preprocessing(base):
    other = load_splits(
        {**BASE, "features": {"name": "drop", "columns": ["proto", "service"]}, "scaler": "minmax",
         "sampler": {"name": "undersample", "ratio": 1.0}},
        seed=42,
    )
    assert other.test_fingerprint == base.test_fingerprint
    assert np.array_equal(other.val.row_ids, base.val.row_ids)
    assert other.n_features < base.n_features


def test_sampling_changes_train_only(base):
    sampled = load_splits({**BASE, "sampler": {"name": "undersample", "ratio": 1.0}}, seed=42)
    n_normal = int((sampled.train.y == 0).sum())
    assert n_normal == int((base.train.y == 0).sum())
    assert abs(int(sampled.train.y.sum()) - n_normal) <= len(np.unique(base.train.attack_type))
    assert set(sampled.train.attack_type) == set(base.train.attack_type)  # no attack type wiped out
    assert np.array_equal(sampled.test.y, base.test.y)


def test_scaler_is_fitted_on_train(base):
    n_numeric = sum(not n.startswith(("proto_", "service_")) for n in base.feature_names)
    train = base.train.X[:, :n_numeric]
    varying = train.std(axis=0) > 0
    assert np.allclose(train.mean(axis=0)[varying], 0, atol=1e-3)
    assert np.allclose(train.std(axis=0)[varying], 1, atol=1e-2)


def test_unknown_names_fail_early():
    with pytest.raises(ValueError, match="data.scaler"):
        load_splits({**BASE, "scaler": "zscore"}, seed=42)
