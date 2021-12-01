#!/usr/bin/env python3

import os
import re

def alt_names(name):
    if name.lower() == 'misha':
        return 'Michael'
    elif name.lower() == 'michael':
        return 'Misha'
    elif name.lower() == 'olga':
        return 'Olya'
    elif name.lower() == 'olya':
        return 'Olga'
    elif name.lower() == 'leo':
        return 'Lev'
    elif name.lower() == 'lev':
        return 'Leo'
    elif name.lower() == 'et':
        return 'Yakov'
    elif name.lower() == 'yakov':
        return 'Et'
    elif name.lower() == 'nadia':
        return 'Hope'
    elif name.lower() == 'hope':
        return 'Nadia'
    elif name.lower() == 'rohit':
        return 'Rudolph'
    elif name.lower() == 'rudolph':
        return 'Rohit'
    elif name.lower() == 'sonakshi':
        return 'Kimberleigh'
    elif name.lower() == 'kimberleigh':
        return 'Sonakshi'
    elif name.lower() == 'nishi':
        return 'Savannah'
    elif name.lower() == 'savannah':
        return 'Nishi'
    elif name.lower() == 'veena':
        return 'Pauline'
    elif name.lower() == 'pauline':
        return 'Veena'

    return ''

def name_combinations(text, names_list, i = 0, n = 0, acc = []):
    acc.append(text)

    regex_names = '|'.join(names_list)
    matches_set = set(re.findall(f'\\b({regex_names})\\b', text, flags=re.IGNORECASE))
    matches = [x for x in matches_set]

    if n == 2 ** len(matches) - 1:
        return acc

    if i == len(matches): i = 0
    new_line = re.sub(matches[i], alt_names(matches[i]), text, flags=re.IGNORECASE)

    return name_combinations(new_line, names_list, i + 1, n + 1, acc)

def main():
    out_results = []

    with open('/mnt/c/users/snowf/dev/projects/aapadmintools/resources/altlines_test.txt', 'r') as f:
        lines = f.readlines()
        names_list = ['misha', 'michael', 'et', 'yakov', 'nadia', 'hope', 'rohit', 'rudolph', 'sonakshi', 'kimberleigh', 'nishi', 'savannah', 'veena', 'pauline']

        for line in lines:
            fields = line.split(sep='\t')
            text = fields[4].strip()
            alt_text = name_combinations(text, names_list)
            append_text = '\t'.join(alt_text)
            new_line = f'{fields[0]}\t{fields[1]}\t{fields[2]}\t{fields[3]}\t{append_text}\n'
            # new_line = f'{append_text}\n'
            print(new_line)
            out_results.append(new_line)
            alt_text.clear()

    # with open('/mnt/c/users/snowf/dev/projects/aapadmintools/resources/etelov_alt.txt', 'w') as f:
    #     for line in out_results:
    #         f.write(line)

    #     f.close()

if __name__ == '__main__':
    main()