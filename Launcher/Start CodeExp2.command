#!/bin/zsh
set -eu
launcher_dir="${0:A:h}"
exec "$launcher_dir/../MacOS/CodeExp2" --terminal
