#!/usr/bin/env python3


from __future__ import annotations
from collections import deque
import itertools
import re
import sys


class _Option:

    @classmethod
    def is_single_short_view(cls, view: str) -> bool:

        return len(view) == 2 and view[0] == '-' and view[1].isalpha()

    @classmethod
    def is_single_long_view(cls, view: str) -> bool:

        result = len(view) >= 3 and view.startswith('--') and view[2].isalpha()

        for char in view[3:]:
            result = result and char.isalnum()

        return result

    def __verify_views(self) -> None:

        if not isinstance(self.__views, set):
            raise ValueError('Views container is not a set.')

        if len(self.__views) == 0:
            raise ValueError('Views container is empty.')

        for view in self.__views:
            if not isinstance(view, str) or not _Option.is_single_short_view(view) and not _Option.is_single_long_view(view):
                raise ValueError('Malformed view ' + str(view) + '.')

    def __verify_acceptor(self) -> None:

        if not callable(self.__acceptor):
            raise ValueError('Acceptor shall be any callable, e.g. function or functor.')

    def __verify_count(self) -> None:

        if (not isinstance(self.__count, tuple) or len(self.__count) != 2):
            raise ValueError('Count parameter ' + str(self.__count) + ' is malformed.')

        if (self.__count[0] == None): self.__count = (0, self.__count[1])

        if (self.__count[1] == None): self.__count = (self.__count[0], sys.maxsize)

        if not (isinstance(self.__count[0], int) and isinstance(self.__count[1], int)) or \
            self.__count[0] < 0 or self.__count[1] < 0 or self.__count[0] > self.__count[1]:
            raise ValueError('Count tuple ' + str(self.__count) + ' is malformed.')

    def __verify_required(self) -> None:

        if not isinstance(self.__required, bool):
            raise ValueError('Required shall be a boolean.')

    def __verify_infos(self):

        for info in [ self.__short_info, self.__long_info ]:
            if not isinstance(info, str):
                raise ValueError('Info shall be a string.')

    def __verify(self) -> None:

        funcs = [
            self.__verify_views,
            self.__verify_acceptor,
            self.__verify_count,
            self.__verify_required,
            self.__verify_infos
        ]

        for func in funcs:
            func()

    def __init__(self, v: set[str] = {}, a: function = lambda id: id,
        c: tuple[int | None, int | None] = (1, None), r: bool = True,
        s: str = '', l: str = '') -> _Option:

        self.__views = v
        self.__acceptor = a
        self.__count = c
        self.__required = r
        self.__short_info = s
        self.__long_info = l

        self.__value = None
        self.__found = False

        self.__verify()

    def __str__(self) -> str:
        return 'Option ' + str(self.__views)

    def views(self) -> set[str]:
        return self.__views

    def has(self, view: str) -> bool:
        return view in self.__views

    def value(self) -> any:
        return self.__value

    def short_info(self) -> str:
        return self.__short_info

    def long_info(self) -> str:
        return self.__long_info

    def is_flag(self) -> bool:
        return self.__count == (0, 0)

    def is_required(self) -> bool:
        return self.__required

    def is_found(self) -> bool:
        return self.__found

    def gather(self, args: deque) -> _Option:

        self.__found = True
        if self.__value == None: self.__value = []

        while args and len(self.__value) < self.__count[1]:
            arg = args.popleft()

            if arg.startswith('-'):
                args.appendleft(arg)
                break

            self.__value.append(arg)

        return self

    def check(self) -> _Option:

        if self.__required and not self.__found:
            raise RuntimeError(str(self) + ' is required, but not found.')

        if self.__found:
            if not (len(self.__value) >= self.__count[0] and len(self.__value) <= self.__count[1]):
                raise RuntimeError(str(self) + ' gathered invalid number of parameters.')

        return self

    def accept(self) -> _Option:
        self.__value = self.__acceptor(self.__value)
        return self

    def reset(self) -> _Option:
        self.__value = None
        self.__found = False
        return self

