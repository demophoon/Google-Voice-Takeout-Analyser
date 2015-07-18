#!/usr/bin/env python
from setuptools import setup

setup(
    name="Takeout Analyser",
    version="0.1.0",
    author="Britt Gresham",
    author_email="britt@brittg.com",
    description=("Make pretty graphs out of Google Takeout Data"),
    license="MIT",
    install_requires=[
        'beautifulsoup4',
        'python-dateutil',
        'sqlalchemy',
        'textblob',
    ],
)
