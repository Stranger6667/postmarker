# coding: utf-8
from setuptools import setup

import postmarker


setup(
    name='postmarker',
    url='https://github.com/FriendlyCoders/postmarker',
    version=postmarker.__version__,
    packages=['postmarker', 'postmarker.models'],
    license='MIT',
    author='FriendlyCoders',
    keywords=['postmark', 'api', 'client', 'email'],
    description='Python client library for Postmark API',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Communications :: Email',
    ],
    include_package_data=True,
    install_requires=['requests'],
)