class OptioParser:

    def __init__(self) -> OptioParser:
        self.__options = []
        self.__plain_args = []
        self.__view2option = dict()

    def __str__(self) -> str:
        return 'Parser [' + ', '.join(list(map(str, self.__options))) + ']'

    def options(self) -> list[_Option]:
        return self.__options

    def plain_args(self) -> list[str]:
        return self.__plain_args

    def add_option(self, views: set[str] = {}, acceptor: function = lambda id: id,
        count: tuple[int | None, int | None] = (1, None), required: bool = True,
        short_info: str = '', long_info: str = '') -> OptioParser:

        option = _Option(views, acceptor, count, required, short_info, long_info)

        for view in views:
            if view in self.__view2option:
                raise RuntimeError('View ' + str(view) + ' conflicts with ' + str(self.__view2option[view]) + '.')
            self.__view2option[view] = option

        self.__options.append(option)

        return self

    def try_get_option(self, view: str) -> _Option | None:
        return self.__view2option.get(view, None)

    def __get_option(self, view) -> _Option:
        opt = self.try_get_option(view)
        if (opt == None):
            raise ValueError('Unknown view ' + view + '.')
        return opt

    def __gather(self, args: list[str]) -> OptioParser:
        args = deque(args)

        only_plain_args = False

        while args:
            arg = args.popleft()

            if only_plain_args:
                self.__plain_args.append(arg)

            elif arg == '--':
                only_plain_args = True

            else:
                if arg.startswith('-'):

                    opt = None

                    if arg.startswith('--'):
                        pos = arg.find('=')

                        view = arg[:pos]
                        param = arg[pos + 1:]

                        if len(param) > 0: args.appendleft(param)

                        if not _Option.is_single_long_view(view):
                            raise ValueError('Malformed long view ' + view + '.')

                        opt = self.__get_option(view)

                    else:
                        if arg == '-' or not arg[1].isalpha():
                            raise ValueError('Malformed argument ' + arg + '.')

                        if _Option.is_single_short_view(arg):
                            opt = self.__get_option(arg)

                        else:
                            view = arg[:2]
                            suffix = arg[2:]

                            if suffix.startswith('-'):
                                raise ValueError('Malformed argument ' + arg + '.')

                            opt = self.__get_option(view)

                            if opt.is_flag():
                                suffix = '-' + suffix

                            args.appendleft(suffix)

                    opt.gather(args)

                else:
                    self.__plain_args.append(arg)

        return self

    def __check(self) -> OptioParser:
        for opt in self.__options:
            opt.check()

        # TODO: improve conflict finding

        for opt in self.__options:
            for conflict in self.__conflicts:
                for item in conflict:
                    if opt.has(item[0]) and opt.is_found():
                        item[1] = True

        for conflict in self.__conflicts:
            result = True
            for item in conflict:
                result = result and item[1]

            if result:
                raise ValueError('Arguments are in conflict ' + str(conflict))

        return self

    def __accept(self) -> OptioParser:
        for opt in self.__options:
            opt.accept()

        return self

    def parse(self, args: list[str] | str, conflicts: list[set[str]] = []) -> OptioParser:

        for opt in self.__options:
            opt.reset()

        self.__plain_args = []

        if (isinstance(args, str)):
            args = [ args ]

        for arg in args:
            if not isinstance(arg, str):
                raise ValueError('Argument ' + arg + 'is not a string.')

        # split arguments with white spaces and flat list of lists
        args = list(itertools.chain.from_iterable(list(map(lambda arg: [ w for w in re.split(r'[ \r\t\n]+', arg) if w != '' ], args))))

        for i in range(len(conflicts)):
            conflicts[i] = [ [ c, False ] for c in conflicts[i] ]
        self.__conflicts = conflicts

        return self.__gather(args).__check().__accept()
