#!/usr/bin/bash
py=$(which python3)
$py setup.py bdist_wheel
$py -m pip install --user --upgrade dist/exul*.whl
$py -m exul enumeratex
