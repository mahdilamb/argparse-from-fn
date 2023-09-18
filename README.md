# ArgParser from a function

Basic implementation of a package that will generate an argument parser from a function generation.

Note that it does not support using user-defined types.

## Installation

```shell

pip install -e git+https://github.com/mahdilamb/argparse-from-fn

```

## Usage

```python

import fn2argparse


def some_function(a:int, b:str,*, k="asas"):
    ...
parser = fn2argparse.convert(fn)
args = parser.parse_args()


```
