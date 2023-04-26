#! /usr/bin/env python3

from setuptools import setup


setup(
    name='lptlib',
    use_scm_version={
        "local_scheme": "node-and-timestamp"
    },
    setup_requires=['setuptools_scm'],
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info at homeinfo dot de>',
    maintainer='Richard Neumann',
    maintainer_email='<r dot neumann at homeinfo priod de>',
    install_requires=[
        'configlib',
        'functoolsplus',
        'flask',
        'hwdb',
        'mdb',
        'trias',
        'hafas',
        'wsgilib'
    ],
    packages=['lptlib'],
    license='GPLv3',
    description='General purpose local public transport API.')
