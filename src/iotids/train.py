"""Training module: the hand-written PyTorch training loop.

Interface:

    history = fit(model, splits.train, splits.val, train_cfg, seed)
    scores  = predict_proba(model, split.X)      # numpy, values in 0..1

`fit` trains in place. With early stopping on, it stops after `early_stopping`
epochs without a better val loss and puts back the weights from the epoch with
the lowest val loss. With early stopping off (0), it trains every epoch and
keeps the last weights, so you can see what overfitting does to the results.

Config keys (train:):
    epochs          max number of passes over the training set
    batch_size      rows per gradient step
    optimizer       "adam" or "sgd"
    lr              learning rate
    class_weight    "none", "balanced", or a number: weight of the attack class
                    in the training loss (normal class weight is 1)
    early_stopping  stop after this many epochs without a better val loss
                    (0 = off)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .data import Split

OPTIMIZERS = {"adam": torch.optim.Adam, "sgd": torch.optim.SGD}


@dataclass
class History:
    """Per-epoch losses. Val loss is plain (unweighted) BCE so runs compare."""

    train_loss: list[float] = field(default_factory=list)
    val_loss: list[float] = field(default_factory=list)
    best_epoch: int = 0  # 1-based epoch with the lowest val loss
    kept_epoch: int = 0  # 1-based epoch whose weights the model ends with


def fit(model: nn.Module, train: Split, val: Split, cfg: Mapping[str, Any], seed: int) -> History:
    torch.manual_seed(seed)
    loader = DataLoader(
        TensorDataset(torch.from_numpy(train.X), torch.from_numpy(train.y)),
        batch_size=int(cfg.get("batch_size", 256)),
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=_attack_weight(cfg.get("class_weight", "none"), train.y))
    optimizer = _optimizer(model, cfg)
    patience = int(cfg.get("early_stopping", 0))

    history = History()
    best_val, best_state, waited = float("inf"), None, 0
    for epoch in range(1, int(cfg.get("epochs", 30)) + 1):
        model.train()
        total, rows = 0.0, 0
        for X_batch, y_batch in loader:
            logits = model(X_batch)  # forward pass
            loss = loss_fn(logits, y_batch)  # how wrong we are
            optimizer.zero_grad()
            loss.backward()  # backpropagation: PyTorch computes the gradients
            optimizer.step()  # update the weights
            total += loss.item() * len(y_batch)
            rows += len(y_batch)

        history.train_loss.append(total / rows)
        history.val_loss.append(_plain_loss(model, val))

        if history.val_loss[-1] < best_val:
            best_val, best_state, waited = history.val_loss[-1], copy.deepcopy(model.state_dict()), 0
            history.best_epoch = epoch
        else:
            waited += 1
        if patience and waited >= patience:
            break

    history.kept_epoch = len(history.train_loss)
    if patience and best_state is not None:
        model.load_state_dict(best_state)
        history.kept_epoch = history.best_epoch
    return history


def predict_proba(model: nn.Module, X: np.ndarray) -> np.ndarray:
    """Probability of "attack" for each row."""
    return torch.sigmoid(_logits(model, X)).numpy()


def _plain_loss(model: nn.Module, split: Split) -> float:
    return nn.functional.binary_cross_entropy_with_logits(_logits(model, split.X), torch.from_numpy(split.y)).item()


@torch.no_grad()
def _logits(model: nn.Module, X: np.ndarray, batch_size: int = 8192) -> torch.Tensor:
    model.eval()
    return torch.cat([model(torch.from_numpy(X[i : i + batch_size])) for i in range(0, len(X), batch_size)])


def _attack_weight(spec: Any, y: np.ndarray) -> torch.Tensor | None:
    if spec == "none":
        return None
    if spec == "balanced":
        n_attack = float(y.sum())
        return torch.tensor((len(y) - n_attack) / n_attack)
    if isinstance(spec, (int, float)) and spec > 0:
        return torch.tensor(float(spec))
    raise ValueError(f"train.class_weight: expected 'none', 'balanced' or a positive number, got {spec!r}")


def _optimizer(model: nn.Module, cfg: Mapping[str, Any]) -> torch.optim.Optimizer:
    name = cfg.get("optimizer", "adam")
    if name not in OPTIMIZERS:
        raise ValueError(f"train.optimizer: unknown {name!r}; choose one of {sorted(OPTIMIZERS)}")
    return OPTIMIZERS[name](model.parameters(), lr=float(cfg.get("lr", 1e-3)))
