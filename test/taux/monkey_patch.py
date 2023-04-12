"""
Some utils to monkey patch 
"""

from dataclasses import dataclass

from unittest.mock import Mock

from typing import List, Dict

from pii_extract.gather.collection.sources.defs import PII_EXTRACT_PLUGIN_ID
from pii_extract_plg_presidio.plugin_loader import PiiExtractPluginLoader

import pii_extract.gather.collection.sources.plugin as mod1
import pii_extract_plg_presidio.task.analyzer as mod_an


# ---------------------------------------------------------------------


def patch_entry_points(monkeypatch):
    """
    Monkey-patch the importlib.metadata.entry_points call to return only our
    plugin entry point
    """
    mock_entry = Mock()
    mock_entry.name = "piisa-detectors-presidio [unit-test]"
    mock_entry.load = Mock(return_value=PiiExtractPluginLoader)

    mock_ep = Mock(return_value={PII_EXTRACT_PLUGIN_ID: [mock_entry]})

    monkeypatch.setattr(mod1, 'entry_points', mock_ep)


# ---------------------------------------------------------------------

PRESIDIO_ENT = ["PERSON", "NRP", "LOCATION", "US_PASSPORT",
                "US_DRIVER_LICENSE", "IT_FISCAL_CODE", "IT_IDENTITY_CARD"]


@dataclass(order=True)
class Result:
    start: int
    end: int
    entity_type: str
    score: float


class AnalyzerEngineMock:

    def __init__(self, results: Dict, **kwargs):
        self.results = {k: [Result(**v) for v in vlist]
                        for k, vlist in results.items()}
        self.data = kwargs
        self.call_args = {}

    def get_supported_entities(self):
        return self.data.get("entities")

    def get_recognizers(self):
        return self.data.get("recognizers")

    def analyze(self, text: str, **kwargs):
        self.call_args[text] = kwargs
        return self.results.get(text)


def patch_presidio_analyzer(monkeypatch, results: Dict,
                            pres_entities: List[str] = None,
                            pres_recognizers: List = None) -> Mock:
    """
    Monkey patch the Presidio API we use
    """

    # Patch NlpEngineProvider
    engine_provider = Mock()
    engine_provider.create_engine = Mock(return_value="<nlp_engine_mock>")
    monkeypatch.setattr(mod_an, 'NlpEngineProvider',
                        Mock(return_value=engine_provider))

    # Create an instance of an analyzer engine mock
    mock_analyzer = AnalyzerEngineMock(results,
                                       entities=pres_entities or PRESIDIO_ENT,
                                       recognizers=pres_recognizers)

    # Patch AnalyzerEngine class
    mock_class = Mock(return_value=mock_analyzer)
    monkeypatch.setattr(mod_an, 'AnalyzerEngine', mock_class)

    # Reset cache
    monkeypatch.setattr(mod_an, 'ENGINE_CACHE', {})

    return mock_class
