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
 * Download the recognition model for the desired language, as instructed by
   the [presidio-analyzer] installation instructions. For instance, for
   [spaCy models]:
      - English model: `python -m spacy download en_core_web_lg`
      - Spanish model: `python -m spacy download es_core_news_md`
 * For additional information on model specification, see [customizing NLP
   models]. If custom models are used, the `nlp_config` element in the plugin
   [configuration](#configuration) must be adjusted accordingly.


## Usage

The package does not have any user-facing entry points (except for one console
script `pii-extract-presidio-info`, which provides information about its
capabilities).

Instead, upon installation it defines a plugin entry point. This plugin is
automatically picked up by executing scripts and classes in [pii-extract-base],
and thus its functionality is exposed to it.


## Configuration

The plugin is governed by a PIISA configuration file; there is one [default
file] included in the package resources. The format tag for the configuration
is `"piisa:config:extract-plg-presidio:main:v1`, and it has two sections:
 * `reuse_engine`: build the engine only once, and reuse it if another task
   object is created (default is `True`)
 * `nlp_config` defines Presidio initialization arguments
     - `languages`: the languages to initialize Presidio with
	 - `nlp_engine_name`: the NLP engine to be used
	 - `models`: a list of NLP models to be loaded (each item contains 
	    `lang_code` and `model_name`), and the available models
 * `pii_list` defines the PIISA instances to be detected. It contains a list
   of standard [pii task descriptors]; each one has an additional `extra`
   field that contains the Presidio PII entity to be mapped to the descriptor.


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
