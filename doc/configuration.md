# Plugin configuration

The plugin is governed by a [PIISA configuration file]; there is one [default
file] included in the package resources. The format tag for the configuration
is `"piisa:config:extract-plg-presidio:main:v1`, and it has two sections:
 * `nlp_config` defines Presidio initialization arguments
 * `pii_list` defines the PII instances to be detected. 

**Important**: the plugin will instantiate a Presidio analyzer with support only
for the languages for which there is a model in the configuration (the PII
instances in `pii_list` that are defined with a language not having an
available model in `nlp_config` will be filtered out).


## Analyzer configuration

The `nlp_config` element can contain the following fields:
 - `nlp_engine_name`: the NLP engine to be used
 - `models`: a list of NLP models to be loaded (each item contains `lang_code`
    and `model_name`)
 - `analyzer_params`: additional keyword arguments to pass to the Presidio
   `AnalyzerEngine` constructor
 - `reuse_engine`: cache the engine instances built, and reuse them if another 
    task object is created with the same config (default is `True`)

The languages to be supported in a specific plugin instance will be the ones
that have an entry in the `models` list. Note that the corresponding language
model should be available in the system (e.g. for SpaCy models, the
appropriate model needs to be downloaded beforehand, as the installation
instructions explain).


## PII List

The `pii_list` element contains a list of standard PIISA [pii task descriptors];
those will be the ones that the plugin makes available to the framework. In order
to create this list the following requirements must be met:
 * the PII descriptor must contain an additional `extra` field that contains the
   Presidio PII entity to be mapped to the descriptor
 * the entity language must have a loaded model defined in the
   `nlp_config` section (which in turn requires the model to be available in
   the system)
   
Not that the requirement for a model for the language to be available holds
even if the PII task instance does not actually use the model (e.g. also for a
regexp detector); this is a Presidio requirement. For this reason, as explained
above, PII descriptors whose defined language is not included in the `models`
list will be automatically removed from the compiled PII list.


[PIISA configuration file]: https://github.com/piisa/piisa/blob/main/docs/configuration.md
[default file]: ../src/pii_extract_plg_presidio/resources/plugin-config.json
[pii task descriptors]: https://github.com/piisa/pii-extract-base/tree/main/doc/task-descriptor.md
