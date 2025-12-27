#!/bin/bash
# Wrapper para facilitar el deployment desde el root del proyecto
exec "$(dirname "$0")/deployment/scripts/deploy-final.sh" "$@"
