#!/usr/bin/python
import argparse
import re
import sys

from icecream import ic

# from collections import defaultdict
from loguru import logger


def debug(message):
    if args.debug:
        logger.debug(message)


parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("-v", "--varfile")
parser.add_argument("--nostata", action="store_true")
parser.add_argument("-i", action="store_true")
parser.add_argument("-c")
parser.add_argument("-o")
parser.add_argument("--cline")
parser.add_argument("--noheader", action="store_true")
parser.add_argument("--condensed", action="store_true")
parser.add_argument("--no_column_num", action="store_true")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--nocontrol", action="store_true")
parser.add_argument("--nocontrol_n", type=int, default=0)
parser.add_argument("-m", "--meta", action="store_true")

args = parser.parse_args()

if args.c:
    args_c = args.c.split()
else:
    args_c = []

changes = [
    ("Observations", "Obs."),
    ("Adjusted R-squared", "Adj. $R^2$"),
    ("R-squared", "$R^2$"),
    #  ('VARIABLES', ''),
]

try:
    with open(args.varfile, "r") as v:
        var = [x.strip().split(" ", 1) for x in v.readlines() if x.strip()]
except:
    var = None
    print("cannot open varfile ...", file=sys.stderr)

with open(args.file, "r") as f:
    c = f.readlines()


def varname(row):
    if var:
        for x, y in var:
            try:
                row = re.sub(r"\b" + x + r"\b", y, row)
            except:
                row = row.replace(x, y)
    return row


def formatrow(row):
    row = re.sub(r"(\d+)(\*+)", r"\1&\2", row)
    row = re.sub(r"(?<![\*\\])\s*&(?!\s*\*)", r"&&", row)
    row = re.sub(r"(?<![\*\w])\s+\\\\", r"&\\\\", row)
    row = re.sub(r"\*\s+&", "*", row)
    row = re.sub(r"&&", r"&", row, 1)
    # adjust star styles
    row = re.sub(r"(\*{1,3})", r"$^{\1}$", row)
    row = re.sub("times", r"$\\times$", row)
    return row


def repeat_title(row):
    row1 = row
    row2 = "&".join([x for x in row.split("&") if ";" in x or re.search("^\s*$", x)])
    for x in re.findall(r"[\w\(\)\.\s\+\-]+;[\w\(\)\.\s\+\-]+", row):
        row1 = row1.replace(x, x.split(";")[0]).replace(r"\hline", "")
        row2 = (
            row2.replace(x, x.split(";")[1]).replace(r"\hline", "").replace(r"\\", "")
        )
    return row1, row2


def process_column_header(l):
    l = l.strip().strip("\\").replace(r"hline", "").rstrip("&")
    l = l.split("&")
    header = ""
    current, counter = "", 0
    for i, x in enumerate(l):
        x = x.strip()
        if i > 1:
            counter += 1
        if x:
            if x != current:
                if current:
                    header += f"\multicolumn{{ {counter} }}{{c}}{{ {current} }} &"
                counter = 0
            current = x
        if i == len(l) - 1:
            counter += 2
            header += f"\multicolumn{{ {counter} }}{{c}}{{ {current} }} &"

    counter = 0
    cline = []
    for i, c in enumerate(l, start=1):
        c = c.strip()
        if i > 1:
            c_clean = " ".join(re.findall("\w+", c)).strip()
            if c_clean:
                counter += 2
                if c == current:
                    try:
                        cline[-1] = i
                    except:
                        pass
                else:
                    cline.append(i)
                    cline.append(i)
                current = c
    output = ""
    if len(cline) == 2:
        return "delete_header"
    cline = iter(cline)
    for c in cline:
        c1, c2 = c, next(cline)
        if c1 != c2:
            output += r"\cline{%s-%s}" % (c1, c2)
        else:
            output += r"\cline{%s-%s}" % (c1, c2 + 1)
    return header.strip("&"), output


