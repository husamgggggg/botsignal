#!/bin/bash
# Script to deploy OANDA Telegram Bot to server

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if state.json exists, create if not
if [ ! -f "state.json" ]; then
    echo "📄 Creating state.json..."
    echo "{}" > state.json
fi

# Test import
echo "🧪 Testing imports..."
python3 -c "import src.main; print('✅ All imports successful')" || {
    echo -e "${RED}❌ Import test failed!${NC}"
    exit 1
}

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "To run the bot:"
echo "  source venv/bin/activate"
echo "  python -m src.main"
echo ""
echo "Or use systemd service:"
echo "  sudo systemctl start oanda-bot"

