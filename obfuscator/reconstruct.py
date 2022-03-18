#!/usr/bin/env python3

import re
from math import inf
from lark import Tree, Token

TAB_MATCHER = re.compile(r"(\t)+[a-zA-Z]")


def join_children(tree: Tree, join_by: str):
    to_return = ""

    for child in tree.children:
        if isinstance(child, Tree):
            to_return += construct(child) + join_by

        else:
            to_return += child + join_by

    return to_return.rstrip(join_by)


def process_extends(tree: Tree):
    return "extends " + construct(tree, max=1) + "\n"


def process_func_def(tree: Tree):
    return "func " + construct(tree, stop=1) + construct(tree, start=1)


def process_func_header(tree: Tree):
    if "func_args" not in tree.pretty():
        return construct(tree, stop=1) + "():\n"

    return construct(tree, stop=1) + construct(tree)


def process_func_args(tree: Tree):
    return "(" + construct(tree) + "):\n"


def process_func_arg_typed(tree: Tree):
    return ",".join([i for i in tree.children if i.type == "NAME"])


def process_if_branch(tree: Tree):
    return construct(tree, stop=1) + ":\n" + construct(tree, start=1)


def process_if_stmt(tree: Tree):
    return "if " + construct(tree)


def process_expr(tree: Tree):
    return construct(tree)


def process_not_test(tree: Tree):
    return "not " + construct(tree, start=1)


def process_type_test(tree: Tree):
    return join_children(tree, " ")


def process_return_stmt(tree: Tree):
    return "return\n"


def process_getattr(tree: Tree):
    return join_children(tree, "")


def process_name(tree: Tree):
    return tree.value


def process_getattr_call(tree: Tree):
    return construct(tree)


def process_expression(tree: Tree):
    return construct(tree)


def process_assignment(tree: Tree):
    return construct(tree)


def process_standalone_call(tree: Tree):
    return join_children(tree, "") + "\n"


def process_func_var_stmt(tree: Tree):
    return construct(tree)


def process_while_stmt(tree: Tree):
    return "while " + construct(tree, stop=1) + ":\n" + construct(tree, start=1)


def process_continue(_tree: Tree):
    return "continue\n"


def process_var_assigned(tree: Tree):
    return "var " + construct(tree, stop=1) + "=" + construct(tree, start=1) + "\n"


def process_comparison(tree: Tree):
    return join_children(tree, "")


def process_else_branch(tree: Tree):
    return "else:\n" + construct(tree)


def process_string(tree: Tree):
    return construct(tree, start=1)


def process_tool_stmt(tree: Tree):
    return "tool\n"


def process_match_stmt(tree: Tree):
    return "match " + construct(tree, start=1)


def process_match_branch(tree: Tree):
    return construct(tree, stop=1) + ":\n" + construct(tree, start=1)


def process_pattern(tree: Tree):
    return construct(tree)


def process_pattern_wildcard(tree: Tree):
    return construct(tree)


def process_default(tree: Tree):
    raise ValueError("No type to handle this case: " + str(tree))


TREE_TYPES = {
    "assignment": process_assignment,
    "comparison": process_comparison,
    "continue": process_continue,
    "else_branch": process_else_branch,
    "expr": process_expr,
    "expression": process_expression,
    "extends": process_extends,
    "func_arg_typed": process_func_arg_typed,
    "func_args": process_func_args,
    "func_def": process_func_def,
    "func_header": process_func_header,
    "func_var_stmt": process_func_var_stmt,
    "getattr": process_getattr,
    "getattr_call": process_getattr_call,
    "if_branch": process_if_branch,
    "if_stmt": process_if_stmt,
    "match_branch": process_match_branch,
    "match_stmt": process_match_stmt,
    "name": process_name,
    "not_test": process_not_test,
    "pattern": process_pattern,
    "return_stmt": process_return_stmt,
    "standalone_call": process_standalone_call,
    "string": process_string,
    "tool_stmt": process_tool_stmt,
    "type_test": process_type_test,
    "var_assigned": process_var_assigned,
    "while_stmt": process_while_stmt,
    "wildcard_pattern": process_pattern_wildcard,
}


def construct(tree: Tree, **kwargs):
    to_return = ""

    start = kwargs.get("start", 0)
    stop = kwargs.get("stop", inf)
    stop = min(stop, len(tree.children))

    for idx in range(start, stop):
        item = tree.children[idx]

        if isinstance(item, Tree):
            to_return += TREE_TYPES.get(item.data, process_default)(item)

        else:
            to_return += item.value

    return to_return


def cleanup(original: str):
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

    # Always put return on a newline
    # original = re.sub(r"((\t)+.*:\s?return)", ":")

    return original


def reconstruct(original: str, tree: Tree, **kwargs):
    to_return = []

    constructed = construct(tree)
    split_original = cleanup(original).split("\n")
    split_construct = constructed.split("\n")

    for idx in range(len(split_construct)):
        tabs = TAB_MATCHER.search(split_original[idx])
        if not tabs:
            to_return.append(split_construct[idx])
            continue

        line = "\t" * (tabs.end() - tabs.start())
        line += split_construct[idx]

        to_return.append(line)

    return "\n".join(to_return)
