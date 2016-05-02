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



------------------------
Config variables
------------------------
``reports.strict_access = true|false`` - if set to True, then just sysadmin allowed to visit /reports pages. Default value: False


``statsresources.report_map = REPORT_NAME:FORMAT:PACKAGE_ID`` - allows multiple values(each from new line). Configure endpoints of `paster statsresources generate` command
For example::
   statsresources.report_map =
      dataset_creation:json:1234-1234-1234-1234
      dataset_creation:csv:1234-1234-1234-1234

Run::

   paster statsresources list -c path/to/config/file.ini #show list of all stat resoruces that will be generated
   paster statsresources generate -c path/to/config/file.ini #create/update corresponding resources
   
-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.statsresources --cover-inclusive --cover-erase --cover-tests

