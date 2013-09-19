from fabric.colors import green, red
from fabric.contrib.files import exists
from fabric.operations import run
from fabric.utils import abort


def _check_r_res(res, o_exp, g_exp, p_exp):
    """
    Checks remote resource exists, owner, group and permission
    """
    print green("Checking %s owner, group, permissions. "
        "Expected: %s, %s, %s" % (res, o_exp, g_exp, p_exp))
    if exists(res):
        resp = run('stat -c %%U,%%G,%%a %s' % res)
        o_act, g_act, p_act = map(str.strip, resp.split(','))
        if o_act != o_exp or g_act != g_exp or p_act != p_exp:
            abort(red("Resource %s params: %s. Expected: %s" % (
                res, (o_act, g_act, p_act), (o_exp, g_exp, p_exp))))
        print green("Resource %s checking passed" % res)
    else:
        abort(red("Resource %s is not exists" % res))


def _fix_r_res(res, o, g, p):
    """
    Sets remote resource owner, group and permissions
    """
    print green("Setting remote resource %s parameters %s, %s, %s" %
        (res, o, g, p))
    run('chown %s:%s %s' % (o, g, res))
    run('chmod %s %s' % (p, res))
