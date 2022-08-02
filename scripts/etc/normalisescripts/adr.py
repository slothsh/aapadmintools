#!/usr/bin/env python3

import os
import json
import tableschema as tblsh
from docx import Document
import sys
from statistics import mean, mode
from fuzzywuzzy import fuzz


def round_to_nearest(x, base=10):
    return base * round(x/base)


def map_characters_to_castings(characters, castings):
    list.sort(castings)
    mapping = []
    for ch in characters:
        collect = []
        for casting in castings:
            split_casting = casting.split('\t')
            if ch.strip().lower() == split_casting[0].strip().lower():
                casting_range = split_casting[1].split('-')
                gender = casting_range[0][0].strip()
                lo = int(casting_range[0][1:].strip())
                hi = int(casting_range[1].strip())
                collect.append((gender, lo, hi))
        mapping.append((ch.strip(), list.copy(collect)))
        collect.clear()

    return mapping


def aggregate_castings(data):
    aggregated = []
    for d in data:
        character = d[0]
        if len(d[1]) > 0:
            mode_gender = mode([x[0] for x in d[1]])
            avg_lo = round_to_nearest(mean([x[1] for x in d[1]]), 5)
            avg_hi = round_to_nearest(mean([x[2] for x in d[1]]), 5)
            if avg_lo >= avg_hi:
                age_dt = 5 if (mode_gender.upper() == 'M' or mode_gender.upper() == 'F') else 3
                avg_lo = avg_hi - age_dt
            aggregated.append((character, mode_gender.upper(), int(avg_lo), int(avg_hi)))

    return aggregated

def find_speaker_aliases(targets, names_list, ratio=70):
    data = []
    for t in targets:
        collect = []
        for n in names_list:
            if fuzz.ratio(t.lower(), n.lower()) >= ratio and t.lower() != n.lower():
                collect.append(n.lower())
        data.append((t.lower(), list.copy(collect)))

    return data


def match_tblheaders(header, key, synonyms=[]):
    for i, c in enumerate(header.cells):
        for s in synonyms:
            if c.text == s:
                return True, i
    return False, 0


def tbl_get_fields(table, fields):
    indexes = []
    first_row = table.rows[0].cells
    for i, c in enumerate(first_row):
        if c.text in fields:
            indexes.append(i)

    return indexes


def tbl_contains_all_fields(table, field_list):
    indexes = []
    first_row = table.rows[0].cells
    for fields in field_list:
        for field in fields[1]:
            for i, c in enumerate(first_row):
                if field.lower() == c.text.lower():
                    indexes.append((fields[0], i))

    return indexes


def script_to_list(path, schema_path):
    absolute_path = os.path.abspath(path).replace('\\', '/')
    absolute_schema = os.path.abspath(schema_path).replace('\\', '/')
    assert os.path.isfile(absolute_path), 'error: invalid path to .docx file: path is not a file'
    assert os.path.isfile(absolute_schema), 'error: invalid path to schema file: schema_path is not a file'

    data = []

    headers = None
    try:
        with open(absolute_schema, 'r') as file:
            headers = json.load(file)
    except Exception as e:
        print(e)

    all_tables = Document(absolute_path).tables
    valid_tables = []

    flattened_schema = [(x['key'], x['synonyms']) for x in headers['header_fields']]

    collect_tables = []
    for tbl in all_tables:
        indexes = tbl_contains_all_fields(tbl, flattened_schema)
        if len(indexes) > 0:
            collect_rows = []
            for r in tbl.rows:
                collect_cols = []
                for c in r.cells:
                    collect_cols.append(c.text)
                collect_rows.append(list.copy(collect_cols))
            collect_tables.append((indexes, list.copy(collect_rows)))

    collect = []
    for item in collect_tables:
        for r in item[1]:
            for i in item[0]:
                collect.append((i[0], r[i[1]]))
            data.append(list.copy(collect))
            collect.clear()

    return data


