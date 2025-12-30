import argparse
import unittest
from unittest import mock

from idss.__main__ import main


class TestMain(unittest.TestCase):
    def test_main(self):
        args = argparse.Namespace(no_act=True)
        with mock.patch(
            "argparse.ArgumentParser.parse_args", return_value=args
        ):
            ret = main()
        self.assertEqual(ret, 0)
