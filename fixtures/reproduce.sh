#!/usr/bin/env sh
set -eu
# Preparation only. Does not invoke Claude or submit an issue.
python -m runners.prepare_fixture "${1:?Provide a new destination directory}"
