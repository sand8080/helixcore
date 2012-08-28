#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd )"

#Set environment
export PATH=$DIR/.env/bin:$PATH
export PYTHONPATH=./src/

#Check, enable, update virtualenv
if [ -d ".env" ]; then
    true
else
    virtualenv .env --no-site-packages
fi
. .env/bin/activate
pip install -r pip-requires.txt
pip install -r pip-requires-ci.txt

find . -name \*.pyc -delete

#Run unittest with coverage report
python src/helixcore_tests.py --verbose --nocapture --with-xunit --xunit-file=reports/nosetests.xml --force-zero-status --with-coverage
coverage xml -i
mv coverage.xml reports

#Get violation data
#Pylint settings
#Disabled messages
# Brain-dead errors regarding standard language features
#   W0142 = *args and **kwargs support
#   W0403 = Relative imports
# Pointless whinging
#   R0201 = Method could be a function
#   W0212 = Accessing protected attribute of client class
#   W0613 = Unused argument
#   W0232 = Class has no __init__ method
#   R0903 = Too few public methods
#   C0301 = Line too long
#   R0913 = Too many arguments
#   C0103 = Invalid name
#   R0914 = Too many local variables
# PyLint's module importation is unreliable
#   F0401 = Unable to import module
#   W0402 = Uses of a deprecated module
# Already an error when wildcard imports are used
#   W0614 = Unused import from wildcard
# Sometimes disabled depending on how bad a module is
#   C0111 = Missing docstring
# Disable the message(s) with the given id(s).
# NOTE: the Stack Overflow thread uses disable-msg, but as of pylint 0.23.0, disable= seems to work.
pylint --ignore=.svn --ignore=.git --ignore=test -f parseable --disable=W0142,W0403,R0201,W0212,W0613,W0232,R0903,W0614,C0111,C0301,R0913,C0103,F0401,W0402,R0914 helixcore > reports/pylint.report

pep8 src/helixcore --exclude=.svn,CVS,.bzr,.hg,.git,test > reports/pep8.report
sloccount --duplicates --wide --details src/helixcore > reports/sloccount.sc
clonedigger --cpd-output -o reports/clonedigger.xml --ignore-dir=test src/helixcore
