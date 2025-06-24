import re

def add_leading_zero_to_floats(input_string):
    pattern = r"(?<!\d)([-+]?)(\.\d+)"

    # Replacement logic:
    # \g<1>    : Refers explicitly to capture group 1 (the sign, if any)
    # 0        : The literal '0' to be inserted
    # \g<2>    : Refers explicitly to capture group 2 (the dot and following digits)
    # This avoids the ambiguity of \1 followed by a digit.
    # So, if the match is '-.99', \g<1> is '-', \g<2> is '.99', replacement is '-0.99'
    # If the match is '.678', \g<1> is empty, \g<2> is '.678', replacement is '0.678'
    return re.sub(pattern, r"\g<1>0\g<2>", input_string)


def replace_float(match):
    """Helper function to format the matched float."""
    pattern = r"[-+]?(?:\d+\.\d+|\.\d+)"
    num_str = match.group(0)
    formatted_num = add_leading_zero_to_floats(num_str)
    return f"({formatted_num})"


def add_parentheses_to_floats(input_string):
    pattern = r"[-+]?(?:\d+\.\d+|\.\d+)"
    result_string = re.sub(pattern, replace_float, input_string)
    return result_string


def clean_table_cells(line: str) -> str:
    processed_line = line.replace("( . )", "")
    processed_line = processed_line.replace("(.)", "")
    return re.sub(r"\b0\.000\b", "", processed_line)
