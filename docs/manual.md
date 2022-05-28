# optio

This document provides an overview of the `optio` library.

# Entities

The library defines two types of entities, `Option` and `Parser`. Further,
we briefly describe classes. More detailed information is available in
a specialized chapters.

## Class Option

Constructor of the class `Option` is used for configuring `Parser` instances.
It takes five arguments in total.

```python
def __init__(views:self, views: set[str], acceptor: function = lambda id: id,
    required: bool = True, short_info: str = "", long_info: str = "") -> Option:
```

`views` are represented by a set of synonyms associated with the `Option`,
such as `{ "-a", "-b", "--option" }`. During parsing, the `Option` will be
identified by any synonym from the set. Different `Options` cannot have
common `views`.

Parsing options with list of parameters might be necessary. However, requirements
on such list could vary and any parsing strategy could hardly cover all use cases.
Therefore, we use another approach.

Constructor parameter `acceptor` is any function taking list of parsed parameters
as an argument. `acceptor` could return any object, which will be stored as a
private member of `Option` instance and could be retrieved later upon calling
method `.params()`.

`required` options shall appear within the arguments. Otherwise, violation is
reported via exception.

Both `short_info` and `long_info` could be used for documentation.

`Option` instances have `.views()`, `.params()` , `.required()`, `.found()`,
`.short_info()`, `.long_info()`, `.accept(params: list[str])`,
`.has_view(view: str)`, `.self_check()` and `.reset()`.

## Class Parser

Essentially `Parser` is a bag of `Options`, new options are added via
constructor or by calling `.add_option()`. Each `Option` is checked whether
is not in conflict with already added.

Once all options are added, we should call
`.parse_args(args: list[str], conflicts: list[str] = [])`. Conflicts are sets
of `views` not allowed to appear in the same argument structure. Once parsing
is finished, we may query structure by calling `.options()`, `.plain_args()`,
`.add_option(in_opt: Option)`, `.try_get_option(view: str)`, and `.parse_args(...)`
methods.

## Use cases

```python
#!/usr/bin/env python3


from __future__ import annotations
from parse import Option, Parser


def int_acceptor(params: list[str] = []) -> list[int]:
    return [ int(param) for param in params ]


option = Option(
    views={ "-a", "-b", "-c", "--help" },
    acceptor=int_acceptor,
    required=True,
    short_info="short info",
    long_info="long info"
)

option.accept([ "42" ])
print(option)
print(option.params())


parser = Parser([ Option(views={ "-f", "--file" }) ])\
    .add_option(Option(views={ "-h", "--help" }))\
    .add_option(Option(views={ "-s", "--secret" }, required=False))

parser.parse_args([ "--help", "--file", "notes.txt", "--", "plain"])

print(parser.try_get_option("-s").found())
print(parser.try_get_option("-f").params())
print(parser.plain_args())

# repeated parsing with the same args is idempotent, strings on input are allowed.
parser.parse_args([ "--help \t --file \n notes.txt \r -- \t\n plain"])
```

Possible output:

```console
Option {'-a', '-b', '-c', '--help'}
[42]
False
['notes.txt']
['plain']
```
