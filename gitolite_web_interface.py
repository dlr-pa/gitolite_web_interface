#!/usr/bin/env python3
"""
Author: Daniel Mohr.
Date: 2021-05-10 (last change).
License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import cgi
import os
import subprocess

# for debugging:
import cgitb
#cgitb.enable()
cgitb.enable(display=0, logdir="/tmp/foo")

def output(title='test page', content='<h1>test</h1>'):
    print('Content-type:text/html\n')
    print('<html>')
    print('<head>')
    print('<title>' + title + '</title>')
    print('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"/>')
    print('<meta http-equiv="Pragma" content="no-cache"/>')
    print('<meta http-equiv="Expires" content="0"/>')
    print('</head>')
    print('<body>')
    print(content)
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
        exit(1)
    if not 'REMOTE_USER' in os.environ.keys():
        exit(2)
    user = os.environ.get('REMOTE_USER')
    if not 'REQUEST_URI' in os.environ.keys():
        exit(3)
    if (('QUERY_STRING' in os.environ.keys()) and
        (len(os.environ['QUERY_STRING']) > 0)):
        #if os.environ['QUERY_STRING'] == 'debug':
        if os.environ['QUERY_STRING'] in ['debug', 'debug%20foo']:
            cgi.test()
            print('#######################\br')
            cgi.print_environ()
            print('#######################\br')
            cgi.print_environ_usage()
            print('#######################\br')
            for key, value in os.environ.items():
                print(key, value)
            print('#######################\br')
            print(user)
            exit(0)
        elif os.environ['QUERY_STRING'] in ['help', 'info']:
            cp = subprocess.run(
                ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, #cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            output(content='<pre>' + cp.stdout.decode() + '</pre>')
            exit(0)
        elif os.environ['QUERY_STRING'].startswith('mngkey'):
            # manage ssh keys with sskm
            if os.environ['QUERY_STRING'] in ['mngkey', 'mngkey0']:
                content = '<h1>manage ssh keys with sskm</h1>\n'
                content += '<p>help: <a href="https://gitolite.com/gitolite/contrib/sskm.html" target="_blank">changing keys -- self service key management</a></p>'
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
                content += '<p>Paste your public ssh key, which is typically in the file "~/.ssh/id_ed25519.pub" . Do not provide your private ssh key -- this would compromise your identity!</p>'
                content += '<p>'
                content += '<form method="POST" action="' + os.environ.get('SCRIPT_NAME') + '?mngkey1">'
                content += '<table>'
                content += '<tr><td>name (e. g. "@computer"): </td><td><input type="text" name="name" size="42"></td></tr>'
                content += '<tr><td>public key (e. g. content of id_ed25519.pub): </td><td><input type="text" name="pubkey" size="100"></td></tr>'
                content += '</table>'
                content += '<input type="submit" value="submit"> <input type="reset" value="reset">'
                content += '</p>'
                output(title='manage ssh keys with sskm', content=content)
            elif os.environ['QUERY_STRING'] == 'mngkey1':
                form = cgi.FieldStorage()
                if ('name' not in form) or ('pubkey' not in form):
                    output(title='ERROR', content='<p>no post data</p>')
                    exit(0)
                #content = "<p>name:", form["name"].value
                #content += "<p>pubkey:", form["pubkey"].value
                #output(content=content)
                new_env = os.environ.copy()
                new_env["QUERY_STRING"] = 'sskm add ' + form["name"].value
                cp = subprocess.run(
                    ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                    input=form["pubkey"].value.encode(),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True,
                    timeout=3, check=False, env=new_env)
                content = '<h1>manage ssh keys with sskm (added)</h1>'
                content += '<p>help: <a href="https://gitolite.com/gitolite/contrib/sskm.html" target="_blank">changing keys -- self service key management</a></p>'
                content += '<h2>output</h2>'
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
                content += 'ssh -i .ssh/newkey gitolite@' + os.environ['HTTP_HOST'] + ' sskm confirm-add ' + form["name"].value
                content += '</pre></p>'
                content += '<p>You can cancel with something like:<pre>'
                content += 'ssh gitolite@' + os.environ['HTTP_HOST'] + ' sskm undo-add ' + form["name"].value
                content += '</pre></p>'
                output(title='manage ssh keys with sskm (added)',
                       content=content)
            exit(0)
        elif os.environ['QUERY_STRING'] in ['sskm', 'sskm%20list', 'sskm%20undo-add']:
            cp = subprocess.run(
                ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, #cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            output(content='<pre>' + cp.stdout.decode() + '</pre>')
            exit(0)
        elif os.environ['QUERY_STRING'].startswith('sskm%20add'):
            # ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB8nHJJFw2TcxJFHqw+7+m4V3RlEjx/tHbo34/qJZa1S mohr@zev
            new_env = os.environ.copy()
            new_env["QUERY_STRING"] = "sskm add @key4"
            cp = subprocess.run(
                ['/var/www/bin/gitolite-suexec-wrapper.sh'],
                input=b'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIK372hEvEeIiMZzgHV8TG9tNB2OZs7SnjbXSQGBtE5Dv mohr@zev',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, #cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=False)
            output(content='<pre>' + cp.stdout.decode() + '</pre>')
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
    content += cmdlink('debug')
    content += cmdlink('help')
    content += cmdlink('info')
    content += cmdlink('mngkey')
    content += '<h2>sskm (<a href="https://gitolite.com/gitolite/contrib/sskm.html" target="_blank">help changing keys</a>) </h2>\n'
    content += '<p><ul>'
    content += cmdlink('sskm list')
    content += cmdlink('sskm add')
    content += cmdlink('sskm undo-add')
    content += '</ul></p>'
    content += '</ul></p>'
    output(title='start', content=content)
    exit(0)


if __name__ == "__main__":
    main()
