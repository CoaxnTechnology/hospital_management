#!/bin/bash
set -a
source /home/echo/app/.env
set +a
exec "$@"
