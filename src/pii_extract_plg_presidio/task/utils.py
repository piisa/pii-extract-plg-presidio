"""
Some configuration utilities
"""

import sys
from pathlib import Path
from os import environ
from importlib.metadata import version

from typing import Dict, Set

from pii_data.helper.exception import ConfigException
from .. import defs


ENV_HF_CACHE = "HUGGINGFACE_HUB_CACHE"


def hf_cachedir(cachedir: str = None):
    """
    Find the place where to keep the HuggingFace cache
    Create the directory if it does not exist
    """
    # Define HF cache directory
    if not cachedir:
        cachedir = environ.get(ENV_HF_CACHE)
    if cachedir:
        cachedir = Path(cachedir)
    else:
        cachedir = Path(sys.prefix) / "var" / "piisa" / "hf-cache"
    # Create directory if neded
    if not cachedir.is_dir():
        cachedir.mkdir(parents=True)
    # Push it to the environment
    environ[ENV_HF_CACHE] = str(cachedir)

def presidio_languages(config: Dict) -> Set[str]:
    """
    Return the set of languages defined in the configuration for Presidio
    """
    models = config.get(defs.CFG_ENGINE, {}).get("models", [])
    try:
        langlist = [m["lang_code"] for m in models]
    except KeyError:
        raise ConfigException("missing 'lang_code' in Presidio plugin model config")
    return set(langlist)


def presidio_version() -> str:
    """
    Return the version of the Presidio package
    """
    return version("presidio_analyzer")
