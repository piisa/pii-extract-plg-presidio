"""
Test the plugin loader mechanics
"""

from pii_data.types import PiiEnum

from pii_extract_plg_presidio import VERSION
from pii_extract_plg_presidio.task.task import PresidioTask
import pii_extract_plg_presidio.plugin_loader as mod


def test10_constructor():
    """
    Test basic construction
    """
    ep = mod.PiiExtractPluginLoader()
    assert str(ep) == f'<PiiExtractPluginLoader: presidio {VERSION}>'


def test20_tasklist():
    """
    Test list of tasks
    """
    ep = mod.PiiExtractPluginLoader()
    tl = list(ep.get_plugin_tasks())
    assert len(tl) == 1


def test30_task_descriptor():
    """
    Test the task descriptor
    """
    ep = mod.PiiExtractPluginLoader()
    got = next(ep.get_plugin_tasks())

    assert sorted(got.keys()) == ["class", "doc", "kwargs", "pii", "source",
                                  "task", "version"]
    assert got["class"] == "PiiTask"
    assert got["task"] == PresidioTask

    assert len(got["pii"]) == 7

    pii_list = sorted(e["type"] for e in got["pii"])
    assert pii_list == [PiiEnum.GOV_ID, PiiEnum.GOV_ID,
                        PiiEnum.GOV_ID, PiiEnum.GOV_ID,
                        PiiEnum.PERSON, PiiEnum.LOCATION, PiiEnum.NORP]
