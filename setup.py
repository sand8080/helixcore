import os
from distutils.core import setup


VERSION = (0, 1, 1, 0)
__versionstr__ = '.'.join(map(str, VERSION))


def subdirs(dir):
    sub_dirs = [os.path.join(dir, o) for o in os.listdir(dir)]
    return filter(os.path.isdir, sub_dirs)


def all_subdirs(dir):
    result = []
    to_check = subdirs(dir)
    while len(to_check) > 0:
        to_check_copy = list(to_check)
        to_check = []
        for d in to_check_copy:
            sub_d = subdirs(d)
            to_check += sub_d
            result.append(d)
    def clean_path(p):
        p = p.replace(dir, '')
        return p.strip(os.path.sep)
    return map(clean_path, result)


def packages(dir):
    sub_dirs = all_subdirs(dir)
    return map(lambda x: x.replace(os.path.sep, '.'), sub_dirs)


def clean_tests(pkgs):
    return filter(lambda x: 'test' not in x, pkgs)


cur_dir = os.path.realpath(os.path.dirname(__file__))
name = 'helixcore'
pkgs = clean_tests(packages(os.path.join(cur_dir, 'src')))

setup(
    name=name,
    version=__versionstr__,
    url='http://helixproject/',
    author='Helixproject Developers',
    author_email='developers@helixproject',
    description='A core library of Helixproject',
    package_dir={'': 'src'},
    packages=pkgs,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
    ]
)
