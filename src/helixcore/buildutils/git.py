import os


def comments_num(repo_path):
    cwd = os.path.realpath(os.path.dirname(os.curdir))
    os.chdir(repo_path)
    commits = os.popen('git log --pretty=format:"%H [%an] %s"').read().split('\n')
    res = len(commits)
    os.chdir(cwd)
    return res
