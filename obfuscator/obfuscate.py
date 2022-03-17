#!/usr/bin/env python3

import os
import re
from lark import Tree, Token
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


def mangle(result: Tree):
    """
    Take in a lark tree and iterate through each
    name (function or variable) mangling them in turn
    """
    return result


def obfuscate():
    for filename in find_all_gdscript_files():
        with open(filename, "r") as fin:
            file_data = fin.read()

        result = parser.parse(file_data)
        result = mangle(result)
        result = reconstruct(file_data, result)

        print(result)
