"""
Create pii-extract-plg-presidio as a Python package
"""

import io
import sys
import re

from setuptools import setup, find_packages

from src.pii_extract_plg_presidio import VERSION

PKGNAME = "pii-extract-plg-presidio"
GITHUB_URL = "https://github.com/piisa/" + PKGNAME

# --------------------------------------------------------------------

PYTHON_VERSION = (3, 8)

if sys.version_info < PYTHON_VERSION:
    sys.exit(
        "**** Sorry, {} {} needs at least Python {}".format(
            PKGNAME, VERSION, ".".join(map(str, PYTHON_VERSION))
        )
    )


def requirements(filename="requirements.txt"):
    """Read the requirements file"""
    with io.open(filename, "r") as f:
        return [line.strip() for line in f if line and line[0] != "#"]


def long_description():
    """
    Take the README and remove markdown hyperlinks
    """
    with open("README.md", "rt", encoding="utf-8") as f:
        desc = f.read()
        # action icons
        desc = re.sub(r"^ \[ ! \[ [^\]]+ \] \( [^\)]+ \) \] \( [^\)]+ \)\n", "",
                      desc, flags=re.X | re.M)
        # References
        desc = re.sub(r"^\[ [^\]]+ \]: \s+ \S.*\n", "", desc, flags=re.X | re.M)
        # Links
        return re.sub(r"\[ ([^\]]+) \] (?: \( [^\)]+ \) )?", r"\1", desc,
                      flags=re.X)


# --------------------------------------------------------------------


setup_args = dict(
    # Metadata
    name=PKGNAME,
    version=VERSION,
    author="Paulo Villegas",
    author_email="paulo.vllgs@gmail.com",
    description="Presidio plugin for PII detection",
    long_description_content_type="text/markdown",
    long_description=long_description(),
    license="Apache",
    url=GITHUB_URL,
    download_url=GITHUB_URL + "/tarball/v" + VERSION,
    # Locate packages
    packages=find_packages("src"),  # [ PKGNAME ],
    package_dir={"": "src"},
    # Requirements
    python_requires=">=" + ".".join(map(str, PYTHON_VERSION)),
    # Optional requirements
    extras_require={
        "test": ["pytest", "nose", "coverage"],
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pii-extract-presidio-info = pii_extract_plg_presidio.app.info:main"
        ],
        "pii_extract.plugins": "piisa-detectors-presidio = pii_extract_plg_presidio.plugin_loader:PiiExtractPluginLoader"
    },
    include_package_data=True,
    package_data={"": ["pii_extract_plg_presidio/resources/*.json"]},
    # Post-install hooks
    cmdclass={},
    keywords=["PIISA, PII"],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)

if __name__ == "__main__":
    # Add requirements
    setup_args["install_requires"] = requirements()
    # Setup
    setup(**setup_args)
