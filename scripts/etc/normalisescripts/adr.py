#!/usr/bin/env python3

import os
from docx import Document

def script_to_list(path):
    data = []
    absolute = os.path.abspath(path).replace('\\', '/')
    if os.path.isfile(absolute):
        tbl = Document(absolute).tables[0]
        for r in tbl.rows:
            entry = {}
            i = 0
            for c in r.cells:
                if i == 0: entry['id'] = c.text
                if i == 1: entry['tcin'] = c.text
                if i == 2: entry['tcout'] = c.text
                if i == 3: entry['character'] = c.text
                if i == 4: entry['line'] = c.text
                i += 1
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
    if (os.path.isfile(absolute) and type[1] == f'.{ext}'): return True
    return False

def get_ext_files(paths, ext):
    validated_paths = []
    for p in paths:
        if validate_ext(p, ext):
            f_abs = os.path.abspath(p)
            validated_paths.append(f_abs)
        elif os.path.isdir(p):
            files_ls = os.listdir(p)
            for ff in files_ls:
                if validate_ext(ff, ext):
                    ff_abs = os.path.abspath(ff)
                    validated_paths.append(ff_abs)

    return validated_paths

