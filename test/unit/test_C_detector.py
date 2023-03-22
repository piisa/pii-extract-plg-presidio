"""
Test building the Presidio task and using it for detection
"""

import pytest

from pii_extract.build.collection import get_task_collection

from taux.monkey_patch import patch_entry_points, patch_presidio_analyzer

# ---------------------------------------------------------------------------


def test10_tasklist(monkeypatch):
    """
    Check the built Presidio task, all languages
    """
    patch_entry_points(monkeypatch)
    patch_presidio_analyzer(monkeypatch, {})

    piic = get_task_collection(debug=False)
    tasks = piic.build_tasks()
    tasks = list(tasks)
    assert len(tasks) == 1
    assert str(tasks[0]) == "<PresidioTask #8>"


def test11_tasklist_lang(monkeypatch):
    """
    Check the built Presidio task, specific language
    """
    patch_entry_points(monkeypatch)
    patch_presidio_analyzer(monkeypatch, {})

    piic = get_task_collection(debug=False)
    tasks = piic.build_tasks("en")
    tasks = list(tasks)
    assert len(tasks) == 1
    assert str(tasks[0]) == "<PresidioTask #4>"


def test12_engine_cache(monkeypatch):
    """
    Check engine object reuse
    """
    patch_entry_points(monkeypatch)
    mck = patch_presidio_analyzer(monkeypatch, {})

    piic = get_task_collection(debug=False)

    # Build once
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    # Check the constructor was called
    assert mck.call_count == 1

    # Build again -- analyzer will be called, but reuse the object
    tasks = piic.build_tasks("es")
    tasks = list(tasks)

    # Check no new calls to the constructor
    assert mck.call_count == 1
