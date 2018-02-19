from io import open
from os import path
from setuptools import setup, find_packages

THIS_FOLDER = path.abspath(path.dirname(__file__))

# Get package version from .version file
with open(path.join(THIS_FOLDER, '.version')) as f:
    VERSION = f.read()

# Get long description from README.rst file
with open(path.join(THIS_FOLDER, 'README.rst'), encoding='utf-8') as f:
    README = f.read()

setup(
    name='saltypie',
    version=VERSION,
    author='Wilson Santos',
    author_email='wilson@codeminus.org',
    url='https://gitlab.com/cathaldallan/saltypie',
    description='Saltypie - salt-api wrapper and return parser',
    long_description=README,
    license='MIT',
    keywords='saltstack salt salt-api wrapper',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'requests',
        'terminaltables',
        'colorclass',
        'colorama',
        'termcolor',
    ],
)
