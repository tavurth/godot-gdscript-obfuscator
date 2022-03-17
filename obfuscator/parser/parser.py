#!/usr/bin/env python3

"""
Initializes and caches the GDScript parsers, using Lark.
Provides a function to parse GDScript code
and to get an intermediate representation as a Lark Tree.
"""
import os
import pickle
import sys
import pkg_resources

from lark import Lark, Tree, indenter
from lark.reconstruct import Reconstructor
from lark.grammar import Rule
from lark.lexer import TerminalDef


class Indenter(indenter.Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    # TODO: guess tab length
    tab_len = 4


# When upgrading to Python 3.8, replace with functools.cached_property
class cached_property:
    """A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.
    """

    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class Parser:
    """Parses GDScript code using lark parsers.
    The parsers are only created once, upon using them for the first time.
    """

    def __init__(self):
        self._directory = os.path.dirname(__file__)
        self._use_grammar_cache = True

    def parse(self, code: str, gather_metadata: bool = False) -> Tree:
        """Parses GDScript code and returns an intermediate representation as a Lark Tree.
        If gather_metadata is True, parsing is slower but the returned Tree comes with
        line and column numbers for statements and rules.
        """
        code += "\n"  # to overcome lark bug (#489)
        return (
            self._parser_with_metadata.parse(code)
            if gather_metadata
            else self._parser.parse(code)
        )

    def _get_parser(
        self,
        name: str,
        add_metadata: bool = False,
        grammar_filename: str = "gdscript.lark",
    ) -> Tree:
        version: str = pkg_resources.get_distribution("gdtoolkit").version

        tree: Tree = None
        grammar_filepath: str = os.path.join(self._directory, grammar_filename)

        tree = Lark.open(
            grammar_filepath,
            parser="lalr",
            start="start",
            postlex=Indenter(),
            propagate_positions=add_metadata,
            maybe_placeholders=False,
        )

        return tree

    @cached_property
    def _parser(self) -> Tree:
        return self._get_parser("parser")

    @cached_property
    def _parser_with_metadata(self) -> Tree:
        return self._get_parser("parser_with_metadata", add_metadata=True)

    @cached_property
    def _comment_parser(self) -> Tree:
        return self._get_parser(
            "parser_comments", add_metadata=True, grammar_filename="comments.lark"
        )


parser = Parser()
