from setuptools import setup, find_packages


VERSION = (0, 1, 1, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))


setup(
    name = 'helixcore',
    version = __versionstr__,
    url = 'http://helixproject/',
    author = 'Helixproject Developers',
    author_email = 'developers@helixproject',
    description = 'A core library of Helixproject',
    packages = find_packages(),
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
