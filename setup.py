"""Distribution package setup script."""
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as readme_file:
    readme = readme_file.read()
try:
    with open('CHANGELOG.rst') as changelog_file:
        changelog = changelog_file.read()
    long_description = '\n\n'.join((readme, changelog))
except FileNotFoundError:
    long_description = readme

setup(
    name='uniswag',

    description='"Universal Signal Waveform Acquisition & Generation" is a GUI-based software for controlling oscilloscopes and signal generators from a variety of vendors.',
    long_description=long_description,
    author='Eric Kondratenko',
    author_email='erickon@mail.uni-paderborn.de',
    url='https://github.com/emtpb/uniswag/',
    license='BSD',

    # Automatically generate version number from git tags
    use_scm_version=True,

    # Automatically detect the packages and sub-packages
    packages=find_packages(),

    # Runtime dependencies
    install_requires=[
        'handyscope',
        'keysightosc',
        'numpy',
        'PySide6',
        'pyusb',
        'scipy',
        'tektronixsg',
        'pyudev; sys_platform=="linux"',
        'pyvisa-py; sys_platform=="win32"',
        'wmi; sys_platform=="win32"',
    ],

    # Python version requirement
    python_requires='>=3',

    # Dependencies of this setup script
    setup_requires=[
        'setuptools_scm',  # For automatic git-based versioning
    ],

    # For a full list of valid classifiers, see:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],

    include_package_data=True,

    entry_points={
        'console_scripts': ['UniSWAG=uniswag.main:main'],
    },
)
