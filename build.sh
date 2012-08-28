#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd )"

#Set environment
export PATH=$DIR/.env/bin:$PATH
export PYTHONPATH=$DIR/src/

#Check, enable, update virtualenv
if [ -d ".env" ]; then
    true
else
    virtualenv .env --no-site-packages
fi
. $DIR/.env/bin/activate

$DIR/.env/bin/python setup.py sdist --dist-dir /var/lib/jenkins/userContent/helixcore
#$DIR/.env/bin/python setup.py register -r local sdist upload -r local
#т.к. нельзя(пока?) переписать в PyPI пакет одной и той же версии, то проводим замену файлов
cp /var/lib/jenkins/userContent/helixcore/helixcore-*.tar.gz /home/chishop/media/dists/
