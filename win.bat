@echo off
setlocal

set VENV_DIR=.venv

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to PATH. Please install Python 3 to proceed.
    exit /b 1
)

:: Check if the virtual environment already exists
if exist %VENV_DIR% (
    echo Virtual environment '%VENV_DIR%' already exists.
) else (
    :: Create the virtual environment
    python -m venv %VENV_DIR%

    :: Check if the virtual environment was created successfully
    if not exist %VENV_DIR% (
        echo Failed to create virtual environment.
        exit /b 1
    )

    echo Virtual environment '%VENV_DIR%' created.
)

:: Activate the virtual environment
call %VENV_DIR%\Scripts\activate.bat

echo Virtual environment '%VENV_DIR%' activated.

:: Run the requirements.py script
python requirements.py
if %errorlevel% neq 0 (
    echo requirements.py failed to execute.
    exit /b 1
)

:: Run the pipeline.py script if requirements.py was successful
python pipeline.py
if %errorlevel% neq 0 (
    echo pipeline.py failed to execute.
    exit /b 1
)

:: Modify pipeline.py to comment specific lines using modifier in tools directory
python tools\modifier.py
if %errorlevel% neq 0 (
    echo Failed to modify pipeline.py.
    exit /b 1
)

:: Run the modified pipeline.py script
python pipeline.py
if %errorlevel% neq 0 (
    echo Modified pipeline.py failed to execute.
    exit /b 1
)

:: Run Streamlit with the modified pipeline.py script
streamlit run ./pipeline.py
if %errorlevel% neq 0 (
    echo Failed to run Streamlit with pipeline.py.
    exit /b 1
)

:end
endlocal
exit /b 0
