#!/usr/bin/env python3


import unittest
from optio import *


def accept_ints(params: list[str]) -> list[int]:
    return [ int(p) for p in params ]


def accept_ignore(_: list[str]) -> None:
    return None


def accept_txt_files(params: list[str]) -> None:
    for p in params:
        if not p.endswith('.txt'):
            raise Exception('Output file must be .txt file')
    return params


class TestsOptioParserOptions(unittest.TestCase):

    def test_Default(self):
        self.assertEqual(OptioParser().options(), [])

    def test_OneItem(self):
        self.assertEqual(OptioParser().add_option({'-v'}).options()[0].views(), {'-v'})

class TestOptioParserPlainArgs(unittest.TestCase):

    def test_Default(self):
        self.assertEqual(OptioParser().plain_args(), [])

    def test_NonEmpty(self):
        self.assertEqual(OptioParser().parse(' x ').plain_args(), ['x'])

    def test_AfterOption(self):
        self.assertEqual(OptioParser().add_option({'-a'}, count=(1, 1)).parse(' -a 1 x ').plain_args(), ['x'])

    def test_BeforeOption(self):
        self.assertEqual(OptioParser().add_option({'-a'}, count=(1, 1)).parse(' x -a 1').plain_args(), ['x'])

    def test_BeforeAfterOption(self):
        self.assertEqual(OptioParser().add_option({'-a'}, count=(1, 1)).parse(' x -a 1 x ').plain_args(), ['x', 'x'])

    def test_EagerOptionGather(self):
        self.assertEqual(OptioParser().add_option({'-a'}).parse(' -a 1 2 ').plain_args(), [])

    def test_SeveralArgs(self):
        self.assertEqual(OptioParser().add_option({'-a'}, required=False).parse(' 1 2 ').plain_args(), ['1', '2'])

    def test_AfterDelimiter(self):
        args = OptioParser()\
            .add_option({'-a'}, required=False)\
            .add_option({'--help'}, required=False)\
            .parse(' -- -a --help x ')\
            .plain_args()
        self.assertListEqual(args, ['-a', '--help', 'x'])

class TestsOptioAddOption(unittest.TestCase):

    def test_AddOptionTwice(self):
        with self.assertRaises(RuntimeError):
            OptioParser().add_option({'-h', '--help'}).add_option({'-h', '--help'})

    def test_AddOptionRepeatedShortView(self):
        with self.assertRaises(RuntimeError):
            OptioParser().add_option({'-h', '-p', '--help'}).add_option({'-p', '-r', '--print'})

    def test_AddOptionRepeatedLongView(self):
        with self.assertRaises(Exception):
            OptioParser().add_option({'-h', '--help', '--dup'}).add_option({'-p', '--print', '--dup'})

    def test_AddSeveralOptions(self):
        self.assertEqual(len(OptioParser().add_option({'-h'}).add_option({'-a'}).options()), 2)

class TestsOptioParserTryGetOption(unittest.TestCase):

    def test_GetExistingOption(self):
        self.assertIsNotNone(OptioParser().add_option({'-h', '-a'}).try_get_option('-a'))

    def test_GetNonExistingOption(self):
        self.assertIsNone(OptioParser().add_option({'-h', '-a'}).try_get_option('-m'))

