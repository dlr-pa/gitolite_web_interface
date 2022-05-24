"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import cgi
import os
import subprocess
import sys
import tempfile

from .output import output
from .myform import generate_form_select_list, extract_set_from_form
from .clone_push_repo import clone_admin_repo, commit_push_config_to_repo
from .get_groups_from_gitolite import get_own_groups_from_gitolite

# pylint: disable=missing-docstring


def _option_creategroup(gitolite_cmd, gitolite_home, creategroup_format):
    content = '<h1>create group</h1>\n'
    content += '<h2>Your current groups are:</h2>\n'
    own_groups, gitolite_stdout = get_own_groups_from_gitolite(
        gitolite_cmd, gitolite_home)
    own_groups = list(own_groups)
    own_groups.sort()
    content += '<pre>' + gitolite_stdout.decode() + '</pre>\n'
    content += '<h2>You can create subgroups in:</h2>\n'
    content += '<pre>' + b'\n'.join(own_groups).decode() + '</pre>\n'
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
    content += '<tr>'
    content += '<td>group/project directory: </td>'
    content += '<td>'
    content += '<select name="project" size="1">'
    content += '<option></option>'
    for groupname in own_groups:
        content += '<option>' + groupname.decode() + '</option>'
    content += '</select>'
    content += '</td>'
    content += '</tr><tr>'
    content += '<td>group name: </td>'
    content += '<td><input type="text" name="name" size="42" ' + \
        'placeholder="group name in the group/project ' + \
        'directory as (sub)group"></td>'
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

def _option_creategroup1(
        ssh_host, gitolite_cmd, gitolite_home, gitolite_admin_repo):
    form = cgi.FieldStorage()
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
    newgroup = ''
    if 'project' in form:
        newgroup += form["project"].value + '/'
    newgroup += form["name"].value
    own_groups, _ = get_own_groups_from_gitolite(
        gitolite_cmd, gitolite_home)
    if (('project' in form) and
            (not form["project"].value.encode() in own_groups)):
        content = '<p>You cannot create a group in this project "'
        content += form["project"].value.encode() + '".</p>'
        output(
            title='ERROR',
            content=content)
        sys.exit(0)
    new_env = os.environ.copy()
    new_env["HOME"] = gitolite_home
    my_cmd = gitolite_cmd + ' list-groups'
    cpi = subprocess.run(
        my_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=True, env=new_env)
    groups = cpi.stdout.splitlines()
    group_exists = False
    for kind in ['owner', 'writer', 'reader']:
        kindnewgroup = '@' + kind + '_' + newgroup
        if kindnewgroup.encode() in groups:
            group_exists = True
            break
    if group_exists:
        content = '<p>group "'
        content += newgroup + '" '
        content += 'exists already. You cannot create it.</p>'
        output(
            title='ERROR',
            content=content)
        sys.exit(0)
    if ssh_host is None:
        ssh_host = os.environ['HTTP_HOST']
    content = '<h1>group "%s" created</h1>\n' % newgroup
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
        group_def_str += '@owner_' + newgroup + ' = '
        group_def_str += ' '.join(ownerlist) + '\n'
    if writerlist:
        group_def_str += '@writer_' + newgroup + ' = '
        group_def_str += ' '.join(writerlist) + '\n'
    if readerlist:
        group_def_str += '@reader_' + newgroup + ' = '
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
                message='added group ' + newgroup)
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
                gitolite_cmd, gitolite_home, creategroup_format)
            # sys.exit(0)
        elif os.environ['QUERY_STRING'] == 'creategroup1':
            _option_creategroup1(
                ssh_host, gitolite_cmd, gitolite_home, gitolite_admin_repo)
            # sys.exit(0)
