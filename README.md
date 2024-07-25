# Extract items from MARC files for Koha

[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)

This application extracts from a MARC file all items as CSV using a Koha MARC framework for headers.
__This script assumes that items fields in MARC file are valid.__
Uses `|` as a separator in case some subfields are repeated.

__Developped with `pymarc 4.2.2`__, might not work with version `5.X.X` of the library.

Set up the following environment variables :

* `RECORDS_FILE` : full path to the file containing all the records
* `KOHA_MARC_FRAMEWORK_FILE` : full path to the MARC framework file (`.csv`)
* `OUTPUT_FILE` : full path to the output file (`.csv`)
* `ERRORS_FILE`: full path to the file with errors (will be created / rewrite existing one)
* `ITEM_FIELD_TAG` : tag used in Koha for items
* `INCLUDE_UNMAPPED_FIELDS` : set to `1` to generate extra columns for subfields not mapped to Koha fields (will be named `{tag}$${code}`, like `995$$1`)
