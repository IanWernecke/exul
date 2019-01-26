#!/usr/bin/bash
py=$(which python3)
tool="exul"
virtual="$(pwd)/virtual"
vpy="$virtual/bin/python"

# ensure virtualenv is installed into python
vexists=$($py -m pip list | grep "^virtualenv" | wc -l)
if [[ $vexists -eq 0 ]]; then
    echo "Virtual Environment not installed."
    exit 1
fi
echo "Virtual Environment is installed."


# create or clean the virtual environment
if [[ ! -d $virtual ]]; then
    echo "Creating virtual environment ..."
    $py -m virtualenv --no-site-packages $virtual
fi
echo "Virtual Environment ready."


# ensure the virtual python binary exists
if [[ ! -f $vpy ]]; then
    echo "Virtual Python not found!"
    exit 1
fi
echo "Virtual Python found."


# clean up old wheels
dist="$(pwd)/dist"
echo "Beginning: Removing old wheels ..."
if [[ -d $dist && $(ls $dist/exul*.whl | wc -l) -gt 0 ]]; then
    rm $dist/exul*.whl
fi
echo "Complete: Removing old wheels."


# build the wheel
echo "Building: $tool wheel ..."
$vpy setup.py bdist_wheel
echo "Complete: $tool wheel ..."


echo "Beginning: $tool installation ..."
$vpy -m pip install --upgrade $dist/exul*.whl
echo "Complete: $tool installation."


echo "Beginning: $tool test ..."
$vpy -m exul enumeratex
echo "Complete: $tool test."
