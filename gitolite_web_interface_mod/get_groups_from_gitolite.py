"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import os
import subprocess

# pylint: disable=missing-docstring


def get_groups_from_gitolite(gitolite_cmd, gitolite_home):
    new_env = os.environ.copy()
    new_env["HOME"] = gitolite_home
    my_cmd = gitolite_cmd + ' list-groups'
    cpi = subprocess.run(
        my_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=True, env=new_env)
    return cpi.stdout.splitlines()


def _member_groups_from_gitolite(gitolite_cmd, gitolite_home):
    new_env = os.environ.copy()
    new_env["HOME"] = gitolite_home
    my_cmd = gitolite_cmd + ' list-memberships -u ' + \
        os.environ.get('REMOTE_USER')
    cpi = subprocess.run(
        my_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=True, env=new_env)
    return cpi.stdout.splitlines(), cpi.stdout


def get_own_groups_from_gitolite(gitolite_cmd, gitolite_home):
    groups, gitolite_stdout = _member_groups_from_gitolite(
        gitolite_cmd, gitolite_home)
    own_groups = set()
    for i, group in enumerate(groups):
        groups[i] = group[1:]
        access, username = groups[i].split(b'_', maxsplit=1)
        if access == b'owner':
            own_groups.add(username)
    return own_groups, gitolite_stdout
