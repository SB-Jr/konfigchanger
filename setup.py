from setuptools import setup

setup(
    name='konfchanger',
    version='0.1',
    py_modules=['konfchanger','konfchanger_utils'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        konfchanger=konfchanger:konfchanger''',
    author='Shrijit Basak(SB-Jr)',
    author_email='shrijitbasak@gmail.com',
    description='A CLI tool to backup/restore configuration files',
    keywords='backup restore configuration config files',

)
