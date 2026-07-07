#!/bin/bash
# Operations Co-Founder Brain — One-Click Installer (Mac/Linux)
# Run this once to set up everything

echo ""
echo "============================================================"
echo "  Operations Co-Founder Brain — Setup"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ from python.org or via:"
    echo "  brew install python3  (on Mac)"
    echo "  sudo apt install python3 (on Linux)"
    exit 1
fi

python_version=$(python3 --version | awk '{print $2}')
echo "[1/4] Python found: $python_version"
echo ""

echo "[2/4] Installing dependencies..."
echo ""

# Install requirements
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[3/4] Dependencies installed successfully!"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "[4/4] Creating .env file..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    echo "  1. Open .env in your text editor"
    echo "  2. Find: ANTHROPIC_API_KEY="
    echo "  3. Add your key: ANTHROPIC_API_KEY=sk-ant-xxxxx"
    echo "  4. Save the file"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
else
    echo "[4/4] .env file already exists (skipping creation)"
fi

echo ""
echo "============================================================"
echo "  Setup complete!"
echo ""
echo "  Next step: Run ./start_dashboard.sh to launch the app"
echo ""
echo "  The dashboard will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "============================================================"
echo ""