output = []
ctrls = []
for _n, row in enumerate(c):
    if row.startswith("o."):
        continue
    for ctrl in args_c:
        ctrl = ctrl.replace("_", "\\_")
        if re.search(
            r"\b" + ctrl.replace("\\", "").replace("_", "") + r"\b",
            row.replace("\\", "").replace("_", ""),
        ):
            ctrls.append(formatrow(varname(row)))
            ctrls.append(formatrow(c[_n + 1]))
            del c[_n + 1]
            break
    else:
        therow = varname(row).strip()
        for x, y in changes:
            therow = therow.replace(x, y)
        if not args.nostata:
            if "multicolumn" in therow:
                continue
        if "1o" in therow or "0b" in therow:
            continue
        if "tabular" in therow:
            continue
        if "{document}" in therow:
            continue
        if "documentclass" in therow:
            continue
        if "setlength" in therow:
            continue
        if "& . &" in therow:
            if not re.search("\d", therow):
                continue
            else:
                therow = therow.replace("& . &", "& &")
        if "& . \\" in therow:
            continue
        if "& (.) &" in therow:
            if not re.search("\d", therow):
                continue
            else:
                therow = therow.replace("& (.) &", "& &")
        if "& - &" in therow:
            continue
        if re.search(r"^(&\s*)+\\\\$", therow):
            continue
        therow = formatrow(therow)
        output.append(therow)
        #  if 'VARIABLES' in row:
        #  output.append('_add_empty_line123')
if args.nostata:
    output = [x for x in output if x.strip()]
    output[-1] = output[-1].replace("\\", "")
output[-1] = output[-1].replace(r"\hline", "")
if output[-1].strip() == "hline":
    del output[-1]

main = []
annotations = []
buffers = []
FE = []

for n, row in enumerate(output, start=1):
    r = row.strip()
    if ("& (1)" in row) and (not args.nostata):
        col_num = row
        continue
    if "VARIABLES" in row:
        r = r.replace("VARIABLES", "").replace(r"\hline", "")
        the_header, the_cline = process_column_header(r)
        if ";" in r and the_cline != "delete_header":
            row1, row2 = repeat_title(the_header)
            if args.noheader:
                main.append(row1 + "\\\\")
            else:
                main.append("&" + row1 + "\\\\")
                main.append("&" + row2 + "\\\\")
        elif the_cline != "delete_header" or args.noheader:
            main.append("&" + the_header + r"\\")
        if args.cline:
            cline_str = ""
            for cline in args.cline.split(","):
                cline_str += r"\cline{%s}" % cline
            main.append(cline_str)
        else:
            main.append(the_cline if the_cline != "delete_header" else "")
        if col_num:
            main.append(col_num)
        main.append(r"\hline")
        continue
    if not args.nostata:
        if re.search(r"^Obs", r):
            buffers.append(row)
            continue
        if re.search(r"^\$R\^2", r):
            buffers.append(row)
            continue
        if re.search("Adj. \$R\^2\$", r):
            buffers.append(row)
            continue
        if "FE&" in row:
            FE.append(row)
            continue
    if (
        (len(main) > 0)
        and (not re.search("\d+", r))
        and ("hline" not in r)
        and (not re.search(r"^\\+$", r))
    ):
        annotations.append(r)
    else:
        main.append(r)

if len(FE) > 3:
    FE[-2], FE[-1] = FE[-1], FE[-2]
buffers = FE + buffers


def clean_line(l):
    l = l.strip()
    if re.search("^\\+$", l):
        if args.nostata:
            return r"\\"
        else:
            return ""
    if l == "":
        return ""
    if len(re.findall(r"hline", l)) > 1:
        l = l.replace(r"\hline\\", "")
    if "_add_empty_line123" in l:
        return "\\\\\n"
    return l


def condenser(row):
    row = row.replace(r"//", "").strip()
    if not row:
        return True


if args.i:
    f = open(args.file, "w")
elif args.o:
    f = open(args.o, "w")
else:
    f = None


if args.meta:
    from datetime import datetime

    today = str(datetime.today()).split()[0]
    print(f"last update: {today}", file=f)

if args.nostata:
    if not args.condensed:
        print(r"\\", file=f)
else:
    print(r"\\", file=f)
    print(r"\hline", file=f)

for i, row in enumerate(main):
    if args.no_column_num:
        if re.search(r"\(\d\)", row):
            continue
    if condenser(row):
        continue
    l = clean_line(row)
    print(l, file=f)

if args.nocontrol:
    if args.nocontrol_n > 0:
        ctrls = ctrls[: args.nocontrol_n * 2]
    else:
        ctrls = []
for row in ctrls:
    if condenser(row):
        continue
    print(clean_line(row), file=f)

if not args.nostata:
    print("\\\\", file=f)
for row in annotations:
    if condenser(row):
        continue
    print(clean_line(row), file=f)

if buffers:
    buffers[-1] = buffers[-1].replace("\\", "")

for row in buffers:
    if condenser(row):
        continue
    if r"\hline \\\\" in row.strip():
        print(row.strip().replace(r"\hline \\\\", ""), file=f)
    else:
        print(clean_line(row), file=f)

if not args.nostata:
    print(r"\\", file=f)
    print(r"\hline", file=f)
