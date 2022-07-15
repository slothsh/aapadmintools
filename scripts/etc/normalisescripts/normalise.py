#!/usr/bin/env python3

import argparse
import adr

def main():
    parser = argparse.ArgumentParser(description='PFT Script Un-fucker')
    parser.add_argument('paths', type=str, nargs='+', default='',
                        help='files to un-fuck')
    parser.add_argument('--ext', type=str, nargs='?', default='docx',
                        help='specific files to process')
    args = parser.parse_args()

    all_data = adr.get_ext_files(args.paths, args.ext)
    for data_path in all_data:
        parsed_lines = [{'id': '#',
                         'start': 'Time IN',
                         'end': 'Time OUT',
                         'character': 'Character',
                         'age': 'Actor Name',
                         'line': 'English Subtitle'}]

        data = adr.script_to_list(data_path)
        data.pop(0)

        collect = []
        additional = {}
        id = 0
        prev_id = ''
        prev_start = ''
        prev_end = ''
        prev_line = ''

        for line in data:
            i = 0
            for k_cell, v_cell in line.items():
                if i == 1:
                    prev_start = adr.fix_tc_frame_rate(v_cell.strip(), '25')
                if i == 2:
                    prev_end = adr.fix_tc_frame_rate(v_cell.strip(), '25')

                # Character name
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
                        collect[min(li, len(collect) - 1)]['line'] = ll.strip().replace('\n', ' ')
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


        out_tokens = adr.file_names(data_path)
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









