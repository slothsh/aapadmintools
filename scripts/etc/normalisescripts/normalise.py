#!/usr/bin/env python3

import argparse
import adr
import os


def main():
    parser = argparse.ArgumentParser(description='PFT Script Un-fucker')
    parser.add_argument('paths', type=str, nargs='+', default='',
                        help='files to un-fuck')
    parser.add_argument('--ext', type=str, nargs='?', default='docx',
                        help='specific files to process')
    parser.add_argument('--schema', type=str, nargs=1, required=True,
                        help='path to schema file to validate table data')
    args = parser.parse_args()

    all_data = adr.get_ext_files(args.paths, args.ext)

    for data_path in all_data:
        all_lines = adr.normalised_script(data_path, os.path.abspath(args.schema[0]))
        out_tokens = adr.file_names(data_path)
        file_name = f'{out_tokens[0].upper()}_{out_tokens[1].upper()}.gen.TAB'
        with open(file_name, 'w') as file:
            for line in all_lines:
                for k, v in line.items():
                    file.write(v)
                    file.write('\t')
                file.write('\n')
            file.close()
        all_lines.clear()


if __name__ == '__main__':
    main()
