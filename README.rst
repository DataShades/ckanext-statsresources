.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/smotornyuk/ckanext-statsresources.svg?branch=master
    :target: https://travis-ci.org/smotornyuk/ckanext-statsresources

.. image:: https://coveralls.io/repos/smotornyuk/ckanext-statsresources/badge.png?branch=master
  :target: https://coveralls.io/r/smotornyuk/ckanext-statsresources?branch=master

=============
ckanext-statsresources
=============

Reports with different stats from your CKAN instance

------------
Requirements
------------

https://github.com/datagovuk/ckanext-report


------------------------
Development Installation
------------------------

To install ckanext-statsresources for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/smotornyuk/ckanext-statsresources.git
    cd ckanext-statsresources
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.statsresources --cover-inclusive --cover-erase --cover-tests

