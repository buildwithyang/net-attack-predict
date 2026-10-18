"""Threshold rules and evaluation numbers on hand-checked examples."""

import numpy as np
import pytest

from iotids.data import Split
from iotids.decision import choose_threshold
from iotids.evaluate import evaluate


def test_evaluate_hand_example():
    split = Split(
        X=np.zeros((4, 1), np.float32),
        y=np.array([0, 0, 1, 1], np.float32),
        attack_type=np.array(["Thing_Speak", "Thing_Speak", "ARP_poisioning", "DOS_SYN_Hping"]),
        row_ids=np.arange(4),
    )
    report = evaluate(np.array([0.1, 0.6, 0.4, 0.9]), split, threshold=0.5)
    assert (report.tn, report.fp, report.fn, report.tp) == (1, 1, 1, 1)
    assert report.detection_rate == report.false_alarm_rate == report.accuracy == 0.5
    assert report.per_type["ARP_poisioning"].flagged_as_attack == 0.0
    assert report.per_type["Thing_Speak"].flagged_as_attack == 0.5
    assert not report.per_type["Thing_Speak"].is_attack


def test_fixed_threshold():
    assert choose_threshold(np.array([0.2]), np.array([0.0]), {"name": "fixed", "value": 0.3}) == 0.3


def test_max_fpr_keeps_false_alarms_under_limit():
    rng = np.random.default_rng(0)
    scores = rng.random(1000).astype(np.float32)
    y = np.zeros(1000, np.float32)
    t = choose_threshold(scores, y, {"name": "max_fpr", "fpr": 0.05})
    assert (scores >= t).mean() <= 0.05
    assert (scores >= t).mean() >= 0.04  # not needlessly strict


def test_unknown_rule_fails_early():
    with pytest.raises(ValueError, match="decision"):
        choose_threshold(np.array([0.2]), np.array([0.0]), "magic")
