import shlex
from typing import Literal, Set

import fn2argparse


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
        "h": {"1", "0", "2", "3"},
        "f": False,
        "g": "3",
        "x": 4,
        "j": "5",
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
        "h": {"1", "0", "2", "3"},
        "f": False,
        "g": "3",
        "x": 4,
        "j": "5",
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
