import setuptools

with open('README.md', 'r') as rdme:
    long_description = rdme.read()

setuptools.setup(
    name='konfchanger',
    version='0.1',
    py_modules=['konfchanger','konfchanger_utils'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        konfchanger=konfchanger:konfchanger''',
    packages=setuptools.find_packages(),
    author='Shrijit Basak(SB-Jr)',
    author_email='shrijitbasak@gmail.com',
    description='A CLI tool to backup/restore configuration files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='backup restore configuration config files',
    url='https://github.com/SB-Jr/konfigchanger',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7.7'
)
