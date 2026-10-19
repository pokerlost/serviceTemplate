#!/bin/sh
case "$1" in
    *Username*) printf '%s\n' x-access-token ;;
    *Password*) cat /run/secrets/sdk_token ;;
    *) exit 1 ;;
esac
