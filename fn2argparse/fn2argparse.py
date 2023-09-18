"""Main package containing the parser."""
import argparse
import ast
from typing import Any, Callable, Collection, Literal, Optional, TypeAlias

import docstring_parser

SUPPORTED_TYPES = bool, int, float, str, complex


def _any(val,):
    """Try and convert the value to a primitive type."""
    try:
        return ast.literal_eval(val)
    except ValueError:
        return val


def _tuple(annotation: TypeAlias):
    """Create a tuple caster."""
    types = annotation.__args__

    def convert(val):
        nonlocal types
        type, *types = types
        return type(val)

    return convert


def convert(
    func: Callable, parser: Optional[argparse.ArgumentParser] = None
) -> argparse.ArgumentParser:
    """Convert a function to an argument parser."""
    parser = parser or argparse.ArgumentParser()
    docstring = docstring_parser.parse(func.__doc__ or "")
    docstring_params = {param.arg_name: param for param in docstring.params}
    parser.description = docstring.short_description
    kwargs_from = func.__code__.co_argcount
    defaults_start = kwargs_from - len(func.__defaults__ or ())
    post_format = {}
    func_code = func.__code__
    for argi, arg in enumerate(
        func_code.co_varnames[: func_code.co_argcount + func_code.co_kwonlyargcount]
    ):
        kwarg_only = argi >= kwargs_from
        default = None
        if kwarg_only and func.__kwdefaults__:
            default = func.__kwdefaults__.get(arg)
        elif func.__defaults__:
            __i = argi - defaults_start
            if __i >= 0:
                default = func.__defaults__[__i]
        ftype = func.__annotations__.get(arg, _any)
        choices = None
        nargs = None
        action = "store"
        if ftype == Any:
            ftype = _any
        elif hasattr(ftype, "__origin__"):
            if ftype.__origin__ is Literal:
                choices = ftype.__args__
                ftype = _any
            elif issubclass(ftype.__origin__, Collection):
                nargs = (
                    "*"
                    if not issubclass(ftype.__origin__, tuple)
                    else len(ftype.__args__)
                )
                kwarg_only = True
                post_format[arg] = ftype.__origin__
                ftype = (
                    ftype.__args__[0]
                    if not issubclass(ftype.__origin__, tuple)
                    else _tuple(ftype)
                )
        elif isinstance(ftype, type):
            if issubclass(ftype, bool):
                action = argparse.BooleanOptionalAction
                kwarg_only = True
            elif not issubclass(ftype, (int, float, str, complex)):
                raise ValueError("User-defined types not supported")
        elif ftype != _any:
            raise ValueError("Unsupported type")
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
