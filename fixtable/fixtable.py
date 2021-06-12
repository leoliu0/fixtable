#!/usr/bin/python
import sys
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('-v', '--varfile')
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
    print('cannot open varfile ...', file=sys.stderr)

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


def repeat_title(row):
    row1 = row
    row2 = '&'.join(
        [x for x in row.split('&') if ';' in x or re.search('^\s*$', x)])
    for x in re.findall(r'[\w\(\)\.\s\+\-]+;[\w\(\)\.\s\+\-]+', row):
        row1 = row1.replace(x, x.split(';')[0]).replace(r'\hline', '')
        row2 = row2.replace(x, x.split(';')[1])
    return row1, row2 + '\\\\ \\hline \n'


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
        therow = varname(row)
        for x, y in changes:
            therow = therow.replace(x, y)
        if not args.nostata:
            if 'multicolumn' in therow:
                continue
        if '1o' in therow or '0b' in therow:
            continue
        if 'tabular' in therow:
            continue
        if '{document}' in therow:
            continue
        if 'documentclass' in therow:
            continue
        if 'setlength' in therow:
            continue
        if '(.)' in therow:
            continue
        if '& . &' in therow:
            continue
        if '& . \\' in therow:
            continue
        if '& (.) &' in therow:
            continue
        therow = formatrow(therow)
        output.append(therow)
        if 'VARIABLES' in row:
            output.append('_add_empty_line123')

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
        if ';' in r:
            row1, row2 = repeat_title(r)
            main.append(row1)
            main.append(row2)
            continue
        main.append(r)


def clean_line(l):
    l = l.strip()
    if re.search('^\\+$', l):
        return ''
    if l == '':
        return ''
    if len(re.findall(r'hline', l)) > 1:
        l = l.replace(r'\hline\\', '')
    if '_add_empty_line123' in l:
        return '\\\\\n'
    return l


if args.i:
    f = open(args.file, 'w')
else:
    f = None

if args.nostata:
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
