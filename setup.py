from setuptools import setup

setup(
    name='manager',
    version='0.1',
    py_modules=['manager'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        manager=manager:cli
    ''',
)