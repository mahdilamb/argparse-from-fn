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
        fn2argparse.converter(blah).parse_args(
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
