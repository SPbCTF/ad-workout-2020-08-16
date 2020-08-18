#!/bin/bash

set -e

BASEDIR=$(dirname "$0")
export PATH=$BASEDIR/node/bin:$PATH

exec "$@"