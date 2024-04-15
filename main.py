# -*- coding: utf-8 -*- 

# external imports
import os
from dotenv import load_dotenv
import re
import pymarc
import csv
from typing import List, Dict

# Internal import
from errors_manager import Errors_Manager, Errors

# ---------- Init ----------
load_dotenv()

RECORDS_FILE_PATH = os.path.abspath(os.getenv("RECORDS_FILE"))
KOHA_MARC_FRAMEWORK_FILE = os.path.abspath(os.getenv("KOHA_MARC_FRAMEWORK_FILE"))
OUTPUT_FILE_PATH = os.path.abspath(os.getenv("OUTPUT_FILE"))
ERRORS_FILE_PATH = os.path.abspath(os.getenv("ERRORS_FILE"))
ERR_MAN = Errors_Manager(ERRORS_FILE_PATH) # DON'T FORGET ME
ITEM_FIELD_TAG = os.getenv("ITEM_FIELD_TAG")
INCLUDE_UNMAPPED_FIELDS = os.getenv("INCLUDE_UNMAPPED_FIELDS") == "1"
# Koha 22.11, capturing groups :
# 2 : tag, 4 : code, 6 : Koha field
# pattern :
#   - Start with : (")
#   - Get value with : ([^\"]*)
#   - Skip X field with : (",(?:"[^\"]*",){X}")
#   - End with : (".*)
MARC_FRAMEWORK_PATTERN = r'^(")([^\"]*)(",(?:"[^\"]*",){0}")([^\"]*)(",(?:"[^\"]*",){5}")([^\"]*)(".*)'
ITEMS_KOHA_FIELDS_MAPPING:Dict[str, str] = {}
ITEMS_EXTRA_FIELDS:List[str] = []

# ---------- Func def ----------

def add_item_subfield(code:str, koha_field:str) -> None:
    """Adds a mapped item subfield"""
    has_matched = re.match(r"^\s*items\.", koha_field)
    if has_matched:
        ITEMS_KOHA_FIELDS_MAPPING[code.strip()] = koha_field.strip()
    else:
        ITEMS_EXTRA_FIELDS.append(code.strip())

def get_output_headers(include_unmapped_fields:bool=False) -> List[str]:
    """Returns all the headers for the output file"""
    output = ["items.biblionumber"]
    output += [ITEMS_KOHA_FIELDS_MAPPING[code] for code in ITEMS_KOHA_FIELDS_MAPPING]
    if include_unmapped_fields:
        for code in ITEMS_EXTRA_FIELDS:
            output.append(f"{ITEM_FIELD_TAG}$${code}")
    return output

def prep_field_for_output(item:pymarc.field.Field, record_id:str):
    """Returns the field as a dict ready for CSV export"""
    output = {"items.biblionumber":record_id}
    subfs = item.subfields_as_dict()
    for code in subfs:
        if code in ITEMS_KOHA_FIELDS_MAPPING:
            output[ITEMS_KOHA_FIELDS_MAPPING[code]] = "|".join(subfs[code])
        # Elif os we exclude unmapped subfields
        elif code in ITEMS_EXTRA_FIELDS:
            output[f"{ITEM_FIELD_TAG}$${code}"] = "|".join(subfs[code])
    return output

# ---------- Load MARC framework ----------
is_first_page = True
with open(KOHA_MARC_FRAMEWORK_FILE, mode="r", encoding="utf-8") as f:
    for index, line in enumerate(f.readlines()):
        # Line separators : change type of data retrieved
        if '"#-#","#-#","#-#","#-#","#-#","#-#","#-#","#-#","#-#","#-#"' in line:
            is_first_page = False
            continue
        # First page : skip
        if is_first_page:
            continue
        # Empty line : skip
        if len(line.split(",")) < 2:
            continue
        # headers : skip
        if '"tagfield"' in line and '"repeatable","mandatory","important"' in line:
            continue
        
        # Subfields
        has_matched = re.match(MARC_FRAMEWORK_PATTERN, line)
        if has_matched:
            tag = has_matched.group(2)
            code = has_matched.group(4)
            koha_field = has_matched.group(6)
            if tag == ITEM_FIELD_TAG:
                add_item_subfield(code, koha_field)

# ---------- Preparing Main ----------
MARC_READER = pymarc.MARCReader(open(RECORDS_FILE_PATH, 'rb'), to_unicode=True, force_utf8=True) # DON'T FORGET ME
OUTPUT_FILE = open(OUTPUT_FILE_PATH, "w", newline="", encoding='utf-8')
CSV_WRITER = csv.DictWriter(OUTPUT_FILE, extrasaction="ignore", fieldnames=get_output_headers(INCLUDE_UNMAPPED_FIELDS), delimiter=";")
CSV_WRITER.writeheader()

# ---------- Main ----------
# Loop through records
for record_index, record in enumerate(MARC_READER):
    # If record is invalid
    if record is None:
        ERR_MAN.trigger_error(record_index, "", Errors.CHUNK_ERROR, "", "")
        continue # Fatal error, skipp

    # Gets the record ID
    record_id = record["001"]
    if not record_id:
        ERR_MAN.trigger_error(record_index, "", Errors.NO_RECORD_ID, "No 001", "")
        continue
    
    # Loop through item field
    for field in record.get_fields(ITEM_FIELD_TAG):
        CSV_WRITER.writerow(prep_field_for_output(field, record_id.data))

OUTPUT_FILE.close()
MARC_READER.close()
ERR_MAN.close()