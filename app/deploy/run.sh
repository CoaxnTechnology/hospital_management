#!/bin/bash
set -a
source /home/echo/echo/.env
set +a
exec "$@"
