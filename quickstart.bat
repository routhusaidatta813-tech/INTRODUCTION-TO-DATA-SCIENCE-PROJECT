@echo off
echo ==========================================================
echo  Movie Opening Weekend Box Office Forecaster Quickstart
echo ==========================================================

echo [1/3] Installing dependencies...
pip install -r requirements.txt -q

echo [2/3] Running End-to-End Pipeline...
python main.py

echo [3/3] Running Statistical Hypothesis Tests...
python src/hypothesis_testing.py

echo ==========================================================
echo  Quickstart Complete!
echo ==========================================================
echo To launch the Web Dashboard:
echo   python -m streamlit run app.py
echo.
pause
