@echo off
rem Windows launcher: double-click this file.
rem It only finds Python 3.10+; scripts\start.py creates .venv, installs packages and shows the menu.
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul && (
    py -3 scripts\start.py %*
    goto end
)
where python >nul 2>nul && (
    python scripts\start.py %*
    goto end
)

echo Python 3.10+ not found.
echo Install it from https://www.python.org/downloads/ (3.12 recommended),
echo and tick "Add python.exe to PATH" in the installer. Then double-click this file again.

:end
pause
