#!/bin/bash
set -e

VENV_DIR=".venv"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3 to proceed."
    exit 1
fi

# Check if the virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' already exists."
else
    # Create the virtual environment
    python3 -m venv $VENV_DIR

    # Check if the virtual environment was created successfully
    if [ ! -d "$VENV_DIR" ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi

    echo "Virtual environment '$VENV_DIR' created."
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

echo "Virtual environment '$VENV_DIR' activated."

# Run the requirements.py script
python3 requirements.py
if [ $? -ne 0 ]; then
    echo "requirements.py failed to execute."
    exit 1
fi

# Run the pipeline.py script if requirements.py was successful
python3 pipeline.py
if [ $? -ne 0 ]; then
    echo "pipeline.py failed to execute."
    exit 1
fi

# Modify pipeline.py to comment specific lines using modifier in tools directory
python3 tools/modifier.py
if [ $? -ne 0 ]; then
    echo "Failed to modify pipeline.py."
    exit 1
fi

# Run the modified pipeline.py script
python3 pipeline.py
if [ $? -ne 0 ]; then
    echo "Modified pipeline.py failed to execute."
    exit 1
fi

# Run Streamlit with the modified pipeline.py script
streamlit run ./pipeline.py
if [ $? -ne 0 ]; then
    echo "Failed to run Streamlit with pipeline.py."
    exit 1
fi

echo "Script completed successfully."
