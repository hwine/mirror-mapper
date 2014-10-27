from __future__ import print_function
import unittest
import sys
import os

from mirrormapper.__main__ import main
from mirrormapper import get_mirror_name, MirrorMapperException


from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


# direct from
# http://stackoverflow.com/questions/18651705/argparse-unit-tests-suppress-the-help-message
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
                main(['prog', '-h'])
        self.assertEqual(stderr.getvalue(), '')
        self.assertEqual(cm.exception.code, 0)
        self.assertNotEqual(len(stdout.getvalue()), 0)

        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                main(['prog', '--help'])
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(stderr.getvalue(), '')
        self.assertNotEqual(len(stdout.getvalue()), 0)


class TestExistingMappings(unittest.TestCase):
    def _no_match(self, desired, generated):
        """ return true if they "match" after corner cases identified
        """
        git_prefix = 'git+ssh://git.m.o/'
        http_prefix = 'https://git.mozilla.org/'
        # all the special cases
        if ((desired.startswith(git_prefix) and
             generated.startswith(http_prefix))):
            desired = desired[len(git_prefix):]
            generated = generated[len(http_prefix):]
        if not desired.endswith('.git'):
            desired += '.git'
        matching = desired == generated
        return not matching

    def test_existing(self):
        """ Check all mappings in test data file"""
        everything_matches = True
        error_list = []
        line_count = good_count = skipped_count = exception_count = \
            no_match_count = 0
        test_data_file = os.path.join(os.path.dirname(__file__),
                                 'current_mappings.txt')
        with open(test_data_file) as test_data:
            for line in test_data.readlines():
                line_count += 1
                if '//hg.mozilla.org/' in line.split()[0]:
                    # we want mapper to fail for hg.m.o -- all of those mappings
                    # must be hand edited at this point, so don't bother testing
                    skipped_count += 1
                    # TODO: should check exception thrown
                    continue
                upstream, junk, real_downstream = line.split()
                try:
                    calc_downstream = get_mirror_name(upstream)
                    if self._no_match(real_downstream, calc_downstream):
                        no_match_count += 1
                        everything_matches = False
                        error_list.append((upstream, real_downstream,
                                        calc_downstream))
                    else:
                        good_count += 1
                except MirrorMapperException as e:
                    exception_count += 1
                    everything_matches = False
                    error_list.append((upstream, real_downstream, str(type(e))))
        if not everything_matches:
            for e in error_list:
                print( ' '.join(map(str, e)))
            text = """
                %5d cases examined
                %5d skipped as out of scope for mapper
                %5d good conversions

                %5d refuse to convert (exception)
                %5d bad conversions
                 ----
                %5d total errors
            """ % (line_count, skipped_count, good_count, exception_count,
                   no_match_count, len(error_list))
            self.fail(text)


if __name__ == '__main__':
    unittest.main()
