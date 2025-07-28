#!/bin/bash

if [[ -d lfs.git ]]; then
  pushd lfs.git
  git fetch
  git pull
  popd
else
  git clone https://git.linuxfromscratch.org/lfs.git lfs.git
fi
