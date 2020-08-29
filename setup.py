# coding: utf-8
from setuptools import setup

import postmarker

install_requires = ["requests>=2.20.0"]


with open("README.rst") as file:
    long_description = file.read()


setup(
    name="postmarker",
    url="https://github.com/Stranger6667/postmarker",
    version=postmarker.__version__,
    packages=["postmarker", "postmarker.models", "postmarker.django"],
    license="MIT",
    author="Dmitry Dygalo",
    author_email="dadygalo@gmail.com",
    maintainer="Dmitry Dygalo",
    maintainer_email="dadygalo@gmail.com",
    keywords=["postmark", "api", "client", "email"],
    description="Python client library for Postmark API",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Communications :: Email",
    ],
    include_package_data=True,
    install_requires=install_requires,
    entry_points={"pytest11": ["postmark = postmarker.pytest"]},
)
