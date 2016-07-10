#!/usr/bin/env python
""" Entry point module. """
from __future__ import print_function, unicode_literals

import argparse
import sys

import git


def fatal(error, code=1):
    """ Prints error message to stderr and exits with error code. """
    message = error if isinstance(error, basestring) else error.message
    print(message, file=sys.stderr)
    sys.exit(code)


def _parse_args():
    parser = argparse.ArgumentParser(description='Easy `git merge --squash`')
    parser.add_argument('source_branch', type=unicode,
                        help='The name of the branch that will be merged.')
    parser.add_argument('dest_branch', type=unicode,
                        help='The name of the branch that the source_branch '
                        'will be merged into.')
    return parser.parse_args()


def entry_point():
    """ Console script entry point. """
    args = _parse_args()
    try:
        merge(args.source_branch, args.dest_branch)
    except git.GitError as exc:
        return fatal(exc)


def merge(source_branch, dest_branch):
    """ Performs the squash-merge. """
    if not git.check_branch_exists(source_branch):
        return fatal('Source branch does not exist.')
    if not git.check_branch_exists(dest_branch):
        return fatal('Destination branch does not exist.')
    if not git.is_clean_workdir():
        return fatal('Current working copy should be clean in order to '
                     'perform merge.')

    git.checkout(dest_branch)

    merge_commit = _get_previous_merge_commit(source_branch, dest_branch)
    if merge_commit:
        print('Branch {source} has already been merged into {dest}. '
              'Deleting the previous merge commit.'
              ''.format(source=source_branch, dest=dest_branch))
        _delete_commit(merge_commit)

    res = git.merge_squash(source_branch)
    if res.status_code != 0:
        return fatal('Automatic merge failed.\n'
                     'Run `git status` to see the conflicts.\n'
                     'Run `git reset --merge` to abort merge.')

    git.commit('--file=.git/SQUASH_MSG')
    print('Merged {source} into {dest}.'
          ''.format(source=source_branch, dest=dest_branch))


def _get_first_commit(source_branch, dest_branch):
    """ Returns SHA of first commit in the log of branch difference. """
    source_commits = git.commits('{}..{}'.format(dest_branch, source_branch),
                                 '--reverse')
    if len(source_commits) == 0:
        return fatal('Nothing to merge.', code=2)
    return source_commits[0]


def _get_previous_merge_commit(source_branch, dest_branch):
    """
    Tries to find if the branch has been previously merged.

    Since the `merge --squash` is used, there is no real merge-commit, and we
    can only guess by log messages.
    """
    sha = _get_first_commit(source_branch, dest_branch)
    merge_commits = git.commits(dest_branch,
                                '--extended-regexp',
                                '--all-match',
                                "--grep=^Squashed commit of the following:$",
                                "--grep=^commit {}$".format(sha))
    return merge_commits[0] if len(merge_commits) > 0 else None


def _delete_commit(sha):
    """
    Removes the given commit from the branch's log.

    **Unsafe** because modifies history.
    """
    git.interactive_rebase(sha,
                           script='sed --in-place --expression="'
                           '/pick {}/ s/pick/drop/"'.format(sha[0:7]))


if __name__ == '__main__':
    entry_point()
