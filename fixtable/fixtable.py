#!/usr/bin/python
import sys
import re

if __name__=='__main__':
    changes = [('Observations','No. of Obs'),('R-squared','$R^2$')]

    try:
        with open(sys.argv[2],'r') as v:
            var = [x.strip().split(' ',1) for x in v.readlines() if x.strip()]
    except:
        var = None

    try:
        f = sys.argv[1]
    except:
        raise ValueError('you must specify a filename to parse')
    with open(f,'r') as file:
        c = file.readlines()

    output = []
    for row in c:
        for x,y in changes:
            row = row.replace(x,y)
        if var:
            for x,y in var:
                row = row.replace(x,y)
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
        row = re.sub(r'(\d+)(\*+)',r'\1&\2',row)
        row = re.sub(r'(?<![\*\\])\s*&(?!\s*\*)',r'&&',row)
        row = re.sub(r'(?<!\*)\s*\\\\',r'&\\\\',row)
        row = re.sub(r'\*\s+&','*',row)
        row = re.sub(r'&&',r'&',row,1)
        output.append(row)

    for row in output:
        print(row.strip())
