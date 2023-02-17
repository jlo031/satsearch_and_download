import os
from setuptools import setup, find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name = "satsearch_and_download",
    version = "0.0.1",
    author = "Johannes Lohse",
    author_email = "johannes.lohse@uit.no",
    description = ("Search and download Copernices Sentinel data."),
    license = "The Ask Johannes Before You Do Anything License",
    long_description=read('README.md'),
    install_requires = [
        'sentinelsat',
        'dateparser',
        'numpy',
        'ipython',
        'loguru',
        'python-dotenv',
    ],
    packages = find_packages(where='src'),
    package_dir = {'': 'src'},
    package_data = {'': ['.env']},
    entry_points = {
        'console_scripts': [
        ]
    },
    include_package_data=True,
)
