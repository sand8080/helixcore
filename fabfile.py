import os
import sys

from fabric.api import env, run
from fabric.colors import green, red
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import prefix, settings
from fabric.decorators import hosts
from fabric.utils import abort
from fabric.operations import local


def _project_dir():
    return os.path.realpath(os.path.dirname(__file__))


sys.path.append(os.path.join(_project_dir(), 'src'))
from helixcore.deploy import _fix_r_res, _check_r_res


def _get_env():
    p_dir = _project_dir()
    env_path = os.path.join(p_dir, '.env')
    if os.path.exists(env_path):
        return env_path
    else:
        abort(red("Environment not found"))


print green("Configuring helixcore production environment")
env.proj_ha_root_dir = '/opt/helixproject/helixauth'
env.proj_ha_dir = os.path.join(env.proj_ha_root_dir, 'helixcore')
env.proj_ha_dir_owner = 'helixauth'
env.proj_ha_dir_group = 'helixauth'
env.proj_ha_dir_perms = '700'
env.proj_hw_root_dir = '/opt/helixproject/helixweb'
env.proj_hw_dir = os.path.join(env.proj_hw_root_dir, 'helixcore')
env.proj_hw_dir_owner = 'helixweb'
env.proj_hw_dir_group = 'helixweb'
env.proj_hw_dir_perms = '700'
env.proj_s_root_dir = '/opt/helixproject/sentry'
env.proj_s_dir = os.path.join(env.proj_s_root_dir, 'helixcore')
env.proj_s_dir_owner = 'sentry'
env.proj_s_dir_group = 'sentry'
env.proj_s_dir_perms = '700'

env.rsync_exclude = ['.*', '*.sh', '*.pyc',
    'fabfile.py', 'pip-requirements-dev.txt']
env.pythonpath = 'export PYTHONPATH="%s"' % _project_dir()
print green("Helixcore production environment configured")


def run_tests():
    with prefix(env.pythonpath):
        print green("Starting tests")
        with settings(warn_only=True):
            t_run = os.path.join(_get_env(), 'bin', 'nosetests')
            t_dir = os.path.join(_project_dir(), 'src', 'helixcore', 'test')
            result = local('%s %s' % (t_run, t_dir))
        if result.failed:
            abort(red("Tests failed"))
        else:
            print green("Tests passed")


@hosts('helixauth@10.100.60.134')
def sync_helixauth():
    print green("Helixcore files synchronization to helixauth started")
    run_tests()
    print green("Project files synchronization")

    rsync_project(env.proj_ha_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    _fix_r_res(env.proj_ha_dir, env.proj_ha_dir_owner, env.proj_ha_dir_group,
        env.proj_ha_dir_perms)
    _check_r_res(env.proj_ha_dir, env.proj_ha_dir_owner, env.proj_ha_dir_group,
        env.proj_ha_dir_perms)
    print green("Helixcore files to helixauth synchronization complete")


@hosts('helixweb@10.100.60.134')
def sync_helixweb():
    print green("Helixcore files synchronization to helixweb started")
    run_tests()
    print green("Project files synchronization")

    rsync_project(env.proj_hw_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    _fix_r_res(env.proj_hw_dir, env.proj_hw_dir_owner, env.proj_hw_dir_group,
        env.proj_hw_dir_perms)
    _check_r_res(env.proj_hw_dir, env.proj_hw_dir_owner, env.proj_hw_dir_group,
        env.proj_hw_dir_perms)
    print green("Helixcore files to helixweb synchronization complete")


@hosts('sentry@10.100.60.134')
def sync_sentry():
    print green("Helixcore files synchronization to sentry started")
#    run_tests()
    print green("Project files synchronization")

    rsync_project(env.proj_s_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    _fix_r_res(env.proj_s_dir, env.proj_s_dir_owner, env.proj_s_dir_group,
        env.proj_s_dir_perms)
    _check_r_res(env.proj_s_dir, env.proj_s_dir_owner, env.proj_s_dir_group,
        env.proj_s_dir_perms)
    print green("Helixcore files to sentry synchronization complete")
