#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import sys

version = '0.2.0'

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': version}
    print "You probably want to also tag the version now:"
    print "  git tag -a %(version)s -m 'version %(version)s'" % args
    print "  git push --tags"
    sys.exit()


setup(
    name='python-yubikey',
    version=version,
    url='http://github.com/fmartingr/python-yubikey',
    license='GPLv2',
    description='Simple Yubico API Wrappers',
    author='Felipe Martin',
    author_email='fmartingr@me.com',
    py_modules=['yubikey'],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('requirements.txt').read().split('\n'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
