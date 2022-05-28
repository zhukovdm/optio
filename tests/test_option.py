#!/usr/bin/env python3


import unittest
from optio import Option


def int_acceptor(params: list[str]) -> list[int]:
    return [ int(param) for param in params ]


class TestsOptionCtor(unittest.TestCase):

    def test_WithEmptyViews(self):
        with self.assertRaises(ValueError): Option(views={  })

    def test_WithBadViews(self):
        for view in [ "", "-", "1", "a", "-1", "-ab", "--", "--a?", "--1" ]:
            with self.subTest(view=view):
                with self.assertRaises(ValueError):
                    Option(views={ view })

    def test_WithBadAcceptor(self):
        with self.assertRaises(ValueError):
            Option({ "-h" }, acceptor=None)

    def test_WithBadRequired(self):
        with self.assertRaises(ValueError):
            Option({ "-h" }, required=None)

    def test_WithBadInfos(self):
        for info in [ None, 1 ]:
            with self.subTest(info=info):
                with self.assertRaises(ValueError):
                    Option({ "-h" }, short_info=info)
            with self.subTest(info=info):
                with self.assertRaises(ValueError):
                    Option({ "-h" }, long_info=info)

    def test_WithShortViewAndAcceptor(self):
        Option({ "-h" }, int_acceptor)

    def test_WithLongViewAndAcceptor(self):
        Option({ "--help" }, int_acceptor)

    def test_DefaultAcceptor(self):
        option = Option({ "-h" })
        option.accept([ 42, "1" ])
        self.assertListEqual(option.params(), [ 42, "1" ])

    def test_CustomAcceptorSuccess(self):
        option = Option({ "-h" }, int_acceptor)
        option.accept([ "42" ])
        self.assertListEqual(option.params(), [ 42 ])

    def test_CustomAcceptorFail(self):
        with self.assertRaises(ValueError):
            Option({ "-h" }, int_acceptor).accept([ "?" ])

    def test_RepeatedAcceptCall(self):
        option = Option({ "-h" }, int_acceptor)
        option.accept([ "1" ])
        with self.assertRaises(ValueError):
            option.accept([ "1" ])

    def test_ResetAfterAccept(self):
        option = Option({ "-h" }, int_acceptor)
        option.accept([ "1" ])
        option.reset()
        self.assertTrue(not option.found() and option.params() == None)

    def test_RepeatedAcceptCallAfterReset(self):
        option = Option({ "-h" }, int_acceptor)
        option.accept([ "1" ])
        option.reset()
        option.accept([ "2" ])
        self.assertListEqual(option.params(), [ 2 ])
        self.assertTrue(option.found())

    def test_StrMagicMethod(self):
        self.assertEqual(str(Option(views={ "-h" })), "Option {'-h'}")

    def test_Views(self):
        self.assertEqual(Option(views={ "-h", "--help" }).views(), { "-h", "--help" })

    def test_Required(self):
        self.assertTrue(Option(views={ "-h" }, required=True).required())

    def test_Found(self):
        option = Option(views={ "-h" })
        option.accept([ "-h" ])
        self.assertTrue(option.found())

    def test_HasView(self):
        self.assertTrue(Option(views={ "-h" }).has_view("-h"))

    def test_HasNotView(self):
        self.assertFalse(Option(views={ "-h" }).has_view("-a"))

    def test_SelfCheckRequiredNotFound(self):
        with self.assertRaises(RuntimeError):
            Option({ "-a", "-h" }, required=True).self_check()

    def test_SelfCheckRequiredAndFound(self):
        Option({ "-a" }, required=True).accept([ "-a" ]).self_check()
