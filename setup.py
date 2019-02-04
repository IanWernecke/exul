"""This file is used for creating and installing the package."""

import os
from setuptools import setup, find_packages

setup(
    name='exul',
    version='0.0.4',
    author='IanWernecke',
    author_email='IanWernecke@protonmail.com',
    description='A package for handling Xlib operations in an easy-to-use fashion.',
    license='GPLv3',
    keywords='xlib xwindows x-windows mouse keyboard event events',
    url='http://github.com/IanWernecke/exul',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'Xlib'
    ]
)
