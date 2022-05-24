"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import os
import sys

from .output import output
from .option_help_info import option_help_info
from .option_mngkey import option_mngkey
from .option_creategroup import option_creategroup
from .option_createrepo import option_createrepo

# pylint: disable=missing-docstring

def cmdlink(name, additionalinfo=''):
    ret = '<li><a href="' + os.environ.get('SCRIPT_NAME') + '?'
    ret += name + '">' + name + '</a>' + additionalinfo + '</li>'
    return ret


def gitolite_web_interface(
        gitolite_wrapper_script,
        ssh_gitolite_user,
        ssh_host=None,
        only_https=True,
        gitolite_cmd='gitolite',
        gitolite_home='/srv/gitolite',
        gitolite_admin_repo='repositories/gitolite-admin.git',
        provided_options=None,
        creategroup_format='auto'):
    # pylint: disable=too-many-arguments,too-many-locals
    # pylint: disable=too-many-branches,too-many-statements
    if provided_options is None:
        provided_options = {'help': True, 'info': True, 'mngkey': True,
                            'creategroup': True, 'createrepo': True}
    # run only with https
    if (only_https and (('HTTPS' not in os.environ) or
                        (os.environ['HTTPS'] != 'on'))):
        output(
            title='error: no HTTPS', content='error: HTTPS is not used')
        sys.exit(0)
    # run only, if REMOTE_USER is known
    if 'REMOTE_USER' not in os.environ.keys():
        output(
            title='error: no REMOTE_USER',
            content='error: no REMOTE_USER known')
        sys.exit(0)
    # run only, if SCRIPT_NAME is known
    if 'SCRIPT_NAME' not in os.environ.keys():
        output(
            title='error: no SCRIPT_NAME', content='error: no SCRIPT_NAME')
        sys.exit(0)
    # run only, if HTTP_HOST is known
    if 'HTTP_HOST' not in os.environ.keys():
        output(
            title='error: no HTTP_HOST', content='error: no HTTP_HOST')
        sys.exit(0)
    if (('QUERY_STRING' in os.environ.keys()) and
            (bool(os.environ['QUERY_STRING']))):
        if ((os.environ['QUERY_STRING'] in ['help', 'info']) and
                (provided_options[os.environ['QUERY_STRING']])):
            option_help_info(gitolite_wrapper_script)
            # sys.exit(0)
        elif (os.environ['QUERY_STRING'].startswith('mngkey') and
              provided_options['mngkey']):
            # manage ssh keys with sskm
            option_mngkey(
                gitolite_wrapper_script, ssh_gitolite_user, ssh_host=ssh_host)
            # sys.exit(0)
        elif (os.environ['QUERY_STRING'].startswith('creategroup') and
              provided_options['creategroup']):
            option_creategroup(
                ssh_host=ssh_host, gitolite_cmd=gitolite_cmd,
                gitolite_home=gitolite_home,
                gitolite_admin_repo=gitolite_admin_repo)
            # sys.exit(0)
        elif (os.environ['QUERY_STRING'].startswith('createrepo') and
              provided_options['createrepo']):
            # create a repository based on groups (assume users are in groups)
            # We assume the group names are like [access]_[name].
            # [access] defines the possibilities:
            #   owner: Can create repositories in the directory [name].
            #          (And get the permission RW+ in gitolite.)
            #   writer: Can read and write repositories
            #           in the directory [name].
            #           (This is the permission RW in gitolite.)
            #   reader: Can read repositories in the directory [name].
            #           (This is the permission R in gitolite.)
            # With the information of a [reponame], this will become in
            # the gitolite configuration:
            #   @repos_[name] = [name]/[reponame]
            #   repo @repos_[name]
            #     RW+ = @owner_[name]
            #     RW = @writer_[name]
            #     R = @reader_[name]
            # It is possible to create many repos in the directory [name]
            # accessible by these groups.
            option_createrepo(
                ssh_gitolite_user, ssh_host=ssh_host,
                gitolite_cmd=gitolite_cmd, gitolite_home=gitolite_home,
                gitolite_admin_repo=gitolite_admin_repo)
            # sys.exit(0)
        else:
            output(
                title='ERROR',
                content='<p>do not understand"' +
                os.environ['QUERY_STRING'] + '"</p>')
            sys.exit(0)
    content = ''
    content += '<h1>Options</h1>\n'
    content += '<p><ul>'
    for cmd in provided_options.keys():
        if provided_options[cmd]:
            content += cmdlink(cmd)
    output(
        title='start', content=content)
    sys.exit(0)
