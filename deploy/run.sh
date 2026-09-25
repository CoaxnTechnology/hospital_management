#!/bin/bash
set -a
source /var/www/echo/.env
set +a
exec "$@"
