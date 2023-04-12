"""
Some configuration utilities
"""

from importlib.metadata import version

from typing import Dict, Set

from pii_data.helper.exception import ConfigException
from .. import defs



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
