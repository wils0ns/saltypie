from setuptools import setup, find_packages
from os import path
from codecs import open

this_folder = path.abspath(path.dirname(__file__))

# Get package version from .version file
with open(path.join(this_folder, '.version')) as f:
    version = f.read()

# Get long description from README.rst file
with open(path.join(this_folder, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='saltypie',
    version=version,
    author='Wilson Santos',
    author_email='wilson@codeminus.org',
    url='https://gitlab.com/cathaldallan/saltypie',
    description='Saltypie - salt-api wrapper',
    long_description=long_description,
    license='MIT',
    keywords='saltstack salt salt-api wrapper',
    classifiers=[
        # 'Programming Language :: Python :: 2.7',
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
