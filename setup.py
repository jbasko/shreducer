#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='shreducer',
    version=read('shreducer/__init__.py').split('\n')[0].split('=', 1)[1].strip().strip("'"),
    author='Jazeps Basko',
    author_email='jazeps.basko@gmail.com',
    maintainer='Jazeps Basko',
    maintainer_email='jazeps.basko@gmail.com',
    license='MIT',
    url='https://github.com/jbasko/shreducer',
    description='Grammars, parsers, and compilers in Python 3.6+',
    long_description=read('README.rst'),
    packages=find_packages(".", exclude=["tests"]),
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)
