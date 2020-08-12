#!/bin/sh

set -e

GIT_HOOKS_DIR=".git/hooks/"
mkdir -p "$GIT_HOOKS_DIR"

for entry in git_hooks/*
do
  cp "$entry" "$GIT_HOOKS_DIR"
  echo "$entry installed"
done
