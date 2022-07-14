#!/usr/bin/env python3

import argparse
import os
from posixpath import sep
import re
import shutil

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

def validate_tsv(file):
    absolute = os.path.abspath(file)
    type = os.path.splitext(os.path.basename(absolute))
    if (os.path.isfile(absolute) and type[1] == '.tsv'): return True
    return False

def get_tsv_files(paths):
    validated_paths = []
    for p in paths:
        if validate_tsv(p):
            f_abs = os.path.abspath(p)
            validated_paths.append(f_abs)
        elif os.path.isdir(p):
            files_ls = os.listdir(p)
            for ff in files_ls:
                if validate_tsv(ff):
                    ff_abs = os.path.abspath(ff)
                    validated_paths.append(ff_abs)

    return validated_paths

def main():
    parser = argparse.ArgumentParser(description='PFT Script Un-fucker')
    parser.add_argument('paths', type=str, nargs='+', default='',
                        help='files to un-fuck')
    args = parser.parse_args()

    all_tsv = get_tsv_files(args.paths)
    for tsv_path in all_tsv:
        parsed_lines = [{'id': '#',
                         'start': 'Time IN',
                         'end': 'Time OUT',
                         'character': 'Character',
                         'age': 'Actor Name',
                         'line': 'English Subtitle'}]

        with open(tsv_path, 'r') as file:
            lines = file.readlines()
            collect = []
            additional = {}
            id = 0
            prev_id = ''
            prev_start = ''
            prev_end = ''
            prev_line = ''

            lines.pop(0)

            for line in lines:
                field = line.split('\t')
                i = 0
                for f in field:
                    if i == 1:
                        prev_start = fix_tc_frame_rate(f.strip(), '25')
                    if i == 2:
                        prev_end = fix_tc_frame_rate(f.strip(), '25')

                    # Character name
                    if i == 3:
                        characters_raw = f.split(',')
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
                        lines_raw = f.split('- ')
                        li = 0
                        for ll in lines_raw:
                            collect[min(li, len(collect) - 1)]['line'] = ll.strip()
                            li += 1
                        if li < len(collect):
                            for ii in range(li, len(collect)):
                                collect[ii]['line'] = '(NO LINE)'

                    i += 1
                id += 1

                for c in collect:
                    #if c['line'] != '(NO LINE)':
                    parsed_lines.append(dict.copy(c))

                collect.clear()
                additional.clear()

            file.close()

        out_tokens = file_names(tsv_path)
        with open(f'{out_tokens[0].upper()}_{out_tokens[1].upper()}.gen.TAB', 'w') as file:
            for line in parsed_lines:
                for k, v in line.items():
                    file.write(v)
                    file.write('\t')
                file.write('\n')
            file.close()
        parsed_lines.clear()

if __name__ == '__main__':
    main()









