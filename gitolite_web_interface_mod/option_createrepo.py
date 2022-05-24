"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""
import cgi
import os
import re
import subprocess
import sys
import tempfile

from .output import output
from .clone_push_repo import clone_admin_repo, commit_push_config_to_repo

def option_createrepo(
        ssh_gitolite_user, ssh_host=None, gitolite_cmd='gitolite',
        gitolite_home='/srv/gitolite',
        gitolite_admin_repo='repositories/gitolite-admin.git'):
    user = os.environ.get('REMOTE_USER')
    if os.environ['QUERY_STRING'] in ['createrepo']:
        content = '<h1>create repository</h1>\n'
        content += '<h2>Your current groups are:</h2>\n'
        new_env = os.environ.copy()
        new_env["HOME"] = gitolite_home
        my_cmd = gitolite_cmd + ' list-memberships -u ' + user
        cpi = subprocess.run(
            my_cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=3, check=True, env=new_env)
        groups = cpi.stdout.splitlines()
        names = set()
        for i, group in enumerate(groups):
            groups[i] = group[1:]
            access, username = groups[i].split(b'_', maxsplit=1)
            if access == b'owner':
                names.add(username)
        names = list(names)
        names.sort()
        content += '<pre>' + cpi.stdout.decode() + '</pre>\n'
        content += '<h2>You can create repositories for:</h2>\n'
        content += '<pre>' + b','.join(names).decode() + '</pre>\n'
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
        for username in names:
            content += '<option>' + username.decode() + '</option>'
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
    elif os.environ['QUERY_STRING'] == 'createrepo1':
        form = cgi.FieldStorage()
        if ('project' not in form) or ('name' not in form):
            #output(
            #    title='ERROR', content=str(form))
            output(
                title='ERROR', content='<p>no post data</p>')
            sys.exit(0)
        content = '<h1>repository created</h1>\n'
        new_env = os.environ.copy()
        new_env["HOME"] = gitolite_home
        my_cmd = gitolite_cmd + ' list-memberships -u ' + user
        cpi = subprocess.run(
            my_cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=3, check=True, env=new_env)
        groups = cpi.stdout.splitlines()
        names = set()
        for i, group in enumerate(groups):
            groups[i] = group[1:]
            access, username = groups[i].split(b'_', maxsplit=1)
            if access == b'owner':
                names.add(username)
        if not form["project"].value.encode() in names:
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
        with tempfile.TemporaryDirectory() as tmpdir:
            (conf_path, gitolite_config) = \
              clone_admin_repo(
                  tmpdir,
                  gitolite_home, gitolite_admin_repo, user)
            repo_group_def = False
            repo_group_def_index = None
            repo_def = False
            iterartion = 0
            for line in gitolite_config:
                if line.startswith(repo_group):
                    repo_group_def_index = iterartion
                    if bool(re.findall(
                            r'^%s = %s$' % (repo_group, repo_path),
                            line)):
                        repo_group_def = True
                elif (line.startswith('repo ') and
                      (repo_group in line)):
                    repo_def = True
                if repo_group_def and repo_def:
                    break
                iterartion += 1
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
            # if DEBUG:
            #    content += '<h3>debug</h3>'
            #    content += '<pre>'
            #    content += '\n'.join(gitolite_config)
            #    content += '</pre>'
            with open(conf_path, 'w') as fd:
                fd.write('\n'.join(gitolite_config) + '\n')
            content += \
              commit_push_config_to_repo(
                  tmpdir,
                  gitolite_home, gitolite_admin_repo,
                  message='added repo ' + repo_path)
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
