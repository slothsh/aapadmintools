#!/usr/bin/env python3

import os
import re
import subprocess
import argparse
import datetime

# TODO: Error handling for arguments parsing
# Input arguments
parser = argparse.ArgumentParser(description='extract keywords from lines')
parser.add_argument('--path', '-p', required=True, help='path containing lines', nargs='+', dest='path', metavar='<path>')
parser.add_argument('--out', '-o', required=True, help='path to output keywords', nargs=1, dest='out', metavar='<path>')
args = vars(parser.parse_args())

stop_words = [x.strip() for x in open('./stopwords.txt').readlines()]

results = []
with open(args['path'][0], 'r') as f:
    lines = f.readlines()

    for l in lines:
        cues = l.split(sep='|')
        name = cues[0]
        tc = cues[1]
        text = cues[2]
        words = [x.strip() for x in text.split(sep=' ')]

        for w in words:
            found = False

            for t in stop_words:
                if (t.lower() == w.lower()):
                    found = True
                    continue

            if  (found == False):
                results.append({ 'tc': tc, 'name': name.lower(), 'line': w.lower() })

with open(args['out'][0], 'w') as f:
    for r in results:
        cmd_str = f'{r["tc"]}\taapgetlines -j hope -c {r["name"]} -l \'{r["line"]}\'\n'
        f.write(cmd_str)
