#!/usr/bin/env python3

import os
import re

# 1) NADIA - HOPE
# 2) LEF - LEV / LEO
# 3) LESHA - LYOSHA
# 4) ET - YAKOV
# 5) OLYA - OLGA

def alt_name(name):
    if name.lower() == 'misha':
        return 'Michael'
    elif name.lower() == 'michael':
        return 'Misha'
    elif name.lower() == 'lev':
        return 'Leo'
    elif name.lower() == 'leo':
        return 'Lev'
    elif name.lower() == 'olga':
        return 'Olya'
    elif name.lower() == 'olya':
        return 'Olga'
    elif name.lower() == 'et':
        return 'Yakov'
    elif name.lower() == 'yakov':
        return 'Et'
    
    return ''

def good_name(name):
    lower_name = name.lower()

    if lower_name == 'michael':
        return 'Misha'
    elif lower_name == 'lev' or lower_name == 'lef':
        return 'Leo'
    elif lower_name == 'olga':
        return 'Olya'
    elif lower_name == 'et':
        return 'Yakov'
    elif lower_name == 'yakov':
        return 'Et'
    
    
    return ''

# c  = 2^i
#                                                                                              i:c
# a1           -> a2                                                                         = 1:2
# a1,b1        -> a2,b1 ; a1,b2 ; a2,b2                                                      = 2:4
# a1,b1,c1     -> a2,b1,c1 ; a1,b2,c1 ; a1,b1,c2 ; a2,b2,c1 ; a2,b1,c2 ; a1,b2,c2 ; a2,b2,c2 = 3:8
# a1,b1,c1,d1  -> a2,b1,c1,d1 ; a1,b2,c1,d1 ; a1,b1,c2,d1 ; a1,b1,c1,d2
#               ; a2,b2,c1,d1 ; a2,b1,c2,d1 ; a2,b1,c1,d2 ; a1,b2,c2,d1
#               ; a1,b2,c1,d2 ; a2,b2,c2,d1 ; a2,b2,c1,d2 ; a1,b1,c2,d2
#               ; a2,b1,c2,d2 ; a1,b2,c2,d2 ; a2,b2,c2,d2                                    = 4:8

# 0 0 0 0 = 0
# 0 0 0 1 = 1
# 0 0 1 0 = 2
# 0 0 1 1 = 3
# 0 1 0 0 = 4
# 0 1 0 1 = 5
# 0 1 1 0 = 6
# 0 1 1 1 = 7
# 1 0 0 0 = 8
# 1 0 0 1 = 9
# 1 0 1 0 = 10
# 1 0 1 1 = 11
# 1 1 0 0 = 12
# 1 1 0 1 = 13
# 1 1 1 0 = 14
# 1 1 1 1 = 15

# pseudo:
#   pop index 0
#   invert index 0
#   append index 0 at index 0
#

def name_combinations(line, i = 0, n = 0, search = [], acc = []):
    acc.append(line)

    re_names = 'nadia|hope|misha|michael|lev|leo|lesha|lyosha|et|yakov|olya|olga'
    n_names = len(set(re.findall(f'\\b({re_names})\\b', line, flags=re.IGNORECASE)))

    if not search:
        matches = set(re.findall(f'\\b({re_names})\\b', line, flags=re.IGNORECASE))
        search = [x for x in matches]
        search.sort()

    if i == len(search):
        print(f'{i}')
        i = 0
    if n == 2 ** n_names - 1:
        return acc

    print(f'{search}')
    alt = search.pop()
    new_line = re.sub(f'\\b({alt})\\b', alt_name(alt), line, flags=re.IGNORECASE)


    return name_combinations(new_line, i + 1, n + 1, search, acc)

def name_replace():
    re_names = 'nadia|michael|lev|lef|lesha|lyosha|et|olya'

def main():
    with open('/Users/stefan/Desktop/hopealtnames/test.tab') as f:
        lines = f.readlines()

        for line in lines:
            fields = line.split(sep='\t')
            original = fields[4].strip()
            new = re.sub(alt_name)
            combinations = name_combinations(original)
                    
        print(combinations)

if __name__ == '__main__':
    main()