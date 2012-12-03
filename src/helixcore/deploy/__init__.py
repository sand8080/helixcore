from fabric.colors import green, red
from fabric.contrib.files import exists
from fabric.operations import run
from fabric.utils import abort


def _check_rd(rd, o_exp, g_exp, p_exp):
    """
    Checks remote directory exists, owner, group and permission
    """
    print green("Checking directory %s owner, group, permissions. "
        "Expected: %s, %s, %s" % (rd, o_exp, g_exp, p_exp))
    if exists(rd):
        res = run('stat -c %%U,%%G,%%a %s' % rd)
        o_act, g_act, p_act = map(str.strip, res.split(','))
        if o_act != o_exp or g_act != g_exp or p_act != p_exp:
            abort(red("Directory %s params: %s. Expected: %s" % (
                rd, (o_act, g_act, p_act), (o_exp, g_exp, p_exp))))
        print green("Directory %s checking passed" % rd)
    else:
        abort(red("Directory %s is not exists" % rd))


def _fix_rd(rd, o, g, p):
    """
    Sets remote directory owner, group and permissions
    """
    print green("Setting project directory parameters")
    run('chown %s:%s %s' % (o, g, rd))
    run('chmod %s %s' % (p, rd))
    print green("Checking project directory parameters")
