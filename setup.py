"""
Manipulate audio with an simple and easy high level interface.

See the README file for details, usage info, and a list of gotchas.
"""

import sys

from setuptools import setup

# This setup.py is kept for backwards compatibility
# Primary configuration is now in pyproject.toml

# For Python 3.13+, we need audioop-lts
requirements = []
if sys.version_info >= (3, 13):
    requirements.append("audioop-lts>=0.2.1")

if __name__ == "__main__":
    setup(
        install_requires=requirements,
    )
