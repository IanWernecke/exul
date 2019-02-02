#!/usr/bin/bash
py=$(which python3)
tool="exul"
virtual="$(pwd)/virtual"
vpy="$virtual/bin/python"
svpy="bin/python"

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
if [[ -d $dist && $(ls $dist/$tool*.whl | wc -l) -gt 0 ]]; then
    rm $dist/$tool*.whl
fi
if [[ -d $virtual && $(ls $virtual/$tool*.whl | wc -l) -gt 0 ]]
then
    rm $virtual/$tool*.whl
fi
echo "Complete: Removing old wheels."


# build the wheel
echo "Building: $tool wheel ..."
$vpy setup.py bdist_wheel
echo "Complete: $tool wheel ..."


# move the wheel to $virtual
echo "Copying wheels to virtual environment ..."
cp $dist/$tool-*.whl $virtual
echo "Copied wheels to the virtual environment."


pushd $virtual

# pip uninstall
echo "Beginning: $tool uninstallation ..."
$svpy -m pip uninstall -y $tool
echo "Complete: $tool uninstallation."


# pip install
echo "Beginning: $tool installation ..."
$svpy -m pip install --upgrade $tool-*.whl
echo "Complete: $tool installation."


# test wheel
echo "Beginning: $tool test ..."
$svpy -m $tool enumerate
echo "Complete: $tool test."

popd
