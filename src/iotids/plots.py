"""Figures for the report and slides.

Interface:

    save_figures(out_dir, title, history, report, test_scores, test_split)

Writes one PNG per chart plus `summary.png`, a one-page overview with the
headline numbers on top. Colours: blue = normal traffic, orange = attack,
everywhere.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from .data import Split  # noqa: E402
from .evaluate import Report  # noqa: E402
from .train import History  # noqa: E402

NORMAL = "#2a78d6"
ATTACK = "#eb6834"
VAL_LINE = "#1baf7a"
TRAIN_LINE = "#52514e"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"
BLUES = LinearSegmentedColormap.from_list(
    "blues", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_2,
        "axes.titlecolor": TEXT,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT_2,
        "font.size": 11,
        "legend.frameon": False,
    }
)


def save_figures(out_dir: Path, title: str, history: History, report: Report, scores: np.ndarray, test: Split) -> None:
    out_dir = Path(out_dir)
    panels = {
        "training_curves": lambda ax: plot_training_curves(ax, history),
        "confusion_matrix": lambda ax: plot_confusion_matrix(ax, report),
        "per_type": lambda ax: plot_per_type(ax, report),
        "score_distribution": lambda ax: plot_score_distribution(ax, scores, test.y, report.threshold),
    }
    sizes = {"per_type": (9, 6.5)}
    for name, draw in panels.items():
        fig, ax = plt.subplots(figsize=sizes.get(name, (8, 5)))
        draw(ax)
        fig.tight_layout()
        fig.savefig(out_dir / f"{name}.png", dpi=150)
        plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(16, 11.5), gridspec_kw={"width_ratios": [1, 1.25]})
    for ax, draw in zip(axes.flat, [panels["training_curves"], panels["per_type"], panels["confusion_matrix"], panels["score_distribution"]]):
        draw(ax)
    fig.suptitle(title, x=0.01, ha="left", fontsize=17, fontweight="bold", color=TEXT)
    fig.text(0.01, 0.935, headline(report), ha="left", fontsize=13, color=TEXT_2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(out_dir / "summary.png", dpi=150)
    plt.close(fig)


def headline(report: Report) -> str:
    return (
        f"Attacks detected {report.detection_rate:.2%}   ·   "
        f"False alarms on normal traffic {report.false_alarm_rate:.2%}   ·   "
        f"Accuracy {report.accuracy:.2%}   ·   "
        f"Test rows {report.n:,}   ·   threshold {report.threshold:.3f}"
    )


def plot_training_curves(ax, history: History) -> None:
    epochs = np.arange(1, len(history.train_loss) + 1)
    ax.plot(epochs, history.train_loss, color=TRAIN_LINE, lw=2, ls="--", label="train loss")
    ax.plot(epochs, history.val_loss, color=VAL_LINE, lw=2, label="validation loss")
    ax.axvline(history.best_epoch, color=TEXT_2, lw=1, ls=":")
    note = f"lowest val loss: epoch {history.best_epoch}"
    if history.kept_epoch != history.best_epoch:
        note += f"\nmodel kept from epoch {history.kept_epoch}"
    ax.annotate(note, (history.best_epoch, 1), xycoords=("data", "axes fraction"), xytext=(4, -6), textcoords="offset points", color=TEXT_2, fontsize=10, va="top")
    ax.set_title("Training: loss per epoch (lower is better)")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss")
    ax.legend(loc="center right")


def plot_confusion_matrix(ax, report: Report) -> None:
    counts = np.array([[report.tn, report.fp], [report.fn, report.tp]])
    shares = counts / counts.sum(axis=1, keepdims=True)
    ax.imshow(shares, cmap=BLUES, vmin=0, vmax=1)
    ax.grid(False)
    for i in range(2):
        for j in range(2):
            ink = "white" if shares[i, j] > 0.55 else TEXT
            ax.text(j, i, f"{counts[i, j]:,}\n{shares[i, j]:.2%} of row", ha="center", va="center", color=ink, fontsize=12)
    ax.set_xticks([0, 1], ["normal", "attack"])
    ax.set_yticks([0, 1], ["normal", "attack"])
    ax.set_xlabel("predicted")
    ax.set_ylabel("true")
    ax.set_title("Test set: confusion matrix")
    for spine in ax.spines.values():
        spine.set_visible(False)


def plot_per_type(ax, report: Report) -> None:
    items = sorted(report.per_type.items(), key=lambda kv: (not kv[1].is_attack, -kv[1].n))
    names = [name for name, _ in items]
    values = [r.flagged_as_attack * 100 for _, r in items]
    colors = [ATTACK if r.is_attack else NORMAL for _, r in items]
    y = np.arange(len(items))[::-1]
    ax.barh(y, values, color=colors, height=0.7)
    for yi, value, (_, r) in zip(y, values, items):
        ax.text(min(value, 100) + 1, yi, f"{value:.1f}%  (n={r.n:,})", va="center", fontsize=10, color=TEXT)
    ax.set_yticks(y, names)
    ax.set_xlim(0, 125)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("% of rows flagged as attack")
    ax.set_title("Test set: flagged as attack, by traffic type")
    ax.bar(0, 0, color=ATTACK, label="attack (want ~100%)")
    ax.bar(0, 0, color=NORMAL, label="normal (want ~0%)")
    # Reserve two empty rows so the legend cannot cover normal-traffic bars.
    ax.set_ylim(-2.5, len(items) - 0.1)
    ax.legend(loc="lower right")


def plot_score_distribution(ax, scores: np.ndarray, y: np.ndarray, threshold: float) -> None:
    bins = np.linspace(0, 1, 51)
    ax.hist(scores[y == 0], bins=bins, histtype="step", lw=2, color=NORMAL, label="normal traffic")
    ax.hist(scores[y == 1], bins=bins, histtype="step", lw=2, color=ATTACK, label="attack traffic")
    ax.axvline(threshold, color=TEXT, lw=1.2, ls="--")
    ax.annotate(f"threshold {threshold:.3f}", (threshold, 1), xycoords=("data", "axes fraction"), xytext=(4, -14), textcoords="offset points", fontsize=10, color=TEXT)
    ax.set_yscale("log")
    ax.set_xlabel("model score: probability of attack")
    ax.set_ylabel("rows (log scale)")
    ax.set_title("Test set: how sure the model is")
    ax.legend(loc="upper left", bbox_to_anchor=(0.08, 1))


RUN_COLORS = [TRAIN_LINE, "#2a78d6", "#eb6834", "#1baf7a"]  # first run (the reference) in neutral ink


def save_comparison(runs: list[dict], histories: list[dict], path: Path, title: str) -> None:
    """One chart comparing experiments that share the same test set.

    `runs` are metrics.json dicts, `histories` the matching history.csv
    columns ({"train_loss": [...], "val_loss": [...]}). Up to 4 runs; the first
    one is the reference and is drawn in grey. Each run keeps one colour in
    all three panels.
    """
    if not 1 <= len(runs) <= len(RUN_COLORS):
        raise ValueError(f"save_comparison: 1 to {len(RUN_COLORS)} runs, got {len(runs)}")
    colors = RUN_COLORS[: len(runs)]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.6), gridspec_kw={"width_ratios": [1.4, 1, 1]})

    ax = axes[0]
    for run, hist, color in zip(runs, histories, colors):
        epochs = np.arange(1, len(hist["val_loss"]) + 1)
        ax.plot(epochs, hist["train_loss"], color=color, lw=1.5, ls="--")
        ax.plot(epochs, hist["val_loss"], color=color, lw=2.2, label=run["name"])
    ax.plot([], [], color=TEXT_2, lw=1.5, ls="--", label="(dashed = train loss)")
    ax.set_yscale("log")
    ax.set_title("Validation loss per epoch (solid)")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss (log scale)")
    ax.legend(loc="upper right", fontsize=10)

    y = np.arange(len(runs))[::-1]
    bars = [
        ("False alarms on normal traffic", [(r["test"]["fp"], r["test"]["fp"] + r["test"]["tn"]) for r in runs]),
        ("Missed attacks", [(r["test"]["fn"], r["test"]["fn"] + r["test"]["tp"]) for r in runs]),
    ]
    for ax, (panel_title, pairs) in zip(axes[1:], bars):
        rates = [100 * k / n if n else 0 for k, n in pairs]
        ax.barh(y, rates, color=colors, height=0.6)
        top = max(rates) or 1
        for yi, rate, (k, n) in zip(y, rates, pairs):
            ax.text(rate + top * 0.02, yi, f"{rate:.2f}%  ({k:,} of {n:,})", va="center", fontsize=10, color=TEXT)
        ax.set_xlim(0, top * 1.7)
        ax.set_yticks(y, [r["name"] for r in runs])
        ax.set_title(f"Test set: {panel_title.lower()}")
        ax.set_xlabel("% of rows (lower is better)")
        ax.grid(axis="y", visible=False)
    axes[2].set_yticks(y, [""] * len(runs))

    fig.suptitle(title, x=0.01, ha="left", fontsize=15, fontweight="bold", color=TEXT)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=150)
    plt.close(fig)
