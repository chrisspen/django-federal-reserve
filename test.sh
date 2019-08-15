#!/bin/bash
# Runs all tests.
set -e
./format-yapf.sh
./pep8.sh
export TESTNAME=; tox
