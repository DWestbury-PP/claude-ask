#!/bin/bash
# Wrapper script to run ask from anywhere
VENV_PATH="/Users/dwestbury/Documents/Source Code/Python/Claude/ask-claude/.venv"
source "$VENV_PATH/bin/activate"
exec "$VENV_PATH/bin/ask" "$@"

