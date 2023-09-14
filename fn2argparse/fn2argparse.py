"""Main package containing the parser."""
import argparse
from typing import Callable, Collection, Literal, Optional

import docstring_parser

IDENTITY = lambda val: val


def convert(
    function: Callable, parser: Optional[argparse.ArgumentParser] = None
) -> argparse.ArgumentParser:
    """Convert a function to an argument parser."""
    parser = parser or argparse.ArgumentParser()
    docstring = docstring_parser.parse(function.__doc__ or "")
    docstring_params = {param.arg_name: param for param in docstring.params}
    parser.description = docstring.short_description
    defaults_start = (
        len(function.__code__.co_varnames)
        - function.__code__.co_kwonlyargcount
        - len(function.__defaults__ or ())
    )
    post_format = {}
    for argi, arg in enumerate(function.__code__.co_varnames):
        kwarg_only = (
            argi
            >= len(function.__code__.co_varnames) - function.__code__.co_kwonlyargcount
        )
        default = None
        if kwarg_only and function.__kwdefaults__:
            default = function.__kwdefaults__.get(arg)
        elif function.__defaults__:
            __i = argi - defaults_start
            if __i >= 0:
                default = function.__defaults__[__i]
        ftype = function.__annotations__.get(arg, IDENTITY)
        choices = None
        nargs = None
        action = "store"
        if hasattr(ftype, "__origin__"):
            if ftype.__origin__ is Literal:
                choices = ftype.__args__
                ftype = IDENTITY
            elif issubclass(ftype.__origin__, Collection):
                nargs = "*"
                kwarg_only = True
                post_format[arg] = ftype.__origin__
                ftype = IDENTITY
        elif isinstance(ftype, type):
            if issubclass(ftype, bool):
                action = argparse.BooleanOptionalAction
                kwarg_only = True
        help = None
        param_help = docstring_params.get(arg)
        if param_help:
            help = param_help.description
        arg_kwargs = dict(
            default=default,
            type=ftype,
            help=help,
            choices=choices,
            nargs=nargs,
            action=action,
        )
        if action != "store":
            del arg_kwargs["nargs"]
        parser.add_argument(("--" if kwarg_only else "") + arg, **arg_kwargs)
    original_parser = parser.parse_known_args

    def parse_known_args(args=None, namespace=None):
        values, unknown = original_parser(args, namespace)
        for arg, fn in post_format.items():
            setattr(values, arg, fn(getattr(values, arg)))
        return values, unknown

    setattr(parser, "parse_known_args", parse_known_args)
    return parser
