#!/usr/bin/env python

"""
    read all the job*_cmds files, output the upstream -> downstream urls

    This is designed to read legacy configuration files, and extract the
    mappings for each repository. The intention is to produce the file
    'current_mappings.txt' used in regression testing.
"""

import abc
import logging
import argparse
import ConfigParser
import fileinput
import os
import re

logger = logging.getLogger(__name__)

jobline = re.compile(r'''\s*                    # leading space
                     "(?P<method>[^:]+):        # hg or git
                     \S+/(?P<work_dir>[^/]+)"   # local path
                     \s+"(?P<dest>.*)"          # destinations
                     \s*''', re.VERBOSE)


class GenericConfigFile(ConfigParser.ConfigParser, object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, conf_file, *args, **kwargs):
        super(GenericConfigFile, self).__init__(*args, **kwargs)
        self.read(conf_file)

    @abc.abstractmethod
    def upstream_url(self):
        # return upstream repository URL, must be overridden
        return

    @abc.abstractmethod
    def downstream_url(self, name):
        # return downstream URL for specified name, must be overridden
        return


class HGConfigFile(GenericConfigFile):
    def __init__(self, config_dir, *args, **kw):
        config_file = os.path.join(config_dir, 'hgrc')
        super(HGConfigFile, self).__init__(config_file, *args, **kw)

    def upstream_url(self):
        return self.get('paths', 'default')

    def downstream_url(self, remote_name):
        value = self.get("paths", remote_name)
        return value


class SlsFlo(object):
    # Strip leading space File like object
    def __init__(self, flo):
        self._flo = flo

    def readline(self):
        line = self._flo.readline()
        if line != '':
            # readline uses '' to mean end of file, don't mess with it
            line = line.lstrip()
            if line == '':
                line = '\n'
        logger.debug("line '%s'", line)
        return line

    def __getattr__(self, attr):
        return getattr(self._flo, attr)


class GitConfigFile(GenericConfigFile):
    def __init__(self, config_dir, *args, **kw):
        config_file = os.path.join(config_dir, 'config')
        super(GitConfigFile, self).__init__(config_file, *args, **kw)

    def read(self, file_name):
        # git config files have leading spaces, wrap readline to remove that
        flo = SlsFlo(open(file_name))
        return self.readfp(flo)

    def upstream_url(self):
        return self.get('remote "origin"', 'url')

    def downstream_url(self, remote_name):
        section = 'remote "{}"'.format(remote_name)
        value = None
        for key in ('pushurl', 'url'):
            try:
                value = self.get(section, key)
                break
            except ConfigParser.NoOptionError:
                pass
        return value


def get_config_file(vcs_type, work_dir):
    if vcs_type == 'hg':
        cf = HGConfigFile(work_dir)
    elif vcs_type == 'git':
        cf = GitConfigFile(work_dir)
    else:
        raise ValueError("unknown vcs type: '%s'" % vcs_type)
    return cf


def get_upstream_url(parent_dir, method, work_dir, dest):
    config_dir = os.path.join(parent_dir, work_dir)
    config_file = get_config_file(method, config_dir)
    return config_file.upstream_url()


def get_mirror_url(parent_dir, work_dir, dest, **kwargs):
    config_dir = os.path.join(parent_dir, work_dir)
    config_file = get_config_file('git', config_dir)
    return config_file.downstream_url('git.m.o')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_files", help='job file names', metavar="FILE",
                        default=None, nargs='*')
    args = parser.parse_args()
    for line in fileinput.input(args.job_files, mode='r'):
        # if first line of new file, cd to same directory as file so
        # configurations lookups will be relative
        if fileinput.isfirstline():
            new_file = fileinput.filename()
            job_dir = os.path.dirname(new_file)
            logger.debug("new file '%s' in '%s'", new_file, job_dir)
        match = jobline.match(line)
        if match:
            mdict = match.groupdict()
            upstream = get_upstream_url(job_dir, **mdict)
            if 'git.m.o' in mdict['dest']:
                downstream = get_mirror_url(job_dir, **mdict)
                print "{} -> {}".format(upstream, downstream)
            else:
                logger.debug("no git.m.o mirror for '%s'", upstream)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    main()
