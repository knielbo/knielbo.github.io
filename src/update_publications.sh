#!/bin/bash

# Advanced publication update script

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Define paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
LOG_FILE="$SCRIPT_DIR/publications_update.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Utility functions
log_info() {
    echo -e "${GREEN}[INFO][$DATE] $1${NC}" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN][$DATE] $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR][$DATE] $1${NC}" | tee -a "$LOG_FILE"
}

check_success() {
    if [ $? -ne 0 ]; then
        log_error "$1 failed! Exiting."
        exit 1
    else
        log_info "$1 completed successfully."
    fi
}

# Header
echo "==============================================" | tee -a "$LOG_FILE"
log_info "Starting publication update process"

# Activate virtual environment if you use one (uncomment if applicable)
# source /path/to/venv/bin/activate

# Step 1: Generate publications.html from pure research outputs
log_info "Executing pure_to_web.py"
python "$SCRIPT_DIR/pure_to_web.py"
check_success "pure_to_web.py"

# Step 2: Generate yearly publication bigraphs
log_info "Executing publication_bigraphs.py"
python "$SCRIPT_DIR/publication_bigraphs.py"
check_success "publication_bigraphs.py"

# Step 3: Insert generated figures into publications.html
log_info "Executing publication_insert_fig.py"
python "$SCRIPT_DIR/publication_insert_fig.py"
check_success "publication_insert_fig.py"

# Completion message
log_info "Publication update completed successfully!"
echo "==============================================" | tee -a "$LOG_FILE"