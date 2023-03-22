"""
Create a Presidio analyzer engine
"""

from importlib.metadata import version

from typing import Dict, List

from pii_extract.helper.logger import PiiLogger

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine

from . import defs


# Cache for engine reuse
ENGINE_CACHE = {}


def presidio_version() -> str:
    """
    Return the version of the Presidio package
    """
    return version("presidio_analyzer")


def presidio_analyzer(config: Dict,
                      logger: PiiLogger = None) -> AnalyzerEngine:
    """
    Create a Presidio AnalyzerEngine object.
    Will reuse an object with the same configuration if it's in the cache
    and `reuse_engine` is True (which is its default value)
    """
    # Fetch NLP engine configuration. Keep only the language models we'll use
    eng = config.get(defs.CFG_ENGINE)
    lang = eng.get("languages", [])
    if isinstance(lang, str):
        lang = [lang]
    langset = set(lang)
    nlp_config = {
        "nlp_engine_name": eng.get("nlp_engine_name"),
        "models": [m for m in eng.get("models")
                   if not langset or m["lang_code"] in langset]
    }

    if logger:
        logger(".. Presidio NLP engine: %s", nlp_config.get("nlp_engine_name"))
        logger(".. Presidio NLP models: %s", nlp_config.get("models"))

    # Reuse engine if it has the same parameters
    reuse = config.get(defs.CFG_REUSE, True)
    if reuse:
        key_l = "-".join(sorted(lang)) if lang else "-"
        key_m = (m["lang_code"] + ":" + m["model_name"]
                 for m in nlp_config["models"])
        key = [key_l, nlp_config['nlp_engine_name'], '-'.join(sorted(key_m))]
        key = '/'.join(key)
        engine = ENGINE_CACHE.get(key)
        if key in ENGINE_CACHE:
            logger(".. Reusing Presidio NLP engine")
            return engine


    # Create an NLP engine, according to the configuration
    logger(".. Creating Presidio NLP engine")
    provider = NlpEngineProvider(nlp_configuration=nlp_config)
    nlp_engine = provider.create_engine()

    # Set up the Presidio Analyzer engine
    engine = AnalyzerEngine(supported_languages=lang or None,
                            nlp_engine=nlp_engine, **config[defs.CFG_PARAMS])
    if reuse:
        ENGINE_CACHE[key] = engine
    return engine
