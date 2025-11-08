from setuptools import setup, find_packages

setup(
    name = "libPyTelegram",
    version = "2.2",
    author = "Erick Rodriguez",
    description = "A lightweight Python library for sending Telegram messages using PyCurl.",
    long_description = open("README.md", encoding = "utf-8").read(),
    long_description_content_type = "text/markdown",
    packages = find_packages(),
    install_requires = ["pycurl"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0",
        "Operating System :: OS Independent",
    ],
    python_requires = ">=3.12",
)