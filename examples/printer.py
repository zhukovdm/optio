#!/usr/bin/env python3


from __future__ import annotations
from optio import *


class Printer:
    def __init__(self, printer: str) -> Printer:
        self.__printer = printer
    
    def __str__(self):
        return 'Printer ' + self.__printer


def accept_ints(params: list[str]) -> list[int]:
    return [ int(p) for p in params ]


def accept_join(params: list[str]) -> str:
    return '/'.join(params)


def accept_kind(params: list[str]) -> Printer:
    return Printer(params[0])


parser = OptioParser()\
    .add_option(views={'-c', '--copy'}, acceptor=accept_ints, count=(1, None), required=True, short_info='', long_info='')\
    .add_option(views={'-p', '--path'}, acceptor=accept_join, count=(1, None), required=True, short_info='', long_info='')\
    .add_option(views={'-f', '--file'},                       count=(1, None), required=True, short_info='', long_info='')\
    .add_option(views={'-k', '--kind'}, acceptor=accept_kind, count=(1,    1), required=True, short_info='', long_info='')

input = ' -c1 2 --file=1.txt 2.txt -p ~ path to folder --kind=xerox -- -a '

parser.parse(input)

print(parser.try_get_option('-c').value())
print(parser.try_get_option('-p').value())
print(parser.try_get_option('-f').value())
print(parser.try_get_option('-k').value())
print(parser.plain_args())

'''
Possible output:

[1, 2]
~/path/to/folder
['1.txt', '2.txt']
Printer xerox
['-a']
'''
