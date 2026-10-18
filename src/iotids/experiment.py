"""Runs one experiment from a config: train -> validate -> test -> save.

This is the only module that writes files. Every other module just returns
results, so each one can be changed or tested on its own.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any, Mapping

import yaml

from .data import load_splits
from .decision import choose_threshold
from .evaluate import Report, evaluate
from .model import build_model
from .plots import headline, save_figures
from .train import fit, predict_proba


def run_experiment(cfg: Mapping[str, Any], out_root: Path) -> Report:
    start = time.time()
    seed = int(cfg["seed"])  # one seed drives the split, the starting weights and the shuffling

    # 1. Data: CSV -> train / val / test number arrays (X, y). Scaler etc. are fitted on train only.
    splits = load_splits(cfg["data"], seed)
    # 2. Model: an untrained MLP whose input size matches the number of feature columns.
    model = build_model(cfg["model"], splits.n_features, seed)
    # 3. Train: update the weights on train, watch val loss each epoch (early stopping).
    #    `model` is changed in place; `history` only records the losses.
    history = fit(model, splits.train, splits.val, cfg["train"], seed)

    # 4. Decide: turn "attack probability" into yes/no. The threshold is picked on val, never on test.
    threshold = choose_threshold(predict_proba(model, splits.val.X), splits.val.y, cfg["decision"])
    # 5. Test: score the test rows once, with the finished model.
    test_scores = predict_proba(model, splits.test.X)
    # 6. Evaluate: confusion matrix, detection rate, false alarm rate, per attack type.
    report = evaluate(test_scores, splits.test, threshold)

    # 7. Save: everything below only writes files to runs/<name>/.
    out_dir = Path(out_root) / cfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.yaml").write_text(yaml.safe_dump(dict(cfg), sort_keys=False))
    with open(out_dir / "history.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "train_loss", "val_loss"])
        writer.writerows(zip(range(1, len(history.train_loss) + 1), history.train_loss, history.val_loss))
    metrics = {
        "name": cfg["name"],
        "test_fingerprint": splits.test_fingerprint,
        "rows": {"train": len(splits.train.y), "val": len(splits.val.y), "test": len(splits.test.y)},
        "n_features": splits.n_features,
        "best_epoch": history.best_epoch,
        "kept_epoch": history.kept_epoch,
        "epochs_run": len(history.train_loss),
        "seconds": round(time.time() - start, 1),
        "test": report.to_dict(),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    save_figures(out_dir, f"IoT attack detection with an MLP: {cfg['name']}", history, report, test_scores, splits.test)

    print(f"[{cfg['name']}] {headline(report)}")
    print(f"[{cfg['name']}] results in {out_dir}")
    return report
