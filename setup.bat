@echo off
echo Setting up WoW Class Learner with uv...

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv is not installed. Installing uv...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    echo uv installed successfully!
) else (
    echo uv is already installed.
)

REM Create virtual environment
echo Creating virtual environment...
uv venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
uv sync

REM Create data directory
echo Creating data directory...
if not exist "data" mkdir data

echo.
echo Setup completed successfully!
echo.
echo To run the server:
echo   uv run python main.py
echo.
echo To activate the environment manually:
echo   .venv\Scripts\activate
echo.
echo To install additional dependencies:
echo   uv add package-name
echo.
pause 