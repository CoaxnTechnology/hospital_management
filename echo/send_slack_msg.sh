#!/bin/bash
message=$1

[ ! -z "$message" ] && curl -X POST -H 'Content-type: application/json' --data "{
              \"text\": \"${message}\"
      }" "$SLACK_WEBHOOK_URL"