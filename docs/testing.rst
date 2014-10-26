=======
Testing
=======

Mirror-mapper has to generate URLs that are consistent with the existing
repositories. The existing repositories have a few "exception" cases,
and the like (i.e. automation happened after years of manual decisions).

To help prevent any regressions, the test suite includes the ability to
read existing mappings from a file. For the legacy vcs-sync system,
there is a script to generate the test data from the production
configuration files.

To create an updated copy of the test data file, do the following::

    hg clone http://hg.mozilla.org/users/hwine_mozilla.com/repo-sync-configs
    cd tests
    python extract_mappings.py ../repo-sync-configs/job* > current_mappings.txt
    git add current_mappings.txt
    git commit -m 'updated legacy mappings'
    cd ..
    rm -rf repo-sync-configs
