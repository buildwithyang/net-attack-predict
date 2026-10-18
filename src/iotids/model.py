"""Model module: builds the MLP from the config.

Interface:

    model = build_model(model_cfg, n_features, seed)   # a torch.nn.Module
    logits = model(X_batch)                       # shape (batch,); > 0 means "attack"

The model outputs one raw score (a logit) per row. `train.predict_proba`
turns it into a probability with a sigmoid. Loss and training live in
`train.py`, so you can change the architecture here without touching training.

Config keys (model:):
    hidden      list of hidden layer sizes, e.g. [64] or [128, 64]
    activation  one of ACTIVATIONS
    dropout     dropout rate after each hidden layer (0 = off)
"""

from __future__ import annotations

from typing import Any, Mapping

import torch
from torch import nn

ACTIVATIONS = {
    "relu": nn.ReLU,
    "tanh": nn.Tanh,
    "sigmoid": nn.Sigmoid,
    "leaky_relu": nn.LeakyReLU,
}


class MLP(nn.Module):
    """Input -> [Linear -> activation -> dropout] x len(hidden) -> Linear(1)."""

    def __init__(self, n_features: int, hidden: list[int], activation: str, dropout: float):
        super().__init__()
        layers: list[nn.Module] = []
        width = n_features
        for size in hidden:
            layers += [nn.Linear(width, size), ACTIVATIONS[activation]()]
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            width = size
        layers.append(nn.Linear(width, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)


def build_model(cfg: Mapping[str, Any], n_features: int, seed: int) -> nn.Module:
    """Same seed -> same starting weights, so runs can be repeated exactly."""
    hidden = list(cfg.get("hidden", [64]))
    activation = cfg.get("activation", "relu")
    dropout = float(cfg.get("dropout", 0.0))
    if activation not in ACTIVATIONS:
        raise ValueError(f"model.activation: unknown {activation!r}; choose one of {sorted(ACTIVATIONS)}")
    if any(size < 1 for size in hidden):
        raise ValueError(f"model.hidden: layer sizes must be >= 1, got {hidden}")
    if not 0 <= dropout < 1:
        raise ValueError(f"model.dropout must be in [0, 1), got {dropout}")
    torch.manual_seed(seed)
    return MLP(n_features, hidden, activation, dropout)
