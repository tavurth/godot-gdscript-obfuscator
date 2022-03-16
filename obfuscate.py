#!/usr/bin/env python3

import re
import os
import string
import random

DRY_RUN = True

TOKENS = ["var ", "func ", "const ", "for "]
EXCLUDED_FILES = ["./scripts/obfuscate.py"]
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

PREPEND_TYPES = ["GDScriptFunctionState", "true", "false"]
PREPEND_FUNCS = ["len", "add_child", "remove_child"]

name = 0
names = {}
name_types = ["_", "__", "___"]


def find(to_search: str):
    return (
        os.popen(
            'pt --ignore "*.gltf" --nonumbers --nocolor --nogroup "' + to_search + '"'
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
    to_return = []
    to_extract = clip_search(to_search)

    for line in found:
        if not line:
            continue

        parts = line.split(":")
        if len(parts) < 2:
            continue

        parts = [i.strip() for i in parts]
        file_name = parts[0]

        if "# no-mangle" in parts:
            continue

        try:
            token_name = extract_token(parts[1], to_search)
        except ValueError:
            continue

        if file_name in EXCLUDED_FILES:
            continue

        if token_name in EXCLUDED_TOKENS:
            continue

        to_return.append({"file": file_name, "value": token_name})

    return to_return


def extract_all(to_search: list):
    to_return = []

    for search_token in to_search:
        to_return += extract(search_token)

    return to_return


def build_files_dict(extracted: list):
    to_return = {}

    for item in extracted:
        if item["file"] not in to_return:
            to_return[item["file"]] = []

        to_return[item["file"]].append(item["value"])

    return to_return


def gen_name_type():
    return random.choice(name_types) + random.choice(string.ascii_letters)


def gen_name(token_name: str):
    global name, names

    if token_name not in names:
        name += 1
        names[token_name] = gen_name_type() + str(name)

    return names[token_name]


NO_TOKEN_MATCH = r"([^a-zA-Z_\"\'])"


def replace(file_data: str, item: str):
    # item, item_b
    return re.sub(
        NO_TOKEN_MATCH + item + NO_TOKEN_MATCH,
        r"\1" + gen_name(item) + r"\2",
        file_data,
    )


def cleanup(file_data):
    # Remove comments
    file_data = re.sub("\t+#.*\n", "", file_data)

    # Remove function return types
    file_data = re.sub(" \-\> (.*)\:", ":", file_data)

    # Remove comment headers
    file_data = re.sub(r'([\'"])\1\1(.*?)\1{3}', "", file_data, flags=re.DOTALL)

    # Remove multiple newlines
    file_data = re.sub("^\t?\n", "", file_data, flags=re.MULTILINE)

    # Put return on sameline after if or func
    file_data = re.sub(":\n\t+return", ":return", file_data)

    # Put return on sameline after statement
    file_data = re.sub("\n+\t+return", ";return", file_data)

    # Remove self references
    file_data = re.sub("self\.", "", file_data)

    # Remove errors
    file_data = re.sub("push_error\(.*\)", "pass", file_data)

    # Remove warnings
    file_data = re.sub("push_warning\(.*\)", "pass", file_data)

    # Remove print statements
    file_data = re.sub("print(s?)\(.*\)", "pass", file_data)

    return file_data


def gen_prepends(file_data: str):
    header_index = file_data.find("extends")

    file_header = file_data[0 : file_data.find("\n", header_index)]
    file_body = file_data[file_data.find("\n", header_index) :]

    # Generate a lot of CONST items so that
    # we can compare types in a more obfuscated way
    for item in PREPEND_TYPES:
        token = gen_name(item)
        token_data = "const {item} = {token}\n".format(item=item, token=token)
        file_body = token_data + file_body

    # Generate a lot of functions so we can replace
    # basic GDScript functions with our obfuscated ones
    for item in PREPEND_FUNCS:
        token = gen_name(item)
        token_data = "func {item}(arg):\n\treturn {token}(arg)\n".format(
            item=item, token=token
        )
        file_body = token_data + file_body

    return file_header + "\n" + file_body


def run(*to_search: list):
    extracted = build_files_dict(extract_all(to_search))

    count = 0
    for file_name in extracted:
        print("[Obfuscating]:", file_name + "...")

        with open(file_name) as fin:
            file_data = fin.read()

        # Do the longest strings first
        # This gives us less chance of a name collision
        for item in sorted(extracted[file_name], key=len, reverse=True):
            file_data = replace(file_data, item)

        file_data = gen_prepends(file_data)
        file_data = cleanup(file_data)

        if DRY_RUN:
            print(file_data)
        else:
            with open(file_name, "w") as fout:
                fout.write(file_data)


run(*TOKENS)
