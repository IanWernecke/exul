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
else
    echo "Virtual Environment is installed."
fi


# create or clean the virtual environment
if [[ ! -d $virtual ]]; then
    echo "Creating virtual environment ..."
    $py -m virtualenv --no-site-packages $virtual
fi
echo "Virtual Environment ready."


# ensure the virtual python binary exists
if [[ -f $vpy ]]; then
    echo "Virtual Python found."
else
    echo "Virtual Python not found!"
    exit 1
fi


# if the virtual environment has a previous
# version of the wheel installed, uninstall it
# toolexists=$($vpy -m pip list | grep "^$tool" | wc -l)
# if [[ $toolexists -gt 0 ]]; then
# 
#     pushd $virtual
#     $vpy -m pip uninstall -y $tool
#     popd
# 
#     # if the virtual environment still has the tool installed,
#     # something went wrong
#     toolexists=$($vpy -m pip list | grep "^$tool" | wc -l)
#     if [[ $toolexists -gt 0 ]]; then
#         echo "$toolexists"
#         echo "Unable to uninstall tool: $tool"
#         exit 1
#     fi
# 
# fi


# build the wheel
echo "Building: $tool wheel ..."
$vpy setup.py bdist_wheel
echo "Complete: $tool wheel ..."


echo "Beginning: $tool installation ..."
$vpy -m pip install --upgrade dist/exul*.whl
echo "Complete: $tool installation."


echo "Beginning: $tool test ..."
$vpy -m exul enumeratex
echo "Complete: $tool test."


