#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging
import sys

from mirrormapper.mapurl import get_mirror_name
from mirrormapper.mapurl import MirrorMapperException

logger = logging.getLogger(__name__)


def parse_args(argv=()):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help='upstream git url', default=None,
                        nargs='+')
    parser.add_argument("--prefix", default=None,
                        help='department prefix to use')
    parser.add_argument("--unique", help='see if already mirrored',
                        default=False, action='store_true')
    parser.add_argument("--verify", help='verify URL is accessible git repo',
                        action='store_true', default=False)
    args = parser.parse_args(argv)
    if args.verify or args.unique:
        parser.error("Not implemented yet")
    if args.prefix and not args.prefix.endswith('-'):
        parser.error("prefix must end with dash, if supplied")
    return args


def main(argv=()):
    """
    Args:
        argv (list): List of arguments

    Returns:
        int: Unix style exit code

    Output the proper git.mozilla.org URL for the given upstream repository.
    """

    args = parse_args(argv)
    for u in args.url:
        if False and u[-1] == '/':
            # get explicit with repo type
            u = u[:-1] + '.git'
        try:
            mapped_url = get_mirror_name(u, args.prefix)
            print("%s -> %s" % (u, mapped_url))
        except MirrorMapperException as e:
            logger.warning("{} on {}".format(' '.join(e.args), u))
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    sys.exit(main(sys.argv))
