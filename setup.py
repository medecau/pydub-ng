__doc__ = """
Manipulate audio with an simple and easy high level interface.

See the README file for details, usage info, and a list of gotchas.
"""

import sys

from setuptools import setup

requirements = []
if sys.version_info >= (3, 13):
    requirements.append('audioop-lts>=0.2.1')

setup(
    name="pydub",
    version="0.25.1",
    author="James Robert",
    author_email="jiaaro@gmail.com",
    description="Manipulate audio with an simple and easy high level interface",
    license="MIT",
    keywords="audio sound high-level",
    url="http://pydub.com",
    packages=["pydub"],
    install_requires=requirements,
    long_description=__doc__,
    classifiers=[
        "Development Status :: 7 - Inactive",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Sound/Audio :: Editors",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
