@echo off
setlocal

python -m pip install -r requirements-build.txt

python -m PyInstaller ^
  --name "Schedule Manager" ^
  --windowed ^
  --onefile ^
  --clean ^
  --noconfirm ^
  main.py

echo.
echo Build complete: dist\Schedule Manager.exe
endlocal
