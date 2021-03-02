# coding: utf-8
from setuptools import find_packages, setup

install_requires = ["requests>=2.20.0"]


with open("README.rst") as file:
    long_description = file.read()


setup(
    name="postmarker",
    url="https://github.com/Stranger6667/postmarker",
    version="0.17.1",
    license="MIT",
    author="Dmitry Dygalo",
    author_email="dadygalo@gmail.com",
    maintainer="Dmitry Dygalo",
    maintainer_email="dadygalo@gmail.com",
    keywords=["postmark", "api", "client", "email"],
    description="Python client library for Postmark API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Communications :: Email",
    ],
    include_package_data=True,
    install_requires=install_requires,
    entry_points={"pytest11": ["postmark = postmarker.pytest"]},
)
