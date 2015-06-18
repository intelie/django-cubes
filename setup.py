#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):
    user_options = TestCommand.user_options + [
        ('environment=', 'e', "Run 'test_suite' in specified environment")
    ]
    environment = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        if self.environment:
            self.test_args.append('-e{0}'.format(self.environment))
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


def get_readme():
    """Return the README file contents. Supports text,rst, and markdown"""
    for name in ('README', 'README.rst', 'README.md'):
        if os.path.exists(name):
            return read_file(name)
    return ''


def install_requires():
    return read_file('requirements.txt')


extras = {
    'facts': 'django-facts>=0.5.3',
    'all': ['django-cubes[%s]' % extra for extra in ['facts']],
}


setup(
    name="django-cubes",
    version="0.0.1",
    url='https://github.com/intelie/django-cubes',
    author='Vitor M. A. da Cruz',
    author_email='vitor.mazzi@intelie.com.br',
    description='',
    long_description=get_readme(),
    packages=find_packages(exclude=["example"]),
    include_package_data=True,
    install_requires=install_requires(),
    extras_require=extras,
    tests_require=['virtualenv>=1.11.2', 'tox>=1.6.1', ],
    cmdclass={'test': Tox},
    test_suite='django_cubes.tests',
    classifiers=[
        'Framework :: Django',
    ],
    license="MIT",
)
