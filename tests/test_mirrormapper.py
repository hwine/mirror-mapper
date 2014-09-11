import unittest
import sys

from mirrormapper import main

from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# direct from http://stackoverflow.com/questions/18651705/argparse-unit-tests-suppress-the-help-message
@contextmanager
def capture_sys_output():
    caputure_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = caputure_out, capture_err
        yield caputure_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err



class MainTestCase(unittest.TestCase):
    def test_main(self):
        """ no args == error """
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                main()
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertNotEqual(len(stderr.getvalue()), 0)

    def test_main_help(self):
        """ -h & --help work """
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                main(['-h'])
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(stderr.getvalue(), '')
        self.assertNotEqual(len(stdout.getvalue()), 0)

        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                main(['--help'])
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(stderr.getvalue(), '')
        self.assertNotEqual(len(stdout.getvalue()), 0)


if __name__ == '__main__':
    unittest.main()
