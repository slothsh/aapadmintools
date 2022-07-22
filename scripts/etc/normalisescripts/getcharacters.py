#!/usr/bin/env python3

import adr
import argparse
import math
import multiprocessing as mp
import os
import sys

def split_characters(names):
    collect = []
    for n in names:
        split1 = n.split(',')
        for s1 in split1:
            if ' to ' in s1:
                split2 = s1.split(' to ')
                for s2 in split2:
                    collect.append(s2.strip())
            else:
                collect.append(s1.strip())

    return collect


def process(paths, ext, out, prefix, split_names, dry_run):
    for p in paths:
        name = os.path.basename(p).split('.')[0]
        out_path = os.path.join(out, f'{prefix}_{name}_out.names')
        raw_names = adr.get_column_data(p, 3)
        if split_names is True:
            raw_names = set(split_characters(raw_names))
        print(raw_names)
        if not dry_run:
            with open(out_path, 'w') as file:
                for n in raw_names:
                    file.write(f'{n}\n')
                file.close()
        else:
            for n in raw_names:
                print(n)



def group_items(items, size):
    groups = []
    group = []
    assert len(items) >= size
    n = 0
    reverse_n = len(items) - 1
    for i, item in enumerate(items):
        group.append(item)

        if n == size - 1 or reverse_n == 0:
            groups.append(list.copy(group))
            group.clear()
            n = 0
        else:
            n += 1
        reverse_n -= 1

    return groups


def get_script_characters(path):
    names = []
    if os.path.isfile(path):
        data = adr.script_to_list(path)
        for d in data:
            names.append(d['character'])
        return names
    return names


def main():
    parser = argparse.ArgumentParser(description='PFT Script Name Collector')
    parser.add_argument('paths', type=str, nargs='+', default='',
                        help='files to for characters to collect')
    parser.add_argument('--out', type=str, nargs='?', default='.',
                        help='path to output directory to save files containing collected names')
    parser.add_argument('--ext', type=str, nargs='?', default='docx',
                        help='specific files to process')
    parser.add_argument('--write-type', type=str, nargs='?', default='a',
                        help='write to file can be a or w')
    parser.add_argument('--process-count', type=int, nargs='?', default=4,
                        help='total processes to spawn in pool; cannot be higher than system total')
    parser.add_argument('--dry-run', action='store_true',
                        help='perform a dry run')
    parser.add_argument('--split-names', action='store_true',
                        help='split names of characters according to stop words')
    args = parser.parse_args()

    write_type = args.write_type.lower()
    valid_write_types = ['a', 'w', 'ab', 'wb']
    if write_type not in valid_write_types:
        write_type = 'a'

    valid_out_path, out_path = adr.validate_directory(args.out)
    if not valid_out_path:
        print(f'Please specify a valid output path\nspecified path: {out_path}')
        sys.exit(1)

    max_proc = min(max(1, args.process_count), os.cpu_count())
    print(f'total cpus: {os.cpu_count()}, user selected: {max_proc}')

    all_paths = adr.get_ext_files(args.paths, args.ext)
    group_size = math.ceil(len(all_paths) / max_proc)
    grouped_paths = group_items(all_paths, group_size)

    print(f'group size: {group_size}')

    pool = []
    for i, p in enumerate(grouped_paths):
        proc = mp.Process(target=process, args=(p,
                                                args.ext,
                                                out_path,
                                                f'process{i}',
                                                args.split_names,
                                                args.dry_run))
        pool.append(proc)

    for p in pool:
        p.start()

    keep_alive = True
    print('Processing Files...')
    while keep_alive:
        prev = False
        for p in pool:
            keep_alive = prev or p.is_alive()


if __name__ == '__main__':
    main()
