#!/usr/bin/env python3

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='a2utils',
    version='0.0.30',
    scripts=[
        'bin/a2conf',
        'bin/a2okerr',
        'bin/a2certbot',
        'bin/a2certbotssh',
        'bin/a2vhost'
        ],

    # install_requires=[],

    url='https://github.com/yaroslaff/a2utils',
    license='MIT',
    author='Yaroslav Polyakov',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author_email='yaroslaff@gmail.com',
    description='apache2 config file utilities',
    install_requires=['a2conf>=0.3.1'],

    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
#        'Programming Language :: Python :: 3.4',
    ]
)
