from setuptools import setup, find_packages
import sys
import os, codecs

if sys.version_info < (3, 6):
    raise Exception('Must be installed with python version 3.6+')

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    python_requires='>=3.6',
    name='contest_tools',
    version='0.1.1',
    description='Useful scripts for programming contests',
    long_description=long_description,
    license='MIT',
    packages=["contest_tools"],
    #install_requires=[],
    entry_points={
        'console_scripts': [
            'contest_tools = contest_tools.contest_tools:main',
        ],
    },
)
