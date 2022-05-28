#!/usr/bin/env python3


import unittest
from optio import Option, Parser


def int_acceptor(params: list[str]) -> list[int]:
    return [ int(param) for param in params ]


def ignore_acceptor(params: list[str]) -> None:
    return None


def text_files_acceptor(params: list[str]):
    for p in params:
        if not p.endswith('.txt'):
            raise Exception('Output file must be .txt file')


class TestsParser(unittest.TestCase):

    def test_AddOptionTwice(self):
        option = Option({ "-h", "--help" })
        with self.assertRaises(RuntimeError):
            Parser().add_option(option).add_option(option)

    def test_AddOptionRepeatedShortView(self):
        option1 = Option({ "-h", "-p", "--help" })
        option2 = Option({ "-p", "-r", "--print" })
        with self.assertRaises(RuntimeError):
            Parser().add_option(option1).add_option(option2)

    def test_AddOptionRepeatedLongView(self):
        option1 = Option({ "-h", "--help", "--dup" })
        option2 = Option({ "-p", "--print", "--dup" })
        with self.assertRaises(Exception):
            Parser().add_option(option1).add_option(option2)

    def test_CtorAddOptionTwice(self):
        option = Option({ "-h", "--help" })
        with self.assertRaises(RuntimeError):
            Parser([ option, option ])

    def test_CtorAddOptionRepeatedShortView(self):
        option1 = Option({ "-h", "-p", "--help" })
        option2 = Option({ "-p", "-r", "--print" })
        with self.assertRaises(RuntimeError):
            Parser([ option1, option2 ])

    def test_CtorAddOptionRepeatedLongView(self):
        option1 = Option({ "-h", "--help", "--dup" })
        option2 = Option({ "-p", "--print", "--dup" })
        with self.assertRaises(Exception):
            Parser([ option1, option2 ])

    def test_ParseArgsUnknownShortView(self):
        with self.assertRaises(Exception):
            Parser().parse_args([ "-u" ])

    def test_ParseArgsUnknownLongView(self):
        with self.assertRaises(Exception):
            Parser().parse_args([ "--unknown" ])

    def test_TryGetOptionBeforeParsing(self):
        self.assertEqual(Parser().try_get_option("-h"), None)

    def test_TryGetShortOptionAfterParsing(self):
        option = Parser([ Option({ "-h", "--help" }) ])\
            .parse_args([ "-h" ])\
            .try_get_option("-h")
        self.assertEqual(isinstance(option,Option), option.found())

    def test_TryGetLongOptionAfterParsing(self):
        option = Parser([ Option({ "-h", "--help" }) ])\
            .parse_args([ "--help" ])\
            .try_get_option("--help")
        self.assertEqual(isinstance(option,Option), option.found())

    def test_TryGetWrongOptionAfterParsing(self):
        option = Parser([ Option({ "-h", "--help" }) ])\
            .parse_args([ "--help" ])\
            .try_get_option("-help")
        self.assertIsNone(option)

    def test_TryGetShortSynonymShortOption(self):
        option = Parser([ Option({ "-h", "-a" }) ])\
            .parse_args([ "-h", "arg1", "arg2"])\
            .try_get_option("-a")
        self.assertTrue(option.found())

    def test_TryGetLongSynonymShortOption(self):
        option = Parser([ Option({ "-h", "--all" }) ])\
            .parse_args([ "-h", "arg1", "arg2"])\
            .try_get_option("--all")
        self.assertTrue(option.found())

    def test_TryGetShortSynonymLongOption(self):
        option = Parser([ Option({ "-h", "--all" }) ])\
            .parse_args([ "--all", "arg1", "arg2"])\
            .try_get_option("-h")
        self.assertTrue(option.found())

    def test_TryGetLongSynonymLongOption(self):
        option = Parser([ Option({ "--help", "--all" }) ])\
            .parse_args([ "--all", "arg1", "arg2"])\
            .try_get_option("--help")
        self.assertTrue(option.found())

    def test_ShortOptionAfterDelimiterNotFound(self):
        option = Parser([ Option({ "-h", "--help" }, required=False) ])\
            .parse_args([ "--", "-h" ])\
            .try_get_option("-h")
        self.assertFalse(option.found())

    def test_LongOptionAfterDelimiterNotFound(self):
        option = Parser([ Option({ "-h", "--help" }, required=False) ])\
            .parse_args([ "--", "--help" ])\
            .try_get_option("--help")
        self.assertFalse(option.found())

    def test_GetPlainArgs(self):
        args = Parser()\
            .parse_args([ "plain", "arguments" ])\
            .plain_args()
        self.assertEqual(args, [ "plain", "arguments" ])

    def test_GetShortViewAsPlainArgument(self):
        args = Parser()\
            .add_option(Option({ "-h" }, required=False))\
            .parse_args([ "--", "-h" ])\
            .plain_args()
        self.assertEqual(args, [ "-h" ])

    def test_GetLongViewAsPlainArgument(self):
        args = Parser()\
            .add_option(Option({ "--help" }, required=False))\
            .parse_args([ "--", "--help" ])\
            .plain_args()
        self.assertEqual(args, [ "--help" ])

    def test_GetPlainArgumentsStartsWithPlain(self):
        args = Parser()\
            .add_option(Option({ "-h" }, required=False))\
            .add_option(Option({ "--help" }, required=False))\
            .parse_args([ "plain", "-h", "--help" ])\
            .plain_args()
        self.assertEqual(args, [ "plain", "-h", "--help" ])

    def test_ParseShortViewWithParamsDefaultAcceptor(self):
        params = Parser()\
            .add_option(Option({ "-a" }, required=False))\
            .parse_args([ "-a", "1" ])\
            .try_get_option("-a")\
            .params()
        self.assertListEqual(params, [ "1" ])

    def test_ParseShortViewWithParamsIntAcceptor(self):
        params = Parser()\
            .add_option(Option({ "-a" }, int_acceptor, False))\
            .parse_args([ "-a", "1" ])\
            .try_get_option("-a")\
            .params()
        self.assertListEqual(params, [ 1 ])

    def test_OptionSelfCheckRequiredNotFound(self):
        parser = Parser()\
            .add_option(Option({ "-a" }))\
            .add_option(Option({ "-b" }))
        with self.assertRaises(RuntimeError):
            parser.parse_args([ "-b" ])

    def test_ParseParamsWithIgnoringAcceptor(self):
        params = Parser()\
            .add_option(Option({ "-h" }, ignore_acceptor))\
            .parse_args([ "-h", "10" ])\
            .try_get_option("-h")\
            .params()
        self.assertIsNone(params)

    def test_ParseBadShortView(self):
        with self.assertRaises(ValueError):
            Parser()\
                .add_option(Option({ "-a" }))\
                .parse_args([ "-a", "-?" ])

    def test_ParseNonExistentView(self):
        with self.assertRaises(ValueError):
            Parser()\
                .add_option(Option({ "-a" }))\
                .parse_args([ "-b" ])

    def test_ParseStringOnInput(self):
        parser = Parser()\
            .add_option(Option({ "-a" }))\
            .add_option(Option({ "--memset" }))\
            .parse_args("  \t\t -a \t \r --memset \n\n  ")
        self.assertTrue(parser.try_get_option("-a").found()\
                    and parser.try_get_option("--memset").found())

    def test_ParseConflictPair(self):
        with self.assertRaises(ValueError):
            Parser()\
                .add_option(Option({ "-a" }))\
                .add_option(Option({ "-b" }))\
                .parse_args(args=[ "-a", "-b" ], conflicts=[{ "-a", "-b" }])

    def test_ParseConflictTriple(self):
        with self.assertRaises(ValueError):
            Parser()\
                .add_option(Option({ "-a" }))\
                .add_option(Option({ "-b" }))\
                .add_option(Option({ "-c" }))\
                .parse_args(args=[ "-a", "-b", "-c" ], conflicts=[{ "-a", "-b", "-c" }])

    def test_ParseHasOptionCorrectArgs(self):
        option = Parser()\
            .add_option(Option({'-v', '--verbose'}))\
            .add_option(Option({'-o', '--output'}, text_files_acceptor))\
            .parse_args(['-v', '--output', 'file.txt'])\
            .try_get_option('-v')
        self.assertEqual(isinstance(option,Option), option.found())

    def test_ParsingIsIdempotent(self):
        parser = Parser()\
            .add_option(Option({ '-v', '--version' }))\
            .add_option(Option({ '-h', '--help' }))
        parser.parse_args(['-v', '1', '-h', '2'])
        self.assertListEqual(parser.try_get_option('--version').params(), ['1'])
        parser.parse_args(['-v', '1', '-h', '2'])
        self.assertListEqual(parser.try_get_option('--help').params(), ['2'])

    def test_GetDefaultParams(self):
        parser = Parser()\
            .add_option(Option({ '-v' }))
        self.assertEqual(parser.try_get_option('-v').params(), None)
