"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import cgi
import os
import sys
import tempfile

from .output import output
from .myform import generate_form_select_list, extract_set_from_form
from .clone_push_repo import clone_admin_repo, commit_push_config_to_repo
from .get_groups_from_gitolite import get_groups_from_gitolite

# pylint: disable=missing-docstring


def _option_creategroup(gitolite_home, creategroup_format):
    content = '<h1>create group</h1>\n'
    content += '<h2>New group:</h2>\n'
    content += '<p>The repository path on the server will be: '
    content += '[group/project directory] + "/" + ' + \
        '[repository name]</p>'
    dav_users_path = os.path.join(gitolite_home, 'dav_users')
    if os.path.exists(dav_users_path):
        with open(dav_users_path, 'r') as fd:
            all_users = (x.strip() for x in fd.readlines())
        # check for valid user names (at the moment very simple):
        all_users = list(filter(bool, all_users))
    # create form
    content += '<p>'
    content += '<form method="POST" action="' + \
        os.environ.get('SCRIPT_NAME') + '?creategroup1">'
    # group/project directory and name
    content += '<table>'
    content += '<td>group/project name: </td>'
    content += '<td><input type="text" name="name" size="42" ' + \
        'placeholder="type your new group/project name"></td>'
    content += '</tr><tr>'
    content += '</table>\n'
    content += '<h3>Select members:</h3>\n'
    content += '<p>'
    content += 'You are always an owner.'
    if ((creategroup_format == 'select') or
            ((creategroup_format == 'auto') and
             (len(all_users) > 5))):
        content += ' You can select many ones by pressing [Ctrl]. '
        content += 'Or you can select a block by pressing [Shift].'
    content += '</p>'
    # select owners:
    content += '<table>'
    content += '<tr>'
    content += '<td>select owners: </td>'
    content += '<td>'
    content += generate_form_select_list(
        creategroup_format, all_users,
        os.environ.get('REMOTE_USER'), key='owner')
    content += '</td>'
    content += '</tr>\n'
    # select writers:
    content += '<tr>'
    content += '<td>select writers:</td>'
    content += '<td>'
    content += generate_form_select_list(
        creategroup_format, all_users, '', key='writer')
    content += '</td>'
    content += '</tr>\n'
    # select readers:
    content += '<tr>'
    content += '<td>select readers:</td>'
    content += '<td>'
    content += generate_form_select_list(
        creategroup_format, all_users, '', key='reader')
    content += '</td>'
    content += '</tr>\n'
    content += '</table>\n'
    # submit buttons
    content += '<input type="submit" value="submit"> '
    content += '<input type="reset" value="reset">'
    content += '</p>'
    output(
        title='create group',
        content=content,
        style='<style>td {vertical-align:top;}</style>')
    sys.exit(0)


def _option_creategroup1_check(gitolite_cmd, gitolite_home, form):
    if 'name' not in form:
        content = '<h1>ERROR</h1>'
        content += '<pre>\n'
        content += str(form)
        content += '\n</pre>\n'
        content += '<h1>ERROR</h1>'
        content += '<p>no post data</p>'
        output(
            title='ERROR', content=content)
        sys.exit(0)
    groups = get_groups_from_gitolite(gitolite_cmd, gitolite_home)
    group_exists = False
    for kind in ['owner', 'writer', 'reader']:
        kindnewgroup = '@' + kind + '_' + form["name"].value
        if kindnewgroup.encode() in groups:
            group_exists = True
            break
    if group_exists:
        content = '<p>group "'
        content += form["name"].value + '" '
        content += 'exists already. You cannot create it.</p>'
        output(
            title='ERROR',
            content=content)
        sys.exit(0)


def _option_creategroup1(
        ssh_host, gitolite_cmd, gitolite_home, gitolite_admin_repo):
    form = cgi.FieldStorage()
    _option_creategroup1_check(gitolite_cmd, gitolite_home, form)
    if ssh_host is None:
        ssh_host = os.environ['HTTP_HOST']
    content = '<h1>group "%s" created</h1>\n' % form["name"].value
    ownerlist = extract_set_from_form(
        form, key='owner', default=[os.environ.get('REMOTE_USER')])
    writerlist = extract_set_from_form(
        form, key='writer')
    readerlist = extract_set_from_form(
        form, key='reader')
    content += '<h2>config lines:</h2>\n'
    content += '<pre>\n'
    group_def_str = ''
    if ownerlist:
        group_def_str += '@owner_' + form["name"].value + ' = '
        group_def_str += ' '.join(ownerlist) + '\n'
    if writerlist:
        group_def_str += '@writer_' + form["name"].value + ' = '
        group_def_str += ' '.join(writerlist) + '\n'
    if readerlist:
        group_def_str += '@reader_' + form["name"].value + ' = '
        group_def_str += ' '.join(readerlist) + '\n'
    content += group_def_str
    content += '</pre>\n'
    with tempfile.TemporaryDirectory() as tmpdir:
        (conf_path, gitolite_config) = \
            clone_admin_repo(
                tmpdir,
                gitolite_home, gitolite_admin_repo,
                os.environ.get('REMOTE_USER'))
        gitolite_config.append('')
        gitolite_config.append(group_def_str)
        with open(conf_path, 'w') as fd:
            fd.write('\n'.join(gitolite_config) + '\n')
        content += \
            commit_push_config_to_repo(
                tmpdir,
                gitolite_home, gitolite_admin_repo,
                message='added group ' + form["name"].value)
    output(
        title='group created', content=content)
    sys.exit(0)


def option_creategroup(
        ssh_host=None, gitolite_cmd='gitolite', gitolite_home='/srv/gitolite',
        gitolite_admin_repo='repositories/gitolite-admin.git',
        creategroup_format='auto'):
    if os.environ['QUERY_STRING'].startswith('creategroup'):
        # create a group for users in gitolite
        # group names are like [access]_[name]
        # [access] defines the possibilities:
        #   owner: Can create repositories in the directory [name].
        #          (And get the permission RW+ in gitolite.)
        #   writer: Can read and write repositories
        #           in the directory [name].
        #           (This is the permission RW in gitolite.)
        #   reader: Can read repositories in the directory [name].
        #           (This is the permission R in gitolite.)
        # We will only create groups in gitolite, which are not empty.
        if os.environ['QUERY_STRING'] in ['creategroup']:
            _option_creategroup(
                gitolite_home, creategroup_format)
            # sys.exit(0)
        elif os.environ['QUERY_STRING'] == 'creategroup1':
            _option_creategroup1(
                ssh_host, gitolite_cmd, gitolite_home, gitolite_admin_repo)
            # sys.exit(0)
