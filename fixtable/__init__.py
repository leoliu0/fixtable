#!/bin/python
import argparse
import re
import sys
from loguru import logger

parser = argparse.ArgumentParser(
    description="process files and customize output format."
)
parser.add_argument("file", help="the file to be processed.")
parser.add_argument(
    "-v",
    "--varfile",
    metavar="varfile",
    help="path to the variable name mapping file.",
)
parser.add_argument(
    "-i", action="store_true", help="replace the input file with the output."
)
parser.add_argument("-c", help="define control variables.")
parser.add_argument(
    "-o",
    help="output file path. if not provided, the output will be printed to standard output.",
)
parser.add_argument(
    "--dep", help="specify the dependent variable in `variables`", default=""
)
parser.add_argument("--cline", help="define clines.")
parser.add_argument(
    "--noheader", action="store_true", help="disable the header in the output."
)
parser.add_argument(
    "--myheader",
    action="store_true",
    help="disable the header and column numbers in the output.",
)
parser.add_argument(
    "--condensed", action="store_true", help="condense the output format."
)
parser.add_argument(
    "--no_column_num",
    action="store_true",
    help="exclude column numbers from the output.",
)
parser.add_argument(
    "--debug", action="store_true", help="enable debug mode for logging."
)
parser.add_argument(
    "--nocontrol",
    action="store_true",
    help="exclude control variables from the output.",
)
parser.add_argument(
    "--nocontrol_n",
    type=int,
    default=0,
    metavar="nocontrol_n",
    help="start from which control variables to exclude from the output.",
)
parser.add_argument(
    "-m",
    "--meta",
    action="store_true",
    help="include metadata such as the last update date in the output.",
)
parser.add_argument(
    "--feorder", action="store_true", help="reorder fixed effects in the output."
)

args = parser.parse_args()


def debug(message):
    if args.debug:
        logger.debug(message)


def clean_line(l):
    l = l.strip()
    if re.search("^\\+$", l):
        return r"\\" if args.nostata else ""
    if not l:
        return ""
    if len(re.findall(r"hline", l)) > 1:
        l = l.replace(r"\hline\\", "")
    if "_add_empty_line123" in l:
        return "\\\\\n"
    return l


def condenser(row):
    return not row.replace(r"//", "").strip()


def printer(x, file=None, last=""):
    if last.strip().strip("\\") == "" and x.strip().strip("\\") == "":
        return "xxx"
    print(x, file=file)
    return x


def varname(row, var):
    row = re.sub(r"[10]\.(?=[a-za-z])", "", row)
    row = (
        row.replace("\\_", "_")
        .replace("times", " $\\times$ ")
        .replace("\\#", " $\\times$ ")
    )
    if var:
        for x, y in var:
            y = y.split("--")[0].strip() if y.endswith("--") else y
            row = re.sub(r"\b" + x + r"\b", y.replace("\\", "\\\\"), row)
    return row.replace("#", " $\\times$ ")


def formatrow(row):
    row = re.sub(r"(\d+)(\*+)", r"\1&\2", row)
    row = re.sub(r"(?<![\*\\])\s*&(?!\s*\*)", r"&&", row)
    row = re.sub(r"(?<![\*\w])\s+\\\\", r"&\\\\", row)
    row = re.sub(r"\*\s+&", "*", row)
    row = re.sub(r"&&", r"&", row, 1)
    row = re.sub(r"(\*{1,3})", r"$^{\1}$", row)
    row = row.replace(" times ", " $\\times$ ")
    row = row.replace(" \\# ", " $\\times$ ")
    return row


