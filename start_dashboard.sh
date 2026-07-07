#!/bin/bash
# Operations Co-Founder Brain — Dashboard Launcher (Mac/Linux)
# Run this to start the dashboard

echo ""
echo "============================================================"
echo "  Operations Co-Founder Brain"
echo "  Starting dashboard..."
echo "============================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo ""
    echo "Please run ./install.sh first to set up the application."
    echo ""
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
if ! grep -q "ANTHROPIC_API_KEY=sk-ant" .env; then
    echo "ERROR: ANTHROPIC_API_KEY not configured in .env"
    echo ""
    echo "Please edit .env and add your API key."
    echo "Get it from: https://console.anthropic.com/"
    echo ""
    exit 1
fi

echo "Launching Streamlit dashboard..."
echo ""
echo "The app will open in your browser at: http://localhost:8501"
echo ""
echo "To stop the app, press CTRL+C in this window"
echo ""

# Start the dashboard
streamlit run dashboard.py
