#!/usr/bin/env python3
"""
Author: Daniel Mohr.
Date: 2021-05-11, 2021-06-08, 2021-06-09, 2021-07-27 (last change).
License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

[gitolite](https://gitolite.com/gitolite/) is a great tool to manage
[git](https://git-scm.com/) repositories and get access by ssh.

There are also possibilities to use http for transport, e. g.:

  * https://gitolite.com/gitolite/http
  * https://gitolite.com/gitolite/contrib/ssh-and-http

With [sskm](https://gitolite.com/gitolite/contrib/sskm) there is also a tool
available to manage ssh keys for the user over ssh.

But until now there is no possibility to manage ssh keys over http.

Therefore this script *gitolite_web_interface.py* should give the possibility
to add ssh keys over http. After this sskm over ssh can be used to further
manage the keys.

Especially if you have already a directory service (e. g. LDAP)
for managing user accounts with password, this script
*gitolite_web_interface.py* provides the possibility to let the users
manage their ssh keys in a gitolite environment.

To use this script, you have to adapt the following few keys of the global
variable CONFIG:

  * gitolite_wrapper_script
  * ssh_gitolite_user
  * ssh_host
  * only_https

Further there is an option to let the user create repositories (no wild repo).

You can also overide the CONFIG variable.
"""

import cgi
import os
import subprocess
import sys
import tempfile

DEBUG = True

CONFIG = {
    # define the script, which is called when using gitolite over http
    # as described in: https://gitolite.com/gitolite/contrib/ssh-and-http
    'gitolite_wrapper_script': '/var/www/bin/gitolite-suexec-wrapper.sh',
    # define the hosting user of your gitolite installation
    # as described in https://gitolite.com/gitolite/quick_install.html
    'ssh_gitolite_user': 'gitolite',
    # define the ssh host as used in a possible ssh comand;
    # if None, it will be set to HTTP_HOST:
    'ssh_host': None,
    # define if only https traffic is accaptable (True or False):
    'only_https': True,
    # define the gitolite command used on command line
    'gitolite_cmd': 'gitolite',
    # define the gitolite home directory
    'gitolite_home': '/srv/gitolite',
    # define the gitolite admin repository path in the gitolite home
    'gitolite_admin_repo': 'repositories/gitolite-admin.git',
    # define, which options should be provided:
    'provided_options': {
        'help': True,
        'info': True,
        'mngkey': True,
        'createrepo': False}
}
# special setting:
CONFIG['gitolite_wrapper_script'] = \
    '/srv/www/bin/gitolite-suexec-wrapper.sh'
CONFIG['ssh_gitolite_user'] = 'git'
CONFIG['provided_options'] = {
    'help': True,
    'info': True,
    'mngkey': True,
    'createrepo': True}

# pylint: disable=missing-docstring


