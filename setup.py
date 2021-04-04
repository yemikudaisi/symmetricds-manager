from setuptools import setup, find_packages
from sdmanager import PROJECT_NAME, VERSION

setup(
    name=PROJECT_NAME,
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        sd-manager=sdmanager.cli:cli
    ''',
)