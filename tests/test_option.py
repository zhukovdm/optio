#!/usr/bin/env python3


from collections import deque
import unittest
from optio.parser import _Option


def accept_ints(params: list[str]) -> list[int]:
    return [int(p) for p in params]


class TestsOptionCtor(unittest.TestCase):

    def test_NonSetViews(self):
        with self.assertRaises(ValueError):
            _Option(v=None)

    def test_EmptyViews(self):
        with self.assertRaises(ValueError):
            _Option(v={})

    def test_MalformedViews(self):
        for view in ['', '-', '1', 'a', '-1', '-ab', '--', '--a?', '--1', 42 ]:
            with self.subTest(view=view):
                with self.assertRaises(ValueError): _Option(v={view})

    def test_NonCallableAcceptor(self):
        with self.assertRaises(ValueError):
            _Option(v={'-h'}, a=None)

    def test_NonTupleCount(self):
        with self.assertRaises(ValueError):
            _Option({'-h'}, c=1)

    def test_BadLengthCount(self):
        with self.assertRaises(ValueError):
            _Option({'-h'}, c=(1, 2, 3))

    def test_InverseIntervalCount(self):
        with self.assertRaises(ValueError):
            _Option({'-h'}, c=(2, 1))

    def test_NonIntegerCount(self):
        with self.assertRaises(ValueError):
            _Option({'-h'}, c=('1', 2))

    def test_MalformedRequired(self):
        with self.assertRaises(ValueError):
            _Option({'-h'}, r=None)

    def test_MalformedInfos(self):

        for info in [ None, 1 ]:

            with self.subTest(info=info):
                with self.assertRaises(ValueError):
                    _Option({'-h'}, s=info)

            with self.subTest(info=info):
                with self.assertRaises(ValueError):
                    _Option({'-h'}, l=info)

    def test_ShortViewAndAcceptor(self):
        _Option({'-h'}, accept_ints)

    def test_LongViewAndAcceptor(self):
        _Option({'--help'}, accept_ints)

class TestsOptionStr(unittest.TestCase):

    def test_Str(self):
        self.assertEqual(str(_Option(v={'-h'})), 'Option {\'-h\'}')

class TestsOptionViews(unittest.TestCase):

    def test_ViewsGetter(self):
        self.assertEqual(_Option(v={'-c', '-h'}).views(), {'-c', '-h'})

class TestsOptionHas(unittest.TestCase):

    def test_HasView(self):
        self.assertTrue(_Option(v={'-c', '-h'}).has('-h'))

    def test_HasNotView(self):
        self.assertFalse(_Option(v={'-h'}).has('-c'))

class TestsOptionValue(unittest.TestCase):

    def test_DefaultValue(self):
        self.assertIsNone(_Option({'-h'}).value())

    def test_GatheredValue(self):
        option = _Option({'-h'}, accept_ints).gather(deque(['1', '2']))
        self.assertListEqual(option.value(), ['1', '2'])

    def test_AcceptedValue(self):
        option = _Option({'-h'}, accept_ints).gather(deque(['1', '2'])).accept()
        self.assertListEqual(option.value(), [1, 2])

class TestOptionInfo(unittest.TestCase):

    def test_GetShortInfo(self):
        self.assertEqual(_Option({'-h'}, s='s').short_info(), 's')

    def test_GetLongInfo(self):
        self.assertEqual(_Option({'-h'}, s='l').short_info(), 'l')

class TestOptionIsFlag(unittest.TestCase):

    def test_DefaultIsFlag(self):
        self.assertFalse(_Option({'-h'}).is_flag())

    def test_IsNotFlag(self):
        self.assertFalse(_Option({'-h'}, c=(1, None)).is_flag())

    def test_IsFlag(self):
        self.assertTrue(_Option({'-h'}, c=(0, 0)).is_flag())

class TestOptionIsRequired(unittest.TestCase):

    def test_DefaultIsRequired(self):
        self.assertTrue(_Option({'-a'}).is_required())

    def test_IsNotRequired(self):
        self.assertFalse(_Option({'-v'}, r=False).is_required())

class TestOptionIsFound(unittest.TestCase):

    def test_IsNotFound(self):
        self.assertFalse(_Option({'-a'}).is_found())

    def test_IsFound(self):
        self.assertTrue(_Option({'-a'}).gather(deque(['1'])).is_found())

class TestOptionGather(unittest.TestCase):

    def test_EmptyDeque(self):
        self.assertListEqual(_Option({'-a'}).gather(deque([])).value(), [])

    def test_FullRemainRest(self):
        d = deque(['1', '2', '3'])
        o = _Option({'-a'}, c=(1, 2)).gather(d)
        self.assertListEqual(o.value(), ['1', '2'])
        self.assertListEqual(list(d), ['3'])

    def test_BelowLowerBound(self):
        self.assertListEqual(_Option({'-a'}, c=(3, None)).gather(deque(['1', '2'])).value(), ['1', '2'])

    def test_HitOption(self):
        d = deque(['1', '-2', '3'])
        o = _Option({'-a'}, c=(1, 2)).gather(d)
        self.assertListEqual(o.value(), ['1'])
        self.assertListEqual(list(d), ['-2', '3'])
    
    def test_SeveralCalls(self):
        self.assertListEqual(_Option({'-a'}).gather(deque(['1'])).gather(deque(['2'])).value(), ['1', '2'])

class TestOptionCheck(unittest.TestCase):

    def test_IsRequiredIsNotFound(self):
        with self.assertRaises(RuntimeError):
            _Option({'-h'}).check()

    def test_IsRequiredIsFound(self):
        _Option({'-h'}).gather(deque(['1'])).check()

    def test_IsFoundLessParams(self):
        with self.assertRaises(RuntimeError):
            _Option({'-h'}, c=(2, None)).gather(deque(['1'])).check()

class TestOptionAccept(unittest.TestCase):

    def test_DefaultAcceptor(self):
        option = _Option({'-h'}).gather(deque(['42', '1'])).accept()
        self.assertListEqual(option.value(), ['42', '1'])

    def test_CustomAcceptorSuccess(self):
        option = _Option({'-h'}, accept_ints).gather(deque(['42'])).accept()
        self.assertListEqual(option.value(), [42])

    def test_CustomAcceptorFail(self):
        with self.assertRaises(ValueError):
            _Option({'-h'}, accept_ints).gather(deque(['?'])).accept()

class TestOptionReset(unittest.TestCase):

    def test_ValueAfterReset(self):
        self.assertIsNone(_Option({'-a'}, accept_ints).gather(deque(['1'])).accept().reset().value())

    def test_IsFoundAfterReset(self):
        self.assertFalse(_Option({'-a'}, accept_ints).gather(deque(['1'])).accept().reset().is_found())
