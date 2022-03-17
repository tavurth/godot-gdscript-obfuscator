#!/usr/bin/env python3

import os
import re
from .parser import parser
from .reconstruct import reconstruct

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


def find(to_search: str, only_files=True):
    to_ignore = " --ignore ".join([""] + EXCLUDED_FILES)
    to_append = '"'

    if only_files:
        to_append += " --files-with-matches"

    return (
        os.popen(
            'pt --ignore "*.gltf" --nonumbers --nocolor --nogroup '
            + to_ignore
            + ' -e "'
            + to_search
            + to_append
        )
        .read()
        .split("\n")
    )


def find_all_gdscript_files():
    to_return = find("(func |var | const | class )")
    return [i for i in to_return if ".gd" in i]


def cleanup_original(original: str):
    """
    Handles the replacement of common GDScript patterns
    Removing newlines and compressing the script in general
    """
    # Remove comments
    original = re.sub(r"\t+#.*\n", "", original)

    # Remove comment headers
    original = re.sub(r'([\'"])\1\1(.*?)\1{3}', "", original, flags=re.DOTALL)

    # Remove multiple newlines
    original = re.sub(r"^\t?\n", "", original, flags=re.MULTILINE)

    return original


def obfuscate():
    for filename in find_all_gdscript_files():
        with open(filename, "r") as fin:
            file_data = cleanup_original(fin.read())

        result = parser.parse(file_data)

        result = reconstruct(file_data, result)

        print(result)
