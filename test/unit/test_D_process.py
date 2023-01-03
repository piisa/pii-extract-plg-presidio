"""
Test building the Presidio task and using it for detection
"""

import pytest

from pii_extract.build.collection import get_task_collection

from taux.monkey_patch import patch_entry_points, patch_presidio_analyzer
from taux.taskproc import process_tasks


TESTCASES = [
    (
        # source document
        "The English mathematician Alan Turing is considered the father of AI",

        # mock the result delivered by Presidio
        [{"start": 4, "end": 11, "entity_type": "NRP", "score": 0.85},
         {"start": 26, "end": 37, "entity_type": "PERSON", "score": 0.85}],

        # expected processed document
        "The <NORP:English> mathematician <PERSON:Alan Turing> is considered the father of AI",

        # expected PII collection
        [{"type": "NORP", "lang": "en", "chunkid": "1",
          "process": {"stage": "detection", "score": 0.85},
          "value": "English", "start": 4, "end": 11},
         {"type": "PERSON", "lang": "en", "chunkid": "1",
          "process": {"stage": "detection", "score": 0.85},
          "value": "Alan Turing", "start": 26, "end": 37}]
    )
]



# ---------------------------------------------------------------------------


def test20_detect(monkeypatch):
    """
    Check detection
    """
    results = {t[0]: t[1] for t in TESTCASES}
    patch_presidio_analyzer(monkeypatch, results)
    patch_entry_points(monkeypatch)

    piic = get_task_collection()
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    for src_doc, _, exp_doc, exp_pii in TESTCASES:
        got_pii, got_doc = process_tasks(tasks, src_doc)
        assert exp_doc == got_doc

        got_pii = list(got_pii)
        assert len(got_pii) == 2

        for e, g in zip(exp_pii, got_pii):
            #print("\nGOT", g.asdict())
            assert e == g.asdict()
