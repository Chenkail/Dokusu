#!/bin/bash

python setup.py sdist bdist_wheel

if [ $1 == "pypi" ]; then
    python -m twine upload dist/*
elif [ $1 == "test" ]; then
    python -m twine upload --repository testpypi dist/*
else
    echo "Invalid argument, could not upload to PyPI"
fi