def output(title='test page', content='<h1>test</h1>'):
    print('Content-type:text/html\n')
    print('<html>')
    print('<head>')
    print('<title>' + title + '</title>')
    print('<meta http-equiv="Cache-Control" ' +
          'content="no-cache, no-store, must-revalidate"/>')
    print('<meta http-equiv="Pragma" content="no-cache"/>')
    print('<meta http-equiv="Expires" content="0"/>')
    print('</head>')
    print('<body>')
    print(content)
    print('<hr>')
    print('<p align="right"><a href="' + os.environ['SCRIPT_NAME'] +
          '">back to start</a></p>')
    print('</body>')
    print('</html>')


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
        provided_options=None):
    if provided_options is None:
        provided_options = {'help': True, 'info': True, 'mngkey': True,
                            'createrepo': True}
    # run only with https
    if (only_https and (('HTTPS' not in os.environ) or
                        (os.environ['HTTPS'] != 'on'))):
        output(title='error: no HTTPS',
               content='error: HTTPS is not used')
        sys.exit(0)
    # run only, if REMOTE_USER is known
    if 'REMOTE_USER' not in os.environ.keys():
        output(title='error: no REMOTE_USER',
               content='error: no REMOTE_USER known')
        sys.exit(0)
    user = os.environ.get('REMOTE_USER')
    # run only, if SCRIPT_NAME is known
    if 'SCRIPT_NAME' not in os.environ.keys():
        output(title='error: no SCRIPT_NAME',
               content='error: no SCRIPT_NAME')
        sys.exit(0)
    # run only, if HTTP_HOST is known
    if 'HTTP_HOST' not in os.environ.keys():
        output(title='error: no HTTP_HOST',
               content='error: no HTTP_HOST')
        sys.exit(0)
    sskm_help_link = '<p>sskm help: <a href="'
    sskm_help_link += 'https://gitolite.com/gitolite/contrib/sskm.html" '
    sskm_help_link += 'target="_blank">'
    sskm_help_link += 'changing keys -- self service key management</a></p>'
    if (('QUERY_STRING' in os.environ.keys()) and
            (bool(os.environ['QUERY_STRING']))):
        if ((os.environ['QUERY_STRING'] in ['help', 'info']) and
                (provided_options[os.environ['QUERY_STRING']])):
            cpi = subprocess.run(
                [gitolite_wrapper_script],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, timeout=3, check=True)
            content = '<h1>gitolite command (' + \
                os.environ['QUERY_STRING'] + ')</h1>\n'
            content += '<h2>Output:</h2>'
            content += '<pre>' + cpi.stdout.decode() + '</pre>'
            title = 'gitolite command (' + os.environ['QUERY_STRING'] + ')'
            output(content=content, title=title)
            sys.exit(0)
        elif (os.environ['QUERY_STRING'].startswith('mngkey') and
              provided_options['mngkey']):
            # manage ssh keys with sskm
            if ((os.environ['QUERY_STRING'] in ['mngkey', 'mngkey0']) and
                    provided_options['mngkey']):
                content = '<h1>manage ssh keys with sskm</h1>\n'
                content += sskm_help_link
                content += '<h2>Your current keys are:</h2>'
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = "sskm list"
                cpi = subprocess.run(
                    [gitolite_wrapper_script],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, timeout=3, check=False, env=new_env)
                content += '<pre>' + cpi.stdout.decode() + '</pre>'
                # create form
                content += '<h2>Your new ssh key:</h2>'
                content += '<p>Paste your public ssh key, which is typically '
                content += 'in the file "~/.ssh/id_ed25519.pub". '
                content += 'Do not provide your private ssh key -- '
                content += 'this would compromise your identity!</p>'
                content += '<p>'
                content += '<form method="POST" action="' + \
                    os.environ.get('SCRIPT_NAME') + '?mngkey1">'
                content += '<table>'
                content += '<tr>'
                content += '<td>name (e. g. "@computer"): </td>'
                content += '<td><input type="text" name="name" size="42"></td>'
                content += '</tr><tr>'
                content += \
                    '<td>public key (e. g. content of id_ed25519.pub): </td>'
                content += \
                    '<td><input type="text" name="pubkey" size="100"></td>'
                content += '</tr>'
                content += '</table>'
                content += '<input type="submit" value="submit"> '
                content += '<input type="reset" value="reset">'
                content += '</p>'
                output(title='manage ssh keys with sskm', content=content)
            elif (os.environ['QUERY_STRING'] == 'mngkey1' and
                  provided_options['mngkey']):
                if ssh_host is None:
                    ssh_host = os.environ['HTTP_HOST']
                form = cgi.FieldStorage()
                if ('name' not in form) or ('pubkey' not in form):
                    output(title='ERROR', content='<p>no post data</p>')
                    sys.exit(0)
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = 'sskm add ' + form["name"].value
                cpi = subprocess.run(
                    [gitolite_wrapper_script],
                    input=form["pubkey"].value.encode(),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True,
                    timeout=3, check=False, env=new_env)
                content = '<h1>manage ssh keys with sskm (added)</h1>'
                content += sskm_help_link
                content += '<h2>Output:</h2>'
                content += '<pre>' + cpi.stdout.decode() + '</pre>'
                content += '<h2>Your ssh keys:</h2>'
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = "sskm list"
                cpi = subprocess.run(
                    [gitolite_wrapper_script],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, timeout=3, check=False, env=new_env)
                content += '<pre>' + cpi.stdout.decode() + '</pre>'
                content += '<h2>Next Step:</h2>'
                content += '<p>Now you have to verify your ssh key (by ssh). '
                content += 'You cannot continue with the web interface.</p>'
                content += '<p>Example:<pre>'
                content += 'ssh -i .ssh/newkey ' + ssh_gitolite_user + '@' + \
                    ssh_host + ' sskm confirm-add ' + form["name"].value
                content += '</pre></p>'
                content += '<h2>Cancel:</h2>'
                content += '<p>You can cancel with something like:\n<pre>'
                content += 'ssh ' + ssh_gitolite_user + '@' + ssh_host + \
                    ' sskm undo-add ' + form["name"].value
                content += '</pre>\n'
                content += '<a href="' + os.environ.get('SCRIPT_NAME') + \
                    '?sskm undo-add ' + form["name"].value
                content += '">cancel ' + form["name"].value + ' by web</a>'
                content += '</p>'
                output(title='manage ssh keys with sskm (added)',
                       content=content)
            sys.exit(0)
        elif (os.environ['QUERY_STRING'].startswith('sskm%20undo-add%20') and
              provided_options['mngkey']):
            content = '<h1>manage ssh keys with sskm (' + \
                os.environ['QUERY_STRING'].replace('%20', ' ') + ')</h1>\n'
            content += sskm_help_link
            content += '<h2>Output:</h2>'
            cpi = subprocess.run(
                [gitolite_wrapper_script],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                timeout=3, check=True)
            content += '<pre>' + cpi.stdout.decode() + '</pre>'
            content += '<h2>Your current keys are:</h2>'
            new_env = os.environ.copy()
            new_env["QUERY_STRING"] = "sskm list"
            cpi = subprocess.run(
                [gitolite_wrapper_script],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, timeout=3, check=False, env=new_env)
            content += '<pre>' + cpi.stdout.decode() + '</pre>'
            title = os.environ['QUERY_STRING'].replace('%20', ' ')
            output(content=content, title=title)
            sys.exit(0)
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
            if ((os.environ['QUERY_STRING'] in ['createrepo']) and
                    provided_options['createrepo']):
                content = '<h1>create repositoy</h1>\n'
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
                for i in range(len(groups)):
                    groups[i] = groups[i][1:]
                    access, username = groups[i].split(b'_', maxsplit=1)
                    if access == b'owner':
                        names.add(username)
                content += '<pre>' + cpi.stdout.decode() + '</pre>\n'
                content += '<h2>You can create repositories for:</h2>\n'
                content += '<pre>' + b','.join(names).decode() + '</pre>\n'
                content += '<h2>New repo:</h2>\n'
                content += '<p>The repository path on the server will be: '
                content += '[project directory] + "/" + [repository name]</p>'
                # create form
                content += '<p>'
                content += '<form method="POST" action="' + \
                    os.environ.get('SCRIPT_NAME') + '?createrepo1">'
                content += '<table>'
                content += '<tr>'
                content += '<td>project directory: </td>'
                content += '<td>'
                content += '<select name="project" size="1">'
                for username in names:
                    content += '<option>' + username.decode() + '</option>'
                content += '</select>'
                content += '</td>'
                content += '</tr><tr>'
                content += '<tr>'
                content += '<td>repository name: </td>'
                content += '<td><input type="text" name="name" size="42"></td>'
                content += '</tr><tr>'
                content += '</table>'
                content += '<input type="submit" value="submit"> '
                content += '<input type="reset" value="reset">'
                content += '</p>'
                output(title='create repo', content=content)
                sys.exit(0)
            elif (os.environ['QUERY_STRING'] == 'createrepo1' and
                  provided_options['createrepo']):
                form = cgi.FieldStorage()
                if ('project' not in form) or ('name' not in form):
                    output(title='ERROR', content=str(form))
                    output(title='ERROR', content='<p>no post data</p>')
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
                for i in range(len(groups)):
                    groups[i] = groups[i][1:]
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
                    git_cmd = 'git clone ' + os.path.join(gitolite_home,
                                                          gitolite_admin_repo)
                    admin_repo_name = os.path.splitext(
                        os.path.split(gitolite_admin_repo)[1])[0]
                    subprocess.run(
                        git_cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=tmpdir, timeout=3, check=True,
                        env=new_env)
                    git_cmd = 'git config user.name "' + user + '"'
                    subprocess.run(
                        git_cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
                        timeout=3, check=True, env=new_env)
                    git_cmd = 'git config user.email "' + user + '@'
                    git_cmd += os.environ.get('HTTP_HOST') + '"'
                    subprocess.run(
                        git_cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
                        timeout=3, check=True, env=new_env)
                    conf_path = os.path.join(
                        tmpdir, admin_repo_name, 'conf/gitolite.conf')
                    with open(conf_path, 'r') as fd:
                        gitolite_config = fd.read().splitlines()
                    repo_group_def = False
                    repo_group_def_index = None
                    repo_def = False
                    iterartion = 0
                    for line in gitolite_config:
                        if line.startswith(repo_group):
                            repo_group_def_index = iterartion
                            if repo_path in line:
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
                            gitolite_config.insert(repo_group_def_index,
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
                        fd.write('\n'.join(gitolite_config))
                    git_cmd = 'git add conf/gitolite.conf'
                    cpi = subprocess.run(
                        git_cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
                        timeout=3, check=True, env=new_env)
                    if DEBUG:
                        content += '<h3>debug</h3>'
                        content += '<pre>'
                        content += git_cmd
                        content += '</pre>'
                        content += '<pre>'
                        content += cpi.stdout.decode()
                        content += '</pre>'
                    git_cmd = 'git commit -m "added repo ' + repo_path + '"'
                    cpi = subprocess.run(
                        git_cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
                        timeout=3, check=True, env=new_env)
                    if DEBUG:
                        content += '<h3>debug</h3>'
                        content += '<pre>'
                        content += git_cmd
                        content += '</pre>'
                        content += '<pre>'
                        content += cpi.stdout.decode()
                        content += '</pre>'
                    git_cmd = 'git push'
                    git_cmd = 'pwd;ls;cat .git/config;git push'
                    git_cmd = 'gitolite push'
                    cpi = subprocess.run(
                        git_cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
                        timeout=3, check=False, env=new_env)
                    if DEBUG:
                        content += '<h3>debug</h3>'
                        content += '<pre>'
                        content += git_cmd
                        content += '</pre>'
                        content += '<pre>'
                        content += cpi.stdout.decode()
                        content += '</pre>'
                        content += '<pre>'
                        content += cpi.stderr.decode()
                        content += '</pre>'
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
                output(title='repo created', content=content)
                sys.exit(0)
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
    output(title='start', content=content)
    sys.exit(0)


if __name__ == "__main__":
    # call the main program:
    gitolite_web_interface(
        CONFIG['gitolite_wrapper_script'],
        CONFIG['ssh_gitolite_user'],
        ssh_host=CONFIG['ssh_host'],
        only_https=CONFIG['only_https'],
        gitolite_cmd=CONFIG['gitolite_cmd'],
        gitolite_home=CONFIG['gitolite_home'],
        gitolite_admin_repo=CONFIG['gitolite_admin_repo'],
        provided_options=CONFIG['provided_options'])
