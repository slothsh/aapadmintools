#!/usr/bin/env python3

import os
import adr
import argparse


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
    parser.add_argument('--out', type=str, nargs='?', default='out.NAMES',
                        help='where to output the collected names')
    parser.add_argument('--ext', type=str, nargs='?', default='docx',
                        help='specific files to process')
    args = parser.parse_args()

    paths = adr.get_ext_files(args.paths, args.ext)
    with open('out.NAMES', 'a') as file:
        for path in paths:
            names = adr.normalised_script(path)
            names.pop(0)
            for n in names:
                file.write(f'{n["character"]}\n')
        file.close()


if __name__ == '__main__':
    main()
