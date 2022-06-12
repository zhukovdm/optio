`optio` is a simple, yet configurable command-line argument parser.

# Definitions

Let us define entities recognized by the parser.

`short view` is a sequence of chars starting with `-` and followed by a letter,
e.g. `-v`.

`long view` is a sequence of chars starting with `--` followed by a letter
followed by a sequence (maybe empty) of alphanumeric chars, e.g. `--v3rb0se`.

`view` is either a `short view` or `long view`. This implies a valid `view`
starts with `-`. Any `view` shall be associated with some `option`.

`parameter` is a string token followed after a view associated with an option.

`option` is a program abstraction used for parser configuration.

`plain argument` is any string token not beginning with `-` if delimiter has
not been encountered, or any string token after delimiter.

`delimiter` is a `--` sequence, after which only `plain arguments` could be
encountered.

# OptioParser

`OptioParser` is a central parsing unit configurable by `.add_option(..)` method.
Only this class is imported upon `from optio import *`.

Internally, parsing is divided into the following phases.

- Configure expected options by calling `.add_option()` with appropriate parameters.
  - `views` is a set of acceptable short and long synonyms, e.g. `-h` or `--help`.
    Two different options must not have `views` in common, collision is reported
    via exception.
  - `acceptor` is a __function__ accepting gathered parameters, e.g. `-h 1 2 3`.
    - `acceptor` is provided by the user of the library to ensure specific behavior.
    - `acceptor` could return any object or do any action, further interaction with
      such object is a responsibility of the user.
  - `count` is a tuple containing two items, `parameters at least` and `parameters at most`.
    - `(0, 0)` is a parameterless flag,
    - `(1, None)` is an option with at least one parameter and __without__ upper bound.
    - `(2, 4)` is an option with any number of parameters from interval `[2, 3, 4]`.
    - `(None, None)` is an option with unbounded parameter count, any number from `0` to `Inf`.
  - `required` is a flag signalizing if an option shall appear in the arguments.
  - `short_info` is a concise description of an option.
  - `long_info` is a long piece of text describing an option.

```python
class OptioParser:
    def add_option(self, views: set[str] = {}, acceptor: function = lambda id: id,
        count: tuple[int | None, int | None] = (1, None), required: bool = True,
        short_info: str = '', long_info: str = '') -> OptioParser:
```

- Recognize views of the configured options and gather parameters into lists.
  Gathering is eager towards option parameters. Consider option `-c` configured
  with count `(1, 2)` and input `-c 1 2 3`. Only the last parameter will be
  recognized as plain argument, other will be recognized as parameters of `-c`.
  In other words, options consume as many parameters as it possibly could.

- Check if configured constraints are fulfilled (parameter count, required/found).

- Accept parameters by the default or custom acceptor. After this transformed
  are converted into option `value`.

For the user, all four phases are hidden in `.parse(..)` call.

# Examples

```python
#!/bin/

import sys
from optio import *

parser = OptioParser()\
    .add_option({'-a'}, count=(1, 1))\
    .add_option({'-b'}, count=(0, 0))\
    .add_option({'-c'}, count=(None, None))\
    .add_option({'-d'})\
    .add_option({'--file'})\
    .parse(sys.args[1:])
```

```console
./program -a 1 2 -bc 3 4 -d5 --file 1.txt 2.txt --file=3.txt -- -h
```

Considering parser and arguments mentioned above, the following entities are
recognized:

- `-a` option with exactly one parameter `1`.
- `-b` parameterless (flag) option.
- `-c` option with unbound amount of parameters, currently `3` and `4`.
- `-d` option with at least one parameter, currently `5`.
- `--file` with at least one parameter, currently `[1.txt, 2.txt, 3.txt]`.
- plain arguments are represented by the list `['2', '-h']`.

Other more detailed examples can be found at
[optio/examples](https://github.com/zhukovdm/optio/tree/main/examples). To run
`printer.py`, clone the repository and execute `python3 -m examples.printer`
from the project root folder.
