#!/usr/bin/env python3

import os
from docx import Document


def validate_docxtbl_header(all_tables, headers):
    valid = False
    index = 0
    for i, tbl in enumerate(all_tables):
        first_row = tbl.rows[0].cells
        if len(first_row) == len(headers):
            for j, h in enumerate(headers):
                print(j, h, first_row[j].text)
                valid = valid or h == first_row[j].text
            if valid:
                return True, i
    return False, 0


def script_to_list(path, headers = []):
    data = []
    absolute = os.path.abspath(path).replace('\\', '/')
    if os.path.isfile(absolute):
        all_tables = Document(absolute).tables
        valid_tbl, tbl_index = validate_docxtbl_header(all_tables, headers)

        if valid_tbl:
            tbl = all_tables[tbl_index]
            for r in tbl.rows:
                entry = {}
                for i, c in enumerate(r.cells):
                    if i == 0:
                        entry['id'] = c.text
                    if i == 1:
                        entry['tcin'] = c.text
                    if i == 2:
                        entry['tcout'] = c.text
                    if i == 3:
                        entry['character'] = c.text
                    if i == 4:
                        entry['line'] = c.text
                data.append(entry)

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


def get_column_data(path, col):
    data = script_to_list(path)
    if len(data) == 0:
        return []

    data.pop(0)

    collect = []
    for line in data:
        i = 0
        for k_cell, v_cell in line.items():
            if i == col:
                collect.append(v_cell)
            i += 1

    return collect


def validate_directory(path):
    path_abs = os.path.abspath(path)
    is_valid = os.path.isdir(path_abs)
    return is_valid, path_abs


def normalised_script(path):
    parsed_lines = [{'id': '#',
                     'start': 'Time IN',
                     'end': 'Time OUT',
                     'character': 'Character',
                     'age': 'Actor Name',
                     'line': 'English Subtitle'}]

    data = script_to_list(path)
    data.pop(0)

    collect = []
    additional = {}
    id = 0
    prev_start = ''
    prev_end = ''

    for line in data:
        i = 0
        for k_cell, v_cell in line.items():
            if i == 1:
                prev_start = fix_tc_frame_rate(v_cell.strip(), '25')
            if i == 2:
                prev_end = fix_tc_frame_rate(v_cell.strip(), '25')
            if i == 3:
                characters_raw = v_cell.split(',')
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
                lines_raw = v_cell.split('- ')
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
