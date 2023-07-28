"""
The Presidio-based PiiTask
"""

import logging
from operator import attrgetter
from collections import defaultdict

from pii_data.helper.exception import ProcException, ConfigException
from pii_data.types import PiiEntity, PiiEntityInfo
from pii_data.types.doc import DocumentChunk
from pii_extract.build.task import BaseMultiPiiTask
from pii_extract.helper.utils import taskd_field
from pii_extract.helper.logger import PiiLogger

from typing import Iterable, Dict, List

from .. import VERSION
from .utils import hf_cachedir



def einfo(p: Dict) -> PiiEntityInfo:
    """
    Create an entity info object from a PII descriptor dict
    """
    return PiiEntityInfo(p["pii"], p.get("lang"), p.get("country"),
                         p.get("subtype"))


# ---------------------------------------------------------------------


class PresidioTask(BaseMultiPiiTask):
    """
    PII Detector wrapper over the Presidio Library
    """
    pii_source = "microsoft:presidio"
    pii_name = "Presidio wrapper"
    pii_version = VERSION


    def __init__(self, task: Dict, pii: List[Dict], cfg: Dict,
                 model_lang: Iterable[str], log: PiiLogger, **kwargs):
        """
          :param task: the PII task info dict
          :param pii: the list of descriptors for the PII entities to include
          :param cfg: the plugin configuration
          :param model_lang: languages to instantiate models for
          :param log: a logger object
        """
        #print("\nPresidioTask INIT", model_lang, pii)

        # Use the "extra" field in the PII dict to build a map (by language)
        # of Presidio entities to PIISA entities
        # (before parent constructor, which will strip away "extra" fields)
        self._ent_map = defaultdict(dict)
        pii_lang = set()
        if isinstance(pii, dict):
            pii = [pii]
        for p in pii:
            try:
                langset = taskd_field(p, "lang")
                pii_lang.update(langset)
                for lang in langset:
                    self._ent_map[lang][p["extra"]["presidio"]] = einfo(p)
            except KeyError as e:
                raise ConfigException("invalid Presidio config: missing field '{}' in: {}", e, p) from e

        # Initialize
        super().__init__(task=task, pii=pii)
        self._log = log

        # Decide a default language for this task (possible if we have only one)
        self.lang = next(iter(pii_lang)) if len(pii_lang) == 1 else None
        self._log(".. PresidioTask (%s): lang=%s tasks=#%d", VERSION,
                  self.lang, len(pii))

        # Define cache directory for HuggingFace, just in case we use Transformers
        cachedir = cfg.get("cachedir")
        if cachedir is not False:
            hf_cachedir(cachedir)

        # Set up the Presidio Analyzer engine
        try:
            from .analyzer import presidio_analyzer
            self.analyzer = presidio_analyzer(cfg, languages=model_lang,
                                              logger=self._log)
        except Exception as e:
            raise ProcException("cannot create Presidio Analyzer engine: {}",
                                e) from e

        # Check that all Presidio entities we want are actually supported
        entities = set(self.analyzer.get_supported_entities())
        missing = {pname for edict in self._ent_map.values() for pname in edict
                   if pname not in entities}
        if missing:
            raise ProcException("recognizer for {} not found in Presidio",
                                missing)


    def __repr__(self) -> str:
        return f"<PresidioTask #{len(self)}>"


    def __len__(self) -> int:
        return sum(len(k) for k in self._ent_map.values())


    def find(self, chunk: DocumentChunk) -> Iterable[PiiEntity]:
        """
        Perform PII detection on a document chunk
        """
        # Decide the language we'll pass to Presidio: chunk language or default
        ctx = chunk.context or {}
        lang = ctx.get("lang", self.lang)
        if lang is None:
            raise ProcException("Presidio task exception: no language defined in task or document chunk")
        elif lang not in self._ent_map:
            raise ProcException("Presidio task exception: no tasks for lang: {}",
                                lang)

        # Take the entity map for our language
        entity_map = self._ent_map[lang]
        #print("LANG", lang, "DATA", chunk.data, entity_map)

        # Call Presidio analyzer to get results
        try:
            results = self.analyzer.analyze(text=chunk.data, language=lang,
                                            entities=list(entity_map))
        except Exception as e:
            raise ProcException("Presidio exception: {}: {}", type(e).__name__,
                                e) from e

        self._log("... Presidio results: %s", results if results else "NONE",
                  level=logging.DEBUG)
        #print("\n**** PRESIDIO", lang, list(self._ent_map), chunk.data, "=>", results, sep="\n")

        # Convert results into PiEntity objects
        for r in sorted(results, key=attrgetter("start")):
            v = chunk.data[r.start:r.end]
            process = {"stage": "detection", "score": r.score}
            yield PiiEntity(entity_map[r.entity_type],
                            v, chunk.id, r.start, process=process)
