import paver.virtual
from paver.easy import *
from paver.setuputils import (find_packages, install_distutils_tasks)


install_distutils_tasks()


VERSION = (0, 1, 1, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

require = ['python-cjson', 'iso8601', 'psycopg2', 'eventlet', 'pytz']

options(
    setup=Bunch(
        name='helixcore',
        version=__versionstr__,
        url='http://helixproject/',
        author='Helixproject Developers',
        author_email='developers@helixproject',
        description='A core library of Helixproject',
        package_dir={'': 'src'},
        packages=find_packages('src'),
        test_suite='nose.collector',
        install_requires=require,
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.6',
            'Operating System :: POSIX',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta',
        ]
    ),
    virtualenv=Bunch(
        packages_to_install=require,
        script_name='bootstrap.py',
        paver_command_line=None,
        no_site_packages=True,
        dest_dir='venv'
    ),
)


@task
@needs(['minilib', 'generate_setup', 'bootstrap', 'setuptools.command.sdist'])
def sdist():
    pass


@task
@needs(['setuptools.command.clean'])
def clean():
    for p in map(path, ('setup.py', 'bootstrap.py', 'paver-minilib.zip', 'build', 'dist')):
        if p.exists():
            if p.isdir():
                p.rmtree()
            else:
                p.remove()