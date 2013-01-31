# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(here, 'README.rst')

install_requirements = [
    'pybit',
    'jsonpickle',
    ]
test_requirements = [
    ]

setup(
    name='cnx-pybit',
    version='1.0',
    author="Connexions/Rhaptos Team",
    author_email="info@cnx.org",
    description='Rhaptos PyBit implementation',
    long_description=open(README).read(),
    url='https://github.com/connexions/cnx-pybit',
    license='GPL2',  # See also LICENSE.txt
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requirements,
    extras_require={
        'tests': test_requirements,
        },
    entry_points = """\
    [console_scripts]
    cnx-pybit = cnx_pybit:run
    """,
    )
