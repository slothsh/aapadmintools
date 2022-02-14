#!/usr/bin/env python3

import argparse
import re
import math

TICK_RATE = 10000000

def tc_to_float(tc, tick_rate) -> float:
    chunks = re.findall('\d+', tc)
    i = 0
    t = 0
    for c in chunks:
        m = 0.0
        if i == 0:
            m = 60.0 * 60.0
        if i == 1:
            m = 60.0
        if i == 2:
            m = 1.0
        t += float(chunks[i]) * m
        i += 1

    return t * tick_rate # Create a precision constant for this

def float_to_tc(n, tick_rate) -> str:
    if n == 0: return '00:00:00'

    h = 0.0
    m = 0.0
    s = 0.0
    f = 0.0

    if n >= (60.0 * 60.0 * tick_rate):
        h = n // (60.0 * 60.0 * tick_rate)
        n = n % (60.0 * 60.0 * tick_rate)
  
    if n >= (60.0 * tick_rate):
        m = n // (60.0 * tick_rate)
        n = n % (60.0 * tick_rate)
    
    if n >= (tick_rate):
        s = n // tick_rate
        n = n % tick_rate

    hs = (len(str(int(h))) == 1) and '0' + str(int(h)) or str(int(h))
    ms = (len(str(int(m))) == 1) and '0' + str(int(m)) or str(int(m))
    ss = (len(str(int(s))) == 1) and '0' + str(int(s)) or str(int(s))

    return f'{hs}:{ms}:{ss}'
       
argparse = argparse.ArgumentParser()
argparse.add_argument('-e', '--episodes', required=True, help='Total episodes')
argparse.add_argument('-r', '--runtime', required=True, help='Average run-time of content')
argparse.add_argument('-g', '--engineers', required=True, help='Total engineers')
argparse.add_argument('-p', '--preptime', required=True, help='Average prep per engineer')

args = vars(argparse.parse_args())

ep = int(args['episodes'])
rt = float(args['runtime'])
eg = int(args['engineers'])
pt = float(args['preptime'])

avg = (ep * rt) / (eg * pt)
