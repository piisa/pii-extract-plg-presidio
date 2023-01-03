"""
Create a Presidio analyzer engine
"""

from importlib.metadata import version

from typing import Dict, List

from pii_extract.helper.logger import PiiLogger

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine

from . import defs


def presidio_version() -> str:
    """
    Return the version of the Presidio package
    """
    return version("presidio_analyzer")


def presidio_analyzer(config: Dict, lang: List[str],
                      logger: PiiLogger = None) -> AnalyzerEngine:
    """
    Create a Presidio AnalyzerEngine object
    """

    # Fetch NLP engine configuration. Keep only the language models we'll use
    langset = set(lang) if lang else None
    eng = config.get(defs.CFG_ENGINE)
    nlp_config = {
        "nlp_engine_name": eng.get("nlp_engine_name"),
        "models": [m for m in eng.get("models")
                   if not langset or m["lang_code"] in langset]
    }
    if logger:
        logger(".. Presidio NLP engine: %s", nlp_config.get("nlp_engine_name"))
        logger(".. Presidio NLP models: %s", nlp_config.get("models"))

    # Create an NLP engine, according to the configuration
    provider = NlpEngineProvider(nlp_configuration=nlp_config)
    nlp_engine = provider.create_engine()

    # Set up the Presidio Analyzer engine
    return AnalyzerEngine(supported_languages=lang or None,
                          nlp_engine=nlp_engine, **config[defs.CFG_PARAMS])
