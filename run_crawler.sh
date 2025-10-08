#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found at venv/bin/activate"
fi

# Prevent system sleep while running (allow display sleep to save energy)
caffeinate -i -w $$ &
CAFFEINATE_PID=$!

# Set display to sleep after 10 minutes to save energy
pmset displaysleep 10

# Cleanup function
cleanup() {
    echo "Stopping crawler..."
    kill $CAFFEINATE_PID 2>/dev/null
    deactivate 2>/dev/null
    exit 0
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Run crawler with auto-restart
while true; do
    echo "Starting crawler at $(date)"
    echo "Working directory: $(pwd)"
    echo "Python version: $(python --version)"
    
    # Run with unbuffered output
    python -u crawl_by_metadata.py
    
    # If script exits, wait 30 seconds and restart
    echo "Crawler stopped at $(date). Restarting in 30 seconds..."
    sleep 30
done