def repeat_title(line):
    if not line.strip().endswith("\\"):
        return [line]

    line = line.strip().strip("&").strip()
    parts = [part.strip() for part in line.rstrip("\\").split("&&")]

    first_line_parts = []
    second_line_parts = []
    cline_ranges = []

    current_label = None
    current_values = []
    current_start_col = 2

    for part in parts:
        if ";" in part:
            label, value = part.split(";")
            if current_label is None:
                current_label = label.strip()
            if label.strip() != current_label:
                # add the current group to the first and second lines
                col_count = len(current_values) * 2
                first_line_parts.append(
                    f"\\multicolumn{{{col_count}}}{{c}}{{{current_label}}}"
                )
                second_line_parts.extend(current_values)
                # track the cline range
                current_end_col = current_start_col + col_count - 2
                cline_ranges.append(f"{current_start_col}-{current_end_col}")
                current_start_col += col_count
                # reset for the new group
                current_label = label.strip()
                current_values = []
            current_values.append(value.strip())
        else:
            # if we encounter a part that doesn't fit the current pattern, finalize the group
            if current_label:
                col_count = len(current_values) * 2
                first_line_parts.append(
                    f"\\multicolumn{{{col_count}}}{{c}}{{{current_label}}}"
                )
                second_line_parts.extend(current_values)
                current_end_col = current_start_col + col_count - 3
                cline_ranges.append(f"{current_start_col}-{current_end_col}")
                current_start_col += col_count
                current_label = None
                current_values = []
            first_line_parts.append(part)
            second_line_parts.append("")
            current_start_col += 3

    # handle the last group
    if current_label:
        col_count = len(current_values) * 2
        first_line_parts.append(f"\\multicolumn{{{col_count}}}{{c}}{{{current_label}}}")
        second_line_parts.extend(current_values)
        current_end_col = current_start_col + col_count - 2
        cline_ranges.append(f"{current_start_col}-{current_end_col}")

    first_line = " & ".join(first_line_parts)
    second_line = " && ".join(second_line_parts)
    cline = "".join([f"\\cline{{{r}}}" for r in cline_ranges])

    return first_line, second_line, cline


def process_column_header(l):
    l = l.strip().strip("\\").replace(r"hline", "").strip("&").strip()
    l = re.split(r"(?<!\\)&&", l)
    header = ""
    current, counter = "", 0
    for i, x in enumerate(l):
        x = x.strip()
        counter += 2
        if x and x != current:
            if current:
                header += f"\\multicolumn{{ {counter} }}{{c}}{{ {current} }} &"
            counter = 0
            current = x
        if i == len(l) - 1:
            counter += 2
            header += f"\\multicolumn{{ {counter} }}{{c}}{{ {current} }} &"
    counter = 0
    cline = []
    current = ""
    for i, c in enumerate(l, start=1):
        c = c.strip()
        c_clean = " ".join(re.findall(r"\w+", c)).strip()
        if c_clean:
            counter += 2
            if c == current:
                cline[-1] = i * 2
            else:
                cline.append(i * 2) if i > 1 else cline.append(2)
                cline.append(i * 2 + 1)
            current = c
    output = ""
    # if len(cline) == 2:
    #     return "delete_header"
    cline = iter(cline)
    for c in cline:
        c1, c2 = c, next(cline)
        output += r"\cline{%s-%s}" % (c1, c2)
    return header.strip("&"), output


