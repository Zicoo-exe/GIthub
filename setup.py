#!/usr/bin/env python3
"""
GitClonePro - Universal GitHub Clone Tool
Author: KL__Zicoo
License: MIT
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitclonepro",
    version="2.0.0",
    author="KL__Zicoo",
    author_email="your@email.com",
    description="Advanced GitHub clone tool with sparse, batch, mirror, and parallel support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/GitClonePro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml>=5.4",
        "requests>=2.25",
        "tqdm>=4.62",
        "colorama>=0.4",
    ],
    entry_points={
        "console_scripts": [
            "gitclone=gitclone.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)