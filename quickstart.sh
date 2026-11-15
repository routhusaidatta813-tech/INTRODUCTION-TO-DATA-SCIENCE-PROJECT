#!/usr/bin/env bash
# Quickstart Script for WSL2 / Linux / Mac

echo "=========================================================="
echo "🎬 Movie Opening Weekend Box Office Forecaster Quickstart"
echo "=========================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 could not be found. Please install Python 3.10+."
    exit 1
fi

echo "📦 1. Checking and installing dependencies..."
pip install -r requirements.txt --break-system-packages -q

echo "🚀 2. Running End-to-End ML Pipeline..."
python3 main.py

echo ""
echo "📊 3. Running Statistical Hypothesis Tests..."
python3 src/hypothesis_testing.py

echo ""
echo "=========================================================="
echo "✅ Quickstart Complete! All models and figures generated."
echo "=========================================================="
echo "To test a prediction in terminal:"
echo "  python3 predict.py --budget 150000000 --theaters 3800 --genre Action --sequel 1 --competition 2"
echo ""
echo "To launch the interactive Web Dashboard:"
echo "  python3 -m streamlit run app.py"
echo "=========================================================="
