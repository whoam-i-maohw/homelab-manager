#!/bin/bash
set -e

if [ -f src/configs/prod.env ]; then
    export $(grep -v '^#' src/configs/prod.env | xargs)
fi

poetry run uvicorn \
    --workers $GATEWAY_WORKERS \
    --port $GATEWAY_PORT \
    src.external_systems.gateway.rest_api.runner:app