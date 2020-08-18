#!/bin/bash

set -eux

VERSION=14.8.0
DISTRO=linux-x64

wget "https://nodejs.org/dist/v${VERSION}/node-v${VERSION}-${DISTRO}.tar.xz"
tar -xJvf node-v${VERSION}-${DISTRO}.tar.xz -C ./
rm node-v${VERSION}-${DISTRO}.tar.xz
mv node-v${VERSION}-${DISTRO} node

