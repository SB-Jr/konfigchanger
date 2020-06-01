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
        konfchanger=konfchanger:konfchanger'''
)
