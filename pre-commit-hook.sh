#!/usr/bin/env bash
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
ARGS="hook-impl --config=.pre-commit-config.yaml --hook-type=pre-commit --hook-dir \"${HOOK_DIR}\" -- ${*}"
GIT_INDEX_FILE_RELATIVE=${GIT_INDEX_FILE#"$(pwd)/"}

exec make pre-commit-run IMAGE_ARGS="${ARGS}" CUSTOM_DOCKER_ARGS="-e GIT_INDEX_FILE=${GIT_INDEX_FILE_RELATIVE}"
