#!/usr/bin/env python3
"""
Author: Daniel Mohr.
Date: 2021-05-11 (last change).
License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

[gitolite](https://gitolite.com/gitolite/) is a great tool to manage git
repositories and get access by ssh.

There are also possibilities to use http for transport, e. g.:

  * https://gitolite.com/gitolite/http
  * https://gitolite.com/gitolite/contrib/ssh-and-http

With [sskm](https://gitolite.com/gitolite/contrib/sskm) there is also a tool
available to manage ssh keys for the user over ssh.

But until now there is no possibility to manage ssh keys over http.

Therefore this script *gitolite_web_interface.py* should give the possibility
to add ssh keys over http. After this sskm over ssh can be used to further
manage the keys.
"""

import cgi
import os
import subprocess


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
    print('<p align="right"><a href="/www/">back to start</a></p>')
    print('</body>')
    print('</html>')


def cmdlink(name, additionalinfo=''):
    ret = '<li><a href="' + os.environ.get('SCRIPT_NAME') + '?'
    ret += name + '">' + name + '</a>' + additionalinfo + '</li>'
    return ret


def main():
    # run only with https
    if ((not 'HTTPS' in os.environ) or
            (os.environ['HTTPS'] != 'on')):
        output(title='error: no HTTPS',
               content='error: HTTPS is not used')
        exit(0)
    if not 'REMOTE_USER' in os.environ.keys():
        output(title='error: no REMOTE_USER',
               content='error: no REMOTE_USER known')
        exit(0)
    sskm_help_link = '<p>sskm help: <a href="'
    sskm_help_link += 'https://gitolite.com/gitolite/contrib/sskm.html" '
    sskm_help_link += 'target="_blank">'
    sskm_help_link += 'changing keys -- self service key management</a></p>'
    user = os.environ.get('REMOTE_USER')
    if not 'REQUEST_URI' in os.environ.keys():
        exit(3)
    if (('QUERY_STRING' in os.environ.keys()) and
            (len(os.environ['QUERY_STRING']) > 0)):
        if os.environ['QUERY_STRING'] in ['help', 'info']:
            cp = subprocess.run(
                ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,  # cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            content = '<h1>gitolite command (' + \
                os.environ['QUERY_STRING'] + ')</h1>\n'
            content += '<h2>Output:</h2>'
            content += '<pre>' + cp.stdout.decode() + '</pre>'
            title = 'gitolite command (' + os.environ['QUERY_STRING'] + ')'
            output(content=content, title=title)
            exit(0)
        elif os.environ['QUERY_STRING'].startswith('mngkey'):
            # manage ssh keys with sskm
            if os.environ['QUERY_STRING'] in ['mngkey', 'mngkey0']:
                content = '<h1>manage ssh keys with sskm</h1>\n'
                content += sskm_help_link
                content += '<h2>Your current keys are:</h2>'
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = "sskm list"
                cp = subprocess.run(
                    ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True,
                    timeout=3, check=False, env=new_env)
                content += '<pre>' + cp.stdout.decode() + '</pre>'
                content += '</pre>'
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
            elif os.environ['QUERY_STRING'] == 'mngkey1':
                form = cgi.FieldStorage()
                if ('name' not in form) or ('pubkey' not in form):
                    output(title='ERROR', content='<p>no post data</p>')
                    exit(0)
                #content = "<p>name:", form["name"].value
                #content += "<p>pubkey:", form["pubkey"].value
                # output(content=content)
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = 'sskm add ' + form["name"].value
                cp = subprocess.run(
                    ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                    input=form["pubkey"].value.encode(),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True,
                    timeout=3, check=False, env=new_env)
                content = '<h1>manage ssh keys with sskm (added)</h1>'
                content += sskm_help_link
                content += '<h2>Output:</h2>'
                content += '<pre>' + cp.stdout.decode() + '</pre>'
                content += '<h2>Your ssh keys:</h2>'
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = "sskm list"
                cp = subprocess.run(
                    ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True,
                    timeout=3, check=False, env=new_env)
                content += '<pre>' + cp.stdout.decode() + '</pre>'
                content += '</pre>'
                content += '<h2>Next Step:</h2>'
                content += '<p>Now you have to verify your ssh key (by ssh). '
                content += 'You cannot continue with the webinterface.</p>'
                content += '<p>Example:<pre>'
                content += 'ssh -i .ssh/newkey gitolite@' + \
                    os.environ['HTTP_HOST'] + \
                    ' sskm confirm-add ' + form["name"].value
                content += '</pre></p>'
                content += '<h2>Cancel:</h2>'
                content += '<p>You can cancel with something like:\n<pre>'
                content += 'ssh gitolite@' + \
                    os.environ['HTTP_HOST'] + \
                    ' sskm undo-add ' + form["name"].value
                content += '</pre>\n'
                content += '<a href="/www/?sskm undo-add ' + form["name"].value
                content += '">cancel ' + form["name"].value + ' by web</a>'
                content += '</p>'
                output(title='manage ssh keys with sskm (added)',
                       content=content)
            exit(0)
        elif os.environ['QUERY_STRING'].startswith('sskm%20undo-add%20'):
            content = '<h1>manage ssh keys with sskm (' + \
                os.environ['QUERY_STRING'].replace('%20', ' ') + ')</h1>\n'
            content += sskm_help_link
            content += '<h2>Output:</h2>'
            cp = subprocess.run(
                ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                timeout=3, check=True)
            content += '<pre>' + cp.stdout.decode() + '</pre>'
            content += '<h2>Your current keys are:</h2>'
            new_env = os.environ.copy()
            new_env["QUERY_STRING"] = "sskm list"
            cp = subprocess.run(
                ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                timeout=3, check=False, env=new_env)
            content += '<pre>' + cp.stdout.decode() + '</pre>'
            title = os.environ['QUERY_STRING'].replace('%20', ' ')
            output(content=content, title=title)
            exit(0)
        else:
            output(
                title='ERROR',
                content='<p>do not understand"' +
                os.environ['QUERY_STRING'] + '"</p>')
            exit(0)
    content = ''
    content += '<h1>Options</h1>\n'
    content += '<p><ul>'
    content += cmdlink('help')
    content += cmdlink('info')
    content += cmdlink('mngkey')
    output(title='start', content=content)
    exit(0)


if __name__ == "__main__":
    main()
