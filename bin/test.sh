#!/bin/env bash
PROJECT_DIR=$(
    cd $(dirname $0)/.. >/dev/null;
    pwd;
)
cd "$PROJECT_DIR"
python -m pytest --exitfirst tests
