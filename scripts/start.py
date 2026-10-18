"""Beginner launcher: set up the Python environment, then pick an experiment from a menu.

Easiest way: double-click `start.command` (macOS) or `start.bat` (Windows) in the project root.
Or run it yourself from the project root:

    python3 scripts/start.py

What it does, in order:
1. First time only: creates a virtual environment in `.venv/` (a private copy of Python
   for this project) and installs the packages from pyproject.toml into it.
   It reinstalls automatically when pyproject.toml changes.
2. Unzips the data (data/raw/rt-iot2022.zip -> RT_IOT2022.csv) if needed.
3. Shows a menu: run experiments, compare finished runs, open results, run the checks.

Only uses the standard library, so it can run before anything is installed.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    print(f"需要 Python 3.10 或更新版本，当前是 {sys.version.split()[0]}。")
    print("请到 https://www.python.org/downloads/ 下载安装后再运行。")
    sys.exit(1)

import hashlib
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root: holds configs/, data/ and runs/
VENV = ROOT / ".venv"
MARKER = VENV / ".iotids-installed"  # holds the hash of pyproject.toml at the last install
CONFIGS = ROOT / "configs"
RUNS = ROOT / "runs"
DATA_ZIP = ROOT / "data" / "raw" / "rt-iot2022.zip"
DATA_CSV = ROOT / "data" / "raw" / "RT_IOT2022.csv"

# Same as .vscode/.env: no __pycache__ in the project folder, matplotlib cache in the temp folder.
ENV = {
    **os.environ,
    "PYTHONDONTWRITEBYTECODE": "1",
    "MPLCONFIGDIR": str(Path(tempfile.gettempdir()) / "iotids-matplotlib"),
}


# ---------------------------------------------------------------- setup (runs with system Python)


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def running_in_venv() -> bool:
    return Path(sys.prefix).resolve() == VENV.resolve()


def ensure_venv() -> None:
    py = venv_python()
    if py.exists() and subprocess.run([str(py), "-c", "pass"], capture_output=True).returncode != 0:
        # Usually the Python it was made from was upgraded or removed.
        print("虚拟环境 .venv 已损坏，重新创建 ...")
        shutil.rmtree(VENV)
    if not py.exists():
        print(f"第一次运行：用 Python {sys.version.split()[0]} 创建虚拟环境 .venv ...")
        if subprocess.run([sys.executable, "-m", "venv", str(VENV)]).returncode != 0:
            fail("创建虚拟环境失败。Linux 上可能要先装 python3-venv。")

    wanted = hashlib.sha256((ROOT / "pyproject.toml").read_bytes()).hexdigest()
    if MARKER.exists() and MARKER.read_text().strip() == wanted:
        return
    print("安装依赖（torch、pandas 等）。第一次要下载几百 MB，大约 1-10 分钟，请耐心等 ...\n")
    if subprocess.run([str(py), "-m", "pip", "install", "-e", ".[dev]"], cwd=ROOT, env=ENV).returncode != 0:
        fail(
            "安装依赖失败。常见原因：\n"
            "  - 网络不通或太慢：换个网络再运行一次，已下载的部分不会重下。\n"
            "  - Python 版本太新、torch 还不支持：装 Python 3.12 后删掉 .venv 文件夹再运行。"
        )
    MARKER.write_text(wanted)
    print("\n依赖安装完成。")


def ensure_data() -> None:
    if DATA_CSV.exists():
        return
    if not DATA_ZIP.exists():
        fail(f"找不到数据文件 {DATA_ZIP.relative_to(ROOT)}。")
    print("解压数据 rt-iot2022.zip ...")
    with zipfile.ZipFile(DATA_ZIP) as z:
        z.extract(DATA_CSV.name, DATA_CSV.parent)


def fail(message: str) -> None:
    print(f"\n[出错] {message}")
    sys.exit(1)


# ---------------------------------------------------------------- menu (runs inside .venv)


def main_menu() -> None:
    actions = {
        "1": ("跑基线实验 baseline（约 30 秒，其他实验都和它比）", run_baseline),
        "2": ("主线实验：标准化 / 学习率 / 网络大小 / 过拟合", lambda: pick_and_run("training")),
        "3": ("补充实验：类别不平衡", lambda: pick_and_run("imbalance")),
        "4": ("对比几个已完成的实验（出一张图 + 一张表）", compare_runs),
        "5": ("打开结果文件夹 runs/", lambda: open_path(RUNS)),
        "6": ("运行自检 pytest（检查代码有没有改坏）", run_tests),
    }
    while True:
        print("\n==================== IoT 攻击检测 · 训练启动器 ====================")
        for key, (label, _) in actions.items():
            print(f"  {key}. {label}")
        print("  0. 退出")
        choice = ask("请输入编号")
        if choice in ("0", "q"):
            return
        if choice not in actions:
            print("没有这个编号，请重新输入。")
            continue
        try:
            actions[choice][1]()
        except KeyboardInterrupt:
            print("\n已中断，回到菜单。")


def run_baseline() -> None:
    train([CONFIGS / "baseline.yaml"])


def pick_and_run(group: str) -> None:
    configs = sorted((CONFIGS / group).glob("*.yaml"))
    print(f"\n{group} 实验（每个只比 baseline 改一处）：")
    for i, path in enumerate(configs, 1):
        done = "  [已跑过]" if (RUNS / path.stem / "metrics.json").exists() else ""
        print(f"  {i}. {path.stem}{done}\n       {describe(path)}")
    print("  a. 全部依次跑一遍")
    picked = pick(configs, ask("输入编号（多个用空格隔开，如 1 3），a 全部，直接回车返回"))
    if not picked:
        return
    if not (RUNS / "baseline" / "metrics.json").exists():
        picked = [CONFIGS / "baseline.yaml", *picked]
        print("还没跑过 baseline，先跑它，后面对比要用。")
    train(picked)


def train(configs: list[Path]) -> None:
    names = ", ".join(path.stem for path in configs)
    print(f"\n开始训练：{names}。按 Ctrl+C 可中断。\n")
    if run([sys.executable, "scripts/train.py", *map(str, configs)]) != 0:
        print("\n[出错] 训练没有完成，看上面的错误信息。")
        return
    last = RUNS / configs[-1].stem
    print(f"\n完成。结果在 {last.relative_to(ROOT)}/ ，summary.png 是一页总结图。")
    if confirm("现在打开 summary.png 看看？"):
        open_path(last / "summary.png")


def compare_runs() -> None:
    runs = sorted(p.parent for p in RUNS.glob("*/metrics.json"))
    if len(runs) < 2:
        print("至少要先跑完两个实验才能对比（比如 baseline 和 lr_high）。")
        return
    print("\n已完成的实验：")
    for i, path in enumerate(runs, 1):
        print(f"  {i}. {path.name}")
    picked = pick(runs, ask("选 2-4 个编号，用空格隔开，第一个作参照（一般选 baseline），如 1 4 5"))
    if not 2 <= len(picked) <= 4:
        if picked:
            print("要选 2 到 4 个。")
        return
    names = [p.name for p in picked]
    title = ask("图的标题（直接回车用默认）") or f"{names[0]} vs " + ", ".join(names[1:])
    out = RUNS / ("compare_" + "_vs_".join(names))
    if run([sys.executable, "scripts/compare.py", *map(str, picked), "--title", title, "--out", str(out)]) != 0:
        print("\n[出错] 对比没有完成，看上面的错误信息。")
        return
    if confirm("现在打开对比图？"):
        open_path(out.with_suffix(".png"))


def run_tests() -> None:
    code = run([sys.executable, "-m", "pytest"])
    print("\n全部通过。" if code == 0 else "\n有检查没通过，看上面的 FAILED 行。")


# ---------------------------------------------------------------- small helpers


def describe(config: Path) -> str:
    """First comment line of a config, e.g. 'Training experiment: learning rate 0.1 ...'."""
    first = config.read_text(encoding="utf-8").splitlines()[0]
    return first.lstrip("# ").strip()


def pick(items: list[Path], answer: str) -> list[Path]:
    if answer.lower() == "a":
        return items
    picked = []
    for token in answer.replace(",", " ").split():
        if not (token.isdigit() and 1 <= int(token) <= len(items)):
            print(f"编号 {token} 不对，请重新选。")
            return []
        picked.append(items[int(token) - 1])
    return picked


def ask(prompt: str) -> str:
    try:
        return input(f"{prompt}：").strip()
    except EOFError:
        print()
        sys.exit(0)


def confirm(prompt: str) -> bool:
    return ask(f"{prompt} [Y/n]").lower() in ("", "y", "yes")


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT, env=ENV).returncode


def open_path(path: Path) -> None:
    if path == RUNS:
        path.mkdir(exist_ok=True)
    if sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    elif os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]  # Windows only
    else:
        subprocess.run(["xdg-open", str(path)])


def main() -> None:
    sys.stdout.reconfigure(line_buffering=True)  # keep our messages in order with the child processes'
    if not running_in_venv():
        ensure_venv()
        # Run this same file again with the venv's Python, so the menu sees torch etc.
        try:
            sys.exit(subprocess.run([str(venv_python()), __file__, *sys.argv[1:]], env=ENV).returncode)
        except KeyboardInterrupt:
            sys.exit(130)
    ensure_data()
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
    print("再见。")


if __name__ == "__main__":
    main()
