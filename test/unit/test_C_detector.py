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
