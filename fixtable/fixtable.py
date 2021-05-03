#!/usr/bin/python
import argparse
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('varfile')
parser.add_argument('--nostata', action='store_true')
parser.add_argument('-i', action='store_true')
parser.add_argument('-c')

args = parser.parse_args()

if args.c:
    args_c = args.c.split()
else:
    args_c = []

changes = [
    ('Observations', 'Obs.'),
    ('Adjusted R-squared', 'Adj. $R^2$'),
    ('R-squared', '$R^2$'),
    ('VARIABLES', ''),
]

try:
    with open(args.varfile, 'r') as v:
        var = [x.strip().split(' ', 1) for x in v.readlines() if x.strip()]
except:
    var = None

with open(args.file, 'r') as f:
    c = f.readlines()


def varname(row):
    if var:
        for x, y in var:
            try:
                row = re.sub(r'\b' + x + r'\b', y, row)
            except:
                row = row.replace(x, y)
    return row


def formatrow(row):
    row = re.sub(r'(\d+)(\*+)', r'\1&\2', row)
    row = re.sub(r'(?<![\*\\])\s*&(?!\s*\*)', r'&&', row)
    row = re.sub(r'(?<![\*\w])\s+\\\\', r'&\\\\', row)
    row = re.sub(r'\*\s+&', '*', row)
    row = re.sub(r'&&', r'&', row, 1)
    # adjust star styles
    row = re.sub(r'(\*{1,3})', r'$^{\1}$', row)
    return row


output = []
ctrls = []
for _n, row in enumerate(c):
    for ctrl in args_c:
        if re.search(r'\b' + ctrl + r'\b', row):
            ctrls.append(formatrow(varname(row)))
            ctrls.append(formatrow(c[_n + 1]))
            del c[_n + 1]
            break
    else:
        row = varname(row)
        for x, y in changes:
            row = row.replace(x, y)
        if not args.nostata:
            if 'multicolumn' in row:
                continue
        if '1o' in row or '0b' in row:
            continue
        if 'tabular' in row:
            continue
        if '{document}' in row:
            continue
        if 'documentclass' in row:
            continue
        if 'setlength' in row:
            continue
        if '(.)' in row:
            continue
        if '& . &' in row:
            continue
        if '& . \\' in row:
            continue
        if '& (.) &' in row:
            continue
        row = formatrow(row)
        output.append(row)

main = []
annotations = []
buffers = []
FE = 0
output[-1] = output[-1].replace(r'\hline', '')
for n, row in enumerate(output, start=1):
    r = row.strip()
    if not re.search(r'\w', row) and 'hline' not in row:
        continue
    if not args.nostata:
        if re.search(r'^Obs', r):
            buffers.append(row)
            continue
        if re.search(r'^\$R\^2', r):
            buffers.append(row)
            continue
        if re.search('Adj. \$R\^2\$', r):
            buffers.append(row)
            continue
        if re.search(r'^[^&]* FE', r):
            buffers.insert(FE, row)
            FE += 1
            continue
    if len(main) > 0 and not re.search('\d+', r) and 'hline' not in r:
        annotations.append(r)
    else:
        main.append(r)


def clean_line(l):
    l = l.strip()
    if re.search('^\\+$', l):
        return ''
    if l == '':
        return ''
    return l


if args.i:
    f = open(args.file, 'w')
else:
    f = None

print('\\\\\n', file=f)
for row in main:
    print(clean_line(row), file=f)
for row in ctrls:
    print(clean_line(row), file=f)

if not args.nostata:
    print('\\\\\n', file=f)
for row in annotations:
    print(clean_line(row), file=f)
for row in buffers:
    if r'\hline \\\\' in row.strip():
        print(row.strip().replace(r'\hline \\\\', ''), file=f)
    else:
        print(clean_line(row), file=f)

#  if args.nostata:
print('\hline', file=f)
