"""
The plugin entry point
"""

from pathlib import Path

from typing import Dict, Iterable, Union, List

from pii_data.helper.exception import ConfigException
from pii_data.helper.config import load_single_config
from pii_extract.build.collection.task_collection import ensure_enum

from . import VERSION, defs
from .task import PresidioTaskCollector

# Elements in the PIISA presidio config to read
CFG_ELEM = defs.CFG_REUSE, defs.CFG_ENGINE, defs.CFG_PARAMS, defs.CFG_MAP


def load_presidio_plugin_config(config: Union[Dict, str] = None) -> Dict:
    """
    Load the config map from Presidio entities to PIISA PiiEntity object
     :param config: either the configuration, or the filename containing it
    """
    # Load config information
    base = Path(__file__).parent / "resources" / "plugin-config.json"
    data = load_single_config(base, defs.FMT_CONFIG, config)
    if not data:
        raise ConfigException("no config '{}' available", defs.FMT_CONFIG)
    if defs.CFG_MAP not in data:
        raise ConfigException("cannot get config field {} from config",
                              defs.CFG_MAP)
    out = {e: data.get(e, {}) for e in CFG_ELEM}

    # Check the PII type field in each raw descriptor
    for elem in out[defs.CFG_MAP]:
        elem["type"] = ensure_enum(elem["type"])

    return out



class PiiExtractPluginLoader:
    """
    The class acting as entry point for the package (the plugin loader)
    """
    source = defs.TASK_SOURCE
    version = VERSION
    description = defs.TASK_DESCRIPTION


    def __init__(self, config: Union[str, Dict] = None, debug: bool = False,
                 languages: List[str] = None, **kwargs):
        """
          :param config: either a configuration for the plugin, or a filename
            containing that configuration
          :param debug: activate debug mode
          :param languages: languages to load in the Presidio analyzer engine
        """
        self.cfg = load_presidio_plugin_config(config)
        self.obj = PresidioTaskCollector(self.cfg, languages=languages,
                                         debug=debug)


    def __repr__(self) -> str:
        return f'<PiiExtractPluginLoader: presidio {VERSION}>'


    def get_plugin_tasks(self, lang: str = None) -> Iterable[Dict]:
        """
        Return an iterable of task definitions
        """
        yield from self.obj.gather_tasks(lang)
