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
    # The first set of mappings are special cases which already exist. They
    # only match the complete string (hence the '$' at end of pattern).
    #
    # While the mapper would never generate a new repo for these, they are
    # included here both as a) documentation and b) aid in regression testing
    # (these case are handled, and thus don't need exceptions maintained in the
    # test code).
    URLMatch('github\.com/mozilla-b2g/gaia$',
             'git.mozilla.org/releases/gaia.git'),
    URLMatch('github\.com/mozilla/Negatus$',
             'git.mozilla.org/b2g/Negatus.git'),
    URLMatch('android\.git\.linaro.org/git-ro/platform/prebuilt\.git$',
             'git.mozilla.org/external/linaro/platform/prebuilt.git'),

    # The following mappings are 'generic' for each server - these are the
    # onese we expect to encounter in practice.
    URLMatch('hg\.mozilla\.org/gaia-l10n/(?P<locale>[^/]+)',
             'git.mozilla.org/releases/l10n/%(locale)s/gaia.git'),
    URLMatch('android\.git\.linaro\.org/(?P<path>.*)',
             'git.mozilla.org/external/linaro/%(path)s'),
    URLMatch('android\.googlesource\.com/(?P<path>.*)',
             'git.mozilla.org/external/aosp/%(path)s'),
    URLMatch('codeaurora\.org/quic/la/(?P<path>.*)',
             'git.mozilla.org/external/caf/%(path)s'),
    URLMatch('codeaurora\.org/(?P<path>.*)',
             'git.mozilla.org/external/caf/%(path)s'),
    URLMatch('github\.com/mozilla/build-(?P<path>.*)',
             'git.mozilla.org/build/%(path)s'),
    URLMatch('github\.com/mozilla-b2g/(?P<path>.*)',
             'git.mozilla.org/b2g/%(path)s'),
    URLMatch('github\.com/(?P<account>[^/]+)/(?P<path>.*)',
             'git.mozilla.org/external/%(account)s/%(path)s'),
    URLMatch('sprdsource\.spreadtrum\.com:8085/b2g/android/(?P<path>.*)',
             'git.mozilla.org/external/sprd-aosp/%(path)s'),
    URLMatch('sprdsource\.spreadtrum\.com:8085/b2g/(?P<path>.*)',
             'git.mozilla.org/external/sprd-b2g/%(path)s'),
    URLMatch('gerrit\.googlesource\.com/(?P<path>.*)',
             'git.mozilla.org/external/google/gerrit/%(path)s'),
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
                logger.debug("using mapping '%s'", mapping.src_regexp)
                new_host = mapping.dest_format % match.groupdict()
                mapped_parts = parts._replace(scheme='https', netloc=new_host,
                                              path='')
                mapped_url = mapped_parts.geturl()
                if not mapped_url.endswith('.git'):
                    mapped_url += '.git'
                break
            else:
                logger.debug(" skip mapping '%s'", mapping.src_regexp)
        else:
            raise MirrorNewUpstream('Upstream host %s unknown, manual '
                                    'intervention required' % parts.hostname)
    return mapped_url
