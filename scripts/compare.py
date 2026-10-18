"""Compare finished experiments in one chart and one table.

    python scripts/compare.py runs/baseline runs/lr_high runs/lr_low --title "Learning rate" --out runs/compare_lr

Up to 4 runs; the first is the reference (drawn in grey). Refuses to compare
runs whose test sets differ (different `test_fingerprint`).
Writes <out>.png and <out>.md.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from iotids.plots import save_comparison

ROOT = Path(__file__).resolve().parents[1]  # project root: holds runs/


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path, help="run folders, reference first")
    parser.add_argument("--title", default="Experiments compared: same test set, one change each")
    parser.add_argument("--out", type=Path, default=ROOT / "runs" / "comparison")
    args = parser.parse_args()

    runs = [json.loads((path / "metrics.json").read_text()) for path in args.runs]
    fingerprints = {r["name"]: r["test_fingerprint"] for r in runs}
    if len(set(fingerprints.values())) != 1:
        sys.exit(f"Different test sets, not comparable: {fingerprints}")
    histories = [read_history(path / "history.csv") for path in args.runs]

    save_comparison(runs, histories, args.out.with_suffix(".png"), args.title)
    args.out.with_suffix(".md").write_text(f"# {args.title}\n\n" + table(runs))
    print(table(runs))
    print(f"Saved {args.out.with_suffix('.png')} and {args.out.with_suffix('.md')}")


def read_history(path: Path) -> dict:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return {key: [float(row[key]) for row in rows] for key in ("train_loss", "val_loss")}


def table(runs: list[dict]) -> str:
    lines = [
        f"Test set: {runs[0]['rows']['test']:,} rows, fingerprint {runs[0]['test_fingerprint']}",
        "",
        "| Experiment | Epochs run | Model from epoch | Attacks detected | False alarm rate | False alarms | Missed attacks | Accuracy | F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in runs:
        t = r["test"]
        lines.append(
            f"| {r['name']} | {r['epochs_run']} | {r.get('kept_epoch', r['best_epoch'])} | {t['detection_rate']:.2%} | "
            f"{t['false_alarm_rate']:.2%} | {t['fp']} | {t['fn']} | {t['accuracy']:.2%} | {t['f1']:.4f} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
