#!/usr/bin/env python
from setuptools import setup, find_packages
import os

from betterforms.version import get_version

__doc__ = """
App for Django featuring improved form base classes.
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-betterforms',
    version=get_version(),
    description=__doc__,
    long_description=read('README.rst'),
    url="https://django-betterforms.readthedocs.org/en/latest/",
    author="Fusionbox",
    author_email='programmers@fusionbox.com',
    packages=[package for package in find_packages() if package.startswith('betterforms')],
    install_requires=[
        'Django>=1.4',
        'six',
    ],
    tests_require=[
        'mock>=1.0.1',
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
