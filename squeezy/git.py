""" Functions calling out to git binary. """
import envoy


class GitError(Exception):
    """ Git error. """
    pass


def _exec_no_raise(cmd):
    return envoy.run([cmd])


def _exec(cmd, **kwargs):
    res = envoy.run([cmd], **kwargs)
    if res.status_code != 0:
        raise GitError(res.std_err)
    return res


def ls_branch(include_remote=False):
    """ Returns the list of branches of current repo. """
    cmd = ['git', 'branch', '--no-color', '--no-column']
    if include_remote:
        cmd.append('--all')
    res = _exec(cmd)
    return [l.split()[-1] for l in res.std_out.splitlines()]


def check_branch_exists(branch_name):
    """ Returns boolean indicating if given branch exists. """
    cmd = ['git', 'rev-parse', '--verify', '--quiet', branch_name]
    return _exec_no_raise(cmd).status_code == 0


def status(porcelain=True):
    """ Executes git status command. """
    cmd = ['git', 'status']
    if porcelain:
        cmd.append('--porcelain')
    return _exec(cmd)


def is_clean_workdir():
    """ Returns boolean indicating if current working copy is clean. """
    res = status()
    return len(res.std_out.splitlines()) == 0


def checkout(*args):
    """ Performs git checkout passing arguments to git. """
    cmd = ['git', 'checkout'] + list(args)
    return _exec(cmd)


def commits(*args):
    """ Lists commit hashes by git log with given arguments. """
    cmd = ['git', 'log', '--oneline', '--no-abbrev-commit'] + list(args)
    res = _exec(cmd)
    if res.status_code != 0:
        raise GitError(res.std_err)
    return [l.split()[0] for l in res.std_out.splitlines()]


def interactive_rebase(sha, script):
    """ Performs git rebase. """
    cmd = ['git', 'rebase', '--interactive', '{}~'.format(sha)]
    res = _exec(cmd, env={'GIT_SEQUENCE_EDITOR': script})
    if res.status_code != 0:
        raise GitError(res.std_err)
    return res


def merge_squash(branch_name):
    """ Performs `git merge --squash <branch_name>`. """
    cmd = ['git', 'merge', '--squash', branch_name]
    return _exec_no_raise(cmd)


def commit(*args):
    """ Performs `git commit`. """
    cmd = ['git', 'commit'] + list(args)
    return _exec(cmd)
