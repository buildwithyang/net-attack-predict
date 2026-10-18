"""Run experiments from config files: train -> validate -> test -> save.

    python scripts/train.py configs/baseline.yaml [configs/other.yaml ...]

Run from the project root, after `pip install -e .`.
Results go to runs/<name>/ (see README.md).
"""

import argparse
from pathlib import Path

import yaml

from iotids.experiment import run_experiment

ROOT = Path(__file__).resolve().parents[1]  # project root: holds configs/, data/ and runs/


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("configs", nargs="+", type=Path, help="one or more YAML config files")
    parser.add_argument("--out", type=Path, default=ROOT / "runs", help="folder for results (default: runs/)")
    args = parser.parse_args()

    for path in args.configs:
        cfg = yaml.safe_load(path.read_text())
        cfg["data"]["path"] = str((ROOT / cfg["data"]["path"]).resolve())
        run_experiment(cfg, args.out)


if __name__ == "__main__":
    main()
