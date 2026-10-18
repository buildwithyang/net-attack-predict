"""Evaluation module: numbers for one split at one threshold.

Interface:

    report = evaluate(test_scores, splits.test, threshold)
    report.to_dict()        # for metrics.json

"Positive" means attack. The two numbers that matter most for this project:

- detection_rate (= recall): share of attack rows flagged as attack
- false_alarm_rate (= false positive rate): share of normal rows flagged as attack

`per_type` breaks the "flagged as attack" share down by original Attack_type,
so you can see which attacks are missed (e.g. ARP_poisioning) and which normal
devices cause false alarms.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .data import Split


@dataclass(frozen=True)
class TypeResult:
    is_attack: bool
    n: int
    flagged_as_attack: float  # share of these rows predicted "attack"


@dataclass(frozen=True)
class Report:
    threshold: float
    n: int
    tn: int  # normal -> normal
    fp: int  # normal -> attack   (false alarm)
    fn: int  # attack -> normal   (missed attack)
    tp: int  # attack -> attack
    accuracy: float
    precision: float
    detection_rate: float
    false_alarm_rate: float
    f1: float
    per_type: dict[str, TypeResult]

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate(scores: np.ndarray, split: Split, threshold: float) -> Report:
    if len(scores) != len(split.y):
        raise ValueError(f"evaluate: {len(scores)} scores for {len(split.y)} rows")
    pred = scores >= threshold
    truth = split.y == 1

    tp = int(np.sum(pred & truth))
    fp = int(np.sum(pred & ~truth))
    fn = int(np.sum(~pred & truth))
    tn = int(np.sum(~pred & ~truth))
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)

    per_type = {}
    for kind in np.unique(split.attack_type):
        rows = split.attack_type == kind
        per_type[str(kind)] = TypeResult(bool(truth[rows][0]), int(rows.sum()), float(pred[rows].mean()))

    return Report(
        threshold=float(threshold),
        n=len(truth),
        tn=tn,
        fp=fp,
        fn=fn,
        tp=tp,
        accuracy=_ratio(tp + tn, len(truth)),
        precision=precision,
        detection_rate=recall,
        false_alarm_rate=_ratio(fp, fp + tn),
        f1=_ratio(2 * precision * recall, precision + recall),
        per_type=per_type,
    )


def _ratio(a: float, b: float) -> float:
    return float(a / b) if b else 0.0
