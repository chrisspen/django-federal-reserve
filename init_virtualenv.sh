#!/bin/bash
set -e
VENV=${2:-.env}
cd "$(dirname "$0")"
[ -d ./$VENV ] && rm -Rf ./$VENV
python3.7 -m venv ./$VENV
. ./$VENV/bin/activate
pip install wheel
python setup.py bdist_wheel 
pip install -r requirements.txt -r requirements-test.txt
#pip install fred>=3.1
