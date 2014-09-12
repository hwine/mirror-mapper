from __future__ import print_function

__version__ = "0.1.0"

import collections
import logging
import re
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

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
            raise MirrorUpstreamUnsupported("missing URL element '{}'".
                                            format(f))
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
