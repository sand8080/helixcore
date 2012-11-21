import os

from fabric.api import env, run
from fabric.colors import green, red
from fabric.contrib.project import rsync_project
from fabric.context_managers import prefix, settings
from fabric.decorators import hosts
from fabric.utils import abort
from fabric.operations import local


def _project_dir():
    return os.path.realpath(os.path.dirname(__file__))


def _get_env():
    p_dir = _project_dir()
    env_path = os.path.join(p_dir, '.env')
    if os.path.exists(env_path):
        return env_path
    else:
        abort(red("Environment not found"))


print green("Configuring helixcore production environment")
env.proj_root_dir = '/opt/helixproject'
env.rsync_exclude = ['.*', '*.sh', '*.pyc',
    'fabfile.py', 'pip-requirements-dev.txt']
env.activate = '. %s/bin/activate' % _get_env()
print green("Helixcore production environment configured")


def run_tests():
    with prefix(env.activate):
        print green("Starting tests")
        with settings(warn_only=True):
            t_run = os.path.join(_get_env(), 'bin', 'nosetests')
            t_dir = os.path.join(_project_dir(), 'src', 'helixcore', 'test')
            result = local('%s %s' % (t_run, t_dir))
        if result.failed:
            abort(red("Tests failed"))
        else:
            print green("Tests passed")


def _check_rd(rd, o_exp, g_exp, p_exp):
    if exists(rd):
        res = run('stat -c %%U,%%G,%%a %s' % rd)
        o_act, g_act, p_act = map(str.strip, res.split(','))
        if o_act != o_exp or g_act != g_exp or p_act != p_exp:
            abort(red("Directory %s params: %s. Expected: %s" % (
                rd, (o_act, g_act, p_act), (o_exp, g_exp, p_exp))))
        print green("Directory %s checking passed" % rd)
    else:
        abort(red("Directory %s is not exists" % env.proj_dir))


def _fix_rd(rd, o, g, p):
    print green("Setting project directory parameters")
    run('chown %s:%s %s' % (o, g, rd))
    run('chmod %s %s' % (p, rd))
    print green("Checking project directory parameters")


@hosts('helixauth@78.47.11.201')
def sync_helixauth():
    print green("Helixcore files synchronization to helixauth started")
    run_tests()
    print green("Project files synchronization")
    proj_root_dir = '/opt/helixproject/helixauth'
    proj_dir = os.path.join(proj_root_dir, 'helixcore')
    proj_dir_owner = proj_dir_group = 'helixauth'
    proj_dir_perms = '700'

    rsync_project(proj_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    _fix_rd(proj_dir, proj_dir_owner, proj_dir_group,
        proj_dir_perms)
    print green("Helixcore files to helixauth synchronization complete")
