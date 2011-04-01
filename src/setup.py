from setuptools import setup

from __version__ import version


setup(
    name = 'helixcore',
    version = version,
    url = 'http://helixproject/',
    author = 'Helixproject Developers',
    author_email = 'developers@helixproject',
    description = 'A core library of Helixproject',
    download_url = 'http://helixproject/releases/helixcore/1.0.0/helixcore-1.0.0.tar.gz',
    install_requires = ['python-cjson', 'iso8601', 'psycopg2', 'eventlet', 'pytz'],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
    ],
)
