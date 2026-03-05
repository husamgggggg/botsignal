@echo off
REM Script to deploy OANDA Telegram Bot on Windows

echo 🚀 Starting deployment...

REM Check if .env exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo Please create .env file from .env.example
    exit /b 1
)

REM Check Python
echo 📋 Checking Python version...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.11+
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if state.json exists
if not exist state.json (
    echo 📄 Creating state.json...
    echo {} > state.json
)

REM Test import
echo 🧪 Testing imports...
python -c "import src.main; print('✅ All imports successful')"
if errorlevel 1 (
    echo ❌ Import test failed!
    exit /b 1
)

echo ✅ Deployment completed successfully!
echo.
echo To run the bot:
echo   venv\Scripts\activate
echo   python -m src.main

pause

