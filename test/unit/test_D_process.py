"""
Test building the Presidio task and using it for detection
"""

import pytest

from pii_data.helper.exception import ProcException
from pii_extract.gather.collection import get_task_collection

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
    # Patch the plugin entry point so that only the presidio plugin is detected
    patch_entry_points(monkeypatch)

    # Patch the presidio analyzer function so that we don't actually call Presidio
    results = {t[0]: t[1] for t in TESTCASES}
    patch_presidio_analyzer(monkeypatch, results)

    # Gather tasks and build them
    piic = get_task_collection()
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    for src_doc, _, exp_doc, exp_pii in TESTCASES:
        got_pii, got_doc = process_tasks(tasks, src_doc, lang="en")
        assert exp_doc == got_doc

        got_pii = list(got_pii)
        assert len(got_pii) == 2

        for e, g in zip(exp_pii, got_pii):
            #print("\nGOT", g.asdict())
            assert e == g.asdict()


def test21_detect_default_lang(monkeypatch):
    """
    Check detection, with a default language
    """
    # Patch the plugin entry point so that only the presidio plugin is detected
    patch_entry_points(monkeypatch)

    # Patch the presidio analyzer function so that we don't actually call Presidio
    results = {t[0]: t[1] for t in TESTCASES}
    patch_presidio_analyzer(monkeypatch, results)

    # Gather tasks and build them
    piic = get_task_collection()
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    for src_doc, _, exp_doc, exp_pii in TESTCASES:
        # No language sent in the chunks -- the task should use the default
        got_pii, got_doc = process_tasks(tasks, src_doc)
        assert exp_doc == got_doc

        got_pii = list(got_pii)
        assert len(got_pii) == 2

        for e, g in zip(exp_pii, got_pii):
            #print("\nGOT", g.asdict())
            assert e == g.asdict()


def test30_error_lang(monkeypatch):
    """
    Check error generation due to language not specified
    """
    # Patch the plugin entry point so that only the presidio plugin is detected
    patch_entry_points(monkeypatch)

    # Patch the presidio analyzer function so that we don't actually call Presidio
    results = {t[0]: t[1] for t in TESTCASES}
    patch_presidio_analyzer(monkeypatch, results)

    # Gather tasks and build them. Use two languages, to preclude definition
    # of a default language in the Presidio task
    piic = get_task_collection()
    tasks = piic.build_tasks(["en", "es"])
    tasks = list(tasks)

    # Process a chunk with no language info, and there's no default in the task
    with pytest.raises(ProcException) as e:
        _ = process_tasks(tasks, TESTCASES[0][0])
    assert str(e.value) == "Presidio task exception: no language defined in task or document chunk"
