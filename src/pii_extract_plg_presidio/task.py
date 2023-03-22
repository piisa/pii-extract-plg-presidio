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
from pii_extract.helper.utils import taskd_field, union_sets
from pii_extract.helper.logger import PiiLogger

from typing import Iterable, Dict, List

from . import VERSION, defs
from .analyzer import presidio_version, presidio_analyzer


# ---------------------------------------------------------------------


def pii_list(config: Dict, lang: List[str]) -> Dict:
    """
    Restrict the Presidio entity mapping to a given set of languages
    """
    langset = set([lang] if isinstance(lang, str) else lang) if lang else None
    piimap = {}
    for p in config[defs.CFG_MAP]:

        key = f"{p['type']}/{p.get('subtype')}"
        lang = p.get("lang")

        # Remove entries with language defined as None
        if lang is None:
            piimap.pop(key, None)
            continue
        elif langset and not taskd_field(p, "lang") & langset:
            continue    # skip if we've been given a precise set of languages

        piimap[key] = p

    return list(piimap.values())


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
    pii_version = presidio_version


    def __init__(self, task: Dict, pii: List[Dict], cfg: Dict,
                 log: PiiLogger, all_lang: List[str] = None, **kwargs):
        """
          :param task: the PII task info dict
          :param pii: the list of descriptors for the PII entities to include
          :param cfg: the plugin configuration
          :param log: a logger object
          :param all_lang: all languages the analyzer should be initialized for
        """

        # Use the "extra" field in each PII descriptor to build the map of
        # Presidio entities to PIISA entities (by language)
        self.ent_map = defaultdict(dict)
        if isinstance(pii, dict):
            pii = [pii]
        for p in pii:
            try:
                langlist = p["lang"]
                if isinstance(langlist, str):
                    langlist = [langlist]
                for lang in langlist:
                    self.ent_map[lang][p["extra"]["presidio"]] = einfo(p)
            except KeyError as e:
                raise ConfigException("invalid Presidio config: missing field '{}' in: {}", e, p)

        # Now call the parent constructor
        super().__init__(task=task, pii=pii)

        self._log = log

        # Decide is the default language (if we have a single one)
        if all_lang is None:
            all_lang = union_sets(taskd_field(t, "lang") for t in pii)
        self.lang = all_lang[0] if len(all_lang) == 1 else None
        self._log(".. PresidioTask (%s): lang=%s tasks=#%d", VERSION,
                  self.lang or all_lang, len(pii))

        # Set up the Presidio Analyzer engine
        try:
            self.analyzer = presidio_analyzer(cfg, log)
        except Exception as e:
            raise ProcException("cannot create Presidio Analyzer engine: {}",
                                e) from e

        # Check that all Presidio entities we want are actually supported
        entities = set(self.analyzer.get_supported_entities())
        missing = {pname for edict in self.ent_map.values() for pname in edict
                   if pname not in entities}
        if missing:
            raise ProcException("recognizer for {} not found in Presidio",
                                missing)


    def __repr__(self) -> str:
        return f"<PresidioTask #{len(self)}>"


    def __len__(self) -> int:
        return sum(len(k) for k in self.ent_map.values())


    def find(self, chunk: DocumentChunk) -> Iterable[PiiEntity]:
        """
        Perform PII detection on a document chunk
        """
        # Decide the language we'll pass to Presidio: chunk language or default
        ctx = chunk.context or {}
        lang = ctx.get("lang", self.lang)
        if lang is None:
            raise ProcException("Presidio task exception: no language defined in task or document chunk")
        elif lang not in self.ent_map:
            raise ProcException("Presidio task exception: no tasks for lang: {}",
                                lang)

        # Take the entity map for our language
        entity_map = self.ent_map[lang]

        # Call Presidio analyzer to get results
        try:
            results = self.analyzer.analyze(text=chunk.data, language=lang,
                                            entities=list(entity_map))
        except Exception as e:
            raise ProcException("Presidio exception: {}: {}", type(e).__name__,
                                e) from e

        self._log("... Presidio results: %s", results if results else "NONE",
                  level=logging.DEBUG)
        #print("\n**** PRESIDIO", lang, list(self.ent_map), chunk.data, "=>", results, sep="\n")

        # Convert results into PiEntity objects
        for r in sorted(results, key=attrgetter("start")):
            v = chunk.data[r.start:r.end]
            process = {"stage": "detection", "score": r.score}
            yield PiiEntity(entity_map[r.entity_type],
                            v, chunk.id, r.start, process=process)


# ---------------------------------------------------------------------

class PresidioTaskCollector:
    """
    The class used by the plugin loader to produce the Presidio task
    """

    def __init__(self, cfg: Dict, languages: List[str] = None,
                 debug: bool = True):
        self.cfg = cfg
        self.lang = languages
        self._log = PiiLogger(__name__, debug)
        self._log(".. Presidio task collector: init (lang=%s)", languages)


    def gather_tasks(self, lang: str = None) -> Iterable[Dict]:
        """
        Return an iterable of available Detector tasks
        (in this case it is a single multi-task)
        """
        if not lang:
            lang = self.lang
        self._log(".. Presidio gather tasks for lang=%s", lang)

        # The configuration to pass to to the task descriptor
        cfg = {k: self.cfg[k] for k in (defs.CFG_ENGINE, defs.CFG_PARAMS)}

        # Prepare the raw task descriptor
        task = {
            "class": "PiiTask",
            "source": defs.TASK_SOURCE,
            "version": VERSION,
            "doc": defs.TASK_DESCRIPTION,
            "task": PresidioTask,
            "kwargs": {"cfg": cfg, "log": self._log, "all_lang": self.lang},
            "pii": pii_list(self.cfg, self.lang)
        }
        yield task
