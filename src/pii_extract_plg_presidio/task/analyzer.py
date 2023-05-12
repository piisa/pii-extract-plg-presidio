"""
Create a Presidio analyzer engine
"""


from typing import Dict, Iterable

from pii_extract.helper.logger import PiiLogger

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine

from .. import defs
from .utils import presidio_languages


# Cache for engine reuse
ENGINE_CACHE = {}


def presidio_analyzer(config: Dict, languages: Iterable[str] = None,
                      logger: PiiLogger = None) -> AnalyzerEngine:
    """
    Create a Presidio AnalyzerEngine object.
    Will reuse an object with the same configuration if it's in the cache
    and `reuse_engine` is True (which is its default value)
    """
    # Fetch NLP engine configuration
    langset = presidio_languages(config)
    #print("ANALYZER", langset, "&", languages, config)
    if languages:
        langset = langset.intersection(languages)
    config = config.get(defs.CFG_ENGINE)

    # Prepare a configuration for the Presidio Analyzer
    # Keep only the language models we'll use
    nlp_config = {
        "nlp_engine_name": config.get("nlp_engine_name"),
        "models": [m for m in config.get("models")
                   if not langset or m["lang_code"] in langset]
    }

    if logger:
        logger(".. Presidio NLP engine: %s", nlp_config.get("nlp_engine_name"))
        logger(".. Presidio NLP models: %s", nlp_config.get("models"))

    # Reuse the engine if we have one with the same parameters
    reuse = config.get(defs.CFG_REUSE, True)
    if reuse:
        key_l = "-".join(sorted(langset)) if langset else "-"
        key_m = (m["lang_code"] + ":" + m["model_name"]
                 for m in nlp_config["models"])
        key = [key_l, nlp_config['nlp_engine_name'], '-'.join(sorted(key_m))]
        key = '/'.join(key)
        engine = ENGINE_CACHE.get(key)
        if key in ENGINE_CACHE:
            if logger:
                logger(".. Reusing Presidio NLP engine")
            return engine

    # Create an NLP engine, according to the configuration
    if logger:
        logger(".. Creating Presidio NLP engine")
    provider = NlpEngineProvider(nlp_configuration=nlp_config)
    nlp_engine = provider.create_engine()

    # Set up the Presidio Analyzer engine
    extra_params = config.get(defs.CFG_PARAMS, {})
    engine = AnalyzerEngine(supported_languages=list(langset) or None,
                            nlp_engine=nlp_engine, **extra_params)
    if reuse:
        ENGINE_CACHE[key] = engine
    return engine
