"""Model + training loop on a tiny toy problem."""

import numpy as np
import pytest

from iotids.data import Split
from iotids.model import build_model
from iotids.train import fit, predict_proba

CFG = {"epochs": 20, "batch_size": 64, "optimizer": "adam", "lr": 0.01, "class_weight": "none", "early_stopping": 5}


def toy(n, seed):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, n).astype(np.float32)
    X = (rng.normal(size=(n, 5)) + y[:, None] * 3).astype(np.float32)
    return Split(X, y, np.where(y == 1, "attack", "normal"), np.arange(n))


def train_once(seed=0):
    model = build_model({"hidden": [16], "activation": "relu", "dropout": 0.0}, n_features=5, seed=seed)
    history = fit(model, toy(800, 1), toy(200, 2), CFG, seed)
    return model, history


def test_learns_a_separable_problem():
    model, history = train_once()
    test = toy(500, 3)
    scores = predict_proba(model, test.X)
    assert scores.shape == (500,) and scores.min() >= 0 and scores.max() <= 1
    assert ((scores >= 0.5) == (test.y == 1)).mean() > 0.95
    assert len(history.train_loss) == len(history.val_loss) >= history.best_epoch >= 1


def test_same_seed_same_result():
    a, _ = train_once(seed=7)
    b, _ = train_once(seed=7)
    X = toy(100, 4).X
    assert np.array_equal(predict_proba(a, X), predict_proba(b, X))


def test_bad_config_fails_early():
    with pytest.raises(ValueError, match="model.activation"):
        build_model({"activation": "swish"}, n_features=5, seed=0)
