===============================
mirror-mapper
===============================

.. image:: http://img.shields.io/travis/hwine/mirror-mapper/master.png
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/hwine/mirror-mapper

.. See: http://www.appveyor.com/docs/status-badges

   image:: https://ci.appveyor.com/api/projects/status/<security-token>/branch/master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/hwine/mirror-mapper

.. image:: http://img.shields.io/coveralls/hwine/mirror-mapper/master.png
    :alt: Coverage Status
    :target: https://coveralls.io/r/hwine/mirror-mapper

.. image:: https://readthedocs.org/projects/mirror-mapper/badge/?style=flat
    :target: https://readthedocs.org/projects/mirror-mapper
    :alt: Documentation Status

Map upstream repo url to mirror location on git.mozilla.org for b2g
projects.

* Free software: `Mozilla License`__

__ https://www.mozilla.org/MPL/

Installation
============

::

    pip install git+https://github.com/hwine/mirror-mapper.git

Documentation
=============

https://mirror-mapper.readthedocs.org/

Development
===========

To run the all tests run::

    tox

Requirements
------------

Developing on this project requires your environment to  have these
minimal dependencies:

* Tox_ - for running the tests
* Setuptools_ - for building the package, wheels etc. Now-days
  Setuptools is widely available, it shouldn't pose a problem :)
* Sphinx_ - for updating the documentation

Note: the layout for this project came from the Cookiecutter_
template https://github.com/ionelmc/cookiecutter-pylibrary-minimal.
      
.. _Travis-CI: http://travis-ci.org/
.. _Tox: http://testrun.org/tox/
.. _Sphinx: http://sphinx-doc.org/
.. _Coveralls: https://coveralls.io/
.. _ReadTheDocs: https://readthedocs.org/
.. _Setuptools: https://pypi.python.org/pypi/setuptools
.. _Pytest: http://pytest.org/
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
