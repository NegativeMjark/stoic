from setuptools import setup
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))


def read_file(path):
    """Read a UTF-8 file from the package. Takes a list of strings to join to
    make the path"""
    file_path = os.path.join(here, *path)
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def exec_file(path, name):
    """Extract a constant from a python file by looking for a line defining
    the constant and executing it."""
    result = {}
    code = read_file(path)
    lines = [line for line in code.split('\n') if line.startswith(name)]
    exec("\n".join(lines), result)
    return result[name]


setup(
    name="stoic",
    version=exec_file(("stoic/__init__.py",), "__version__"),
    description="A reliable way to run programs",
    long_description=read_file(("README.rst",)),
    url="https://github.com/NegativeMjark/stoic",
    author="Mark Haines",
    author_email="mjark@negativecurvature.net",
    license="Apache License, Version 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
    ],
    keywords="shell",
    packages=["stoic"],
    scripts=["scripts/stoic"],
    install_requires=["pyyaml", "daemonize"],
)
