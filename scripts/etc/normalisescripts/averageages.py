#!/usr/bin/env python3

import adr
import argparse
import os
import sys
from statistics import mean, mode


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    parser = argparse.ArgumentParser(description='Calculate average age range for characters')
    parser.add_argument('--characters', type=str, required=True,
                        help='path to text file with target names of characters')
    parser.add_argument('--castings', type=str, required=True,
                        help='path to text file with age ranges for characters')
    parser.add_argument('--aliases', type=str, required=True,
                        help='path to text file with all aliases for all characters')
    parser.add_argument('--ratio', type=int, required=True,
                        help='lowest ratio for fuzzy-matching to pass an alias for a target name')
    args = parser.parse_args()

    characters_path = os.path.abspath(args.characters)
    castings_path = os.path.abspath(args.castings)
    aliases_path = os.path.abspath(args.aliases)

    if os.path.isfile(characters_path) is False:
        eprint(f'error: invalid path to file: {characters_path}')
        sys.exit(1)
    if os.path.isfile(castings_path) is False:
        eprint(f'error: invalid path to file: {castings_path}')
        sys.exit(1)
    if os.path.isfile(aliases_path) is False:
        eprint(f'error: invalid path to file: {aliases_path}')
        sys.exit(1)

    characters = None
    castings = None
    aliases = None
    try:
        characters = set(open(characters_path, 'r').readlines())
        castings = open(castings_path, 'r').readlines()
        aliases = open(aliases_path, 'r').readlines()
    except Exception as e:
        eprint(e)

    if len(characters) == 0:
        eprint(f'error: no characters available in file: {characters_path}')
        sys.exit(1)
    if len(castings) == 0:
        eprint(f'error: no ages available in file: {castings_path}')
        sys.exit(1)
    if len(aliases) == 0:
        eprint(f'error: no names available in file: {aliases_path}')
        sys.exit(1)

    data = adr.map_characters_to_castings(characters, castings)
    aggregated = adr.aggregate_castings(data)
    sorted_aliases = adr.find_speaker_aliases([x[0] for x in aggregated], [x.strip() for x in aliases], args.ratio)


    for a in sorted_aliases:
        print(a)


if __name__ == "__main__":
    main()
