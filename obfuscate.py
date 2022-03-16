#!/usr/bin/env python3

import re
import os
import string
import random

DRY_RUN = True

EXCLUDED_FILES = [os.path.basename(__file__)]
EXCLUDED_TOKENS = [
    "_process",
    "_physics_process",
    "_ready",
    "_init",
    "_enter_tree",
    "_exit_tree",
    "_notification",
    "translated",
    "rotated",
    "basis",
]

TOKENS = ["class ", "var ", "func ", "const ", "for "]
PREPEND_TYPES = ["true", "false"]
PREPEND_FUNCS = ["len"]

name = 0
names = {}


def find(to_search: str):
    to_ignore = " --ignore ".join([""] + EXCLUDED_FILES)
    return (
        os.popen(
            'pt --ignore "*.gltf" --nonumbers --nocolor --nogroup '
            + to_ignore
            + ' "'
            + to_search
            + '"'
        )
        .read()
        .split("\n")
    )


def clip_search(search: str):
    return re.sub("[^A-Za-z0-9]+", "", search)


def filter_tokens(tokens: list):
    tokens = [i.strip() for i in tokens]
    tokens = [i for i in tokens if len(i)]

    return tokens


def extract_tokens(line: str):
    return filter_tokens(
        line.replace(" ", "~")
        .replace("(", "~")
        .replace(")", "~")
        .replace(":", "~")
        .split("~")
    )


def extract_token(line: str, search: str):
    tokens = extract_tokens(line)
    search = search.strip()

    if search not in tokens:
        raise ValueError("Token not found " + " ".join(tokens))

    index = tokens.index(search)
    return tokens[index:][1]


def extract(to_search: str):
    found = find(to_search)
    to_process = []
    to_extract = clip_search(to_search)

    for line in found:
        if not line:
            continue

        parts = line.split(":")
        if len(parts) < 2:
            continue

        parts = [i.strip() for i in parts]
        file_name = parts[0]

        try:
            token_name = extract_token(parts[1], to_search)
        except ValueError:
            continue

        if token_name in EXCLUDED_TOKENS:
            continue

        to_process.append({"file": file_name, "type": to_extract, "value": token_name})

    return to_process


def process_no_mangle(to_return: dict):
    matcher = re.compile("^(.+)# no-mangle", re.MULTILINE)

    for file_name in to_return:
        with open(file_name, "r") as fin:
            file_data = fin.read()

        if "# no-mangle" not in file_data:
            continue

        results = matcher.findall(file_data)

        for result in results:
            # TODO: Match more than function name
            #       Now we only extract func <name>()
            token = extract_tokens(result)[1]

            to_set = []

            for item in to_return[file_name]:
                if item["type"] == "func":
                    if item["value"] == token:
                        continue

                to_set.append(item)

            to_return[file_name] = to_set

    return to_return


def has_type(array: list, item: dict):
    for subitem in array:
        if not subitem["type"] == item["type"]:
            continue

        if not subitem["value"] == item["value"]:
            continue

        return True

    return False


def merge(old: dict, new: dict):
    # Now sort everything into a dictionary of files -> values
    to_return = old

    for item in new:
        file_name = item["file"]
        del item["file"]

        if file_name not in to_return:
            to_return[file_name] = []

        if not has_type(to_return[file_name], item):
            to_return[file_name].append(item)

    return to_return


def extract_all():
    to_return = {}

    for search_token in TOKENS:
        to_return = merge(to_return, extract(search_token))

    return process_no_mangle(to_return)


def gen_name(item: dict):
    global name, names

    print(item)
    token_name = item["type"] + "_" + item["value"]
    print(token_name)

    if token_name not in names:
        name += 1
        names[token_name] = "_" + str(name)

    return names[token_name]


NO_TOKEN_MATCH = r"([^a-zA-Z_\"\'])"
NO_FUNCTION_MATCH = r"([^a-zA-Z_\"\'\(])"


def obfuscate_token(file_data: str, item: dict):
    """
    Handles replacing a <token> such as function name
    or variable name in the file. A new name will be automatically
    generated and inserted throughout the file
    """
    to_search = r""

    # Only match function calls and definitions
    if item["type"] == "func":
        to_search = NO_TOKEN_MATCH + item["value"] + NO_TOKEN_MATCH

    else:
        to_search = NO_TOKEN_MATCH + item["value"] + NO_FUNCTION_MATCH

    print(to_search)
    return re.sub(to_search, r"\1" + gen_name(item) + r"\2", file_data)


def obfuscate(file_data):
    """
    Handles the replacement of common GDScript patterns
    Removing newlines and compressing the script in general
    """

    # Remove comments
    file_data = re.sub(r"\t+#.*\n", "", file_data)
    file_data = re.sub(r"\s?#.*\n", "\n", file_data)

    # Remove function return types
    file_data = re.sub(r" \-\> (.*)\:", ":", file_data)

    # Remove comment headers
    file_data = re.sub(r'([\'"])\1\1(.*?)\1{3}', "", file_data, flags=re.DOTALL)

    # Remove multiple newlines
    file_data = re.sub(r"^\t?\n", "", file_data, flags=re.MULTILINE)

    # Put return on sameline after if or func
    file_data = re.sub(r":\n\t+return", ": return", file_data)

    # Remove self references
    file_data = re.sub(r"self\.", "", file_data)

    # Remove errors
    file_data = re.sub(r"push_error\(.*\)", "pass", file_data)

    # Remove warnings
    file_data = re.sub(r"push_warning\(.*\)", "pass", file_data)

    # Remove print statements
    file_data = re.sub(r"print(s?)\(.*\)", "pass", file_data)

    return file_data


def gen_prepends(file_data: str):
    header_index = file_data.find("extends")

    file_header = file_data[0 : file_data.find("\n", header_index)]
    file_body = file_data[file_data.find("\n", header_index) :]

    # Generate a lot of CONST items so that
    # we can compare types in a more obfuscated way
    for item in PREPEND_TYPES:
        token = gen_name({"value": item, "type": "var"})
        token_data = "const {token} = {item}\n".format(item=item, token=token)
        file_body = file_body.replace(item, token)
        file_body = token_data + file_body

    # Generate a lot of functions so we can replace
    # basic GDScript functions with our obfuscated ones
    for item in PREPEND_FUNCS:
        token = gen_name({"value": item, "type": "func"})
        token_data = "func {token}(arg):\n\treturn {item}(arg)\n".format(
            item=item, token=token
        )
        file_body = file_body.replace(item, token)
        file_body = token_data + file_body

    return file_header + "\n" + file_body


def value_sorted(array: list):
    return


def run():
    extracted = extract_all()

    for file_name in extracted:
        print("[Obfuscating]:", file_name)
        print("--------------------------------------------------")

        # Read the current file
        with open(file_name) as fin:
            file_data = fin.read()

        # Do the longest strings first
        # This gives us less chance of a name collision
        for item in sorted(
            extracted[file_name], key=lambda x: len(x["value"]), reverse=True
        ):
            file_data = obfuscate_token(file_data, item)

        file_data = gen_prepends(file_data)
        file_data = obfuscate(file_data)

        if DRY_RUN:
            print(file_data)
        else:
            with open(file_name, "w") as fout:
                fout.write(file_data)


run()