class TestsOptioParserParse(unittest.TestCase):

    def test_UnknownView(self):
        with self.assertRaises(ValueError):
            OptioParser().parse(['-u'])

    def test_TryGetShortOptionAfterParse(self):
        option = OptioParser()\
            .add_option({'-h'}, count=(0, 0))\
            .parse(' -h ')\
            .try_get_option('-h')
        self.assertIsNotNone(option)

    def test_TryGetLongOptionAfterParsing(self):
        option = OptioParser()\
            .add_option({'--help'}, count=(0, 0))\
            .parse(['--help'])\
            .try_get_option('--help')
        self.assertIsNotNone(option)

    def test_TryGetOptionBySynonym(self):
        option = OptioParser()\
            .add_option({'-a', '-h'}, count=(0, 0))\
            .parse(['-a'])\
            .try_get_option('-h')
        self.assertIsNotNone(option)

    def test_OptionAfterDelimiterNotFound(self):
        option = OptioParser()\
            .add_option({'-h'}, required=False)\
            .parse(['--', '-h'])\
            .try_get_option('-h')
        self.assertFalse(option.is_found())

    def test_ShortViewAsPlainArgument(self):
        args = OptioParser()\
            .add_option({'-h'}, required=False)\
            .parse(['--', '-h'])\
            .plain_args()
        self.assertEqual(args, ['-h'])

    def test_ParseWithDefaultAcceptor(self):
        value = OptioParser()\
            .add_option({'-a'}, required=False)\
            .parse(['-a', '1'])\
            .try_get_option('-a')\
            .value()
        self.assertListEqual(value, ['1'])

    def test_ParseWithIntAcceptor(self):
        value = OptioParser()\
            .add_option({'-a'}, accept_ints)\
            .parse(['-a', '1'])\
            .try_get_option('-a')\
            .value()
        self.assertListEqual(value, [1])

    def test_IsRequiredIsNotFound(self):
        with self.assertRaises(RuntimeError):
            OptioParser()\
                .add_option({'-a'})\
                .add_option({'-b'})\
                .parse(['-b'])

    def test_CondensedShortOptions(self):
        parser = OptioParser()\
            .add_option({'-a'}, count=(0, 0))\
            .add_option({'-b'}, count=(0, 0))\
            .add_option({'-c'}, count=(0, 0))\
            .parse('-abc')
        self.assertTrue(parser.try_get_option('-a').is_found() and\
            parser.try_get_option('-b').is_found() and\
            parser.try_get_option('-c').is_found())

    def test_ShortOptionWithParameter(self):
        value = OptioParser()\
            .add_option({'-a'}, accept_ints)\
            .parse('-a1')\
            .try_get_option('-a')\
            .value()
        self.assertListEqual(value, [1])

    def test_ShortParameterlessOptionThenParametrizedOption(self):
        value = OptioParser()\
            .add_option({'-a'}, count=(0, 0))\
            .add_option({'-b'})\
            .parse('-ab1')\
            .try_get_option('-b')\
            .value()
        self.assertListEqual(value, ['1'])

    def test_LongOptionWithoutEquality(self):
        value = OptioParser()\
            .add_option({'-f', '--file'}, accept_ints)\
            .parse(' --file 1 2 3 ')\
            .try_get_option('-f')\
            .value()
        self.assertListEqual(value, [1, 2, 3])

    def test_LongOptionWithEquality(self):
        value = OptioParser()\
            .add_option({'-f', '--file'}, accept_ints)\
            .parse(' --file=1 2 3 ')\
            .try_get_option('-f')\
            .value()
        self.assertListEqual(value, [1, 2, 3])

    def test_LongOptionWithRepeatedEquality(self):
        value = OptioParser()\
            .add_option({'-f', '--file'})\
            .parse(' --file=1=2=3 ')\
            .try_get_option('-f')\
            .value()
        self.assertListEqual(value, ['1=2=3'])

    def test_ParameterlessLongOptionWithEquality(self):
        value = OptioParser()\
            .add_option({'-f', '--file'}, count=(None, None))\
            .parse(' --file= ')\
            .try_get_option('-f')\
            .value()
        self.assertListEqual(value, [])

    def test_InputWithWhiteChars(self):
        parser = OptioParser()\
            .add_option({'-m'}, count=(0, 0))\
            .add_option({'--memset'}, count=(0, 0))\
            .parse("  \t \t -m \t \r --memset \n \n  ")
        self.assertTrue(parser.try_get_option('-m').is_found()\
                    and parser.try_get_option('--memset').is_found())

    def test_RepeatedParsingFlags(self):
        parser = OptioParser()\
            .add_option({'-a'}, count=(0, 0), required=False)\
            .add_option({'-b'}, count=(0, 0), required=False)

        self.assertFalse(parser.parse('-a').parse('-b').try_get_option('-a').is_found())

    def test_RepeatedParsingWithParameters(self):
        parser = OptioParser()\
            .add_option({'-a'}, count=(1, 1), required=False)\
            .add_option({'-b'}, count=(1, 1), required=False)

        self.assertEqual(parser.parse('-a1').parse('-b2').try_get_option('-a').value(), None)

    def test_ParseConflictSingle(self):
        with self.assertRaises(ValueError):
            OptioParser()\
                .add_option({'-a', '-b'}, count=(0, 0))\
                .parse(args=['-a', '-b'], conflicts=[{'-a', '-b'}])

    def test_ParseConflictPair(self):
        with self.assertRaises(ValueError):
            OptioParser()\
                .add_option({'-a'}, count=(0, 0))\
                .add_option({'-b'}, count=(0, 0))\
                .parse(args=['-a', '-b'], conflicts=[{'-a', '-b'}])

    def test_ParseConflictTriple(self):
        with self.assertRaises(ValueError):
            OptioParser()\
                .add_option({'-a'}, count=(0, 0))\
                .add_option({'-b'}, count=(0, 0))\
                .add_option({'-c'}, count=(0, 0))\
                .parse(args=['-a', '-b', '-c'], conflicts=[{'-a', '-b', '-c'}])

    def test_ParseConflictSynonyms(self):
        with self.assertRaises(ValueError):
            OptioParser()\
                .add_option({'-a', '-b'}, count=(0, 0))\
                .add_option({'-c', '-d'}, count=(0, 0))\
                .parse(args=['-a', '-c'], conflicts=[{'-b', '-d'}])
