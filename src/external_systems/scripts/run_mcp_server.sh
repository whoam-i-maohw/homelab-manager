#!/bin/bash
set -e

if [ -f src/configs/prod.env ]; then
    export $(grep -v '^#' src/configs/prod.env | xargs)
fi

poetry run uvicorn \
    --workers 1 \
    --host "0.0.0.0" \
    --port $MCP_PORT \
    src.external_systems.gateway.rest_api.runner:app