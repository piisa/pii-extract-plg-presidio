"""
Test the list of collected tasks
"""

import pytest

from pii_extract.build.collection import get_task_collection

from pii_extract_plg_presidio.task import PresidioTask

from taux.monkey_patch import patch_entry_points



# ---------------------------------------------------------------------------

def _get_tasks():
    piic = get_task_collection()
    tasklist = piic.taskdef_list()
    return list(tasklist)


def test10_tasklist(monkeypatch):
    """
    Check the task list size
    """
    patch_entry_points(monkeypatch)

    tasks = _get_tasks()
    assert len(tasks) == 1


def test20_task_obj(monkeypatch):
    """
    Check the created task
    """
    patch_entry_points(monkeypatch)

    tasks = _get_tasks()
    t = tasks[0]
    tdef = t["obj"]
    assert tdef["class"] == "piitask"
    assert tdef["task"] == PresidioTask
    assert sorted(tdef["kwargs"].keys()) == ["cfg", "log"]


def test30_task_pii(monkeypatch):
    """
    Check the list of used Presidio PII
    """
    patch_entry_points(monkeypatch)

    tasks = _get_tasks()
    pii = tasks[0]["piid"]
    assert len(pii) == 8

    got_presidio_ent = [(p["extra"]["presidio"], p["lang"]) for p in pii]
    exp_presidio_ent = [
        ("PERSON", "en"), ("PERSON", "es"),
        ("NRP", "en"), ("NRP", "es"),
        ("LOCATION", "en"), ("LOCATION", "es"),
        ("US_PASSPORT", "en"),
        ("IT_FISCAL_CODE", "it")
    ]
    assert exp_presidio_ent == got_presidio_ent
