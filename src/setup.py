from setuptools import setup

from helixcore.version import __version__


setup(
    name = 'helixcore',
    version = __version__,
    url = 'http://helixproject/',
    author = 'Helixproject Developers',
    author_email = 'developers@helixproject',
    description = 'A core library of Helixproject',
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