# parse command-line arguments
def main():
    if args.myheader:
        args.noheader = True

    args_c = args.c.split() if args.c else []

    changes = [
        ("Observations", "Obs."),
        ("Adjusted R-squared", "Adj. $R^2$"),
        ("R-squared", "$R^2$"),
        ("c.", ""),
    ]

    try:
        with open(args.varfile, "r") as v:
            var = [line.strip().split(" ", 1) for line in v.readlines() if line.strip()]
            var = [[x[0], ""] if len(x) == 1 else x for x in var]
    except:
        var = None
        print("cannot open varfile ...", file=sys.stderr)

    with open(args.file, "r") as f:
        c = f.readlines()

    output = []
    ctrls = []
    const = []
    skip = False
    stata = False
    for _n, row in enumerate(c):
        if row.startswith("VARLABELS"):
            stata = True
        if skip:
            skip = False
            continue
        if row.startswith("Constant"):
            const.append(varname(formatrow(row), var))
            const.append(formatrow(c[_n + 1]))
            skip = True
            continue
        if row.startswith("o."):
            continue
        for ctrl in args_c:
            ctrl = ctrl.replace("_", "\\_").lower().replace("l.", "l.")
            if re.search(
                r"\b" + ctrl.replace("\\", "").replace("_", "") + r"\b",
                row.replace("\\", "").replace("_", ""),
            ):
                ctrls.append(varname(formatrow(row), var))
                ctrls.append(formatrow(c[_n + 1]))
                del c[_n + 1]
                break
        else:
            therow = formatrow(varname(row, var)).strip()
            for x, y in changes:
                therow = therow.replace(x, y)
            if stata:
                if "multicolumn" in therow:
                    continue
            if any(
                term in therow
                for term in [
                    "1o",
                    "0b",
                    "tabular",
                    "{document}",
                    "documentclass",
                    "setlength",
                ]
            ):
                continue
            if "& .&" in therow and not re.search(r"\d{2}", therow):
                continue
            if "& (.)&" in therow and not re.search(r"\d{2}", therow):
                continue
            if "& . &" in therow and not re.search(r"\d{2}", therow):
                continue
            if "& (.) &" in therow and not re.search(r"\d", therow):
                therow = therow.replace("& (.) &", "& &")
            if "& - &" in therow or re.search(r"^(&\s*)+\\\\$", therow):
                continue
            output.append(therow)

    if not stata:
        output = [x for x in output if x.strip()]
        output[-1] = output[-1].replace("\\", "")
    if output[-1].strip() == "hline":
        del output[-1]

    if const:
        ctrls.extend(const)

    main = []
    annotations = []
    buffers = []
    fe = []

    ncolumns = 10
    for n, row in enumerate(output, start=1):
        r = row.strip()
        if ("& (1)" in row) and (stata):
            col_num = row
            continue
        if "VARIABLES" in row:
            ncolumns = len(row.split("&")) // 2
            r = r.replace("VARIABLES", "").replace(r"\hline", "")
            if ";" in r:
                row1, row2, the_cline = repeat_title(r)
                if args.noheader:
                    main.append(row1 + "\\\\")
                    main.append(the_cline)
                else:
                    main.append("&" + row1 + "\\\\")
                    main.append("&" + row2 + "\\\\")
                    if args.cline:
                        main.append(r"\cline{" + args.cline + "}")
                    else:
                        main.append(the_cline)

            elif not args.noheader:
                the_header, the_cline = process_column_header(r)
                main.append(args.dep + "&" + the_header + r"\\")
                if args.cline:
                    main.append(r"\cline{" + args.cline + "}")
                else:
                    main.append(the_cline)

            if col_num:
                main.append(col_num)
            main.append(r"\hline")
            continue
        if stata:
            if any(
                re.search(pattern, r)
                for pattern in [r"^Obs", r"^\$R\^2", r"Adj. \$R\^2\$", r"Wald F"]
            ):
                # if r.endswith("\\\\"):
                #     r = r[:-2]
                buffers.append(r)
                continue
            if re.search(r"FE&", r):
                if "hline" in r:
                    r = r[:-7]
                fe.append(r)
                continue
        if (
            len(main) > 0
            and not re.search(r"\d+", r)
            and "hline" not in r
            and not re.search(r"^\\+$", r)
        ):
            annotations.append(r)
        else:
            main.append(r)

    if args.feorder and len(fe) > 3:
        fe[-2], fe[-1] = fe[-1], fe[-2]
    buffers = fe + buffers

    output_file = (
        open(args.o, "w") if args.o else (open(args.file, "w") if args.i else None)
    )

    if args.meta:
        from datetime import datetime

        today = str(datetime.today()).split()[0]
        print(f"last update: {today}", file=output_file)

    if not stata and not args.condensed:
        print(r"\\", file=output_file)
    elif not args.myheader:
        print(r"\\", file=output_file)
        print(r"\hline", file=output_file)

    printed = []
    for i, row in enumerate(main):
        if args.no_column_num and re.search(r"\(\d\)", row):
            continue
        if condenser(row):
            continue
        l = clean_line(row)
        print(l, file=output_file)
        printed.append(l)

    if args.nocontrol:
        ctrls = ctrls[: args.nocontrol_n * 2] if args.nocontrol_n > 0 else []

    for row in ctrls:
        if condenser(row):
            continue
        print(clean_line(row), file=output_file)

    last = "xxx"
    for i, row in enumerate(annotations):
        if condenser(row):
            continue
        last = printer(clean_line(row), output_file, last)

    for row in buffers:
        if "hline" in row:
            row = row[:-7]
        if "Obs" in row.lower() and not args.condensed:
            last = printer(f"{'&' * ncolumns} \\\\", output_file, last)
        if condenser(row):
            continue
        print(clean_line(row), file=output_file)
    if not stata:
        print(r"\hline", file=output_file)
