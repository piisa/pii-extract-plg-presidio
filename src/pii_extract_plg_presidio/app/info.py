"""
Command-line script to show information about the package
"""

import sys
import argparse
from operator import attrgetter

from typing import List, TextIO

from presidio_analyzer import RemoteRecognizer, PatternRecognizer

from pii_data import VERSION as VERSION_DATA
from pii_data.helper.exception import ProcException
from pii_extract import VERSION as VERSION_EXTRACT
from pii_extract.gather.parser import parse_task_descriptor
from pii_extract.gather.collection.sources.utils import RawTaskDefaults
from pii_extract.gather.collection.task_collection import filter_piid
from pii_extract.build.build import build_task

from .. import VERSION
from ..plugin_loader import load_presidio_plugin_config
from ..task.analyzer import presidio_analyzer
from ..task.utils import presidio_version
from ..task import PresidioTaskCollector


class Processor:

    def __init__(self, args: argparse.Namespace, debug: bool = False):
        self.args = args
        self.debug = debug


    def _init_presidio(self):
        """
        Initialize the Presidio recognizer object
        """
        config = load_presidio_plugin_config(self.args.config)
        try:
            return presidio_analyzer(config, languages=self.args.lang)
        except Exception as e:
            raise ProcException("cannot create Presidio Analyzer engine: {}",
                                e) from e


    def proc_version(self, out: TextIO):
        """
        List package versions
        """
        print(". Installed package versions", file=out)
        version = {"PII data": VERSION_DATA,
                   "PII extract-base": VERSION_EXTRACT,
                   "PII Presidio plugin": VERSION,
                   "Presidio": presidio_version()}
        for n, v in version.items():
            print(f"{n:>20}: {v}")


    def proc_presidio_recognizers(self, out: TextIO):
        """
        Print entity recognizers in presidio
        """
        analyzer = self._init_presidio()
        print(f". Recognizers available in Presidio (lang={self.args.lang})")
        for rec in sorted(analyzer.get_recognizers(), key=attrgetter("name")):
            rtype = "remote" if isinstance(rec, RemoteRecognizer) else \
                    "pattern" if isinstance(rec, PatternRecognizer) else \
                    "local"
            if bool(rec.context):
                rtype += ",context"
            ft = "{name:" + ("<" if self.args.entities else ">") + "28} {version:<8} {supported_language:<10} {type:20}"
            print(ft.format(has_ctx=bool(rec.context), type=rtype, **vars(rec)))
            if self.args.entities:
                print(" entities:", ", ".join(rec.supported_entities), "\n")


    def proc_presidio_entities(self, out: TextIO):
        """
        Print entities defined in presidio
        """
        analyzer = self._init_presidio()
        print(f". Defined entities in Presidio (lang={self.args.lang})")
        for ent in sorted(analyzer.get_supported_entities()):
            print("  ", ent)


    def proc_pii_entities(self, out: TextIO):
        """
        Print entity recognizers in presidio
        """
        config = load_presidio_plugin_config(self.args.config)

        # Get the Presidio task descriptor
        tc = PresidioTaskCollector(config, languages=self.args.lang,
                                   debug=self.debug)
        raw_tdesc = tc.gather_tasks()

        # Ensure it is normalized
        reformat = RawTaskDefaults()
        tdesc = reformat(raw_tdesc)

        print(f". PII entities defined from Presidio (lang={self.args.lang})")
        for td in tdesc:
            # Create the task definition (inc. pii demultiplexing)
            tdef = parse_task_descriptor(td)

            # Filter by language
            if self.args.lang:
                lset = set(self.args.lang)
                tdef["piid"] = filter_piid(tdef["piid"], lang=lset)

            # Build the task
            task = build_task(tdef)

            # Now traverse the pii_info list
            for t in task.pii_info:
                nam = f"{t.pii.name}, {t.subtype}" if t.subtype else t.pii.name
                method = task.get_method(t)
                print(f"  {nam:40} {t.lang:5} {method}")



def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Show information about usable PII tasks (version {VERSION})")

    opt_com1 = argparse.ArgumentParser(add_help=False)
    c1 = opt_com1.add_argument_group('Configuration options')
    c1.add_argument("--config", nargs="+",
                    help="add PIISA configuration file(s)")
    c1.add_argument("--lang", nargs='+', help="language to select")

    opt_com2 = argparse.ArgumentParser(add_help=False)
    c1 = opt_com2.add_argument_group('Task selection options')

    opt_com3 = argparse.ArgumentParser(add_help=False)
    c2 = opt_com3.add_argument_group("Other")
    c2.add_argument("--debug", action="store_true", help="debug mode")
    c2.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')

    subp = parser.add_subparsers(help='command', dest='cmd')

    subp.add_parser('version', help='show version information for components',
                    parents=[opt_com1, opt_com3])

    subp1 = subp.add_parser('presidio-recognizers',
                            help='information about recognizers available in presidio',
                            parents=[opt_com1, opt_com3])
    subp1.add_argument("--entities", action="store_true")

    subp1 = subp.add_parser('presidio-entities',
                            help='information about entities defined in presidio',
                            parents=[opt_com1, opt_com3])

    subp1 = subp.add_parser('pii-entities',
                            help='information about PII tasks defined via Presidio',
                            parents=[opt_com1, opt_com3])

    parsed = parser.parse_args(args)
    if not parsed.cmd:
        parser.print_usage()
        sys.exit(1)
    return parsed


def main(args: List[str] = None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)

    try:
        proc = Processor(args, args.debug)
        mth_name = 'proc_' + args.cmd.replace('-', '_')
        mth = getattr(proc, mth_name)
        mth(sys.stdout)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.reraise:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
