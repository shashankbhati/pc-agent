@echo off
echo Starting PC Agent...
echo.
cd /d "%~dp0"
pip install -r requirements.txt -q
echo.
python app.py
pause
