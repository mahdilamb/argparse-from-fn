import shlex
from typing import Any, Literal, Set, Tuple

import fn2argparse


def positionals_no_types_test():
    def fn(
        a,
        b,
        c,
    ):
        ...

    assert vars(fn2argparse.convert(fn).parse_args(shlex.split("1 2 3"))) == dict(
        a=1, b=2, c=3
    )


def positionals_test():
    def fn(
        a: int,
        b: float,
        c: bool,
    ):
        ...

    parser = fn2argparse.convert(fn)
    args = parser.parse_args(shlex.split("1 1 --c"))
    assert vars(args) == dict(a=1, b=1.0, c=True)


def initial_test():
    def blah(
        a: Literal["a", "b"],
        /,
        h: Set[int],
        f: bool,
        g,
        x: int = 2,
        j=3,
        *,
        y: int = 3,
        z=8,
    ):
        """Not a real function, for good reasons.

        Parameters
        ----------
        x : int, optional
            An int, by default 2
        """

    assert vars(
        fn2argparse.convert(blah).parse_args(
            shlex.split(f'"a" 3 4 5 --no-f --h 0  1 2 3')
        )
    ) == {
        "a": "a",
        "h": {1, 0, 2, 3},
        "f": False,
        "g": 3,
        "x": 4,
        "j": 5,
        "y": 3,
        "z": 8,
    }


def no_default_test():
    def blah(
        a: Literal["a", "b"],
        /,
        h: Set[int],
        f: bool,
        g,
        x: int,
        j,
        *,
        y: int,
        z,
    ):
        """Not a real function, for good reasons.

        Parameters
        ----------
        x : int, optional
            An int, by default 2
        """

    assert vars(
        fn2argparse.convert(blah).parse_args(
            shlex.split(f'"a" 3 4 5 --no-f --h 0  1 2 3')
        )
    ) == {
        "a": "a",
        "h": {1, 0, 2, 3},
        "f": False,
        "g": 3,
        "x": 4,
        "j": 5,
        "y": None,
        "z": None,
    }


def kwarg_only_with_defaults_test():
    def test(
        *,
        a: int = 1,
        b: int = 2,
        c: int = 3,
    ):
        ...

    assert vars(fn2argparse.convert(test).parse_args([])) == dict(a=1, b=2, c=3)


def kwarg_only_no_defaults_test():
    def test(*, a: int, b: int, c: int):
        ...

    assert vars(
        fn2argparse.convert(test).parse_args(shlex.split("--a 1 --b 2 --c 3"))
    ) == dict(a=1, b=2, c=3)


def tuple_test():
    def fn(a: Tuple[int, int, str]):
        ...

    assert vars(fn2argparse.convert(fn).parse_args(shlex.split("--a 1 2 3"))) == dict(
        a=(1, 2, "3")
    )


def any_test():
    def fn(a: Any):
        ...

    assert vars(fn2argparse.convert(fn).parse_args(shlex.split("1"))) == dict(a=1)


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(
        pytest.main(
            [
                "-vv",
                "-s",
            ]
            + sys.argv
        )
    )
