"""
Some helper utilities to build & execute detection tasks
"""

from operator import attrgetter
from itertools import chain

from typing import Dict, List, Tuple, Iterable

from pii_data.types import PiiEntity, PiiCollection
from pii_data.types.doc import DocumentChunk
from pii_extract.build.task import BasePiiTask
from pii_extract.gather.parser import parse_task_descriptor
from pii_extract.gather.parser.defs import TYPE_TASKD
from pii_extract.gather.collection.sources.utils import RawTaskDefaults
from pii_extract.build.build import build_task


# -------------------------------------------------------------------------

def pii_build_tasks(tasks: Iterable[TYPE_TASKD],
                    defaults: Dict = None) -> Iterable[BasePiiTask]:
    """
    Build a list of task objects from its raw descriptors
    """
    if isinstance(tasks, dict):
        tasks = [tasks]
    reformat = RawTaskDefaults(defaults, normalize=True)
    for tdesc in reformat(tasks):
        tdef = parse_task_descriptor(tdesc)
        #print("TDESC", tdesc, "TDEF", tdef, sep="\n")
        yield build_task(tdef)


def pii_detect(chunk: DocumentChunk,
               tasklist: List[BasePiiTask]) -> Iterable[PiiEntity]:
    return chain.from_iterable(t(chunk) for t in tasklist)


def pii_replace(pii_list: Iterable[PiiEntity], chunk: DocumentChunk):
    """
    Replace the PII values in a document chunk by an annotated version
           <PII-TYPE:VALUE>
    """
    output = []
    pos = 0
    doc = chunk.data
    for pii in sorted(pii_list, key=attrgetter('pos')):
        # Add all a pair (text-prefix, transformed-pii)
        f = pii.fields
        output += [doc[pos:pii.pos], f'<{f["type"]}:{f["value"]}>']
        pos = pii.pos + len(pii)
    # Reconstruct the document (including the last suffix)
    doc = "".join(output) + doc[pos:]
    return DocumentChunk(chunk.id, doc, chunk.context)


# ----------------------------------------------------------------------

def process_tasks(tasklist: List, text: str,
                  lang: str = None) -> Tuple[PiiCollection, str]:
    """
      Test a task implementation against a testcase
        :param tasklist: a list of tasks
        :param text: source text
        :param lang: language to define
    """
    chunk = DocumentChunk('1', text) if not lang else \
        DocumentChunk('1', text, {"lang": lang})
    pii = pii_detect(chunk, tasklist)
    pii = list(pii)
    got = pii_replace(pii, chunk)
    return pii, got.data
