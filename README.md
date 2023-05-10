# Pii Extractor plugin: Presidio

[![version](https://img.shields.io/pypi/v/pii-extract-plg-presidio)](https://pypi.org/project/pii-extract-plg-presidio)
[![changelog](https://img.shields.io/badge/change-log-blue)](CHANGES.md)
[![license](https://img.shields.io/pypi/l/pii-extract-plg-presidio)](LICENSE)
[![build status](https://github.com/piisa/pii-extract-plg-presidio/actions/workflows/pii-extract-plg-presidio-pr.yml/badge.svg)](https://github.com/piisa/pii-extract-plg-presidio/actions)

This repository builds a Python package that installs a [pii-extract-base]
plugin to perform PII detection for text data using the Microsoft [Presidio]
Python library.

The name of the plugin entry point is `piisa-detectors-presidio`


## Requirements

The package neads
 * at least Python 3.8
 * the [pii-data] and the [pii-extract-base] base packages
 * the [presidio-analyzer] package
 * an NLP engine model for the desired language


## Installation

 * Install the package: `pip install pii-extract-plg-presidio` (it will
   automatically install its dependencies, including `presidio-analyzer`)
 * Download the recognition model for the desired language(s), as instructed by
   the [presidio-analyzer] installation instructions. The default plugin
   [configuration file] defines three [spaCy models]:
      - English model: `python -m spacy download en_core_web_lg`
      - Spanish model: `python -m spacy download es_core_news_md`
      - Italian model: `python -m spacy download it_core_news_md`
 * For additional information on model specification, see [customizing NLP
   models] in the Presidio documentation. If custom models are used, the
   `nlp_config` element in the plugin [configuration file] must be
   adjusted accordingly.


## Usage

The package does not have any user-facing entry points (except for one console
script `pii-extract-presidio-info`, which provides information about its
capabilities).

Instead, upon installation it defines a plugin entry point. This plugin is
automatically picked up by executing scripts and classes in [pii-extract-base],
and thus its functionality is exposed to it.

Runtime behaviour is governed by a [configuration file], which sets up what
recognizers from Presidio will be instantiated and used. Note that the
configuration defines which languages are available for detection, but the
plugin can also be initialized with a _subset_ of those languages.

The task created from the plugin is a standard [PII task] object, using the
`pii_extract.build.task.MultiPiiTask` class definition. It will be called,
as all PII task objects, with a `DocumentChunk` object containing the data to
analyze. The chunk **must** contain language specification in its metadata, so
that Presidio knows which language to use (unless the plugin task has been
built with *only one* language; in that case if the chunk does not contain
a language specification, it will use that single language).


## Building

The provided [Makefile] can be used to process the package:
 * `make pkg` will build the Python package, creating a file that can be
   installed with `pip`
 * `make unit` will launch all unit tests (using [pytest], so pytest must be
   available)
 * `make install` will install the package in a Python virtualenv. The
   virtualenv will be chosen as, in this order:
     - the one defined in the `VENV` environment variable, if it is defined
     - if there is a virtualenv activated in the shell, it will be used
     - otherwise, a default is chosen as `/opt/venv/pii` (it will be
       created if it does not exist)



[pii-data]: https://github.com/piisa/pii-data
[pii-extract-base]: https://github.com/piisa/pii-extract-base
[pii task descriptors]: https://github.com/piisa/pii-extract-base/tree/main/doc/task-descriptor.md
[Presidio]: https://microsoft.github.io/presidio/
[presidio-analyzer]: https://microsoft.github.io/presidio/analyzer/
[customizing NLP models]: https://microsoft.github.io/presidio/analyzer/customizing_nlp_models/
[spaCy models]: https://spacy.io/usage/models
[Makefile]: Makefile
[pytest]: https://docs.pytest.org
[default file]: src/pii_extract_plg_presidio/resources/plugin-config.json
[configuration file]: doc/configuration.md
[PII task]: https://github.com/piisa/pii-extract-base/blob/main/doc/task-implementation.md
