"""Decision module: turns attack probabilities into a yes/no threshold.

Interface (a Seam, chosen with `decision:` in the config):

    threshold = choose_threshold(val_scores, val.y, decision_cfg)
    is_attack = scores >= threshold

The threshold is chosen on the validation set only. The test set is used
once, afterwards, to report results.

Adapters:
    fixed    {name: fixed, value: 0.5}      always the same threshold
    max_fpr  {name: max_fpr, fpr: 0.01}     lowest threshold whose false alarm
                                             rate on val normal traffic <= fpr
                                             (catches as many attacks as allowed)

To add a rule: write a function (val_scores, val_y, **params) -> float and
register it in RULES.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

import numpy as np


def fixed(val_scores: np.ndarray, val_y: np.ndarray, value: float = 0.5) -> float:
    return float(value)


def max_fpr(val_scores: np.ndarray, val_y: np.ndarray, fpr: float = 0.01) -> float:
    if not 0 <= fpr < 1:
        raise ValueError(f"decision max_fpr: fpr must be in [0, 1), got {fpr}")
    normal_scores = val_scores[val_y == 0]
    if len(normal_scores) == 0:
        raise ValueError("decision max_fpr: validation set has no normal rows")
    # Just above the (1 - fpr) quantile, so at most `fpr` of normal rows score >= threshold.
    q = np.quantile(normal_scores, 1 - fpr, method="higher")
    return float(np.nextafter(np.float32(q), np.float32(np.inf)))


RULES: dict[str, Callable[..., float]] = {"fixed": fixed, "max_fpr": max_fpr}


def choose_threshold(val_scores: np.ndarray, val_y: np.ndarray, spec: str | Mapping[str, Any]) -> float:
    params = {"name": spec} if isinstance(spec, str) else dict(spec)
    name = params.pop("name", None)
    if name not in RULES:
        raise ValueError(f"decision: unknown name {name!r}; choose one of {sorted(RULES)}")
    return RULES[name](val_scores, val_y, **params)
