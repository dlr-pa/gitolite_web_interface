"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import cgi
import os
import re
import sys
import tempfile

from .output import output
from .clone_push_repo import clone_admin_repo, commit_push_config_to_repo
from .get_groups_from_gitolite import get_own_groups_from_gitolite

# pylint: disable=missing-docstring


def _option_createrepo(gitolite_cmd, gitolite_home):
    content = '<h1>create repository</h1>\n'
    #content += '<h2>Your current groups are:</h2>\n'
    own_groups, _ = get_own_groups_from_gitolite(
        gitolite_cmd, gitolite_home)
    own_groups = list(own_groups)
    own_groups.sort()
    #content += '<pre>' + gitolite_stdout.decode() + '</pre>\n'
    content += '<h2>You can create repositories for:</h2>\n'
    content += '<pre>' + b','.join(own_groups).decode() + '</pre>\n'
    content += '<h2>New repo:</h2>\n'
    content += '<p>The repository path on the server will be: '
    content += '[group/project directory] + "/" + ' + \
        '[repository name]</p>'
    # create form
    content += '<p>'
    content += '<form method="POST" action="' + \
        os.environ.get('SCRIPT_NAME') + '?createrepo1">'
    content += '<table>'
    content += '<tr>'
    content += '<td>group/project directory: </td>'
    content += '<td>'
    content += '<select name="project" size="1">'
    for groupname in own_groups:
        content += '<option>' + groupname.decode() + '</option>'
    content += '</select>'
    content += '</td>'
    content += '</tr><tr>'
    content += '<td>repository name: </td>'
    content += '<td><input type="text" name="name" size="42"></td>'
    content += '</tr>'
    content += '</table>'
    content += '<input type="submit" value="submit"> '
    content += '<input type="reset" value="reset">'
    content += '</p>'
    output(
        title='create repo', content=content)
    sys.exit(0)


def _adapt_gitolite_config(gitolite_config, repo_group, repo_path, form):
    repo_group_def = False
    repo_group_def_index = None
    repo_def = False
    iteration = 0
    for line in gitolite_config:
        if line.startswith(repo_group):
            repo_group_def_index = iteration
            if bool(re.findall(
                    r'^%s = %s$' % (repo_group, repo_path),
                    line)):
                repo_group_def = True
        elif (line.startswith('repo ') and
              (repo_group in line)):
            repo_def = True
        if repo_group_def and repo_def:
            break
        iteration += 1
    if not repo_group_def:
        repo_group_def_str = repo_group + ' = ' + repo_path
        if repo_group_def_index is not None:
            gitolite_config.insert(1 + repo_group_def_index,
                                   repo_group_def_str)
        else:
            gitolite_config.append('')
            gitolite_config.append(repo_group_def_str)
    if not repo_def:
        gitolite_config.append('')
        gitolite_config.append('repo ' + repo_group)
        gitolite_config.append(
            '    RW+ = @owner_' + form["project"].value)
        gitolite_config.append(
            '    RW = @writer_' + form["project"].value)
        gitolite_config.append(
            '    R = @reader_' + form["project"].value)
    if repo_group_def and repo_def:
        content = '<p>Repository "'
        content += repo_path + '"exists.</p>'
        output(
            title='ERROR',
            content=content)
        sys.exit(0)


def _update_gitolite_admin_repo(
        gitolite_home, gitolite_admin_repo, repo_group, repo_path, form):
    content = ''
    with tempfile.TemporaryDirectory() as tmpdir:
        (conf_path, gitolite_config) = \
            clone_admin_repo(
                tmpdir,
                gitolite_home, gitolite_admin_repo,
                os.environ.get('REMOTE_USER'))
        _adapt_gitolite_config(gitolite_config, repo_group, repo_path, form)
        with open(conf_path, 'w') as fd:
            fd.write('\n'.join(gitolite_config) + '\n')
        content += \
            commit_push_config_to_repo(
                tmpdir,
                gitolite_home, gitolite_admin_repo,
                message='added repo ' + repo_path)
    return content


def _option_createrepo1(
        ssh_gitolite_user, ssh_host, gitolite_cmd, gitolite_home,
        gitolite_admin_repo):
    form = cgi.FieldStorage()
    if ('project' not in form) or ('name' not in form):
            # output(
            #    title='ERROR', content=str(form))
        output(
            title='ERROR', content='<p>no post data</p>')
        sys.exit(0)
    content = '<h1>repository created</h1>\n'
    own_groups, _ = get_own_groups_from_gitolite(gitolite_cmd, gitolite_home)
    if not form["project"].value.encode() in own_groups:
        content = '<p>You cannot create a repo in this project "'
        content += form["project"].value.encode() + '".</p>'
        output(
            title='ERROR',
            content=content)
        sys.exit(0)
    if ssh_host is None:
        ssh_host = os.environ['HTTP_HOST']
    content += '<h2>config lines:</h2>\n'
    content += '<pre>\n'
    repo_group = '@repos_' + form["project"].value
    repo_path = form["project"].value + '/' + form["name"].value
    content += repo_group + ' = ' + repo_path + '\n'
    content += 'repo ' + repo_group + '\n'
    content += '    RW+ = @owner_' + form["project"].value + '\n'
    content += '    RW = @writer_' + form["project"].value + '\n'
    content += '    R = @reader_' + form["project"].value + '\n'
    content += '</pre>\n'
    content += _update_gitolite_admin_repo(
        gitolite_home, gitolite_admin_repo, repo_group, repo_path, form)
    content += '<h2>Repository access:</h2>\n'
    content += '<ul>'
    content += '<li><pre>git clone git+ssh://'
    content += ssh_gitolite_user + '@' + ssh_host + \
        '/' + form["project"].value + '/' + \
        form["name"].value + '</pre></li>'
    content += '<li><pre>git clone https://'
    content += os.environ['HTTP_HOST'] + \
        '/git/' + form["project"].value + '/' + \
        form["name"].value + '</pre></li>'
    content += '</ul>'
    output(
        title='repo created', content=content)
    sys.exit(0)


def option_createrepo(
        ssh_gitolite_user, ssh_host=None, gitolite_cmd='gitolite',
        gitolite_home='/srv/gitolite',
        gitolite_admin_repo='repositories/gitolite-admin.git'):
    if os.environ['QUERY_STRING'] in ['createrepo']:
        _option_createrepo(gitolite_cmd, gitolite_home)
        sys.exit(0)
    elif os.environ['QUERY_STRING'] == 'createrepo1':
        _option_createrepo1(
            ssh_gitolite_user, ssh_host, gitolite_cmd, gitolite_home,
            gitolite_admin_repo)
