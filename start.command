#!/bin/bash
# macOS / Linux 启动器：在访达里双击即可。也可以在终端里运行：bash start.command
# 只负责找到 Python 3.10+，其余（建 .venv、装依赖、菜单）都在 scripts/start.py 里。

cd "$(dirname "$0")" || exit 1

for candidate in python3.12 python3.13 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
        exec "$candidate" scripts/start.py "$@"
    fi
done

echo "没找到 Python 3.10 或更新版本。"
echo "请到 https://www.python.org/downloads/ 下载安装（推荐 3.12），装好后再双击本文件。"
read -r -p "按回车键关闭 ..."
exit 1
