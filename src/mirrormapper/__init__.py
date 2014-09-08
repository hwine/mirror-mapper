"""
    Given a git repo URL, see if we can map it to a mirror name
"""

__version__ = "0.1.0"

import argparse
import collections
import logging
import re
import urlparse

logger = logging.getLogger(__name__)

# mappings are regexp -> format_string
# they are tried in order, so be careful!
URLMatch = collections.namedtuple('URLMatch', 'src_regexp dest_format')
known_mappings = [
    URLMatch('hg\.mozilla\.org/gaia-l10n/(?P<locale>[^/]+)',
             'git.mozilla.org/releases/l10n/%(locale)s/gaia.git'),
    URLMatch('android\.git\.linaro\.org', 'git.mozilla.org/external/linaro'),
    URLMatch('android\.googlesource\.com', 'git.mozilla.org/external/aosp'),
    URLMatch('codeaurora\.org', 'git.mozilla.org'),
    # URLMatch('github\.com/mozilla', 'git.mozilla.org/%(prefix)s%(paths)s'),
    URLMatch('github\.com/mozilla-b2g', 'git.mozilla.org/b2g'),
    URLMatch('github\.com/(?P<account>[^/]+)/(?P<path>.*)',
             'git.mozilla.org/external/%(account)s/%(path)s'),
    URLMatch('sprdsource\.spreadtrum\.com:8085/b2g/android',
             'git.mozilla.org/external/sprd-aosp/')
]


class MirrorMapperException(Exception):
    pass


class MirrorPolicyViolation(MirrorMapperException):
    pass


class MirrorUpstreamUnsupported(MirrorMapperException):
    pass


class MirrorNewUpstream(MirrorMapperException):
    pass


def is_url_supported(split_result):
    required_fields = ('scheme', 'netloc', 'path')
    forbidden_fields = ('query', 'fragment', 'username', 'password')
    for f in required_fields:
        if split_result.__getattribute__(f) is '':
            raise MirrorUpstreamUnsupported("missing URL element '%s'" % f)
    for f in forbidden_fields:
        # optional forbidden fields default to None, some empty string
        if split_result.__getattribute__(f) not in ['', None]:
            raise MirrorUpstreamUnsupported("unsupported URL element '%s'" % f)


def get_mirror_name(url, prefix=None):
    """ return our mirror name, if knowable
    """
    parts = urlparse.urlsplit(url)
    is_url_supported(parts)
    if parts.hostname is 'git.mozilla.org':
        # this is true for a new mirror, but a mapping does exist
        # these are pass through for manifest mapping
        raise MirrorPolicyViolation('no mirroring from mozilla')
    else:
        upstream = parts.netloc + parts.path
        for mapping in known_mappings:
            match = re.match(mapping.src_regexp, upstream)
            if match:
                new_host = mapping.dest_format % match.groupdict()
                if new_host != mapping.dest_format:
                    # a substitution was made, don't reuse old path
                    parts = parts._replace(path='')
                mapped_parts = parts._replace(scheme='https', netloc=new_host)
                mapped_url = mapped_parts.geturl()
                if not mapped_url.endswith('.git'):
                    mapped_url += '.git'
                break
        else:
            raise MirrorNewUpstream('Upstream host %s unknown, manual '
                                    'intervention required' % parts.hostname)
    return mapped_url


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
            print "%s -> %s" % (u, mapped_url)
        except MirrorMapperException as e:
            logger.warning("{} on {}".format(e.message, u))
    return 0


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    sys.exit(main(sys.argv))