def fix_tc_frame_rate(tc, fps):
    chunks = tc.split(":")
    if chunks[3] == fps:
        chunks[3] = str(int(chunks[3]) - 1)

    return f'{chunks[0]}:{chunks[1]}:{chunks[2]}:{chunks[3]}'


def file_names(path):
    if os.path.isfile(path):
        name = os.path.splitext(os.path.basename(os.path.abspath(path)))
        codes = str.split(name[0], sep='_', )
        return (codes[0], codes[1])
    return ('DEFAULT', 'PROD')


def validate_ext(file, ext):
    absolute = os.path.abspath(file)
    type = os.path.splitext(os.path.basename(absolute))
    if (os.path.isfile(absolute) and type[1] == f'.{ext}'):
        return True
    return False


def get_ext_files(paths, ext):
    validated_paths = []
    for p in paths:
        if validate_ext(p, ext):
            f_abs = os.path.abspath(p)
            validated_paths.append(f_abs)
        elif os.path.isdir(p):
            p_abs = os.path.abspath(p)
            files_ls = os.listdir(p)
            for ff in files_ls:
                ff_abs = os.path.join(p_abs, ff)
                if validate_ext(ff_abs, ext):
                    validated_paths.append(ff_abs)

    return validated_paths


def tbl_column_by_name(path, name):
    data = script_to_list(path)
    if len(data) == 0:
        return []

    header = data.pop(0)
    index = -1
    for i, c in enumerate(header):
        if c == name:
            index = i

    if index < 0:
        return []

    collect = []
    for line in data:
        k, v = line.items()
        for i, c in enumerate(line):
            if i == index:
                collect.append(v)

    return collect


def tbl_column_by_index(path, index, schema_path):
    data = script_to_list(path, schema_path)
    if len(data) == 0:
        return []

    data.pop(0)

    collect = []
    for line in data:
        k, v = line.items()
        for i, e in enumerate(line):
            if i == index:
                collect.append(v)

    return collect


def validate_directory(path):
    path_abs = os.path.abspath(path)
    is_valid = os.path.isdir(path_abs)
    return is_valid, path_abs


def normalised_script(path, schema_path):
    parsed_lines = [{'id': '#',
                     'start': 'Time IN',
                     'end': 'Time OUT',
                     'character': 'Character',
                     'age': 'Actor Name',
                     'line': 'English Subtitle'}]

    data = []
    try:
        data = script_to_list(path, schema_path)
    except Exception as e:
        print(e)

    print(data)

    collect = []
    additional = {}
    id = 0
    prev_start = ''
    prev_end = ''

    for j, line in enumerate(data):
        if j == 0:
            continue
        i = 0
        for l in line:
            if i == 1:
                prev_start = fix_tc_frame_rate(l.strip(), '25')
            if i == 2:
                prev_end = fix_tc_frame_rate(l.strip(), '25')
            if i == 3:
                characters_raw = l.split(',')
                increment = len(characters_raw) - 1
                for c in characters_raw:
                    names = c.split('to')[0]
                    additional['id'] = str(id)
                    if len(characters_raw) > 1 and increment != 0:
                        id += 1
                        increment -= 1
                    additional['start'] = prev_start
                    additional['end'] = prev_end
                    additional['character'] = names.strip().upper()
                    additional['age'] = 'CAST ME'
                    collect.append(dict.copy(additional))
                    additional.clear()
            if i == 4:
                lines_raw = l.split('- ')
                li = 0
                for ll in lines_raw:
                    stripped = ll.strip().replace('\n', ' ')
                    collect[min(li, len(collect) - 1)]['line'] = stripped
                    li += 1
                if li < len(collect):
                    for ii in range(li, len(collect)):
                        collect[ii]['line'] = '(NO LINE)'

            i += 1
        id += 1

        for c in collect:
            parsed_lines.append(dict.copy(c))

        collect.clear()
        additional.clear()

    return parsed_lines
